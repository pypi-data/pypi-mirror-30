# -*- coding: utf-8
#
# This file is a part of Typhoon HIL API library.
#
# Typhoon HIL API is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from __future__ import unicode_literals

import logging
import sys
import os
import io
import json
import zmq

if sys.version_info[0] < 3:
    import ConfigParser
else:
    import configparser as ConfigParser


def get_version():
    """
    Return Typhoon API version. Used in setup.py and anywhere
    where version is needed.
    """
    return "1.1.0"


__version__ = get_version()


def get_installation_dir():
    """
    Returns path to the Typhoon software installation directory.

    Args:
        None

    Returns:
        Path to the installation directory as string.
        Empty string is returned if installation dir can't be found.
    """
    if sys.platform.startswith("win"):
        # Use Windows registry to get installation path.
        if sys.version_info[0] < 3:
            import _winreg as winreg
        else:
            import winreg

        # noinspection PyBroadException
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment"
            )
            install_dir = winreg.QueryValueEx(key, "TYPHOON")[0]
            winreg.CloseKey(key)
            return install_dir
        except Exception:
            return ""

    return ""


__author__ = 'Alen Suljkanovic'

config_parser = None
JSON_RPC_VER = "2.0"
API_VER = "1.0"

# Request constants
REQUEST_TIMEOUT = 1000
REQUEST_RETRIES = 3

# Severity constants
DEBUG = "DEBUG"
INFO = "INFO"
ERROR = "ERROR"

BAT_TEMPLATE = """
@echo off
start {cmd}
"""


def serialize_obj(obj):
    from typhoon.api.schematic_editor import ItemHandle
    from typhoon.api.schematic_editor.const import ITEM_HANDLE

    if isinstance(obj, ItemHandle):
        d = obj.__dict__
        d[ITEM_HANDLE] = True
        return d
    return obj


def thread_safe(lock):
    """Decorator that makes given function thread safe using RLock mutex

    Args:
        lock - RLock instance that will be used for locking decorated function.
    """

    # when decorator have arguments inner decorator is needed
    def inner_decorator(func):

        def func_wrapper(*args, **kwargs):
            # lock function call
            with lock:
                return func(*args, **kwargs)

        return func_wrapper

    return inner_decorator


def build_rep_msg(msg_id, method_name, result=None, error=None, warnings=None):
    """

    Args:
        msg_id:
        method_name:
        result:
        error:
        warnings:

    Returns:
         JSON
    """
    message = {
        "jsonrpc": JSON_RPC_VER,
        "method": method_name,
        "id": msg_id
    }

    if result and error:
        raise Exception("Invalid response message! Response message cannot"
                        "contain both 'result' and 'error' objects.")

    if error:
        message["error"] = error
    else:
        message["result"] = result

    if warnings:
        message["warnings"] = warnings

    return json.dumps(message, default=serialize_obj)


def get_settings_conf_path():
    if sys.platform.startswith("win"):
        return os.path.join(os.path.expandvars("%PROGRAMDATA%"),
                            "typhoon", "settings.conf")
    else:
        raise Exception("get_settings_conf: Windows OS is currently supported.")


def get_conf_value(section, key):
    """Get value from settings.conf

    Args:
        section: section name
        key: value identifier
    """
    global config_parser

    settings_path = get_settings_conf_path()

    if not config_parser:
        if sys.version_info[0] < 3:
            config_parser = ConfigParser.SafeConfigParser()
        else:
            config_parser = ConfigParser.ConfigParser()

        config_parser.read(settings_path)

    return config_parser.get(section, key)


def set_conf_value(section, key, value):
    """Set value to the settings.conf

    Args:
        section: section name
        key: value identifier
        value: value to be put

    Returns:

    """
    global config_parser

    settings_path = get_settings_conf_path()

    try:
        config_parser.add_section(section)
    except ConfigParser.DuplicateSectionError:
        pass  # section already exists

    config_parser.set(section, key, str(value))

    with open(settings_path, "w") as f:
        config_parser.write(f)


# dict of all loggers for given file
_loggers = {}


def get_logger(logger_name, file_name):
    """Return logger with given name and file handler name."""
    if file_name in _loggers:
        return _loggers[file_name]

    from logging import handlers

    # create logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    # create file handler which logs even debug messages
    fh = handlers.RotatingFileHandler(file_name, encoding="utf-8",
                                      backupCount=3, maxBytes=5*1024*1024)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    _loggers[file_name] = logger

    return logger


def get_install_path():
    """
    Returns the root for the typhoon application installation.
    """
    return os.path.split(os.path.abspath(os.path.realpath(sys.executable)))[0]


