#  twitch-ban-tracker

Simple python app to track if specified twitch channels are banned. Will notify you once a channel gets banned or unbanned.
Quick and dirty implementation, not very sophisticated or dynamic.

## Configuration

See [config.yml.example](./config.yml.example) for example config. Config is expected to be located in `./storage/config.yml` relative to `twitch-ban-tracker.py`.

## Docker
To build the container run `./build.sh`
