# sm_exporter

Internet radio speech music discrimination using libopus and ffmpeg.

This script wraps `ffmpeg` and the analysis executable and exports the results as Prometheus metrics.

```
[icecast stream]  ->  [ffmpeg]  ->  [opus_sm]  ->  [prometheus]
                      ^^^^^^^^^^^^^^^^^^^^^^^  (sm_exporter scope)
```

You'll need a compiled `opus_sm_demo` executable and ffmpeg installed. This script forks them using submodule.

## Metrics

### Music probability

> P("Content is music")

```
# HELP sm_music_probability Probability of music in stream
# TYPE sm_music_probability gauge
sm_music_probability{url="..."} 0.999795
```

### Result instrumentation

This is a histogram measuring time between analysis results, you can use it to select an appropriate `scrape_interval`.

```
# HELP sm_analysis_result_s Instrumenting analysis executable output
# TYPE sm_analysis_result_s histogram
sm_analysis_s_bucket{le="0.005",url="..."} 26.0
  ...
sm_analysis_result_s_bucket{le="+Inf",url="..."} 791.0
sm_analysis_result_s_count{url="..."} 791.0
sm_analysis_result_s_sum{url="..."} 156.07464370007
```

### Stream retries

This counter is incremented when `ffmpeg` or `opus_sm_demo` exit, resulting in them being reinitialized.

```
# HELP sm_stream_retries_total Incremented on retry
# TYPE sm_stream_retries_total counter
sm_stream_retries_total{url="..."} 0.0
```

## opus_sm

You can find a fork of opus_sm that adds support for streaming here:

https://github.com/aleksipirttimaa/opus_sm

The build instructions in the aforementioned repository work just fine. On Debian you'll need to install some packages:

```sh
sudp apt install build-essential automake libtool
```

Just to recap building:

```sh
./autogen.sh
./configure
make
```

the resulting binary is `./opus_sm_demo`

## Running

1. Make sure you have `opus_sm_demo` and `ffmpeg`

```sh
which opus_sm_demo && which ffmpeg
```

2. Install pipenv, which is used for dependency management

```sh
python -m pip install --user pipenv
```

3. Create virtualenv and install dependencies

```sh
python -m pipenv install
```

4. run src/main.py

```sh
python -m pipenv run python src/main.py https://stream.example.com/example.m3u8
```

## Add to prometheus

Add to your `prometheus.yml`:

```
scrape_configs:
- job_name: 'speechmusic'
    scrape_interval: 1s
    static_configs:
    - targets: ['localhost:9069']
```

A good `scrape_interval` depends on the incoming stream transport and encoding, as analysis can only be performed after an entire frame of the encoded audio has been received.