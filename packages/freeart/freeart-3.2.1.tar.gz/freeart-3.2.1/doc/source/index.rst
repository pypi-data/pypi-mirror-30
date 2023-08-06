.. FreeART documentation master file, created by
   sphinx-quickstart on Fri Feb 27 12:46:07 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to FreeART's documentation!
===================================

Introduction
************
This is the reference documentation for all classes provided to the user by the FreeART library. **FreeART** is a tomographic image reconstruction library using Algebraic Reconstruction Technique (ART). Instead of implementing pure ART algorithm, FreeART is using a SART (Simultaneous Algebraic Reconstruction Technique). Using **SART** instead of pure ART leads to a better looking images by reducing the salt and pepper noise introduced by ART techniques. The FreeART specificity compared to other ART tomographic reconstruction library is that is also includes **self-absorption physical** effects into the reconstruction algorithm. On top of classical transmission absorption effect, supported self-absorption physical effects are  :

   * The *compton* effect
   * The *fluorescence* effect

FreeART allow simple transmission reconstruction.

In *compton/fluorescence* mode, the self-absorption physical effect taken into account are: 


    * The incoming beam attenuation inside the sample
    * The fluorescence detector solid angle from source point in the sample
    * The absorption in the sample seen by the fluorescence/compton emitted beam (for fluorescence the energy of the emitted beam must be known is known)

Using FreeART, it is also possible to reverse the classical tomographic reconstruction process. Starting from a phantom from which you already know the absorption matrix, it is possible to compute the sinogram.


First steps
***********

The simplest entry point on freeart is using the python binding.
freeart has an executable to run reconstructions from a configuration file using (see executable section):

.. code-block:: bash

    freeart interpreter myfile.cfg 5

The description of the configuration file parameters is given in ``freeart.configuration.config``.


Contents:

.. toctree::
    :maxdepth: 1

    installation
    geometry
    io_data
    transmission
    fluorescence
    limitations
    developers
    units
    tutorials
    modules/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

