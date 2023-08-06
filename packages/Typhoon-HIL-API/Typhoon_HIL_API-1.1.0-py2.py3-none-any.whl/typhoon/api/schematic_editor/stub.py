# -*- coding: utf-8 -*-
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
from __future__ import print_function, unicode_literals
import sys
import threading
from typhoon.api import get_conf_value, LoggingMixin, ClientStub, thread_safe
from typhoon.api.schematic_editor.const import ITEM_HANDLE
from typhoon.api.schematic_editor.util import ItemHandle


lock = threading.RLock()

# Functions that existed before the API update (these functions return True if
# everything went OK, and False in case of an error)
old_functions = {"load", "save", "save_as", "compile", "set_hw_settings",
                 "detect_hw_settings", "get_hw_settings",
                 "set_simulation_method", "set_simulation_time_step",
                 "set_component_property",
                 "set_property_attribute",  # deprecated, but still added
                                            # just in case
                 }


class ClientAPIStub(LoggingMixin, ClientStub):

    def __init__(self, log_file="client.log"):
        super(ClientAPIStub, self).__init__(log_file=log_file)

        req_socket = get_conf_value("schematic_editor", "server_rep_port")
        self._server_addr = "tcp://localhost:{}".format(req_socket)
        self._req_socket.connect(self._server_addr)

        self._ping()

    def __getattr__(self, name):
        try:
            attr = self.__getattribute__(name)
            return attr
        except:

            @thread_safe(lock)
            def wrapper(*args, **kwargs):
                msg = self.build_req_msg(name, **kwargs)

                self.log("{} message: {}".format(name, msg))

                self._req_socket.send_json(msg)

                response = self._req_socket.recv_json()

                repid = response["id"]

                result = response.get("result")
                error = response.get("error")
                warnings = response.get("warnings", [])

                self.log("{} status: {}".format(name, result))

                for warning in warnings:
                    if sys.version_info[0] < 3:
                        print(warning.encode("utf-8"))
                    else:
                        print(warning)

                if error:
                    err_msg = error["message"]
                    err_msg = err_msg.encode("utf-8") \
                        if sys.version_info[0] < 3 else err_msg

                    if name in old_functions:
                        print(err_msg)
                        # Set result to False to ensure backward compatibility
                        result = False
                    else:
                        raise Exception(err_msg)

                # If result is None, and no errors occurred, it means that the
                # method is successfully called, but we need to switch result
                # to True to ensure backward compatibility.
                if result is None and error is None:
                    result = True
                elif isinstance(result, dict) and ITEM_HANDLE in result:
                    # If a function returns ItemHandle object, server will
                    # serialize into a dictionary. So, now we need to create an
                    # ItemHandle instance from that dictionary and return it to
                    # the client.

                    result = ItemHandle(**result)
                elif isinstance(result, list):
                    result = [ItemHandle(**res) if (isinstance(res, dict)
                                                    and ITEM_HANDLE in res)
                              else res for res in result]

                return result

            return wrapper


_CL_STUB = None


def clstub():
    global _CL_STUB

    if not _CL_STUB:
        _CL_STUB = ClientAPIStub()

    return _CL_STUB