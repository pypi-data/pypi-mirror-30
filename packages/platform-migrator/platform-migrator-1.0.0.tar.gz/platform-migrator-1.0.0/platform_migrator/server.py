"""This module contains the HTTP server that communicates with the base system

The server is implemented in the ``PMServer`` class and runs as daemon,
listening for requests on the ``/migrate`` path. The server can be controlled
by running ``platform-migrator server start`` and
``platform-migrator server stop``.

The module also contains the ``MigrateRequestHandler`` class which handles the
requests. On recieving a request, the server returns a Python script that can
be executed on the base system to start the migration process for a package.
The Python script is in the ``base_sys_script.py`` file and the server's
environment is updated whileresponding to a request.

The module is run as script when the application is started in server mode.
It takes the following positional arguments:

    :host: The hostname/IP address to listen on
    :port: The post to listen on
    :working_directory: The working directory of the server
"""


import atexit
import base64
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from threading import Thread
import os
import signal
import sys


class MigrateRequestHandler(BaseHTTPRequestHandler):
    """Request handler for the PMServer class

    The class processes each request recieved and sends the responses
    accordingly. It only supports GET requests on ``/migrate`` and POST
    requests on ``/yml`` and ``/zip``.
    """

    def do_GET(self):
        """Method to handle GET requests

        The method responds with status 200 and the modified
        ``base_sys_script.py`` file as the response body on ``/migrate``
        path. For all other paths, it responds with status code 400
        """
        if not self.path.endswith('/migrate'):
            self.send_error(400, 'Bad Request', 'No such path is served by the server')
            self.end_headers()
            return

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open('base_sys_script.py') as resp:
            self.wfile.write(resp.read().encode('utf-8'))

    def do_POST(self):
        """Method to handle POST requests

        The method responds with status 200 on ``/yml``, ``/min`` and ``/zip``
        paths if the request was processed without errors. Otherwise, it
        responds with status 400 in case of client error or status 500 in case
        of server error
        """
        if not (self.path.endswith('/yml') or self.path.endswith('/zip')
                or self.path.endswith('/min')):
            self.send_error(400, 'Bad Request', 'No such path is served by the server')
            self.end_headers()
            return

        error = True
        try:
            length = int(self.headers['content-length'])
            req = json.loads(self.rfile.read(length).decode('utf-8'))
            if not os.path.isdir(req['name']):
                os.mkdir(req['name'])
            assert 'data' in req
        except json.JSONDecodeError:
            self.send_error(400, 'Could not parse JSON')
        except AssertionError:
            self.send_error(400, 'Attribute data not present in JSON')
        except KeyError:
            self.send_error(400, 'Attribute name not present in JSON')
        except OSError:
            self.send_error(500, 'Failed to create directory for migration')
        else:
            error = False

        if error:
            self.end_headers()
            return

        try:
            if self.path.endswith('/yml'):
                with open(req['name'] + '/env.yml', 'w') as f_obj:
                    f_obj.write(base64.urlsafe_b64decode(req['data']).decode('utf-8'))
            elif self.path.endswith('/min'):
                with open(req['name'] + '/min-deps.json', 'w') as f_obj:
                    f_obj.write(base64.urlsafe_b64decode(req['data']).decode('utf-8'))
            else:
                with open(req['name'] + '/pkg.zip', 'wb') as f_obj:
                    f_obj.write(base64.urlsafe_b64decode(req['data']))
        except (IOError, OSError):
            self.send_error(500, 'Error while saving data')
        else:
            self.send_response(200, 'Success')
        finally:
            self.end_headers()
            f_obj.close()


class PMServer():
    """A simple HTTP server that listens for requests for migration

    It listens for new requests on ``/migrate`` path and the data for a
    request is received on ``/yml`` and ``/zip`` paths. The server is
    started using the ``run()`` method for the instance. The server creates
    a PIDFILE and starts a separate process to listen for requests.
    """

    def __init__(self, host, port):
        """
        Args:
            :host (str): The hostname or IP address to listen on
            :port (int): The port to listen on
        """
        if os.path.exists('PIDFILE'):
            raise ValueError('Server is already running')

        __file_dir = os.path.dirname(os.path.abspath(__file__))
        if __file_dir == os.getcwd():
            raise AttributeError(
                'Server must be run in a working directory other than package directory'
            )

        with open('PIDFILE', 'w') as f_obj:
            f_obj.write('%d' % os.getpid())
        atexit.register(os.remove, 'PIDFILE')
        atexit.register(os.remove, 'base_sys_script.py')


        self.host = host
        self.port = port
        self.httpd = HTTPServer((self.host, self.port), MigrateRequestHandler)
        self.thread = Thread(target=self.httpd.serve_forever)

        with open(__file_dir + '/base_sys_script.py', 'r') as f_obj:
            script = f_obj.read()
        script = (script.replace('HOST = None', 'HOST = "%s"' % self.host)
                  .replace('PORT = None', 'PORT = %d' % self.port))
        with open('base_sys_script.py', 'w') as f_obj:
            f_obj.write(script)


    def run(self):
        """Start the server"""
        self.thread.start()

    def shutdown(self, *args):
        """Shutdown the server and exit

        This method is a signal handler and is registered to SIGINT and
        SIGTERM during init.
        """
        self.httpd.shutdown()
        self.thread.join()


if __name__ == '__main__':
    os.chdir(sys.argv[3])
    SRV = PMServer(sys.argv[1], int(sys.argv[2]))
    signal.signal(signal.SIGINT, SRV.shutdown)
    signal.signal(signal.SIGTERM, SRV.shutdown)
    SRV.run()
