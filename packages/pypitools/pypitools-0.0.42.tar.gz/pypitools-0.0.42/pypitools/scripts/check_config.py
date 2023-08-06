"""
This script checks your config file
"""

import click

from pypitools import common


@click.command()
def main():
    """
    This script checks your config file and prints it out
    """
    common.setup_main()
    config_data = common.ConfigData()
    config_data.print_config()


if __name__ == '__main__':
    main()
