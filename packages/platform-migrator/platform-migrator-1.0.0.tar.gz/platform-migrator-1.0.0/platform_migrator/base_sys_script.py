"""
This module runs on the base system as a Python script

The module mainly discovers the existing conda environments and sends
the source code over to the target system for further processing.

NOTE:
    The script should be compatible with both Python 2 and 3. It will
    be executed using whichever version of Python is available using
    ``python`` command.
"""

import base64
from io import BytesIO
import json
import os
import subprocess
import sys
import zipfile

try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen

HOST = None
PORT = None


def get_conda_env(env=None):
    """Return the yml file of current conda environment

    The function runs a subprocess to get the yml file of the current
    conda environment. The results of the subprocess are returned as
    a tuple and if the yml file was obtained, it will be index 1 of
    the tuple.

    Kwargs:
        :env=None: Conda environment to source, if not the currently
            active environment.

    Return:
        A tuple whose elements are a boolean indicating whether the
        process ran error free, the stdout of the process and the
        stderr of the process
    """
    source_cmd = 'source ./activate %s &&' % env if env is not None else ''
    proc = subprocess.Popen('%s conda env export --no-builds' % source_cmd,
                            shell=True, universal_newlines=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    return (not bool(proc.returncode)), out, err


def get_conda_min_deps(env, source_env=False):
    """Try to create a list of minimal dependencies to install

    The function queries the conda environment for all dependencies and
    then tries to determine the which dependencies are sub-dependencies of
    others. In this way, a minimal list of dependencies is created.

    Args:
        :env: The name of the conda environment to query

    Kwargs:
        :source_env=False: Boolean indicator whether to source conda env
            before getting data or not

    Return:
        A list of conda package objects if succesful, or None
        if the conda envrionment could not be loaded
    """
    source_cmd = 'source ./activate %s &&' % env if source_env else ''
    proc = subprocess.Popen('%s conda list --json' % source_cmd,
                            shell=True, universal_newlines=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if proc.returncode != 0:
        sys.stderr.write(err)
        return None

    all_deps = json.loads(out)
    min_deps = [dep for dep in all_deps]

    for dep in all_deps:
        if dep not in min_deps:
            continue
        proc = subprocess.Popen("%s conda create --dry-run --json -n dummy %s=%s=%s"
                                % (source_cmd, dep['name'], dep['version'], dep['build_string']),
                                shell=True, universal_newlines=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if proc.returncode != 0:
            continue
        sub_deps = []
        actions = json.loads(out)['actions']
        for action in actions:
            sub_deps.extend(action['LINK'])
        for sub_dep in sub_deps:
            if sub_dep in min_deps and sub_dep != dep:
                min_deps.remove(sub_dep)
    return min_deps


def create_zip_file(zip_dir, quiet=False):
    """Create a zip file of a directory

    Args:
        :zip_dir: The directory to zip

    Kwargs:
        :quiet=False: If True, no messages are printed

    Return:
        A bytes buffer containing the zip file data
    """
    buf = BytesIO()
    zip_file = zipfile.ZipFile(buf, 'w')
    zip_file.write(zip_dir)
    for pardir, _, files in os.walk(zip_dir):
        for filename in files:
            if not quiet:
                print('Zipping %s' % os.path.join(pardir, filename))
            zip_file.write(os.path.join(pardir, filename))
    zip_file.close()
    return buf.getvalue()

def send_data(app_name, path, data, name, quiet=False):
    """Send data back to the server

    Args:
        :app_name (str): The name of the application
        :path (str): The path to send data to, without the base address
        :data: Buffer containing the data
        :name (str): The name to use for the data in messages

    Kwargs:
        :quiet=False (bool): If True, no messages are printed
    """
    if sys.version_info[0] == 2:
        __data = base64.urlsafe_b64encode(data)
    else:
        __data = base64.urlsafe_b64encode(data).decode('utf-8')

    data_json = json.dumps({'name': app_name, 'data': __data}).encode('utf-8')
    req = Request('http://%s:%d/%s' % (HOST, PORT, path),
                  data=data_json)
    resp = urlopen(req)
    resp.read()

    if not quiet:
        if resp.getcode() == 200:
            print('%s sent succesfully' % name)
        else:
            print('Error while sending %s' % name)
            print('Response code is %d' % resp.status)


def send_env_yml(app_name, env_yml, quiet=False):
    """Send the environment yml data back to the server

    Args:
        :app_name (str): The name of the application
        :env_yml: Buffer containing the environment yml data

    Kwargs:
        :quiet=False (bool): If True, no messages are printed
    """
    return send_data(app_name, 'yml', env_yml.encode('utf-8'), 'Environment yml file', quiet=quiet)


def send_repo_zip(app_name, zip_file, quiet=False):
    """Send a zip of the repository back to the server

    Args:
        :app_name (str): The name of the application
        :zip_file: Buffer containing the zip of the code repository

    Kwargs:
        :quiet=False (bool): If True, no messages are printed
    """
    return send_data(app_name, 'zip', zip_file, 'Package zip file', quiet=quiet)


def send_min_deps(app_name, min_deps, quiet=False):
    """Send a zip of the repository back to the server

    Args:
        :app_name (str): The name of the application
        :min_deps (list): List containing the minimal required dependencies

    Kwargs:
        :quiet=False (bool): If True, no messages are printed
    """
    return send_data(app_name, 'min', json.dumps(min_deps).encode('utf-8'),
                     'Minimal dependency list', quiet=quiet)


def main():
    """Main function that is executed"""
    if sys.version_info[0] == 2:
        input = raw_input
    else:
        input = __builtins__.input

    print('Attempting to identify conda environment and packages')
    success, env_yml, err = get_conda_env()
    if success:
        env = env_yml.split('\n')[0].split(':')[1].strip()
        print('Using environment %s' % env)
        source_env = False
    else:
        print('Failed to identify environment')
        env = input('Which conda environment should be activated: ').strip('\n')
        success, env_yml, err = get_conda_env(env)
        if not success:
            sys.stderr.write('Failed to collect conda environment details\n')
            # Python 2 compatibilty requires the str(err.decode(...))
            # In Python 3, it will cast str to str and in Python it will cast unicode to str
            # Either ways, it will create the proper string for printing out
            sys.stderr.write('Error is:\n%s' % str(err.encode('utf-8')))
            sys.stderr.write('Please activate manually and rerun\n')
            sys.exit(-1)
        source_env = True
    print('Trying to create a minimal dependency list...this may take some time')
    min_deps = get_conda_min_deps(env, source_env=source_env)
    if min_deps is None or min_deps == []:
        print('Failed to obtain minimal dependencies...continuing with all packages')
    app_name = input('Please enter name of application: ')
    zip_dir = input('Please enter the directory of the source code to zip: ')
    os.chdir(zip_dir + os.path.sep + os.path.pardir)
    zip_file = create_zip_file(os.path.relpath(zip_dir))
    send_env_yml(app_name, env_yml)
    send_repo_zip(app_name, zip_file)
    if min_deps:
        send_min_deps(app_name, min_deps)
    print('All data has been copied to target system.')
    print('You can now attempt setting up the software there')


if __name__ == '__main__':
    main()
