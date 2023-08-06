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
__date__ = "16/11/2017"

import unittest
import numpy as np
import silx
if silx._version.MINOR < 7:
    from silx.test.utils import ParametricTestCase
else:
    from silx.utils.testutils import ParametricTestCase
import freeart
from freeart.unitsystem import metricsystem
from freeart.utils import raypointsmethod, testutils
import numpy
import logging

_logger = logging.getLogger("unitests")


class TestTxProjection_2D(ParametricTestCase):
    """
    the unit test related to the transmission projector in a classical 2D case
    """

    oversampling = 1
    phDimX = 101
    phDimY = 101
    phDimZ = 1

    def test_projector_1(self):
        """
        A simple test to try the projector on a single attenuating voxel
        """
        xpos = 50
        ypos = 50
        zpos = 0

        for precision in [numpy.float32, numpy.float64]:
            for I0 in [2.0, 3.5e3, 9.8e8]:
                for voxelSize in [1.0*metricsystem.centimeter, 2.3*metricsystem.millimeter, 0.56*metricsystem.meter]:
                    # all the absorption factor to test
                    for absorption_factor in np.linspace(0.2, 10, 5):
                        with self.subTest(precision=precision, I0=I0, voxelSize=voxelSize, absorptionFactor=absorption_factor):
                            # create the simple phantom
                            phantom = np.zeros((self.phDimX, self.phDimY, self.phDimZ),
                                               dtype=precision)
                            phantom[ypos, xpos, zpos] = absorption_factor  # unit : g/cm2

                            # create the sinogram
                            al = freeart.TxFwdProjection(phantom,
                                                         minAngle=0,
                                                         maxAngle=2.0*np.pi,
                                                         anglesNb=9)
                            al.setOverSampling(8)
                            al.setVoxelSize(voxelSize)
                            al.setI0(I0)
                            sinogram, angles = al.makeSinogram()

                            # check that the max value <=> absorption_factor on the voxel == theoretical value
                            dist_in_mat = 1.0 * voxelSize    # distance : 1.0 cm
                            theoreticalValue = np.exp(-dist_in_mat*absorption_factor)*I0
                            # we are only interested of the sinogram obtained for the central ray for the first angle ( 0 degree ).
                            freeARTValue = sinogram[0][0][xpos]

                            if precision == numpy.float64:
                                self.assertAlmostEqual(first=precision(theoreticalValue),
                                                       second=freeARTValue)

    def test_projector_3(self):
        """
        a simple test to check values for a uniform filled in a 3x3 voxels phantom
        """
        voxelSize = 1.0 * metricsystem.centimeter
        for precision in [numpy.float32, numpy.float64]:
            for absorption_factor in np.linspace(0.2, 10, 15):
                with self.subTest(precision=precision, absorption_factor=absorption_factor):

                    # create the simple phantom
                    phantom = np.zeros((self.phDimX, self.phDimY, self.phDimZ), dtype=precision)
                    phantom[49:52, 49:52, 0] = absorption_factor  # unit : g/cm2

                    # create the sinogram
                    al = freeart.TxFwdProjection(phantom,
                                                 minAngle=0,
                                                 maxAngle=2.0*np.pi,
                                                 anglesNb=9)
                    al.setOverSampling(self.oversampling)
                    al.setRandSeedToZero(True)
                    al.setVoxelSize(voxelSize)

                    sinogram, angles = al.makeSinogram()

                    # check that the max value <=> absorption_factor on the voxel == theoretical value
                    dist_in_mat = 3.0 * voxelSize
                    theoreticalValue = np.exp(-dist_in_mat*absorption_factor)
                    # we are only interested of the sinogram obtained for the central ray for the first angle ( 0 degree ).

                    # we are only interested of the sinogram obtained for the central ray for the first angle ( 0 degree ).
                    freeARTValue1 = sinogram[0][0][49]
                    freeARTValue2 = sinogram[0][0][50]
                    freeARTValue3 = sinogram[0][0][51]

                    # when the incoming beam hit the sample at 45 degree
                    sinoVal45_degree = sinogram[0][1][50]
                    freeARTValue_45 = sinoVal45_degree
                    # when the incoming beam hit the sample at 90 degree
                    sinoVal90_degree = sinogram[0][2][50]
                    freeARTValue_90 = sinoVal90_degree

                    # check that the max value <=> absorptionFactor on the voxel == theoretical value
                    theoreticalValue = np.exp(-dist_in_mat*absorption_factor)

                    theoreticalValue_90 = np.exp(-dist_in_mat*absorption_factor)*voxelSize
                    theoreticalValue_45 = np.exp(-np.sqrt(dist_in_mat*dist_in_mat + dist_in_mat*dist_in_mat)*absorption_factor)*voxelSize

                    self.assertEqual(freeARTValue1, freeARTValue2)
                    self.assertEqual(freeARTValue1, freeARTValue3)
                    self.assertAlmostEqual(theoreticalValue, freeARTValue1)

                    self.assertAlmostEqual(theoreticalValue_90, freeARTValue_90)
                    self.assertAlmostEqual(theoreticalValue_45, freeARTValue_45)

    def test_projector_1_shifted(self):
        """
        Test one off-center voxel if we find back the theorical value
        """
        xpos = 26
        ypos = 65
        voxelSize = 1.0 * metricsystem.centimeter

        for absorptionFactor in np.linspace(0.5, 10, 10):
            # create the simple phantom
            phantom = np.zeros((self.phDimX, self.phDimY, self.phDimZ),
                               dtype=np.float64)
            phantom[ypos, xpos, 0] = absorptionFactor  # unit : g/cm2

            # create the sinogram
            al = freeart.TxFwdProjection(phantom,
                                         minAngle=0,
                                         maxAngle=2.0*np.pi,
                                         anglesNb=9)
            al.setRandSeedToZero(True)
            al.setVoxelSize(voxelSize)
            sinogram, angles = al.makeSinogram()

            # check that the max value <=> absorptionFactor on the voxel == theoretical value
            distInMat = 1.0 * voxelSize
            theoreticalValue = np.exp(- distInMat*absorptionFactor)
            # we are only interested of the sinogram obtained for the central ray for the first angle ( 0 degree ).
            freeARTValue = sinogram[0][0][xpos]

            _logger.info("theoreticalValue = " + str(theoreticalValue))
            _logger.info("freeARTValue = " + str(freeARTValue))

            self.assertAlmostEqual(theoreticalValue, freeARTValue)


