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

from hashlib import md5
from json import dump, load, dumps as json_dumps
from base64 import b64decode, b64encode
from pickle import dumps, loads
from os import path, makedirs
from . import OneServer
from tblib import pickling_support
from sys import exc_info, version_info
from six import reraise
from collections import OrderedDict

pickling_support.install()

class OneServerTester(OneServer):
    '''
    This class extends the OneServer to facilitate unit testing
    The idea is to be able to "record" fixitures while testing with a live OpenNebula platform.
    Those recordings can later be use in "replay" mode to simulate an OpenNebula platform.
    XMLAPI method calls are recorded as test_base/unit_test/method_signature_instance
    The signature is generated as the md5 of the parameters
    if several calls with the same signature are doing during the same unit test, instance is incremented.
    The order in which calls happen within the same unit_test must be deterministic.
    '''
    def __init__(self, uri, session, fixture_path, timeout=None, fixture_replay=False, **options):
        if not path.exists(fixture_path):
            makedirs(fixture_path)

        # all members involved in the fixtures must be predefined or
        # the magic getter method will trigger resulting in stack overflows
        self._fixture_keys = dict()
        self._fixture_test_path = fixture_path
        self._fixture_path = fixture_path
        self._fixture_replay = fixture_replay
        self._fixture_unit_test = "init"

        OneServer.__init__(self, uri, session, timeout, **options)

    def set_fixture_unit_test(self,name):
        """
        Set the name of the unit test. this will create a new fixture directory
        It will create the directory if it does not exists
        Will reset the fixture key counter
        :param name:
        :return:
        """

        self._fixture_unit_test = name
        self._fixture_test_path = path.join(self._fixture_path, name)
        self._fixture_keys = dict()

        if not path.exists(self._fixture_test_path):
            makedirs(self._fixture_test_path)

    def _get_fixture_file(self,methodname, params):
        '''
        returns the fixture file, in its directory.
        increases the instance number each time the same key is requested.
        :param methodname: XMlRPC method
        :param params: the paramters passed
        :return: file name were to store to or read from the fixture data
        '''
        signature_md5 = md5()
        sparms=json_dumps(params,sort_keys=True).encode()
        signature_md5.update(sparms)
        signature = signature_md5.hexdigest()

        fixture_key = "%s_%s" % (methodname, signature)

        if fixture_key in self._fixture_keys:
            instance = self._fixture_keys[fixture_key] + 1
        else:
            instance = 0

        self._fixture_keys[fixture_key]= instance

        return path.join(self._fixture_test_path, "%s_%d.json" % (fixture_key, instance))

    def _do_request(self,method,params):
        '''
        Intercepts requests.
        In record mode they are recorded before being returned.
        In replay mode they are read from fixtures instead
        '''

        file = self._get_fixture_file(method, params)
        ret = None
        f = None

        if self._fixture_replay:
            try:
                f = open(file, 'r')
                ret = load(f)
                if 'exception' in ret:
                    reraise(*loads(b64decode(ret['exception'])))
            except IOError:
                raise Exception("Could not read fixture file, if any parameter changed you must re-record fixtures")
            finally:
                if f:
                    f.close()
        else:
            try:
                f = open(file, 'wb')
                ret = OneServer._do_request(self, method, params)
            except Exception as exception:
                ret = {
                    "exception": b64encode(dumps(exc_info(), 2)).decode(),
                }
                raise exception
            finally:
                f.write(json_dumps(ret).encode())
                f.close()
        return ret

    def _cast_parms(self,params):
        """
        Parameters will be used to generate the singnature of the method, an md5.
        So we need signatures to be deterministics. There are two sources of randomness
        - Python version, in particular differences in dealing with encodings
        - Unsortered sets.
        This method will add casting transformations to fix those, only required for testing.

        :param params:
        :return: a list of parameters that should generate a deterministic md5 signature.
        """
        lparams = list(params)

        for i, param in enumerate(lparams):
            if isinstance(param, dict):
                lparams[i] = self._to_ordered_dict(param)

        return  OneServer._cast_parms(self, lparams)

    def _to_ordered_dict(self, param):
        """
        deep orders a dictionary
        :param param:
        :return:
        """

        if isinstance(param,dict):
            # ensure the dictionary is ordered
            param = OrderedDict(sorted(param.items()))
            # recurse
            for key, value in param.items():
                if isinstance(value, dict):
                    param[key] = self._to_ordered_dict(value)
        return param