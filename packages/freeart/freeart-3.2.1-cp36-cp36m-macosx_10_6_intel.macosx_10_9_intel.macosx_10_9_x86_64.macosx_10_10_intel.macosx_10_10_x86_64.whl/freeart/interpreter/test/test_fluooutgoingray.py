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
from freeart.unitsystem import metricsystem
from freeart.utils import reconstrutils, raypointsmethod, outgoingrayalgorithm

import logging
_logger = logging.getLogger("unitests")

class testFluoSubdivisionSampling(unittest.TestCase):
    """The  unit test to check if the option matriceSubdivision for computing the values of the outgoing attenuation is correct.
    Note : previously we had tests for incoming or outgoing beam attenaution effect using the option withInterpolation.
    This is not very relevant here because the interpolation will get the value fron the close voxels for the density (phantom), 
    the incoming beam attenuation (absMat) AND the outgoing beam attenaution. So this complexifiate the theoretical value
    we are supposed to get. Or to simplify we have to take large phantom and this slow down the results.
    """

    phDimX = 3
    phDimY = 3
    phDimZ = 1

    detectorRadius = 10.0 * metricsystem.cm
    detectorDistance = 1000.0 * metricsystem.cm

    def test_outgoingRayCalculation(self):           
        """Test the attenuation for the outgoing beam hitting n lines of material.
        Material attenuation of the incoming beam is zero.
        Material attenuation of the outgoing beam is outgoingAbsorptionFactor 
        To make sure results are ok we are testing different detector position, 
        which are directly defining the angle of the outgoing beam.
        """

        # The outgoing beam attenuation to consider for this test case
        outgoingAbsorptionFactor = 1.0  # g/cm2
        interactionProba = 1.0

        detAngle = np.pi/4.0
        oversamplings = [100]
        subdivisionFactors = [10]

        methodGBeams = raypointsmethod.withoutInterpolation

        detPos = (np.sin(detAngle)*self.detectorDistance, np.cos(detAngle)*self.detectorDistance, 0)
        detSetup = [(detPos, self.detectorRadius)]

        ### RUN the FREE ART EXPERIMENTATION
        # create the simple phantom
        phantom    = np.zeros((self.phDimX, self.phDimY, self.phDimZ), dtype=np.float64)
        absMat     = np.zeros((self.phDimX, self.phDimY, self.phDimZ), dtype=np.float64)
        selfAbsMat = np.zeros((self.phDimX, self.phDimY, self.phDimZ), dtype=np.float64)

        phantom[1, 1, 0]    = interactionProba
        selfAbsMat[1, 1, 0] = outgoingAbsorptionFactor

        for oversampling in oversamplings : 
            # The value here for an angle of 45 degree should get close to 1/2 with a constant solid angle of 1 
            # will cover the full voxel. So beams hitting the detector should cover the entire voxel and go throught a mean of half the voxel
            # so the result should approach np.exp(-1.0*0.5)
            _logger.info("\n\n OVERSAMPLING = " + str(oversampling))
            _logger.info("\n -- RAW --  ")
                
            optionOutgoing = outgoingrayalgorithm.rawApproximation
            sinogram, angles = reconstrutils.makeFreeARTFluoSinogram(
                phantom, absMat, selfAbsMat, 1, detSetup, oversampling, methodGBeams, optionOutgoing, turnOffSolidAngle = True );
            theoreticalResult = np.exp(-np.sqrt(2)*0.5)
            np.testing.assert_allclose(sinogram[0][0], [0.0, theoreticalResult, 0.0], rtol=0.1 )

            _logger.info("\n -- CREATE ONE RAY PER SAMPLE POINT --  ")
    
            # this method gave the true attenaution off the outgoing ray. But we still have to sample enought point to get the true result.
            optionOutgoing = outgoingrayalgorithm.createOneRayPerSamplePoint
            sinogram, angles = reconstrutils.makeFreeARTFluoSinogram(
                phantom, absMat, selfAbsMat, 1, detSetup, oversampling, methodGBeams, optionOutgoing, turnOffSolidAngle = True );

            theoreticalResult = np.exp(-1*0.5)
            np.testing.assert_allclose(sinogram[0][0], [0.0, theoreticalResult, 0.0], rtol=0.1 )

            _logger.info(" -- MATRICE SUBDIVISION -- ")

            for subdivisionFactor in subdivisionFactors : 
                _logger.info("subdivision factor : " + str(subdivisionFactor))
    
                optionOutgoing = outgoingrayalgorithm.matriceSubdivision
        
                sinogram, angles = reconstrutils.makeFreeARTFluoSinogram    (
                    phantom, absMat, selfAbsMat, 1, detSetup, oversampling, methodGBeams, optionOutgoing, subdivisionValue=subdivisionFactor, turnOffSolidAngle=True );

                theoreticalResult = np.exp(-(interactionProba*outgoingAbsorptionFactor*0.5))
                _logger.info("res : " + str(sinogram[0][0][1]))
                _logger.info("theoretical res : " + str(theoreticalResult))

                np.testing.assert_allclose(sinogram[0][0], [0.0, theoreticalResult, 0.0], rtol=0.1 )
                
def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(testFluoSubdivisionSampling))
    
    return test_suite

if __name__ == '__main__':
    unittest.main(defaultTest="suite")