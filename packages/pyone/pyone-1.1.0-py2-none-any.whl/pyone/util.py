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


import dicttoxml
import xmltodict
from lxml.etree import tostring
from collections import OrderedDict

#
# This function will cast parameters to make them nebula friendly
# flat dictionaries will be turned into attribute=value vectors
# dictionaries with root dictionary will be serialized as XML
#
# Structures will be turned into strings before being submitted.


def dict2one(param):
    # if this is a structured type
    if isinstance(param, dict):
        # in case we passed a dictionary that is part of another
        if hasattr(param,'_root'):
            param = param._root
        # if the dictionary is not empty
        if bool(param):
            root = list(param.values())[0]
            if isinstance(root, dict):
                # We return this dictionary as XML
                return dicttoxml.dicttoxml(param, root=False, attr_type=False).decode('utf8')
            else:
                # We return this dictionary as attribute=value vector
                ret = str()
                for (k, v) in param.items():
                    ret = ret + k + " = " + str('"') + str(v) + str('"') + str('\n')
                return ret
        else:
            raise Exception("Cannot cast empty dictionary")
    else:
        return param

#
# This function returns a dictionary from a binding
# The dictionary can then be used
# Deprecated

def one2dict(element):
    # provide backwards compatibility for TEMPLATE and USER_TEMPLATE only
    return element._root

#
# Utility Function to intgerate
#

def child2dict(element):
    # Create a dictionary for the documentTree
    xml = tostring(element)
    ret = xmltodict.parse(xml)

    # get the tag name and remove the ns attribute if present
    if "}" in element.tag:
        tagName = element.tag.split('}')[1]
        del ret[tagName]['@xmlns']
    else:
        tagName = element.tag

    # Reemplace no-dictionary with empty dictionary
    if ret[tagName] == None:
        ret[tagName] = OrderedDict()

    # return the contents dictionary, but save a reference
    ret[tagName]._root = ret
    return ret[tagName]

#
# initializes the TEMPLATE elements in bindings
#

def build_template_node(obj,nodeName,child):
    if nodeName == "TEMPLATE":
        obj.TEMPLATE = child2dict(child)
        return True
    elif nodeName == "USER_TEMPLATE":
        obj.USER_TEMPLATE = child2dict(child)
        return True
    else:
        return False

#
# Mixings for bindings subclass
#
class TemplatedType(object):
    def buildChildren(self, child_, node, nodeName_, fromsubclass_=False):
        if not build_template_node(self, nodeName_, child_):
            super(TemplatedType, self).buildChildren(child_,node,nodeName_,fromsubclass_)