BuildVu Python Client
=====================

The Buildvu Python Client is the Python API for IDRSolutions’ `BuildVu
Microservice Example`_.

It functions as an easy to use, plug and play library that lets you use
`BuildVu`_ from Python.

--------------

Installation
------------

Using PIP:
~~~~~~~~~~

::

    pip install buildvu_python_client

For other methods / ways to install, check out the `Python Docs`_.

--------------

Usage
-----

Basic:
~~~~~~

First, import BuildVu and setup the converter details using
``setup()`` :

::

    from BuildVuClient import BuildVu as buildvu
    buildvu.setup('http://localhost:8080/microservice-example')

You can now convert files by calling ``convert()``. For example, to
convert to html5 :

::

    buildvu.convert('/path/to/input.pdf', '/path/to/output/dir')

Advanced:
~~~~~~~~~

*Coming soon…*

--------------

Who do I talk to?
=================

Found a bug, or have a suggestion / improvement? Let us know through the
Issues page.

Got questions? You can contact us `here`_.

--------------

Code of Conduct
===============

Short version: Don’t be an awful person.

Longer version: Everyone interacting in the BuildVu Ruby Client
project’s codebases, issue trackers, chat rooms and mailing lists is
expected to follow the `code of conduct`_.

--------------

Copyright 2018 IDRsolutions

Licensed under the Apache License, Version 2.0 (the “License”); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an “AS IS” BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

.. _BuildVu Microservice Example: https://github.com/idrsolutions/buildvu-microservice-example
.. _BuildVu: https://www.idrsolutions.com/buildvu/
.. _Python Docs: https://packaging.python.org/tutorials/installing-packages
.. _here: https://idrsolutions.zendesk.com/hc/en-us/requests/new
.. _code of conduct: CODE_OF_CONDUCT.md

