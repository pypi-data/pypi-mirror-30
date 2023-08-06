IO data in FreeART
==================

Main inputs and outputs data for FreeART are :
They are structured as presented :

* **sinogram** : This is the output of a projector (forward projection) and the input of a reconstruction algorithm.
    It is a 3D vector but for now we only take into account 2D sinograms. 
    Shape should be :

    * first dimension for now should always be 1 until we stay in 2D.
    * second dimension is the number of projections.
    * third dimension is the definition of the detector (number of cell). We will simulate one ray per cell during the reconstruction.

* **phantom** : This is the input of a projector and the output of a reconstruction. This is a voxelisation of the sample. Shape is the following :

    * first dimension : represents the x axis of the phantom voxelisation (should be equal to the third dimension of the sinogram ) 
    * second dimension : represents the y axis of the phantom voxelisation (should be equal to the third dimension of the sinogram and to the first dimension of the phantom )
    * third dimension : for now should always be 1 until we stay in 2D.

* **absorption matrices** : In the case of fluorescence we can add the effect of the **incoming beam absorption** (with the **absorption matrix**)) AND the **outgoing beam absorption** (with the **self absorption matrix**).
    This can be an input for the sinogram generation (in compton or in fluorescence) or during a reconstuction.
    The shape of those matrices are  mimicking the phantom structure. At each voxel we set the absorption in :math:`g.cm^{-2}`.
