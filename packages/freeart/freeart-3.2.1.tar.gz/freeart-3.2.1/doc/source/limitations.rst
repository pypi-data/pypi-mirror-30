limitations
===========

for now we only run tests for FreeART using double precision for *Fluorescence* and *Transmission*.

.. warning:: a lot of "historical" about Diffraction is still included in freeart. But not of it has not been tested.

Mask haven t been tested yet with unittests.


Treated region
--------------

For the fluorescence mode during the forward projection ( sinogram generation ) we are limiting the region of acquisition to the discincluded in the phantom rectangle for a choose of simplification during the algorithm of sampling and to deal with rays.

.. image:: ../images/discLimitation.png
    :align: center

Reconstruction
--------------

the reconstruction algorithm is for now able to take only one detector.    


python interface
----------------

The python interface is only accessible for double and float.


Optimization
------------

FreeART core has been developed to be mono threaded. 
the configinterpreter is able to launch different reconstructions in multiple thread.
I don t think freeart can be eavily optimized (let say by a factor 2) anymore. with the current structure and technologies. 
If you want to highly increase performances you might go multithreaded or try some technologies as cuda or openCL.  