"""This module contains the ``Migrator`` class which does a migration

The module also contains some helper functions to operate with the Migrator
class, notably, the ``migrate`` function which migrates one or more packages
"""


import atexit
from collections import OrderedDict
from configparser import ConfigParser
from datetime import datetime
import json
import logging
import os
import shutil
import subprocess
import zipfile

import yaml

from .package_manager import get_package_manager


def get_target_from_search(results):
    """Prompt the user to select which package to install

    This is a helper function for getting the user's preferred package to
    install from the packages that match the search criteria

    Args:
        :results: The results of the search. It is a list of dict-like objects
            where each item has the ``'pck'`` key and optionall a ``'ver'`` key
            for the package name and version respectively

    Return:
        The user's selected package and version to install or None, if the user
        wants to skip the installation
    """

    def get_choice():
        try:
            return int(input('Please enter the option you would like to install: '))
        except ValueError:
            return float('inf')

    choices = [None]
    for res in results:
        if res not in choices:
            choices.append(res)

    print('Following options available for installation:')
    for i, opt in enumerate(choices):
        if opt is None:
            print('0)\tSkip installation')
        else:
            if 'ver' in opt:
                print('%d)\t%s %s' % (i, opt['pck'], opt['ver']))
            else:
                print('%d)\t%s' % (i, opt['pck']))

    choice = get_choice()
    while choice >= len(choices) or choice < 0:
        print('Invalid option. Please enter a valid option from above.')
        choice = get_choice()
    return choices[choice]


