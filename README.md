# Etherium Bot

This script runs a Reddit bot which replies to all comments that misspell "Ethereum" as "Etherium", saying how it should be spelled correctly :)


## Installation

The code requires the [praw](https://github.com/praw-dev/praw) module for connecting to the Reddit API, so install it first:

    pip3 install praw


## Configuration

To connect to the Reddit API as the bot user, you need to provide a `praw.ini` file with the necessary configuration. Use the included `praw.ini.example` file as the template.


## Running the bot

To run the bot, call:

    python3 etherium_bot.py


## Credits & contributing

Copyright © 2019 [Kuba Suder](https://mackuba.eu). Licensed under [WTFPL License](http://www.wtfpl.net).
