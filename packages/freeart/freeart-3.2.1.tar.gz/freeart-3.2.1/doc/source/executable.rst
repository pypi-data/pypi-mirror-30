Executable
==========


To help the user an executable which take a configuration file (.h5, .cfg, .ini)
files and the number of iteration to run has been create.

To launch it you can go for:

.. code-block:: bash

    freeart interpreter myfile.cfg 5

.. note:: once the reconstruction is runned this will display one silx Plot window per reconstruction.
    The goal is not to have a gui for reconstruction. This is done by tomogui (http://gitlab.esrf.fr/tomoTools/tomogui)