#
# Start API server...
#
def _get_dir_name():
    #
    # Determine location where server is located.
    # If settings.conf has entry for path for server location use that.
    # If not present, check installation directory (Windows registry).
    # If all fails report error.
    #

    def _get_inst_dir():
        dname = get_installation_dir()
        if not os.path.exists(dname):
            raise Exception("Error: Server path is not valid."
                            "Please install Typhoon software")
        return dname

    try:
        dir_name = os.path.normpath(get_conf_value("path", "src_path"))
        if not os.path.exists(dir_name):
            dir_name = _get_inst_dir()
    except ConfigParser.NoOptionError:
        return _get_inst_dir()
    return dir_name


def start_server():
    """Starts a server. Raises WindowsError if server cannot be started."""
    import subprocess

    dir_name = _get_dir_name()

    source_file = os.path.join(dir_name, "typhoon_hil.py")
    exe_file = os.path.join(dir_name, "typhoon_hil.exe")

    if os.path.exists(source_file):
        # Handle server from source.
        args = " -hapi"
        #
        # When running with server from source, get python for running of
        # server from settings.conf.
        #
        try:
            python_path = get_conf_value("path", "python_path")
        except ConfigParser.NoOptionError:
            raise Exception("Can't start Typhoon server, python_path must be"
                            " defined in settings.conf under 'path' section")
        python_exe = os.path.join(python_path, "python.exe")
        cmd = '%s %s %s' % (python_exe, source_file, args)
        print("CMD: %s" % cmd)

    elif os.path.exists(exe_file):
        # Handle server from installation.
        cmd = '"" "%s" %s' % (exe_file, "-hapi")
        print("CMD: %s" % cmd)
    else:
        print("Error: There is no server executable. "
              "Please install Typhoon software")
        return

    bat_template = BAT_TEMPLATE.format(cmd=cmd)

    bat_file = os.path.join(os.path.split(os.path.abspath(__file__))[0],
                            "run.bat")

    with open(bat_file, "w+") as f:
        f.write(bat_template)

    # suppress showing of command prompt on the .bat file executing
    params = dict()
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        params['startupinfo'] = startupinfo

    subprocess.Popen([bat_file], **params)


class LoggingMixin(object):
    """Mixin class for all stubs that need logging."""
    def __init__(self, log_file):
        super(LoggingMixin, self).__init__()
        self._logging_on = get_conf_value("debug", "logging_on") == "True"

        if self._logging_on:
            self.logger = get_logger(__name__, log_file)

    def log(self, msg, severity=DEBUG, level=0):
        """Logs message info a file, if the debug mode is activated."""
        if self._logging_on:

            callables = {
                INFO: lambda m: self.logger.log(level, m),
                DEBUG: self.logger.debug,
                ERROR: self.logger.error
            }

            fnc = callables[severity]
            fnc(msg)


class ClientStub(object):
    """Client stub class."""

    # message ID
    ID = 0

    def __init__(self):
        super(ClientStub, self).__init__()
        # ZMQ context
        self._context = zmq.Context()

        # Request socket
        self._req_socket = self._context.socket(zmq.REQ)

        self.poll = zmq.Poller()
        self.poll.register(self._req_socket, zmq.POLLIN)

    @property
    def _id(self):
        ClientStub.ID += 1
        return ClientStub.ID

    def build_req_msg(self, method_name, **params):
        """Builds a JSON-RCP request message that is being sent to the server

        Args:
            method_name (str): name of the method on the server that will be
                called
            params (dict): method arguments
        Returns:
            dict: JSON-like dict object
        """

        message = {
            "api": API_VER,
            "jsonrpc": JSON_RPC_VER,
            "method": method_name,
            "params": {k: serialize_obj(v) for k, v in params.items()},
            "id": self._id
        }

        return message

    def _ping_resp_handler(self, response):
        """Handles the response from the server if the ping is successful"""
        pass

    def _ping(self):
        """Pings server to check if it's running

        If server is not responding, and the number of retries is reached,
        client will try to start the server.
        """
        retries_left = REQUEST_RETRIES
        while retries_left:

            message = self.build_req_msg("ping")
            self._req_socket.send_json(message)

            expect_reply = True
            while expect_reply:
                socks = dict(self.poll.poll(REQUEST_TIMEOUT))
                if socks.get(self._req_socket) == zmq.POLLIN:
                    response = self._req_socket.recv_json()
                    if not response:
                        # Server did not respond
                        break

                    # Server responded
                    expect_reply = False
                    retries_left = 0

                    self._ping_resp_handler(response)
                else:
                    # No response from the server, retry..
                    self.poll.unregister(self._req_socket)
                    self._req_socket.setsockopt(zmq.LINGER, 0)
                    self._req_socket.close()

                    retries_left -= 1
                    if retries_left == 0:
                        # Start a server thread in HEADLESS_MODE...
                        try:
                            start_server()
                        except WindowsError as er:
                            print("Unable to start server.")
                            return

                    self._req_socket = self._context.socket(zmq.REQ)
                    self._req_socket.connect(self._server_addr)
                    self.poll.register(self._req_socket, zmq.POLLIN)
                    self._req_socket.send_json(message)
