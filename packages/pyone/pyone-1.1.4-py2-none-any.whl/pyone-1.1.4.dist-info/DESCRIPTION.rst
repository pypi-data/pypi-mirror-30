PyONE: Open Nebula Python Bindings
==================================

.. image:: https://travis-ci.org/OpenNebula/addon-pyone.svg?branch=master
    :target: https://travis-ci.org/OpenNebula/addon-pyone

Description
-----------

PyOne is an implementation of Open Nebula XML-RPC bindings in Python.

The main goals of this library are **completeness and maintainability**.

Proxies and generators have been used whenever possible to minimize the impact of
API updates, ensuring that the distributed xsd files are the only update required
when new API versions are released.

This library is meant to be used together with OpenNebula API documentation:

The `XML-RPC API <http://docs.opennebula.org/5.4/integration/system_interfaces/api.html>`_ must
be used to know which calls to make.

Development
-----------

To contribute enhancements or fixes use GitHub tools: Pull requests and issues.
Please note that by contributing to this project you accept that your contributions
are under the Apache License 2.0, just like the rest of this project. Please take
some time to read and understand the license terms and ensure that you are happy with it.

If you have access to a large OpenNebula deployment, contribute by testing on it.

Authors
-------

* Rafael del Valle (rvalle@privaz.io)

Compatibility
-------------

* PyONE is compatible with OpenNebula v5.4.x
* It should be easy to backport PyOne to any OpenNebula version with XML-RPC API that includes XML Schema Definition (XSD) files.

Requirements
------------

* Python 2.7 or 3.6
* Connectivity and Credentials to OpenNebula XML-RPC Server.

Installation
------------

PyONE is distributed as a python package, it can be installed as:

.. code:: shell

  $ pip install pyone

Configuration
-------------

You can configure your XML-RPC Server endpoint and credentials in the constructor:

.. code:: python

  import pyone
  one = pyone.OneServer("http://one/RPC2", session="oneadmin:onepass" )

If you are connecting to a test platform with a self signed certificate you can disable
certificate verification as:

.. code:: python

  import pyone
  import ssl
  one = pyone.OneServer("http://one/RPC2", session="oneadmin:onepass", context=ssl._create_unverified_context() )

It is also possible to modify the default connection timeout, but note that the setting
will modify the TCP socket default timeout of your Python VM, ensure that the chosen timeout
is suitable to any other connections running in your project.

Usage
-----

**Making Calls**

Calls match the API documentation provided by Open Nebula:

.. code:: python

  import pyone

  one = pyone.OneServer("http://one/RPC2", session="oneadmin:onepass" )
  hostpool = one.hostpool.info()
  host = hostpool.HOST[0]
  id = host.ID

Note that the session parameter is automatically included as well as the "one." prefix to the method.

**Returned Objects**

The returned types have been generated with generateDS and closely match the XSD specification.
You can use the XSD specification as primary documentation while your IDE will
offer code completion as you code or debug.

.. code:: python

   marketpool = one.marketpool.info()
   m0 = marketpool.MARKETPLACE[0]
   print "Markeplace name is " + m0.NAME

**Structured Parameters**

When making calls, the library will translate flat dictionaries into attribute=value
vectors. Such as:

.. code:: python

  one.host.update(0,  {"LABELS": "HD"}, 1)

When the provided dictionary has a "root" dictionary, it is considered to be root
element and it will be translated to XML:

.. code:: python

  one.vm.update(1,
    {
      'TEMPLATE': {
        'NAME': 'abc',
        'MEMORY': '1024',
        'ATT1': 'value1'
      }
    }, 1)

GenerateDS creates members from most returned parameters, however, some elements in the XSD are marked as anyType
and GenerateDS cannot generate members automatically, TEMPLATE and USER_TEMPLATE are the common ones. Pyone will
allow accessing its contents as a plain python dictionary.

.. code:: python

  host = one.host.info(0)
  arch = host.TEMPLATE['ARCH']

This makes it possible to read a TEMPLATE as dictionary, modify it and use it as parameter
for an update method, as following:

.. code:: python

  host = one.host.info(0)
  host.TEMPLATE['NOTES']="Just updated"
  one.host.update(0,host.TEMPLATE,1)

**Constants**

Some methods will return encoded values such as those representing the STATE of a resource. Constant are
provided to better handle those.

.. code:: python

  from pyone import MARKETPLACEAPP_STATES
  if app.STATE == MARKETPLACEAPP_STATES.READY:
    # action that assumes app ready

**Building from Source**

Note that a Makefile is provided to generate the python bindings

**Runing Tests**

There are two main sets of tests.

- CI Tests: unit tests meant for continious integration, do not require an OpenNebula platform, run mainly on XML samples, etc.
- Integration Tests: meant to be used with a TESTING OpenNebula platform. Will create and modify OpenNebula objects.

IntegrationTests use a specialized XMLRPC client, OneServerTester that will also **record** Fixtures that can later be used
in **replay** mode. In reply mode the calls to OpenNebula are intercepted and the fixtures are returned instead. This is
useful to detect regressions but any modification to the tests cases will require to re-record Fixtures.

You can run the tests as follows:

.. code:: sh

  $ export PYONE_SESSION="oneadmin:onepass"
  $ export PYONE_ENDPOINT="https://192.168.121.55/RPC2"
  $ python -m unittest discover -v -s tests/ci/
  $ python -m unittest discover -v -s tests/integration

Known Issues
------------

In some instances OpenNebula generates non-conformant XML elements, elements that according to the XSD should not
be there. GenerateDS will silently ignore them and they will not be accessible.

Those cases should be reported to OpenNebula for the XSDs to be completed. 

References
----------

PyONE started as part of the `Privazio <http://privaz.io>`_ project.

Privazio is a private cloud for residential users,
startups or workgroups with a special focus on privacy.

PyONE is the core component of the following `Ansible module for OpenNebula <https://github.com/privazio/ansible>`_.

License
-------

PyONE is licensed under Apache License 2.0


