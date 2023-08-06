"""Main entry point for the package

This script parses the command line arguments and decides whether to run in
server mode or migration mode.
"""


import argparse
import logging
import os
import signal
import subprocess
import sys

from .migrator import migrate

PCK_DIR = os.path.dirname(os.path.abspath(__file__))
WORK_DIR = os.environ['HOME'] + os.path.sep + '.platform_migrator'
LOGGER = logging.getLogger('pm_logger')
LOGGER.setLevel(logging.INFO)
LOGGER.addHandler(logging.StreamHandler())


def parse_args(cl_args):
    """Parse the command line arguments

    Args:
        :cl_args: A list of arguments to parse

    Return:
        An ``argparser.Namespace`` object containing the parsed arguments
    """
    arg_parser = argparse.ArgumentParser(prog='platform-migrator')
    modes = arg_parser.add_subparsers(title='Mode of execution', dest='mode')

    server_args = modes.add_parser('server', description='Server mode')
    server_args.add_argument('--host', default='localhost',
                             help='Hostname or IP address to listen on')
    server_args.add_argument('--port', default=9001, type=int,
                             help='Port number to listen on')
    server_args.add_argument('action', choices=['start', 'stop', 'status'],
                             help='Command to run')

    migrate_args = modes.add_parser('migrate', description='Migrate mode')
    migrate_args.add_argument('name', nargs=1,
                              help='Name of package to migrate')
    migrate_args.add_argument('--skip-tests', action='store_true', dest='skip_tests',
                              default=False,
                              help='Skip tests but install dependencies and copy files')
    migrate_args.add_argument('test_files', nargs='+',
                              help='One or more test configuration files for migration')
    migrate_args.add_argument('--pck-mgr-configs', dest='pck_mgr_configs', action='append',
                              help='Config file for additional package managers')

    # NOTE: These may be implemented in the future
    #
    #list_args = modes.add_parser('list', description='List mode',
    #                             epilog='If no arguments are passed, all details are printed')
    #list_args.add_argument('--package-managers', action='store_const', default=0, const=1,
    #                       dest='pck_mgr', help='List all package managers that are configured')
    #list_args.add_argument('--history', action='store_const', default=0, const=1,
    #                       help='Print history of migrations')
    #list_args.add_argument('--incompatibles', action='store_const', default=0, const=1,
    #                       help='Print known incompatible packages')

    return arg_parser.parse_args(cl_args)


def start_server(host, port):
    """Start the server as a subprocess

    The function starts the server as a subprocess and then exits.

    Args:
        :host: The hostname or IP address to listen on
        :port: The port number to listen on
    """
    subprocess.Popen([sys.executable, PCK_DIR + os.path.sep + 'server.py',
                      host, str(port), os.getcwd()])
    LOGGER.info('Started server on address %s:%d', host, port)


def stop_server():
    """Stop the server

    This is done by sending SIGTERM to the process running the server.
    The PID of the process is obtained from the PIDFILE
    """
    if not os.path.exists('PIDFILE'):
        LOGGER.info('Server is not running')
        return

    with open('PIDFILE') as f_obj:
        pid = int(f_obj.readline())
    os.kill(pid, signal.SIGTERM)
    LOGGER.info('Stopped the server')


def print_server_status():
    """Print whether server is running or not"""
    if not os.path.exists('PIDFILE'):
        LOGGER.info('Server is not running')
    else:
        with open('base_sys_script.py') as f_obj:
            lines = f_obj.readlines()
        for line in lines:
            if 'HOST = ' in line:
                host = line.split('=')[1].strip('"\n ')
            elif 'PORT = ' in line:
                port = line.split('=')[1].strip('\n ')
        LOGGER.info('Server is running on address %s:%s', host, port)


def __chdir():
    """Change directory to WORK_DIR"""
    if not os.path.isdir(WORK_DIR):
        os.mkdir(WORK_DIR)
    os.chdir(WORK_DIR)


def main():
    """Main function of the script

    It sets the working directory, parses the command line arguments and
    calls the associated helper functions.
    """
    args = parse_args(sys.argv[1:])
    if args.mode == 'server':
        __chdir()
        if args.action == 'start':
            start_server(args.host, args.port)
        elif args.action == 'stop':
            stop_server()
        else:
            print_server_status()
    elif args.mode == 'migrate':
        test_files = [os.path.abspath(fname) for fname in args.test_files]

        pck_mgr_configs = None
        if args.pck_mgr_configs is not None:
            pck_mgr_configs = [os.path.abspath(fname) for fname in args.pck_mgr_configs]

        __chdir()
        migrate(args.name[0], test_files, pck_mgr_configs, args.skip_tests)
    else:
        raise ValueError('Command %s has not been implemented yet' % args.mode)


if __name__ == '__main__':
    main()