class TestTxRecontruction_2D(ParametricTestCase):
    """Test that the reconstruction of the transmission work"""
    phDimX = 100
    phDimY = 100
    phDimZ = 1

    def test_reconstruction_lines_y(self):
        """
        Test the reconstruction of a phantom containig a line of voxels set
        with a uniform absorption factor
        """
        absToTest = [10.0]

        oversampling = 8
        nbIterations = 2
        I0 = 2.3e3
        voxelSize = 2.0 * metricsystem.mm

        for precision in [numpy.float32, numpy.float64]:
            for absorptionFactor in absToTest:
                with self.subTest(precision=precision, absorption_factor=absorptionFactor):

                    # make the sinogram
                    initialPhantom = np.zeros((self.phDimX, self.phDimY, self.phDimZ),
                                              dtype=precision)
                    initialPhantom[20:64, 15, 0] = absorptionFactor

                    methodGBeams = raypointsmethod.withInterpolation

                    # create the sinogram
                    alConstr = freeart.TxFwdProjection(initialPhantom,
                                                       minAngle=0,
                                                       maxAngle=2.0*np.pi,
                                                       anglesNb=360)
                    alConstr.setRandSeedToZero(True)
                    alConstr.setOverSampling(oversampling)
                    alConstr.setRayPointCalculationMethod(methodGBeams)
                    alConstr.setI0(I0)
                    alConstr.setVoxelSize(voxelSize)
                    sinogram, angles = alConstr.makeSinogram()

                    # make the reconstruction
                    alRecons = freeart.TxBckProjection(-np.log(sinogram/I0), angles)
                    alRecons.setRandSeedToZero(True)
                    alRecons.setOverSampling(oversampling)
                    alRecons.setRayPointCalculationMethod(methodGBeams)
                    alRecons.setI0(I0)
                    alRecons.setVoxelSize(voxelSize)
                    alRecons.setDampingFactor(0.2)
                    # make the reconstruction
                    reconstructedPhantom = alRecons.iterate(nbIterations)

                    _logger.info("absorptionFactor = " + str(absorptionFactor))
                    _logger.info("max value in the reconstructed = " + str(np.amax(reconstructedPhantom)))

                    if precision is numpy.float64:
                        np.testing.assert_allclose(reconstructedPhantom,
                                                   initialPhantom,
                                                   rtol=0.1,
                                                   atol=0.01)

    def test_reconstruction_symetric(self):
        """
        Test the reconstruction process on a phantom containing
        two elements.
        The background absorption is 0.
        Then on top of this background we have a cross with a value of
        absorption set to crossAbsorption.
        And on the higher level we have a disc with a value of absorption set
        to discAbsorption.
        """
        oversampling = 5
        nbIterations = 4

        methodGBeams = raypointsmethod.withInterpolation

        discRadius = 20
        I0 = 2.3e5
        voxelSize = 0.2 * metricsystem.millimeter

        # create the mask for the phantom
        crossMask = np.zeros((self.phDimX, self.phDimY), dtype=np.float64)
        crossMask[40:60, :] = 1.0
        crossMask[:, 40:60] = 1.0

        discMask = np.zeros((self.phDimX, self.phDimY), dtype=np.float64)
        discOrigin = (self.phDimX/2.0, self.phDimY/2.0)
        for x in np.arange(0, discMask.shape[0]):
            for y in np.arange(discMask.shape[1]):
                if testutils.getDistance_2D((x, y), discOrigin) <= discRadius:
                    discMask[x, y] = 1.0

        for precision in (numpy.float32, numpy.float64):
            # test for different absorption level on the disc
            for discAbsorption in (4.e-2, 5.2):
                # test for different absorption level on the cross
                for crossAbsorption in (1.e-2, 2.2):
                    with self.subTest(precision=precision,
                                      discAbsorption=discAbsorption,
                                      crossAbsorption=crossAbsorption):

                        # update the phantom
                        initialPhantom = np.zeros((self.phDimX, self.phDimY, self.phDimZ),
                                                  dtype=np.float64)
                        initialPhantom[crossMask == 1] = crossAbsorption
                        initialPhantom[discMask == 1] = discAbsorption

                        # remove the blind voxel due to the fact that freeART is reducing the projection area
                        # to the higher circle contained in the phantom (simplification)
                        initialPhantom = testutils.removeAvoidVoxel(initialPhantom)

                        alProjo = freeart.TxFwdProjection(initialPhantom,
                                                          minAngle=0,
                                                          maxAngle=2.0*np.pi,
                                                          anglesNb=360)
                        alProjo.setOverSampling(oversampling)
                        alProjo.setRayPointCalculationMethod(methodGBeams)
                        alProjo.setVoxelSize(voxelSize)
                        alProjo.setI0(I0)
                        sinogram, angles = alProjo.makeSinogram()

                        alRecons = freeart.TxBckProjection(-np.log(sinogram/I0),
                                                           angles)
                        alRecons.setOverSampling(oversampling)
                        alRecons.setRayPointCalculationMethod(methodGBeams)
                        alRecons.setDampingFactor(0.05)
                        alRecons.setRandSeedToZero(True)
                        alRecons.setVoxelSize(voxelSize)
                        alRecons.setI0(I0)
                        reconstructedPhantom = alRecons.iterate(nbIterations)

                        # filtering external voxel for the tests
                        reconstructedPhantom[0, :] = 0
                        reconstructedPhantom[:, 0] = 0
                        reconstructedPhantom[:, self.phDimX-1] = 0
                        reconstructedPhantom[self.phDimY-1, :] = 0

                        initialPhantom[0, :] = 0
                        initialPhantom[:, 0] = 0
                        initialPhantom[:, self.phDimX-1] = 0
                        initialPhantom[self.phDimY-1, :] = 0

                        absoluteTol = 0.2 * (max(crossAbsorption, discAbsorption))

                        _logger.info("test for crossAbsorption = " + str(crossAbsorption) + ", discAbsorption = " + str(discAbsorption))
                        np.testing.assert_allclose(reconstructedPhantom, initialPhantom, rtol=0.1, atol=absoluteTol)


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestTxProjection_2D))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestTxRecontruction_2D))
    return test_suite


if __name__ == '__main__' and __package__ is None:
    unittest.main(defaultTest="suite")
