# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "01/09/2016"

import unittest
import numpy as np

import freeart
from freeart.utils import unittestpercentage, reconstrutils, testutils, raypointsmethod, outgoingrayalgorithm
from freeart.unitsystem import metricsystem

import logging
_logger = logging.getLogger("unitests")

class testRayParameters(unittestpercentage.testPercentage):
    """The class to test some of the parameters relative to rays"""

    # detector properties
    detectorRadius  = 10.0 *metricsystem.cm
    detectorDistance = 1000 *metricsystem.cm
    # Dimensions of the phantom to test
    phDimX = 9 # voxels
    phDimY = 9 # voxels
    phDimZ = 1 # voxels

    xpos   = 4 # voxels
    ypos   = 4 # voxels
    zpos   = 0 # voxels

    origin = (0.0, 0.0, 0.0)

    I0 = 17.5e4 

    voxelPosInPhantomRef = (xpos, ypos, zpos)
    voxelPosInExpRef = testutils.toExperimentationRef( voxelPosInPhantomRef, phDimX, phDimY, phDimZ)

    # we are setting an hight value to get close from the theoretical values
    oversampling = 10
    # For this test case we are skipping the attenuation of the incoming beam and only focusing on the outgoing
    interactionProba = 1.0

    def testRayIntensityProjection(self):           
        """
        Check if the intensity of the source is well taking into account during the projection
        """

        _logger.info("running testRayIntensity")

        # The outgoing beam attenuation to consider for this test case
        incomingAbsorptionFactor = 0.5 
        outgoingAbsorptionFactor = 0.25

        methodGBeams = raypointsmethod.withInterpolation
        optionsOutgoing = [ outgoingrayalgorithm.createOneRayPerSamplePoint, 
            outgoingrayalgorithm.matriceSubdivision, 
            outgoingrayalgorithm.rawApproximation ] 

        detAngle = 0.0
        # we are in the trigonometric reference
        detPos = (np.sin(detAngle)*self.detectorDistance, np.cos(detAngle)*self.detectorDistance, self.zpos)
        detSetup = [(detPos, self.detectorRadius)]

        ### RUN the FREE ART EXPERIMENTATION
        # create the simple phantom
        phantom    = np.zeros((self.phDimX, self.phDimY, self.phDimZ), dtype=np.float64)
        absMat     = np.zeros((self.phDimX, self.phDimY, self.phDimZ), dtype=np.float64)
        selfAbsMat = np.zeros((self.phDimX, self.phDimY, self.phDimZ), dtype=np.float64)

        # dans ce cas dans le repere de freeART les lignes se trouve en (:, -5:-7)
        phantom[self.ypos, self.xpos, self.zpos]    = self.interactionProba
        absMat[self.ypos, self.xpos, self.zpos]     = incomingAbsorptionFactor
        selfAbsMat[self.ypos, self.xpos, self.zpos] = outgoingAbsorptionFactor

        for optionOutgoing in optionsOutgoing :

            sinogram, angles = reconstrutils.makeFreeARTFluoSinogram(
                phantom, absMat, selfAbsMat, 1, detSetup, self.oversampling, methodGBeams, optionOutgoing, I0=self.I0 )

            # The momentum when we are going trought the n voxel ( n == width )
            I_FreeARTValue_NVoxels = sinogram[0][0][self.xpos]

            ### GET THE THEORETICAL VALUES
            I_theoreticalValue_NVoxels = testutils.getFluoTheoreticalValue(
                detPos,
                self.detectorRadius,
                self.voxelPosInExpRef,           # < voxel position in the freeART reference
                incomingAbsorptionFactor,        # < mass attenuation for the incoming beam
                outgoingAbsorptionFactor,        # < mass attenuation for the outgoing beam
                np.pi/2.0,                       # < angle of entry of the incoming beam
                np.pi/2.0 - detAngle,            # < outgoing beam angle to the sample
                1.0,                             # < tau
                1.0,                             # < material width (in cm)
                I0=self.I0
                )


            _logger.info("theoreticalValue n voxel 0 s= " + str(I_theoreticalValue_NVoxels))
            _logger.info("FreeART value 0 = " + str(I_FreeARTValue_NVoxels))
            _logger.info("error = " + str(self.getError(I_theoreticalValue_NVoxels, I_FreeARTValue_NVoxels)) + " %")
            
            self.assertErrorPercentageAlmostEqual( I_theoreticalValue_NVoxels, I_FreeARTValue_NVoxels, 5 )

    def testRayIntensityReconstruction(self):
        """Check if the intensity of the source is well taking into account during the projection and the reconstruction"""

        _logger.info("running testRayIntensity")

        # The outgoing beam attenuation to consider for this test case
        incomingAbsorptionFactor = 0.5 
        outgoingAbsorptionFactor = 0.25

        methodGBeams = raypointsmethod.withInterpolation
        optionsOutgoing = [ outgoingrayalgorithm.createOneRayPerSamplePoint,
            outgoingrayalgorithm.matriceSubdivision, 
            outgoingrayalgorithm.rawApproximation ] 

        detAngle = 0.0
        # we are in the trigonometric reference
        detPos = (np.sin(detAngle)*self.detectorDistance, np.cos(detAngle)*self.detectorDistance, self.zpos)
        detSetup = [(detPos, self.detectorRadius)]

        ### RUN the FREE ART EXPERIMENTATION
        # create the simple phantom
        initial_phantom    = np.zeros((self.phDimX, self.phDimY, self.phDimZ), dtype=np.float64)
        absMat     = np.zeros((self.phDimX, self.phDimY, self.phDimZ), dtype=np.float64)
        selfAbsMat = np.zeros((self.phDimX, self.phDimY, self.phDimZ), dtype=np.float64)

        # dans ce cas dans le repere de freeART les lignes se trouve en (:, -5:-7)
        initial_phantom[self.ypos, self.xpos, self.zpos]    = self.interactionProba
        absMat[self.ypos, self.xpos, self.zpos]     = incomingAbsorptionFactor
        selfAbsMat[self.ypos, self.xpos, self.zpos] = outgoingAbsorptionFactor

        for optionOutgoing in optionsOutgoing :

            sinogram, angles = reconstrutils.makeFreeARTFluoSinogram(
                initial_phantom, absMat, selfAbsMat, 60, detSetup, self.oversampling, methodGBeams, optionOutgoing, I0=self.I0 )


           # make the reconstruction with the absMat
            alRecons = freeart.FluoBckProjection(sinoDat=sinogram, sinoAngles=angles, expSetUp=detSetup, absorp=absMat, selfAbsorp=selfAbsMat)

            alRecons.setOverSampling(self.oversampling)
            alRecons.setDampingFactor(0.1)
            alRecons.setRayPointCalculationMethod(raypointsmethod.withInterpolation)
            alRecons.setOutgoingRayAlgorithm(optionOutgoing)
            alRecons.setSubdivisionSelfAbsMat(2)
            alRecons.setI0(self.I0)
            alRecons.setRandSeedToZero(True)
            alRecons.setVoxelSize(1.0*metricsystem.cm)
            
            reconstructedPhantom = alRecons.iterate(2)
            _logger.info("testing outgoingMethod " + str(optionOutgoing))
            _logger.info("theoretical value = " + str(self.interactionProba))
            _logger.info("freeART value = " + str(reconstructedPhantom[self.ypos, self.xpos]) )

            np.testing.assert_allclose(initial_phantom, reconstructedPhantom, rtol=0.12 , atol=1e-2 )

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(testRayParameters))
    
    return test_suite

if __name__ == '__main__':
    unittest.main(defaultTest="suite")
