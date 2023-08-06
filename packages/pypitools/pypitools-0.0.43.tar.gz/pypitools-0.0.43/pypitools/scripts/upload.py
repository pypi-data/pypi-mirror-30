"""
This script uploads your module to where ever you configure it.
It's default is to upload to pypi but you can override by putting
a pypi.cnf file in the root of your source tree.


It does the following:
- clean
- setup.py sdist
- twine upload
- clean again

Notes:
- This script could be done via setuptools using the following:
$ python3 setup.py sdist upload -r pypi --identity="Mark Veltzer" --sign
but this has bad security implications as it sends user and password plain text.
- we use twine(1) to upload the package.
On ubuntu twine(1) is from the 'twine' official ubuntu package.

References:
- https://pypi.python.org/pypi/twine
- https://python-packaging-user-guide.readthedocs.org/en/latest/index.html
- http://peterdowns.com/posts/first-time-with-pypi.html
"""

import click

from pypitools.common import ConfigData, setup_main


@click.command()
def main():
    """
    upload a package to pypi or gemfury
    :return:
    """
    setup_main()
    config = ConfigData(clean=True)
    try:
        config.upload()
    finally:
        config.clean_after_if_needed()


if __name__ == '__main__':
    main()
