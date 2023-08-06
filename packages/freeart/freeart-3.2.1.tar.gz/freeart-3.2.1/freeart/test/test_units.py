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
from freeart.utils import unittestpercentage, raypointsmethod, outgoingrayalgorithm, reconstrutils, testutils
from freeart.unitsystem import metricsystem

class testUnits(unittestpercentage.testPercentage):
    """Here we want to test the incoming beam attenuation in a stacks of voxels."""

    origin          = (0.0, 0.0)
    detectorRadius  = 10.0 *metricsystem.cm
    detectorArea    = detectorRadius * 2.0
    detectorWidth   = detectorRadius*2.0
    detectorDistance = 1000 *metricsystem.cm

    def testCompareMillimeterAndCentimeter(self):
        """
        A simple test to make sure absortpion across a voxel of 1cm is close to the absorption of 10 voxels of 1mm
        if the absorption in those voxels (in g/cm2) is the same 
        """
        incomingAbsorption = 1.0
        interactionProba = 1.0
        outgoingAbsorptionFactor = 0.0 # g/cm2
        phDimX = 31 # voxel
        phDimY = 31 # voxel
        phDimZ = 1  # voxel

        # to avoid bord effect it is better to avoid interpolation 
        methodGBeams = raypointsmethod.withInterpolation
        # and set sampling to 1
        oversampling = 4
        optionOutgoing = outgoingrayalgorithm.rawApproximation

        detAngle = 0
        detPos = (np.sin(detAngle)*self.detectorDistance, np.cos(detAngle)*self.detectorDistance, 0.0)
        detSetup = [(detPos, self.detectorRadius)]
        
        ### RUN the FREE ART EXPERIMENTATION
        phantom_cm = np.zeros((phDimX, phDimY, phDimZ), dtype=np.float64)
        phantom_cm[15, 15, 0] = interactionProba
        absMat_cm = np.zeros((phDimX, phDimY, phDimZ), dtype=np.float64)
        absMat_cm[15, 15, 0] = incomingAbsorption
        selfAbsMat_cm = np.zeros((phDimX, phDimY, phDimZ), dtype=np.float64)
        selfAbsMat_cm[15, 15, 0] = outgoingAbsorptionFactor

        phantom_mm = np.zeros((phDimX, phDimY, phDimZ), dtype=np.float64)
        phantom_mm[8:18, 8:18, 0] = interactionProba
        absMat_mm = np.zeros((phDimX, phDimY, phDimZ), dtype=np.float64)
        absMat_mm[8:18, 8:18, 0] = incomingAbsorption
        selfAbsMat_mm = np.zeros((phDimX, phDimY, phDimZ), dtype=np.float64)
        selfAbsMat_mm[8:18, 8:18, 0] = outgoingAbsorptionFactor

        sinogram_cm, angles = reconstrutils.makeFreeARTFluoSinogram(
            phantom_cm, absMat_cm, selfAbsMat_cm, 1, detSetup, oversampling, methodGBeams, optionOutgoing, 
            voxelSize=1.0*metricsystem.cm, turnOffSolidAngle=True );

        sinogram_mm, angles = reconstrutils.makeFreeARTFluoSinogram(
            phantom_mm, absMat_mm, selfAbsMat_mm, 1, detSetup, oversampling, methodGBeams, optionOutgoing, 
            voxelSize=1.0*metricsystem.mm, turnOffSolidAngle=True );

        # sinogram_mm return It ot in the case of voxel set to 1 mm then as the absortpion is computing 
        # on the voxel surface the ray will be less absorbed.
        self.assertAlmostEqual( sinogram_mm[0][0][15], sinogram_cm[0][0][15], 1)

    def testFluoRecons(self):
        """
        Simple test on having a fluo reconstruction with a voxel size set to 1.2 mm
        """
        oversampling = 12
        nbIterations = 3
        voxelSize = 1.2*metricsystem.millimeter

        detPos = (1000*metricsystem.cm, 0, 0)
        detSetup = [(detPos, self.detectorRadius)]
        sheppLogan = testutils.SheppLoganReconstruction()

        sino, angles, absMat, selfAbsMat, initialPhantom = sheppLogan.produce_SheppLogan_sinogram(32, _oversampling=oversampling, 
            _anglesNb=400, _detSetup=detSetup, _voxelSize = voxelSize )

        reconstructedPhantom = sheppLogan.make_reconstruction(_sinogram=sino, _angles=angles, _absMat=absMat, 
            _selfAbsMat=selfAbsMat, _detSetup=detSetup, _nbIter=nbIterations, _oversampling=oversampling, 
            _voxelSize = voxelSize, _dampingFactor=0.05)

        np.testing.assert_allclose(reconstructedPhantom, initialPhantom, rtol=0.15, atol=1e-3)

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(testUnits))
    return test_suite

if __name__ == '__main__' and __package__ is None :
    unittest.main(defaultTest="suite")