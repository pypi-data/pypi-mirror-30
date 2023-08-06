from freeart.utils import reconstrutils, testutils
import freeart
import numpy

width=128
phantom = numpy.zeros((width, width, 1), dtype=numpy.float)
absMat = phantom.copy()

phantom[34:94, 34:94] = 1.0
absMat[34:94, 34:94] = 5.0
selfAbsMat = absMat.copy() * 1.5

detAngle = numpy.pi/2.0
detectorDistance = 1000
detPos = (numpy.sin(detAngle), numpy.cos(detAngle), 0.0)
detectorRadius = 200
detSetup = [(detPos, detectorRadius)]
voxelSize = 0.001

# generate sinogram
sinogram, angles = reconstrutils.makeFreeARTFluoSinogram(phantom=phantom,
                                                         absMat=absMat,
                                                         selfAbsMat=selfAbsMat,
                                                         numAngle=180,
                                                         detSetup=detSetup,
                                                         oversampling=8,
                                                         beamCalcMeth=0,
                                                         outRayPtCalcMeth=0,
                                                         voxelSize=voxelSize,
                                                         minAngle=0.0,
                                                         maxAngle=numpy.pi)

reconstrutils.saveMatrix(sinogram, 'sinogram.edf')
reconstrutils.saveMatrix(phantom, 'initialPhantom.edf')

# reconstruction
nbIterations = 10
oversampling = 8
dampingFactor = 0.03

# reconstruction without self Abs
artRecons = freeart.FluoBckProjection(sinoDat=sinogram,
                                      sinoAngles=angles,
                                      absorp=absMat,
                                      selfAbsorp=selfAbsMat,
                                      expSetUp=detSetup)
artRecons.setOverSampling(oversampling)
artRecons.setDampingFactor(dampingFactor)
artRecons.setVoxelSize(voxelSize)
reconstructedPhantom = artRecons.iterate(nbIterations)

reconstrutils.saveMatrix(reconstructedPhantom, 'reconsPhantom.edf')

# with a no selfAbsMat
artRecons = freeart.FluoBckProjection(sinoDat=sinogram,
                                      sinoAngles=angles,
                                      absorp=absMat,
                                      selfAbsorp=numpy.zeros(absMat.shape,
                                                          dtype=numpy.float64),
                                      expSetUp=detSetup)
artRecons.setOverSampling(oversampling)
artRecons.setDampingFactor(dampingFactor)
artRecons.setVoxelSize(voxelSize)
reconstructedPhantomNoSelfAbs = artRecons.iterate(nbIterations)

reconstrutils.saveMatrix(reconstructedPhantomNoSelfAbs,
                         'reconsPhantomNoSelfAbs.edf')

# with a no abs and no selfAbs
artRecons = freeart.FluoBckProjection(sinoDat=sinogram,
                                      sinoAngles=angles,
                                      absorp=numpy.zeros(absMat.shape,
                                                      dtype=numpy.float64),
                                      selfAbsorp=numpy.zeros(absMat.shape,
                                                          dtype=numpy.float64),
                                      expSetUp=detSetup)
artRecons.setOverSampling(oversampling)
artRecons.setDampingFactor(dampingFactor)
artRecons.setVoxelSize(voxelSize)
reconstructedPhantomAbsAndNoSelfAbs = artRecons.iterate(nbIterations)

reconstrutils.saveMatrix(reconstructedPhantomAbsAndNoSelfAbs,
                         'reconsPhantomNoAbsorptions.edf')
exit(0)