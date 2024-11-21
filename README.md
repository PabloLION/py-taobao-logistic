## Taobao Order History

Taobao does not offer a way to export the order history.
This script is a workaround to get the order history.
The returned value is a dictionary with the order number as the key,
and the track information as the value.
I made this for personal use, but it should be easy to adapt to other uses.

## Features

- [x] Use cookies to authenticate across sessions
- [x] Print track information in stdout
- [ ] Dedicated config file
- [ ] CLI interface
- [ ] Export more information with a dedicated class

## How to use

1. Install with [Poetry](https://python-poetry.org/)

    ```sh
    poetry install
    ```

2. Change the config in the first lines in `taobao_track/__main__.py`

3. Use poetry to execute the script

    ```sh
    poetry run taobao_track/__main__.py
    ```

## Note

- Hardcoded CSS selectors are sensitive to dynamic class name generation.
- Tested only on MacOS with Chrome.
