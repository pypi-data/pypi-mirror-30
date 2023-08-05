.. ===============LICENSE_START=======================================================
.. Acumos CC-BY-4.0
.. ===================================================================================
.. Copyright (C) 2017-2018 AT&T Intellectual Property & Tech Mahindra. All rights reserved.
.. ===================================================================================
.. This Acumos documentation file is distributed by AT&T and Tech Mahindra
.. under the Creative Commons Attribution 4.0 International License (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..      http://creativecommons.org/licenses/by/4.0
..
.. This file is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.
.. ===============LICENSE_END=========================================================

========================
Acumos DCAE Model Runner
========================

The Acumos DCAE model runner enables Acumos models to be run as if they were
DCAE components.

Each Acumos model method is mapped to a subscriber and publisher stream,
with ``_subscriber`` and ``_publisher`` suffixes respectively. For example,
a model with a ``transform`` method would have ``transform_subscriber`` and
``transform_publisher`` streams.

The model runner implements DCAE APIs such as health checks and configuration
updates.

The ``acumos_dcae_model_runner`` Python package provides a command line utility
that can be used to instantiate the model runner. See the tutorial for more information.

The ``acumos_dcae_model_runner`` package should be installed in the docker image
that is ultimately on-boarded into DCAE. The model runner CLI utility should be
the entry point of that Docker image, as shown in the Dockerfile provided
in ``example/`` directory in the root of the repository.

Installation
============

The ``acumos_dcae_model_runner`` package can be installed with pip like so:

.. code:: bash

    pip install acumos_dcae_model_runner --process-dependency-links

**Note:** The ``--process-dependency-links`` flag is **required**
because the required ``dcaeapplib`` dependency is not yet hosted on
PyPI.

If you'd prefer, you can maintain a local directory of Python packages containing
``dcaeapplib``, and use the ``--find-links`` option:

.. code:: bash

    pip install acumos_dcae_model_runner --find-links path/to/pkgs/

.. ===============LICENSE_START=======================================================
.. Acumos CC-BY-4.0
.. ===================================================================================
.. Copyright (C) 2017-2018 AT&T Intellectual Property & Tech Mahindra. All rights reserved.
.. ===================================================================================
.. This Acumos documentation file is distributed by AT&T and Tech Mahindra
.. under the Creative Commons Attribution 4.0 International License (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..      http://creativecommons.org/licenses/by/4.0
..
.. This file is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.
.. ===============LICENSE_END=========================================================

========
Tutorial
========

CLI Usage
=========

To execute the model runner, use the provided CLI:

.. code:: bash

    $ acumos_dcae_model_runner --help
    usage: acumos_dcae_model_runner [-h] [--timeout TIMEOUT] [--debug] model_dir

    positional arguments:
      model_dir          Directory that contains either the dumped model.zip or
                         its unzipped contents.

    optional arguments:
      -h, --help         show this help message and exit
      --timeout TIMEOUT  Timeout (ms) used when fetching.
      --debug            Sets the log level to DEBUG

DCAE Onboarding Example
=======================

The ``python-dcae-model-runner`` repository has an ``example/`` directory
that shows how an Acumos model can be onboarded as a DCAE component.

After executing the steps below, the directory should have this
structure:

.. code:: bash

    example/
    ├── Dockerfile
    ├── dcae-artifacts
    │   ├── component.json
    │   ├── number-out.json
    │   └── numbers-in.json
    ├── example-model
    │   ├── metadata.json
    │   ├── model.proto
    │   └── model.zip
    ├── example_model.py
    └── requirements.txt

**Note:** For this example, the ``requirements.txt`` file should reflect the
packages and versions listed in ``example-model/metadata.json``.

Steps
-----

1) Create the Acumos model
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``example_model.py`` script defines a simple Acumos model that can
add two integers together. The following will generate
``example-model/``:

.. code:: bash

    python example_model.py

2) Build the docker image
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    docker build -t acumos-python-model-test:0.1.0 .

3) Onboard the Acumos model to DCAE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The onboarding procedure involves adding the component and data format
artifacts provided in ``example/dcae-artifacts`` to the DCAE catalog.

Refer to the official DCAE onboarding documentation for the full
procedure.

.. ===============LICENSE_START=======================================================
.. Acumos CC-BY-4.0
.. ===================================================================================
.. Copyright (C) 2017-2018 AT&T Intellectual Property & Tech Mahindra. All rights reserved.
.. ===================================================================================
.. This Acumos documentation file is distributed by AT&T and Tech Mahindra
.. under the Creative Commons Attribution 4.0 International License (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..      http://creativecommons.org/licenses/by/4.0
..
.. This file is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.
.. ===============LICENSE_END=========================================================

=============
Release Notes
=============

v0.1
====

-  Initial release of the Acumos DCAE Python model runner

.. ===============LICENSE_START=======================================================
.. Acumos CC-BY-4.0
.. ===================================================================================
.. Copyright (C) 2017-2018 AT&T Intellectual Property & Tech Mahindra. All rights reserved.
.. ===================================================================================
.. This Acumos documentation file is distributed by AT&T and Tech Mahindra
.. under the Creative Commons Attribution 4.0 International License (the "License");
.. you may not use this file except in compliance with the License.
.. You may obtain a copy of the License at
..
..      http://creativecommons.org/licenses/by/4.0
..
.. This file is distributed on an "AS IS" BASIS,
.. WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
.. See the License for the specific language governing permissions and
.. limitations under the License.
.. ===============LICENSE_END=========================================================

=======================
Contributing Guidelines
=======================

Testing
=======

We use a combination of ``tox``, ``pytest``, and ``flake8`` to test
``acumos``. Code which is not PEP8 compliant (aside from E501) will be
considered a failing test. You can use tools like ``autopep8`` to
“clean” your code as follows:

.. code:: bash

    $ pip install autopep8
    $ cd python-dcae-model-runner
    $ autopep8 -r --in-place --ignore E501 acumos_dcae_model_runner/

Run tox directly:

.. code:: bash

    $ cd python-dcae-model-runner
    $ export WORKSPACE=$(pwd)  # env var normally provided by Jenkins
    $ tox

You can also specify certain tox environments to test:

.. code:: bash

    $ tox -e py34  # only test against Python 3.4
    $ tox -e flake8  # only lint code


