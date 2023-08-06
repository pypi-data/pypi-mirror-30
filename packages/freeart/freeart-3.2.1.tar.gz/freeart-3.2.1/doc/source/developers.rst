developers extra-informations
=============================

C++ code
--------

The core of freeart has been developed in cpp.
If you want to skip the python binding you can use cmake or cmake gui in order
to generate the library and the executable given in examples/
It can also be useful for debugging using valgrind or other..


General information
-------------------

Oversampling
^^^^^^^^^^^^
If we set the oversampling value to one then we will evaluate one point of the ray each VOXEL WIDTH.
If we have n as oversampling value then we will estimate the a point of the ray each  :math:`\frac{VOXEL WIDTH}{n}`.

.. warning:: For the fluorescence in the case you are using the CREATE_ONE_RAY_PER_SAMPLE_POINT as we are creating the 'real' outfoing ray we will generate n time more rays (one outgoing rays for each sample point)

Tips and tricks
^^^^^^^^^^^^^^^
FreeART has bright new unit tests, easily launchable :


.. code-block:: python
    :emphasize-lines: 3,5

    python run_tests.py

It is strongly recommended to launch the unit test before each commit.
Is also be nice to associate each new development with an adapted unit tests. 

execution time and complexity
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ray point calculation method
""""""""""""""""""""""""""""

We actually have two methods to compute the points sampled for a ray : 

* without interpolation : this is the simplest one. For each sample point we are simply taking the value of the voxel the point is in.
* with interpolation : In this case we are computing the point sampled value from the four neighbooring voxels and adding a weight to those values according to the distance between the sample point ant the center of the sample voxels.

.. note:: Due to the algorithm we have to keep in memory the voxel used to sample each point and the weight (distace to the voxel center). So the withinterpolation method is about four time more memory consuming. 

Outgoing beam algorithm
"""""""""""""""""""""""

In the case of a fluorescence (or compton) reconstruction or projection we have to estimate the outgoing ray.
We have three algorithm to do this : 

* raw approximation : this is the faster way to compute those but this also include a big approximation. We are computing one ray per voxel. And we will take for the incoming ray point sampled the value of the voxel the point is in. Due to the algorithm this can "blur" the projection and the reconstruction.

* matrix subdivision : this is the same approach as raw approximation except that we are subdividing each voxel into :math:`n.n` voxels. You can set n with the setSubdivisionSelfAbsMat. This is also more heavy in memory because the self abs mat will be multiple by n in both dimension. Otherwise thise doesn't affect the size in memory of the sample points but add one conversion.

* createOneRayPerSamplePoint : this will for each sample point of the incoming ray create and estimate the real outgoing ray. But if we have :math:`n` voxels with :math:`x` sample we will produce :math:`nx` rays (and :math:`nx` sample point for rays in the worst case ). This is the method closest to the reallity but also the more costly approach (in memory and in computational time)

Diffraction
^^^^^^^^^^^
Has you might saw, the structure of the diffraction is in the FreeART source code. But none of ot has been tested (and has unit tests.).
So it is has been removed from the python interface for now.

Building documentation
----------------------

Python documentation
^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash
    :emphasize-lines: 3,5

    python setup.py build_doc

Note : sphinx should be installed

Debugging and analysing
^^^^^^^^^^^^^^^^^^^^^^^

you can run your unit tests locally 

.. code-block:: bash
    :emphasize-lines: 3,5

    python run_tests.py -i 


You can debug using valgrind for example

Debugging with gdb
""""""""""""""""""

see https://wiki.python.org/moin/DebuggingWithGdb

Analysing with valgrind
"""""""""""""""""""""""

Analysing function call

.. code-block:: bash
    :emphasize-lines: 3,5

    valgrind --tool=callgrind python
    
    >>> execfile("my_script.py")

Checking for memory leaks


.. code-block:: bash
    :emphasize-lines: 3,5

    valgrind --tool=memcheck python
    
    >>> execfile("my_script.py")


Platform tested
----------------

Debian 8 - 64 bits 

* python 2.7
* python 3.4
* python 3.5


A fiew information about sampling algorithm:
""""""""""""""""""""""""""""""""""""""""""""

- Rays are 'inverted'. This mean that the first points sampled by the ray are the last points stored by the ray.
Final points
- direction of the ray is also inverted
- rays are now storing all the point sampled.
- some 'normalization' work have been started in the 'new binding' branch. Also including a python binding for the sampling algorithm. This is not ended.
