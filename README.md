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
sm_music_probability 0.999795
```

### Stream retries

This counter is incremented when `ffmpeg` or `opus_sm_demo` exit, resulting in them being reinitialized.

```
# HELP sm_stream_retries_total Incremented on retry
# TYPE sm_stream_retries_total counter
sm_stream_retries_total 0.0
```

## opus_sm

You can find a fork of opus_sm that adds support for streaming here:

https://github.com/aleksipirttimaa/opus_sm

## Running

1. Make sure you have `opus_sm_demo` and `ffmpeg`

```sh
which `opus_sm_demo` && which `ffmpeg`
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
