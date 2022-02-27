#  twitch-ban-tracker

Simple python app to track if specified twitch channels are banned. Will notify you once a channel gets banned or unbanned.
Quick and dirty implementation, not very sophisticated or dynamic.


## Limitations
- The Twitch API does not provide any means to identify if a channel is banned or not. If a channel is banned it simply disappears from the site and API.  
This means specifying non-existent channels or someone renaming their channel will count as a ban.
- Currently a maximum of 100 users can be checked.

## Configuration

See [config.yml.example](./config.yml.example) for example config. Config is expected to be located in `./storage/config.yml` relative to `twitch-ban-tracker.py`.

## Docker
To build the container run `./build.sh`
