Installation
============

FreeART is a cpp library which can be access from python.
We mainly recommand to use it from python.

To install if download the source code :

.. code-block:: bash
    :emphasize-lines: 3,5

    git clone git@gitlab.esrf.fr:freeart/freeart.git
    pip install .
    python run_tests.py

.. note:: you will need to have a gitlab account to get the rights to clone the
    git project.


Build doc
---------

.. code-block:: shell

    python setup.py build build_doc
