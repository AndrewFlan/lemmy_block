# Block Lemmy Communities from an entire Instance

Thank you to [Ac500's lemmy_account_sync](https://github.com/Ac5000/lemmy_account_sync) and [wescode's lemmy_migrate](https://github.com/wescode/lemmy_migrate) scripts for inspiration and guidance!

This script utilizes [Plemmy](https://github.com/tjkessler/plemmy/tree/main), a Python package for accessing the Lemmy API.

This script will gather all the communities from any supplied instances and block each one on any supplied accounts.

## Configuration

This program has two configuration files, `accounts.ini` and `blocklist.ini`.

Copy `example_accounts.ini` and `example_blocklist.ini` to the `lemmy_block` folder and rename them to `accounts.ini` and `blocklist.ini`.

You can have as many accounts and instances to block as you want. Labels in this `ini` files can be anything you want.

## Usage

Run `lemmy_block.py` after the configuration files are in place. I am using Python 3.11 and the only package you should need is [Plemmy](https://github.com/tjkessler/plemmy/tree/main)

If using `pipenv`: `pipenv sync`

Or just `pip`: `pip install plemmy`
