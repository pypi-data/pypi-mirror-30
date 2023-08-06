Transmission
============

Generate a sinogram
-------------------
FreeART offers a transmission projector to produce a sinogram from a phantom.
You don t have to deal with the detector has FreeART will automatically setup the experimentation to define a detector at 180 degree from the incoming beam source. 

From python
"""""""""""

.. code-block:: python
    :emphasize-lines: 3,5
    
    import freeart
    
    # the simplest way to produce a sinogram from a phantom is the following call :
    projector = freeart.TxFwdProjection(phantom, minAngle = 0, maxAngle = 2.0*np.pi, anglesNb = 40)
    sinogram, angles = projector.makeSinogram()


.. note:: A larger example is given in freeart/python_utils/example_tx.py


From cpp
""""""""
.. code-block:: cpp
    :emphasize-lines: 3, 5

    // setting up the geometry for the sinogram generation
    algoIO.prepareSinogramGeneration(phantomFileName, 0.0, 2.0*M_PI, 125, phantom, sinosGeo);

    // defining the transmission reconstruction (here to use double precision )
    FreeART::SARTAlgorithm<double,FreeART::TxReconstruction>* al = new FreeART::SARTAlgorithm<double,FreeART::TxReconstruction>(phantom,sinosGeo);
    // launch the projection
    al->makeSinogram();
    // get the sinogram generated
    FREEART_NAMESPACE::GenericSinogram3D<double> sinogram = al->getSinogram();

.. note:: A larger example is given into examples/cpp/projector_tx.cpp


Reconstruction
--------------

For a transmission reconstruction you need  : 
    - a sinogram matrix.
    - the angle of acquisition of the given sinogram

From python
"""""""""""

.. code-block:: python
    :emphasize-lines: 3,5

    import freeart

    # the simplest way to make a reconstruction fron a sinogram and a set of angles is :
    reconstruction = freeart.TxBckProjection(_sinogram, _angles)
    # set the relaxation factor. Key parameter for an ART reconstruction
    reconstruction.setDampingFactor(0.02)
    reconstructed_phantom = reconstruction.iterate(_nbIter)

From cpp
""""""""

.. code-block:: cpp
    :emphasize-lines: 3, 5

    // set up the geometry (sinosgeo) and the stack of sinogram (sinos)
    // from a sinoFile and an experiemt setup.
    // Here because we are in the transmission case, the experiment setup can be empty of detector
    algoIO.buildSinogramGeometry(sinoFile, esu, sinos, sinosGeo);

    // create the transmission reconstruction
    FreeART::SARTAlgorithm<double,FreeART::TxReconstruction> *al;
    al = new FreeART::SARTAlgorithm<double,FreeART::TxReconstruction>(sinos,sinosGeo);
    // launch the reconstruction over iterNb iterations
    al->doWork(iterNb);

    // get the reconstructed phantom
    const FreeART::BinVec3D<double>* v = &(al->getPhantom());


.. note:: A more detailled example is given in the freeart/cpp_utils/projector_fluo.cpp file


