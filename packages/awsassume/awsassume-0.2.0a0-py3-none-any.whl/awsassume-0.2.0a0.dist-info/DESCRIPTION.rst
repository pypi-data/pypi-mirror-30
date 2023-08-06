aws-assume
==========

.. image:: https://travis-ci.org/zulhilmizainuddin/aws-assume.svg?branch=master
    :target: https://travis-ci.org/zulhilmizainuddin/aws-assume

.. image:: https://api.codeclimate.com/v1/badges/cc17f352128d8ce24a9c/maintainability
   :target: https://codeclimate.com/github/zulhilmizainuddin/aws-assume/maintainability
   :alt: Maintainability

Execute AWS CLI commands after assuming role

Prerequisite
------------

-  **Python 3.6 or above**
-  AWS CLI or equivalent AWS supported CLI

Install
-------

Install using pip

::

    $ pip install awsassume

Install using setup script

::

    $ python setup.py install

Usage
-----

::

    usage: awsassume [-h] -a ROLE_ARN -n ROLE_SESSION_NAME [--no-cache]
                 [-r REGION] [-c ...]

    Execute AWS CLI commands after assuming role

    optional arguments:
    -h, --help            show this help message and exit
    --no-cache            Disable caching of the assumed role response
    -r REGION, --region REGION
                            The region to be associated with the client
    -c ..., --command ...
                            The AWS CLI command to execute after assuming role

    required arguments:
    -a ROLE_ARN, --role-arn ROLE_ARN
                            The ARN of the role to assume
    -n ROLE_SESSION_NAME, --role-session-name ROLE_SESSION_NAME
                            An identifier for the assumed role session

Caching
~~~~~~~

By default, the assumed role response will be cached to ``~/.awsassume/cache`` and used until it expires.
The cache will expire one hour after the assume role request is successful.

If caching of the assumed role response is undesirable, use the ``--no-cache`` flag to disable caching of the assumed role response.

Example
^^^^^^^

::

    $ awsassume -a arn:aws:iam::0123456789012:role/assume_role_test -n sessionname --no-cache

Region
~~~~~~

The ``-r`` or ``--region`` option can be used to set the ``AWS_DEFAULT_REGION`` environment variable.

Example
^^^^^^^

::

    $ awsassume -a arn:aws:iam::0123456789012:role/assume_role_test -n sessionname -r ap-southeast-1

Command
~~~~~~~

The ``-c`` or ``--command`` option can be used to pass the AWS CLI that is to be executed after successfully assuming role.
The command will be executed with the following environment variables set to the credentials returned by the assumed role response.

- ``AWS_ACCESS_KEY_ID``
- ``AWS_SECRET_ACCESS_KEY``
- ``AWS_SESSION_TOKEN``
- ``AWS_DEFAULT_REGION`` (only if the ``-r`` or ``--region`` option is set)

Example
^^^^^^^

::

    $ awsassume -a arn:aws:iam::0123456789012:role/assume_role_test -n sessionname -c aws s3 ls

If the ``-c`` or ``--command`` option is omitted, the output of the program can be evaluated to export the following environment variables to the current shell.

- ``AWS_ACCESS_KEY_ID``
- ``AWS_SECRET_ACCESS_KEY`` 
- ``AWS_SESSION_TOKEN``
- ``AWS_DEFAULT_REGION`` (only if the ``-r`` or ``--region`` option is set)

Example
^^^^^^^

::

    $ `awsassume -a arn:aws:iam::0123456789012:role/assume_role_test -n sessionname`

Development
-----------

Clone the repository

::

    $ git clone https://github.com/zulhilmizainuddin/aws-assume.git

Create and activate virtual environment

::

    $ python -m venv ./venv
    $ source ./venv/bin/activate

Install into development environment

::

    $ python setup.py develop

Run unit test with pytest

::

    $ python setup.py test

Run typing checking with mypy

::

    $ mypy awsassume

Publishing to PyPI
------------------

Create source and binary distribution

::

    $ python setup.py sdist bdist_wheel

Upload to PyPI

::

    $ twine upload dist/*


