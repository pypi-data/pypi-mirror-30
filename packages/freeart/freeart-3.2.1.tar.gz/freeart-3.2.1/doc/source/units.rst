Units
=====

* The default metric in FreeARt is the centimeter.

* Absorption is always record as :math:`g.cm^{-2}`. 
    Internally to compute the absorption in the voxel we will compute the absorption from 
    stepLength*voxelAbsorption with 
        - stepLength = distance cross the voxel 
        - voxelAbsorption = absorption on this voxel (:math:`g.cm^{-2}`)


in python
"""""""""

.. code-block:: python
    :emphasize-lines: 3,5
    
    from freeart.unitsystem import metricsystem 
    ...
    detectorDistance = 1000 *metricsystem.cm
    detectorRadius  = 10.0 *metricsystem.mm
    ...

in cpp
""""""

.. code-block:: cpp
    :emphasize-lines: 3,5
    
    #include <units.h>
    ...
    FreeART::ExperimentSetUp esu(1, FreeART::DetectorSetUp(FreeART::Position_FC(1000.0*UNITS::cm, 0.0,0.0), 10*UNITS::mm));
    ...