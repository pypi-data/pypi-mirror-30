# Copyright (C) 2018 DataArt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from six.moves import http_client


__all__ = ['Router']


class Router(object):

    def __init__(self, handler, routes):
        self.__routes = routes
        self.__handler = handler

    def route(self, path):
        handler = self.__handler
        for regexp, controller in self.__routes:
            match = re.search(regexp, path)
            if match:
                obj = controller(handler.server)
                try:
                    obj.dispatch(
                        handler, *match.groups(), **match.groupdict()
                    )
                except NotImplementedError:
                    handler.send_error(
                        http_client.NOT_IMPLEMENTED,
                        "Unsupported method ({})".format(handler.command))
                    return

                return

        # Not found
        self.__handler.send_response(http_client.NOT_FOUND)
        self.__handler.end_headers()
        self.__handler.wfile.write(b'404 Not found!')
