Topos
=====

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - code
      - |travis| |coveralls|
    * - pypi
      - |version| |supported-versions|

.. |travis| image:: https://travis-ci.org/alcarney/topos.svg?branch=dev
    :target: https://travis-ci.org/alcarney/topos

.. |coveralls| image:: https://coveralls.io/repos/github/alcarney/topos/badge.svg?branch=dev
    :target: https://coveralls.io/github/alcarney/topos?branch=dev

.. |docs| image:: https://readthedocs.org/projects/topos/badge/?version=latest
    :target: http://topos.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |version| image:: https://img.shields.io/pypi/v/topos.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/topos

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/topos.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/topos

Creating 3D meshes with a blend of python and maths

**DISCLAIMER**: It is very early stages for this package and features may be
added/broken/removed without warning while the core concepts are hashed out.

README under construction...

Developing
----------

**IMPORTANT**: The following commands all need to be run from the root of this
project

Topos uses `pipenv`_ to manage dependencies and virtual environments. The first
step is to create a virtual environemnt

.. code-block:: sh

    $ pipenv --three

Then with your virtual environment created install all the dependencies

.. code-block:: sh

    $ pipenv install --dev

Finally to work within the virtual environment you have created run

.. code-block:: sh

    $ pipenv shell


.. _pipenv: https://docs.pipenv.org/
