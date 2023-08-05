# Copyright 2018 www.privaz.io Valletech AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pyone import bindings
from six import string_types
import xmlrpc.client
import socket

from .util import dict2one

#
# Exceptions as defined in the XML-API reference
#

class OneException(Exception):
    pass
class OneAuthenticationException(OneException):
    pass
class OneAuthorizationException(OneException):
    pass
class OneNoExistsException(OneException):
    pass
class OneActionException(OneException):
    pass
class OneApiException(OneException):
    pass
class OneInternalException(OneException):
    pass


##
#
# XML-RPC OpenNebula Server
# Slightly tuned ServerProxy
#
class OneServer(xmlrpc.client.ServerProxy):

    #
    # Override the constructor to take the authentication or session
    # Will also configure the socket timeout
    #

    def __init__(self, uri, session, timeout=None, **options):
        self.__session = session
        if timeout:
            # note that this will affect other classes using sockets too.
            socket.setdefaulttimeout(timeout)
        xmlrpc.client.ServerProxy.__init__(self, uri, **options)

    #
    # Override/patch the (private) request method to:
    # - structured parameters will be casted to attribute=value or XML
    # - automatically prefix all methodnames with "one."
    # - automatically add the authentication info as first parameter
    # - process the response
    def _ServerProxy__request(self, methodname, params):

        # cast parameters, make them one-friendly
        lparams = list(params)
        for i,param in enumerate(lparams):
            lparams[i] = dict2one(param)
        params = tuple(lparams)

        params = ( self.__session, ) + params
        methodname = "one." + methodname
        try:
            ret = xmlrpc.client.ServerProxy._ServerProxy__request(self, methodname, params)
        except xmlrpc.client.Fault as e:
            raise OneException(e)

        return self.__response(ret)

    #
    # Process the response from one XML-RPC server
    # will throw exceptions for each error condition
    # will bind returned xml to objects generated from xsd schemas
    def __response(self, rawResponse):
        sucess = rawResponse[0]
        code = rawResponse[2]

        if sucess:
            ret = rawResponse[1]
            if isinstance(ret, string_types):
                # detect xml
                if ret[0] == '<':
                    return bindings.parseString(ret.encode("utf-8"))
            return ret

        else:
            message = rawResponse[1]
            if code == 0x0100:
                raise OneAuthenticationException(message)
            elif code == 0x0200:
                raise OneAuthorizationException(message)
            elif code == 0x0400:
                raise OneNoExistsException(message)
            elif code == 0x0800:
                raise OneActionException(message)
            elif code == 0x1000:
                raise OneApiException(message)
            elif code == 0x2000:
                raise OneInternalException(message)
            else:
                raise OneException(message)


