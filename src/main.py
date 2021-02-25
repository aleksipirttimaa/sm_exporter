'''
Speech music discrimination from a stream using opus_sm exported as a prometheud metric

The input audio is received by ffmpeg

ffmpeg -i https:// ...

Analysis is performed by opus_sm, a fork of libopus that instead of encoding
audio, exports music probability measurement.

https://github.com/aleksipirttimaa/opus_sm
https://github.com/proudzhu/opus_sm
'''
import argparse
import subprocess
import time

from prometheus_client import start_http_server, Counter, Gauge



FFMPEG = "ffmpeg"
OPUS_SM = "opus_sm_demo"

DEFAULT_PORT = "9069"



def assert_available(command):
    cp = subprocess.run(('which', str(command)), stdout=subprocess.DEVNULL)
    cp.check_returncode()



class StreamAnalyzer():
    def __init__(self, url, gauge):
        self._url = str(url)
        self._gauge = gauge

        # subprocess
        self._ffmpeg = None
        self._analyzer = None

    def run(self):
        self._start = time.time()

        ffmpeg_args = [
            "-i",
            self._url,
            "-f",
            "s16le",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-loglevel",
            "error",
            "pipe:1"
        ]

        self._ffmpeg = subprocess.Popen((FFMPEG, *ffmpeg_args), stdout=subprocess.PIPE)
        self._analyzer = subprocess.Popen((OPUS_SM, "-"), stdin=self._ffmpeg.stdout, stdout=subprocess.PIPE)

        while True:
            if self._ffmpeg.poll() != None:
                # ffmpeg has terminated
                break

            # read lines from analyzer
            line = self._analyzer.stdout.readline().decode('utf-8')
            if not line:
                # opus_sm has terminated
                break

            # parse line
            split = line.split(" ", 1)
            seconds = float(split[0])
            probability = float(split[1].rstrip("\n"))

            # set gauge
            self._gauge.set(probability)

    def __del__(self):
        if self._ffmpeg:
            self._ffmpeg.kill()
        if self._analyzer:
            self._ffmpeg.kill()



if __name__ == '__main__':
    # assert commands
    assert_available(FFMPEG)
    assert_available(OPUS_SM)

    # command line
    parser = argparse.ArgumentParser()
    parser.add_argument("--listen-port", type=int, default=DEFAULT_PORT,
                        help=F"start exporter on port (default: {DEFAULT_PORT})")
    parser.add_argument("url", help="url or file passed to 'ffmpeg -i'")

    args = parser.parse_args()

    port = args.listen_port
    url = args.url

    # prometheus client
    start_http_server(port)

    gauge = Gauge("sm_music_probability", "Probability of music in stream")
    retries = Counter("sm_stream_retries", "Incremented on retry")

    while True:
        analyzer = StreamAnalyzer(url, gauge)
        analyzer.run()
        # rate limit retry
        time.sleep(5)
        retries.inc()
