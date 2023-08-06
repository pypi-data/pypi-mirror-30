"""
Install a package from the local folder
"""

import shutil
import os

import click

from pypitools import common


@click.command()
def main():
    """
    Install a package from the local folder
    :return:
    """
    common.setup_main()
    config = common.ConfigData()
    dist_folder = 'dist'

    if os.path.isdir(dist_folder):
        shutil.rmtree(dist_folder)
    args = [
        '{}'.format(config.python),
        'setup.py',
        'sdist',
    ]
    if config.setup_quiet:
        args.extend([
            '--quiet',
        ])
    common.check_call_no_output(args)
    files = list(os.listdir(dist_folder))
    assert len(files) == 1, "too many files in {}".format(dist_folder)
    new_file = os.path.join(dist_folder, files[0])
    args = []
    if config.use_sudo:
        args.extend([
            'sudo',
            '-H',
        ])
    args.extend([
        '{}'.format(config.pip),
        'install',
        '--quiet',
        '--upgrade',
        new_file,
    ])
    if config.pip_quiet:
        args.extend([
            '--quiet',
        ])
    if config.install_in_user_folder:
        args.extend([
            '--user',
        ])
    common.check_call_no_output(args)


if __name__ == '__main__':
    main()
