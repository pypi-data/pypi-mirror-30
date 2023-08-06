"""
This is common pypitools functionality
"""

import configparser
import subprocess
import os
import logging

import pylogconf.core


def get_config_file() -> str:
    """
    Return the pypitools configuration file
    :return:
    """
    return os.path.expanduser('~/.pypirc')


def check_call_no_output(args) -> None:
    """
    Run a process and check that it returns an OK return code
    and has no output
    :param args:
    :return:
    """
    logger = logging.getLogger(__name__)
    logger.debug("running %s", args)
    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    (res_stdout, res_stderr) = process.communicate()
    if process.returncode:
        res_stdout = res_stdout
        res_stderr = res_stderr
        print(res_stdout, end='')
        print(res_stderr, end='')
        raise ValueError('exit code from [{}] was [{}]'.format(" ".join(args), process.returncode))


def git_clean_full() -> None:
    """
    Clean the current git repo in a strict way
    :return:
    """
    check_call_no_output([
        'git',
        'clean',
        '-qffxd',
    ])


class ConfigData:
    """
    All the configuration data of pypitools
    """
    def __init__(self, clean=False):
        """
        Construct a ConfigData object
        """
        self.upload_method = None
        self.clean_before = None
        self.clean_after = None
        self.install_in_user_folder = None
        self.use_sudo = None
        self.pip_quiet = None
        self.setup_quiet = None
        self.pip = None
        self.gemfury_user = None
        self.python = None
        self.register_method = None
        # now read the config
        self.read_config()
        if clean:
            if self.clean_before:
                git_clean_full()

    def print_config(self):
        print("upload_method = [{}]".format(self.upload_method))
        print("clean_before = [{}]".format(self.clean_before))
        print("clean_after = [{}]".format(self.clean_after))
        print("install_in_user_folder = [{}]".format(self.install_in_user_folder))
        print("use_sudo = [{}]".format(self.use_sudo))
        print("pip_quiet = [{}]".format(self.pip_quiet))
        print("setup_quiet = [{}]".format(self.setup_quiet))
        print("pip = [{}]".format(self.pip))
        print("gemfury_user = [{}]".format(self.gemfury_user))
        print("python = [{}]".format(self.python))
        print("register_method = [{}]".format(self.register_method))

    def read_config(self):
        """
        Read all configuration data
        :return:
        """
        section = "pypitools"
        # read setup.cfg config file
        config = configparser.ConfigParser()
        homedir_filename = os.path.expanduser("~/.setup.cfg")
        if os.path.isfile(homedir_filename):
            config.read(homedir_filename)
        local_filename = "setup.cfg"
        if os.path.isfile(local_filename):
            config.read(local_filename)
        self.upload_method = config.get(section, "upload_method")
        assert self.upload_method in ["setup", "twine", "gemfury"]
        self.clean_before = config.getboolean(section, "clean_before")
        self.clean_after = config.getboolean(section, "clean_after")
        self.install_in_user_folder = config.getboolean(section, "install_in_user_folder")
        self.use_sudo = config.getboolean(section, "use_sudo")
        self.pip_quiet = config.getboolean(section, "pip_quiet")
        self.setup_quiet = config.getboolean(section, "setup_quiet")
        self.pip = config.get(section, "pip")
        self.gemfury_user = config.get(section, "gemfury_user")
        self.python = config.get(section, "python")
        self.register_method = config.get(section, "register_method")
        assert self.register_method in ["setup", "twine", "upload"]

    def get_package_version(self) -> str:
        """
        Get the version of the package
        :return:
        """
        output = subprocess.check_output([
            '{}'.format(self.python),
            'setup.py',
            '--version',
        ]).decode()
        return output.rstrip()

    def get_package_fullname(self) -> str:
        """
        Get the full name of the package
        :return:
        """
        output = subprocess.check_output([
            '{}'.format(self.python),
            'setup.py',
            '--fullname',
        ]).decode()
        return output.rstrip()

    def get_package_filename(self) -> str:
        """
        Get the package filename
        :return:
        """
        return os.path.join("dist", self.get_package_fullname() + ".tar.gz")

    def upload_by_setup(self) -> None:
        """
        upload by setup.py sdist upload
        :return:
        """
        check_call_no_output([
            '{}'.format(self.python),
            'setup.py',
            'sdist',
            'upload',
            '-r',
            'pypi',
        ])

    def upload_by_twine(self) -> None:
        """
        upload by twine
        :return:
        """
        check_call_no_output([
            '{}'.format(self.python),
            'setup.py',
            'sdist',
        ])
        filename = self.get_package_filename()
        check_call_no_output([
            'twine',
            'upload',
            filename,
            # '--config-file',
            # common.config_file,
        ])

    def upload_by_gemfury(self) -> None:
        """
        upload to gemfury
        :return:
        """
        check_call_no_output([
            '{}'.format(self.python),
            'setup.py',
            'sdist',
        ])
        filename = self.get_package_filename()
        check_call_no_output([
            'fury',
            'push',
            '--as={}'.format(self.gemfury_user),
            filename,
        ])

    def upload(self) -> None:
        """
        upload via the method configured
        :return:
        """
        if self.upload_method == "setup":
            self.upload_by_setup()
        if self.upload_method == "twine":
            self.upload_by_twine()
        if self.upload_method == "gemfury":
            self.upload_by_gemfury()

    def register(self) -> None:
        """
        Register via the method configured
        :return:
        """
        if self.register_method == "twine":
            self.register_by_twine()
        if self.register_method == "setup":
            self.register_by_setup()
        if self.register_method == "upload":
            self.upload()

    def register_by_setup(self) -> None:
        """
        register via setup.py register
        :return:
        """
        check_call_no_output([
            '{}'.format(self.python),
            'setup.py',
            'register',
            '-r',
            'pypi',
        ])

    def register_by_twine(self) -> None:
        """
        register via the twine method
        :return:
        """
        check_call_no_output([
            '{}'.format(self.python),
            'setup.py',
            'bdist_wheel',
        ])

        # at this point there should be only one file in the 'dist' folder
        filename = self.get_package_filename()
        check_call_no_output([
            'twine',
            'register',
            filename,
        ])

    def clean_before_if_needed(self) -> None:
        """
        Clean the git repo if needed
        :return:
        """
        if self.clean_before:
            git_clean_full()

    def clean_after_if_needed(self) -> None:
        """
        Clean the git repo if needed
        :return:
        """
        if self.clean_after:
            git_clean_full()


def setup_main() -> None:
    """
    Method to be called at beginning of every entry point
    :return:
    """
    pylogconf.core.setup()
