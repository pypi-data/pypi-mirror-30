"""This module contains the ``PackageManager`` class and related functions

It is used to search for and install packages on a given system. It also
provides a helper function ``get_package_manager`` to instantiate a
package manager from a .ini file.

The instances act as interfaces to the actual executables on the system and
they parse and run the commands as configured. There is not real package
manager implemented by platform migrator.
"""

from configparser import ConfigParser
import re
import subprocess


def get_package_manager(package_manager, extra_config_files=None):
    """Create a new package manager from name

    The function will read the default config file
    ``conf/package-managers.ini`` and any extra config files provided.
    If the package manager is defined as section in any of these files,
    a ``PackageManager`` object will be created and returned for that
    package manager.

    Args:
        :package_manager: The name of the package manager to use. It must
            be a section in one of the config files.

    Kwargs:
        :extra_config_files=None: A list of extra .ini files to read for the
            package manager configuration

    Return:
        A new ``PackageManager`` object

    Raises:
        :KeyError: If the package manager was not defined in any of the
            .ini files parsed
    """
    config = ConfigParser(interpolation=None)
    config.read('config/package-managers.ini')
    if extra_config_files:
        config.read(extra_config_files)
    if package_manager in config:
        return PackageManager(config[package_manager])
    raise KeyError('No such package manager defined: %s' % package_manager)


def parse_and_validate(config):
    """Parse and validate a package manager's configuration

    The function checks that all the required keys are present and that the
    values for the options are valid.

    Args:
        :config: A dict-like objecct that contains the raw configuration
            options for a package manager

    Return:
        A dict which contains the parsed and transformed commands for the
        package manager

    Raises:
        :KeyError: If any of the required keys is missing
        :ValueError: If an input cannot be parsed or fails validation
    """
    def replace_exec(cmd, exec_cmd):
        return (cmd.replace('%e', exec_cmd)
                if '%e' in cmd
                else cmd)

    def replace_pck(cmd, required=True):
        if required and '%p' not in cmd:
            return False
        elif '%p' not in cmd:
            return '%s %s' % (cmd, '%(pck)s')
        return cmd.replace('%p', '%(pck)s')

    def replace_str(cmd):
        return ('%s %s' % (cmd, '%(expr)s')
                if '%s' not in cmd
                else cmd.replace('%s', '%(expr)s'))

    def replace_ver(cmd, required=True):
        if required and '%v' not in cmd:
            return False
        elif '%v' not in cmd:
            return cmd
        return cmd.replace('%v', '%(ver)s')

    def validate_result_fmt(fmt):
        if '(' in fmt:
            fmt = fmt.replace('(', r'\(')
        if ')' in fmt:
            fmt = fmt.replace(')', r'\)')
        tmp_fmt = r'^%s$' % fmt.replace('%p', r'(?P<pck>\S+)')
        if '%v' not in fmt:
            return tmp_fmt
        return tmp_fmt.replace('%v', r'(?P<ver>\S+)')

    for key in ['name', 'search', 'install', 'install_version', 'result_fmt']:
        if key not in config:
            raise KeyError('%s is not present in the package manager configuration'
                           % key)

    exec_cmd = config['exec'] if 'exec' in config else config['name']
    install = replace_pck(replace_exec(config['install'], exec_cmd), False)
    install_version = replace_ver(replace_pck(replace_exec(config['install_version'], exec_cmd)))
    search = replace_str(replace_exec(config['search'], exec_cmd))
    result_fmt_regex = re.compile(validate_result_fmt(config['result_fmt']))
    return {'install': install,
            'install_version': install_version,
            'search': search,
            'result_fmt_regex': result_fmt_regex,
            'result_fmt': config['result_fmt'],
            'name': config['name'],
            'exec': exec_cmd,
           }


class PackageManager():
    """A package manager that can search and install packages

    Each instance represents a package manager that is available on the
    system. It can search for packages and also install them, with user
    confirmation. It can also list any currently installed packages.
    """

    def __init__(self, config):
        """
        Args:
            :config: A dict-like object that contains the commands to be
                executed for the various operations

        Raises:
            :KeyError: If any of the required keys is missing
            :ValueError: If the inputs fail validation
        """
        self.__config = parse_and_validate(config)

    def search(self, expr):
        """Search for packages using the ``search`` command

        The method will search the package manager and return a list of the
        results found. The ``exprs`` argument are the search expressions that
        will be passed as an argument to the ``search`` command defined for the
        instance. The output must be in the format defined as per the
        ``result_fmt`` in the .

        Args:
            :expr (str): An expression to search for

        Return:
            A list of ``Package`` objects obtained from the search result

        Raises:
            :ValueError: If any of the results cannot be parsed
        """
        search_cmd = self.__config['search'] % {'expr': expr}
        proc = subprocess.run(search_cmd, shell=True,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return self.parse_result(proc.stdout.decode('utf-8'))

    def parse_result(self, result):
        """Parse the results of a search

        The method is will take a string and try to parse it aa per the
        ``result_fmt`` format string defined for the instance.

        Return:
            If succesful, the method returns a list of dictionaries which
            contain the parsed results
        """
        regex = re.compile(self.__config['result_fmt_regex'])
        lines = result.split('\n')
        matches = map(regex.match, lines)
        packages = []
        for match in matches:
            if match is None:
                continue
            packages.append(match.groupdict())
        return packages

    def install(self, package, version=None, dry_run=False):
        """Install a package on the system

        The method will call the ``install`` or ``install_version`` command
        for the instance and try to install the package. In case version is
        not None, the specific version will be installed using the
        ``install_version`` command.

        Args:
            :package (str): The name of the package to install

        Kwargs:
            :version=None (str): A version string to install a specifc version
                of the package
            :dry_run=False (bool): If True, returns the command that will run
                without executing it.

        Return:
            A Boolean indicating whether installation was succesful or not

        Raises:
            :subprocess.CalledProcessError: If the installation command fails
        """
        if version is None:
            install_cmd = self.__config['install'] % {'pck': package}
        else:
            install_cmd = self.__config['install_version'] % {'pck': package,
                                                              'ver': version,
                                                             }
        if dry_run:
            return install_cmd
        proc = subprocess.run(install_cmd, shell=True)
        return proc.returncode == 0