class Migrator:
    """The Migrator class is basically a simple test suite runner

    It reads the software config file provided, checks whether various
    packages are avialable or need to be installed and runs the test to
    verify whether the migration was succesful. It also stores any
    issues it encounters for easy look up later.
    """

    def __init__(self, app_name, test_config_files):
        """
        Args:
            :app_name: The name of the software to migrate
            :test_config_files: A list of filenames containing the test
                configuration for the package. This can be a single string
                for just one file or an iterable of strings for multiple
                files
        """
        if not os.path.isdir(app_name):
            raise ValueError('No such software available for migration: %s' % app_name)
        if not zipfile.is_zipfile(app_name + '/pkg.zip'):
            raise ValueError('Package zipfile is not valid')

        self.logger = logging.getLogger('pm_logger.migrator')
        self.app_name = app_name
        self.test_config = ConfigParser()
        self.test_config.read(test_config_files)
        self.saved_wd = os.getcwd()
        self.migration_id = 'migration-%s' % datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        self.pck_dir = ''

        if not os.path.isabs(self.test_config[self.app_name]['output_dir']):
            raise ValueError('output_dir must be an absolute path')

        os.chdir(app_name)
        os.mkdir(self.migration_id)
        os.chdir(self.migration_id)

        with open('%s/%s/env.yml' % (self.saved_wd, app_name)) as f_obj:
            self.env_yaml = yaml.load(f_obj)
        remove_deps = []
        for dep in self.env_yaml['dependencies']:
            if isinstance(dep, str) and dep.startswith('conda'):
                remove_deps.append(dep)
        for dep in remove_deps:
            self.env_yaml['dependencies'].remove(dep)
        with open('env.yml', 'w+') as f_obj:
            yaml.dump(self.env_yaml, f_obj)

        self.pck_zip = zipfile.ZipFile('%s/%s/pkg.zip' % (self.saved_wd, app_name))
        atexit.register(self.pck_zip.close)
        self.pck_mgrs = OrderedDict()

    def load_pck_mgrs(self, extra_pck_mgr_configs=None):
        """Load the configuration options of various package managers

        The method calls get_package_manager with the names of the package
        managers found in the package_managers option of the test config file.

        Kwargs:
            :extra_pck_mgr_configs: Any extra configuration files to read for
                obtaining the package manager's commands
        """
        __wd = os.getcwd()
        os.chdir(self.saved_wd)
        for pck_mgr in [p.strip() for p in
                        self.test_config[self.app_name]['package_managers'].split(',')]:
            if pck_mgr != 'conda':
                self.pck_mgrs[pck_mgr] = get_package_manager(pck_mgr, extra_pck_mgr_configs)
            else:
                self.pck_mgrs['conda'] = True
        os.chdir(__wd)

    def create_conda_env(self):
        """Create a conda environment from a yml file

        The environment is created using a subprocess and it is expected that
        the conda command is available on the PATH variable or at least one of
        CONDA_HOME and CONDA_ROOT_DIR environment variables is set to the
        prefix of the conda installation.

        Return:
            True if the environment was created succesfully else False
        """
        self.logger.info('Creating new conda environment %s', self.app_name)
        conda_dir = os.getenv('CONDA_HOME', os.getenv('CONDA_ROOT_DIR', ''))
        conda = os.path.join(conda_dir, 'bin/conda')
        proc = subprocess.run("{0} env create -n {1} --file 'env.yml'"
                              .format(conda, self.app_name), shell=True)
        if proc.returncode == 0:
            self.logger.info('Conda environment %s created for application\n', self.app_name)
        else:
            self.logger.error('Failed to create conda environment. %s',
                              'Please review error message and retry the migration again.')
        return proc.returncode == 0

    def fail_migration(self, err_code):
        if err_code == 'env':
            self.logger.error('Failed to setup environment')
        elif err_code == 'tests':
            self.logger.error('Failed to pass all tests')
        else:
            self.logger.error('Unknown error')
        self.logger.error('Migration discontinued')

    def setup_env(self):
        """Set up the environment for the application

        This method parses the environment yml file and uses the package
        managers to install the required dependencies.

        Return:
            A Boolean indicating whether all dependencies were succesfully
            installed
        """
        if 'conda' in self.pck_mgrs:
            return self.create_conda_env()

        if os.path.exists('../min-deps.json'):
            with open('../min-deps.json') as f_obj:
                min_deps = json.load(f_obj)
            deps = [[d['name'], d['version']]
                    for d in min_deps
                    if d['name'] not in ('conda', 'conda-env')]
        else:
            deps = [d.split('=')[:2]
                    for d in self.env_yaml['dependencies']
                    if isinstance(d, str) and (not d.startswith('conda'))]
            if 'pip' in self.env_yaml['dependencies']:
                deps.extend([d.split('==') for d in self.env_yaml['dependecies']['pip']])
        install_lists = {}
        for dep in deps:
            skip = False
            self.logger.info('Processing package %s', dep[0])
            for name, obj in self.pck_mgrs.items():
                if name not in install_lists:
                    install_lists[name] = []
                self.logger.info('Trying package manager %s', name)

                results = obj.search(r'^%s' % dep[0])
                _results = [r for r in results if r['pck'] == dep[0]]
                if _results != []:
                    results = _results
                if results == []:
                    results.extend(obj.search(dep[0]))
                if results == []:
                    self.logger.info('%s: No results found for %s', name, dep[0])
                    continue

                target = get_target_from_search(results)
                if target is None:
                    self.logger.info('%s: Skipping installation of %s', name, dep[0])
                    skip = True
                    continue

                install_lists[name].append(target)
                self.logger.info('%s: Package %s marked for installation', name, target[0])
                break
            else:
                if skip:
                    continue
                self.logger.error('Cannot find %s in any package manager', dep[0])
                resp = input('Do you want to stop further checks? (y/n)')
                if resp == 'y':
                    self.logger.error('Failing the migration')
                    return False
            self.logger.info('Finished package %s\n', dep[0])

        self.logger.info('Installing selected packages')
        for name, obj in self.pck_mgrs.items():
            for pck in install_lists[name]:
                obj.install(pck[0], pck[1])
        return True

    def run_tests(self):
        """Run the tests configured for the application

        The tests are run in a shell which is started as a subprocess. All
        tests are run regardless of failures to provide as much information
        as possible in a single run.

        Return:
            True if all the tests passed else False
        """
        conda_dir = os.getenv('CONDA_HOME', os.getenv('CONDA_ROOT_DIR', ''))
        tests = ['test_%s' % t.strip()
                 for t in self.test_config[self.app_name]['tests'].split(',')]
        success = True
        self.pck_zip.extractall()
        self.pck_dir = [i for i in os.listdir() if os.path.isdir(i)][0]
        os.chdir(self.pck_dir)
        for test in tests:
            if 'conda' in self.pck_mgrs:
                __exec = 'source {0}/bin/activate {1} && {2} && source {0}/bin/deactivate'.format(
                    conda_dir.rstrip('/') if conda_dir is not None else '.',
                    self.app_name, self.test_config[test]['exec'])
            else:
                __exec = self.test_config[test]['exec']

            proc = subprocess.run(__exec, shell=True,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if proc.returncode == 0:
                self.logger.info('Test %s passed', test.partition('test_')[2])
                self.logger.info(proc.stdout.decode('utf-8'))
            else:
                self.logger.error('Test %s failed', test.partition('test_')[2])
                self.logger.error(proc.stdout.decode('utf-8'))
                success = False
        os.chdir(os.path.pardir)
        shutil.rmtree(self.pck_dir)
        return success

    def migrate_files(self):
        """Copy application files to installation location"""
        path = self.test_config[self.app_name]['output_dir']
        self.pck_zip.extractall(path=path)
        self.logger.info('Package saved as %s/%s', path, self.pck_dir)

    def run_migration(self, skip_tests=False):
        """Run the migration process

        The method setups the environment, runs the tests and if succesful,
        copies the files to the installation lcoation.

        :Kwargs:
            :skip_test=False: Skip running tests but perform the rest of the steps
        """
        if not self.setup_env():
            self.fail_migration('env')
            return
        if skip_tests:
            self.logger.warning('Skipping all tests')
        elif not self.run_tests():
            self.fail_migration('tests')
            return
        self.migrate_files()


def migrate(name, test_files, pck_mgr_configs=None, skip_tests=False):
    """Wrapper function to migrate one software

    The function takes a list of test configuration files and attempts
    to migrate the package to the target system. All work is logged and
    saved and is used to determine any known incompatibilities.

    Args:
        :name: Name of the application to migrate
        :test_files: An iterable of filenames which contain the configuration
            for testing a package

    Kwargs:
        :pck_mgr_configs: An iterable of filenames which contain additional
            package manage configurations
        :skip_test=False: Skip running tests but perform the rest of the steps
    """
    migrator = Migrator(name, test_files)
    migrator.load_pck_mgrs(pck_mgr_configs)
    migrator.run_migration(skip_tests=skip_tests)
