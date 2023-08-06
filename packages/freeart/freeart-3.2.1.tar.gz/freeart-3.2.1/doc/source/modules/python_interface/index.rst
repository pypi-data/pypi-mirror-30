
.. currentmodule:: freeart.FreeART

:class:`FreeARTBaseClass`
-------------------------

FreeART API

Transmission class
""""""""""""""""""

.. code-block:: python

   import freeart
   import scipy.misc
   import numpy

   # forward projection
   image = scipy.misc.ascent()
   image.reshape(image.shape[0], image.shape[1], 1)
   freeart.TxBckProjection(image.astype(numpy.float64), numpy.linspace(0, numpy.pi))

   algoProj = freeart.TxFwdProjection(l.astype(numpy.float64), minAngle=0, maxAngle=numpy.pi, anglesNb=360)
   sino, angles = algoProj.makeSinogram()

   # backward projection
   algoRecons = freeart.TxBckProjection(sino, angles)
   recons = algoRecons.iterate(1)


.. autoclass:: TxFwdProjection
   :show-inheritance:
   :members: makeSinogram


.. autoclass:: TxBckProjection
   :show-inheritance:
   :members: iterate

Fluorescence class
""""""""""""""""""

.. code-block:: python

   import freeart
   from freeart.utils import genph
   import numpy

   # forward projection
   phGenerator = genph.PhantomGenerator()
   sheppLogan_phantom = phGenerator.get2DPhantomSheppLogan(128)
   sheppLogan_phantom.shape = (sheppLogan_phantom.shape[0], sheppLogan_phantom.shape[1], 1)

   absMat     = sheppLogan_phantom * 20.0 
   selfAbsMat = sheppLogan_phantom / 10.0 

   detPos = (0., 1000., 0.)
   detSetup = [(detPos, 10.)]

   alProj = freeart.FluoFwdProjection(phMatr=sheppLogan_phantom, 
                                                     expSetUp=detSetup,
                                                     absorpMatr=absMat,
                                                     selfAbsorpMatrix=selfAbsMat,
                                                     minAngle=0., 
                                                     maxAngle=numpy.pi*2.0, 
                                                     anglesNb=360)

   sinogram, angles = alProj.makeSinogram()

   # backward projection
   alRecons = freeart.FluoBckProjection(sinoDat=sinogram, sinoAngles=angles, expSetUp=detSetup, 
            absorp=absMat, selfAbsorp=selfAbsMat)
   recons = alRecons.iterate(1) 

.. autoclass:: FluoFwdProjection
   :show-inheritance:
   :members: makeSinogram

.. autoclass:: FluoBckProjection
   :show-inheritance:
   :members: iterate

