"""
This script registers your project in pypi.

when registering via twine(1) you need to:
- full clean
- build wheel using setup.py
- twine register
- full clean
This method works, if you register twice it is ok.
You just need to do it once...:)

when registering via setup.py you need to:
- full clean
- python setup.py register -r pypi
- full clean
registering the same package many times works.
You just need to do it once...:)

References:
- https://packaging.python.org/distributing/

TODO:
- check if I'm already registered and don't register if that is the case.
"""
import click

from pypitools.common import ConfigData, setup_main


@click.command()
def main():
    """
    register a function on pypi or gemfury
    :return:
    """
    setup_main()
    config = ConfigData(clean=True)
    try:
        config.register()
    finally:
        config.clean_after_if_needed()


if __name__ == '__main__':
    main()
