Tutorials
=========

Create and save a simple absorption matrix
-------------------------------------------

In many cases you might need to generate an absorption matrix to give to freeart.
It might be a numpy array of float64 type to be compliant with the actual version of freeart.

Here is a short example of the generation of such a matrix to an edf file from an ipython console :

.. code-block:: bash
    :emphasize-lines: 3,5

    import numpy
    from freeart.utils import reconstrutils
    # initialize a 56x56 matrix
    mat=numpy.zeros((56, 56),dtype=numpy.float64)
    reconstrutils.saveMatrix(mat, "myMat.edf")


Run freeart from command line
-----------------------------

If you are an advanced user then you can have a look a the freeart API which will give you access to many option and a large control of operations.
For "classical" users you can create a cfg file that freeart will be able to interprete and launch a recosntruction from.

Here is an example from an ipython console : 

.. code-block:: bash
    :emphasize-lines: 3,5

    from freeart.interpreter.configInterperter import GlobalConfigInterpreter
    interpreter = GlobalConfigInterpreter("<filePath.cfg>")

    # then you can iterate directly from this interpreter.
    interpreter.iterate(<nbIteration>)

    # then you can see or save the reconstructed phantom :
    interpreter.saveCurrentReconstructionsTo(<path to folder>)

    # or you can access to all ART algorithm generated
    for art_algo in interpreter.getReconstructionAlgorithms():
        # and operate on them (like saving reconstructed phantom or normalized sinogram)
        reconstrutils.savePhantom( algos[algoName].getPhantom(), outputFile )

.. note:: each iteration will run each back projection once

You can see an example of the cfg struture in the nexe section


.. note:: For now the interpreter for fluorescence and compton need to get directly the absorption matrix and the self absorption matrix. Because we don't want to deal with an input validation of matrices in the "core" library. But you can start from I0 and It fromthe GUI (tomoGUI). 

Configuration file for reconstruction
-------------------------------------

Here is a simple example of a cfg file for transmission : 

.. code-block:: text
    :emphasize-lines: 3,5


    [general_settings]
    reconstruction_type = Transmission
    
    [data_source_tx]
    sino_file = <pathToSinigram.edf>
    
    [reconstruction_properties]
    voxel_size = 2.5                        
    oversampling = 6
    relaxation_factor = 0.04
    
    [projection_information]
    min_angle = 0.0
    max_angle = 6.28318530718               
    start_projection = 0
    end_projection = 359            

for compton :

.. code-block:: text
    :emphasize-lines: 3,5

    [general_settings]
    reconstruction_type = Compton
    ; 2016-10-20 at 13:32:19.545258 = 
    ; freeartconfig version : 3.0.0 = 
    ; tomogui version : 0.0.0-dev1 = 
    freeart_version = 3.0.0

    [data_source_fluo]
    absorption_file_is_a_sinogram = False
    absorption_file = <pathToAbsMat.edf>
    interaction_matrix_file = 
    self_absorption_file = 
    materials_file = 

    [fluo_sino_file_0]
    file_path = <pathToSinigram1.edf>
    data_set_index_0 = 0
    data_name_0 = Cu
    data_physical_element_0 = Cu
    ef_0 = 1.0

    [fluo_sino_file_1]
    file_path = <pathToSinigram2.edf>
    data_set_index_0 = 0
    data_name_0 = Fe
    data_physical_element_0 = Fe
    ef_0 = 1.0

    [normalization]
    rotation_center = 327
    normalizei0fromafile = False
    i0 = 1.0

    [reconstruction_properties]
    voxel_size = 1.0
    oversampling = 10
    relaxation_factor = 0.01
    bean_calculation_method = 0
    outgoing_bean_calculation_method = 0
    solid_angle_is_off = False
    include_last_angle = False

    [reduction_data]
    definition_reducted_by = 2
    projection_number_reducted_by = 1

    [projection_information]
    min_angle = 0.0
    max_angle = 6.28318530718
    start_projection = 0
    end_projection = 321

    [detector_setup]
    detector_width = 1.0
    det_pos_x = 1000.0
    det_pos_y = 1000.0
    det_pos_z = 0.0


Configuration interpreter
.........................

:mod:`freeart.interpreter.configinterpreter`: API of the configuration interpreter

:mod:`freeart.interpreter.config`: keywords used into the cfg file
