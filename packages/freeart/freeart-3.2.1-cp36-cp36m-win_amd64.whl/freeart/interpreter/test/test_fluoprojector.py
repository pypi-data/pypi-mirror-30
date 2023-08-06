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
import numpy
import silx
if silx._version.MINOR < 7:
    from silx.test.utils import ParametricTestCase
else:
    from silx.utils.testutils import ParametricTestCase
from freeart.unitsystem import metricsystem
from freeart.utils import testutils, reconstrutils, raypointsmethod, outgoingrayalgorithm
import logging

_logger = logging.getLogger("unitests")


class TestFluoIncomingBeam_2D(ParametricTestCase):
    """
    Here we want to test the incoming beam attenuation in a stacks of voxels.
    """
    origin = (0.0, 0.0)
    detectorRadius = 10.0*metricsystem.cm
    detectorArea = detectorRadius * 2.0
    detectorWidth = detectorRadius*2.0
    detectorDistance = 1000*metricsystem.cm

    oversampling = 40
    phDimX = 31
    phDimY = 31
    phDimZ = 1

    xpos = 15
    ypos = 15
    zpos = 0

    interactionProba = 1.0
    outgoingAbsorptionFactor = 0.0  # g.cm2

    voxelPosInPhantomRef = (xpos, ypos, zpos)
    voxelPosInExpRef = testutils.toExperimentationRef(voxelPosInPhantomRef,
                                                      phDimX,
                                                      phDimY,
                                                      phDimZ)

    def testProjectorIncomingBeamAbsorption(self):
        """
        We have n lines of material with a particular attenuation (incoming
        beam attenuation).
        The outgoing beam will not be attenuated>
        Then for different incoming beam angle we will compare the values
        returned by FreeART and given by the theory.
        """
        
        widthsToTest = [5]  # in voxels
        incomingAbsorptionToTest = [1e-4, 2.0]  # in g/cm2

        methodGBeams = raypointsmethod.withInterpolation
        optionOutgoing = outgoingrayalgorithm.rawApproximation


        detAngle = 0
        detPos = (numpy.sin(detAngle)*self.detectorDistance,
                  numpy.cos(detAngle)*self.detectorDistance,
                  self.zpos)
        detSetup = [(detPos, self.detectorRadius)]

        for precision in (numpy.float32, numpy.float64):
            for incomingAbsorptionFactor in incomingAbsorptionToTest:
                for width in widthsToTest:
                    for voxelSize in [0.2*metricsystem.cm, 0.3*metricsystem.mm]:
                        with self.subTest(incomingAbsorptionFactor=incomingAbsorptionFactor,
                                          width=width, voxelSize=voxelSize,):

                            phantom = numpy.zeros((self.phDimX, self.phDimY, self.phDimZ),
                                                  dtype=precision)
                            absMat = numpy.zeros((self.phDimX, self.phDimY, self.phDimZ),
                                                 dtype=precision)
                            selfAbsMat = numpy.zeros((self.phDimX, self.phDimY, self.phDimZ),
                                                     dtype=precision)

                            for delta in numpy.arange(0, width, 1) :
                                phantom[self.ypos+delta, :, self.zpos] = self.interactionProba
                                absMat[self.ypos+delta, :, self.zpos] = incomingAbsorptionFactor
                            sinogram, angles = reconstrutils.makeFreeARTFluoSinogram(phantom,
                                                                                     absMat,
                                                                                     selfAbsMat,
                                                                                     360/15 +1,
                                                                                     detSetup,
                                                                                     self.oversampling,
                                                                                     methodGBeams,
                                                                                     optionOutgoing,
                                                                                     voxelSize=voxelSize)
                            I_FreeARTValue_0 = sinogram[0][0][self.xpos]
                            I_FreeARTValue_30 = sinogram[0][2][self.xpos]
                            I_FreeARTValue_45 = sinogram[0][3][self.xpos]
                            I_FreeARTValue_60 = sinogram[0][4][self.xpos]
                            I_FreeARTValue_180 = sinogram[0][12][self.xpos]

                            I_theoreticalValue_0 = testutils.getFluoTheoreticalValue(
                                detPos,
                                self.detectorRadius,
                                self.voxelPosInExpRef,           # < voxel position in the freeART reference
                                incomingAbsorptionFactor,        # < mass attenuation for the incoming beam
                                self.outgoingAbsorptionFactor,   # < mass attenuation for the outgoing beam
                                numpy.pi/2.0,                    # < angle of entry of the incoming beam
                                numpy.pi/2.0 - detAngle,         # < outgoing beam angle to the sample
                                1.0,                             # < tau
                                width*voxelSize                  # < When sampling value is 1, then we will get the attenuation on the whole voxel.
                                )

                            I_theoreticalValue_30 = testutils.getFluoTheoreticalValue(
                                detPos,
                                self.detectorRadius,
                                self.voxelPosInExpRef,            # < voxel position in the freeART reference
                                incomingAbsorptionFactor,         # < mass attenuation for the incoming beam
                                self.outgoingAbsorptionFactor,    # < mass attenuation for the outgoing beam
                                numpy.pi/2.0 - 30.0*numpy.pi/180, # < angle of entry of the incoming beam
                                numpy.pi/2.0 - detAngle,          # < outgoing beam angle to the sample
                                1.0,
                                width*voxelSize
                                )

                            I_theoreticalValue_45 = testutils.getFluoTheoreticalValue(
                                detPos,
                                self.detectorRadius,
                                self.voxelPosInExpRef,               # < voxel position in the freeART reference
                                incomingAbsorptionFactor,            # < mass attenuation for the incoming beam
                                self.outgoingAbsorptionFactor,       # < mass attenuation for the outgoing beam
                                numpy.pi/2.0 - 45.0*numpy.pi/180.0,  # < angle of entry of the incoming beam
                                numpy.pi/2.0 - detAngle,             # < outgoing beam angle to the sample
                                1.0,
                                width*voxelSize
                                )

                            I_theoreticalValue_60 = testutils.getFluoTheoreticalValue(
                                detPos,
                                self.detectorRadius,
                                self.voxelPosInExpRef,              # < voxel position in the freeART reference
                                incomingAbsorptionFactor,           # < mass attenuation for the incoming beam
                                self.outgoingAbsorptionFactor,      # < mass attenuation for the outgoing beam
                                numpy.pi/2.0 - 60.0*numpy.pi/180.0, # < angle of entry of the incoming beam
                                numpy.pi/2.0 - detAngle,            # < outgoing beam angle to the sample
                                1.0,
                                width*voxelSize
                                )

                            I_theoreticalValue_180 = testutils.getFluoTheoreticalValueForTransmission(
                                detPos,
                                self.detectorRadius,
                                self.voxelPosInExpRef,          # < voxel position in the freeART reference
                                incomingAbsorptionFactor,       # < mass attenuation for the incoming beam
                                self.outgoingAbsorptionFactor,  # < mass attenuation for the outgoing beam
                                numpy.pi/2.0,                   # < angle of entry of the incoming beam
                                numpy.pi/2.0 - detAngle,        # < outgoing beam angle to the sample
                                1.0,
                                width*voxelSize
                                )

                        self.assertAlmostEqual(I_theoreticalValue_0, I_FreeARTValue_0, 5)
                        self.assertAlmostEqual(I_theoreticalValue_30, I_FreeARTValue_30, 5)
                        self.assertAlmostEqual(I_theoreticalValue_45, I_FreeARTValue_45, 5)
                        self.assertAlmostEqual(I_theoreticalValue_60, I_FreeARTValue_60, 5)
                        self.assertAlmostEqual(I_theoreticalValue_180, I_FreeARTValue_180, 5)


class TestFluoOutgoingBeam_2D(ParametricTestCase):
    """the unit test related to the fluorescence projector, focus
    on the incoming beam attenuations.
    """
    # detector properties
    detectorRadius = 10.0*metricsystem.cm
    detectorArea = detectorRadius * 2.0
    detectorWidth = detectorRadius * 2.0
    detectorDistance = 1000*metricsystem.cm
    # Dimensions of the phantom to test
    phDimX = 21
    phDimY = 21
    phDimZ = 1

    xpos = 10
    ypos = 10
    zpos = 0

    origin = (0.0, 0.0)
    voxelPosInPhantomRef = (xpos, ypos, zpos)
    voxelPosInExpRef = testutils.toExperimentationRef(voxelPosInPhantomRef,
                                                      phDimX,
                                                      phDimY,
                                                      phDimZ)

    # we are setting an hight value to get close from the theoretical values
    # we need a large number of ray especially for the case where we are not
    # using the interpolation process.
    oversampling = 40
    # For this test case we are skipping the attenuation of the incoming beam
    # and only focusing on the outgoing
    interactionProba = 1.0
    incomingAbsorptionFactor = 0.0

    def test_outgoing_beam_absorption_width_voxels_y(self):
        """Test the attenuation for the outgoing beam hitting n lines of
        material.
        Material attenuation of the incoming beam is zero.
        Material attenuation of the outgoing beam is outgoingAbsorptionFactor
        To make sure results are ok we are testing different detector position,
        which are directly defining the angle of the outgoing beam.
        """
        width = 8
        optionOutgoing = outgoingrayalgorithm.createOneRayPerSamplePoint

        for precision in (numpy.float32, numpy.float64):
            for methodGBeams in [raypointsmethod.withInterpolation, raypointsmethod.withoutInterpolation]:
                for outgoingAbsorptionFactor in (1.e-5, 2.0):
                    for detAngle in (0, 60*numpy.pi/180):
                        detPos = (numpy.sin(detAngle) * self.detectorDistance,
                                  numpy.cos(detAngle) * self.detectorDistance,
                                  self.zpos)
                        detSetup = [(detPos, self.detectorRadius)]

                        for voxelSize in (0.2 * metricsystem.cm, 0.3 * metricsystem.nm):

                            with self.subTest(precision=precision, calculationBMethod=methodGBeams,
                                              outgoingAbsorptionFactor=outgoingAbsorptionFactor,
                                              voxelSize=voxelSize):

                                ### RUN the FREE ART EXPERIMENTATION
                                # create the simple phantom
                                phantom = numpy.zeros((self.phDimX, self.phDimY, self.phDimZ),
                                                      dtype=precision)
                                absMat = numpy.zeros((self.phDimX, self.phDimY, self.phDimZ),
                                                     dtype=precision)
                                selfAbsMat = numpy.zeros((self.phDimX, self.phDimY, self.phDimZ),
                                                         dtype=precision)

                                for delta in numpy.arange(0, width, 1):
                                    phantom[self.ypos+delta, :, self.zpos] = self.interactionProba
                                    selfAbsMat[self.ypos+delta, :, self.zpos] = outgoingAbsorptionFactor

                                sinogram, angles = reconstrutils.makeFreeARTFluoSinogram(phantom=phantom,
                                                                                         absMat=absMat,
                                                                                         selfAbsMat=selfAbsMat,
                                                                                         numAngle=2,
                                                                                         detSetup=detSetup,
                                                                                         oversampling=self.oversampling,
                                                                                         beamCalcMeth=methodGBeams,
                                                                                         outRayPtCalcMeth=optionOutgoing,
                                                                                         voxelSize=voxelSize)

                                # The momentum when we are going trought the n voxel ( n == width )
                                I_FreeARTValue_NVoxels = sinogram[0][0][self.xpos]

                                # GET THE THEORETICAL VALUES
                                I_theoreticalValue_NVoxels = testutils.getFluoTheoreticalValue(
                                    detPos,
                                    self.detectorRadius,
                                    self.voxelPosInExpRef,           # < voxel position in the freeART reference
                                    self.incomingAbsorptionFactor,   # < mass attenuation for the incoming beam
                                    outgoingAbsorptionFactor,        # < mass attenuation for the outgoing beam
                                    numpy.pi/2.0,                    # < angle of entry of the incoming beam
                                    numpy.pi/2.0 - detAngle,         # < outgoing beam angle to the sample
                                    1.0,                             # < tau
                                    width*voxelSize                  # < material width
                                    )
                                places = 6 if precision is numpy.float64 else 3
                                self.assertAlmostEqual(I_theoreticalValue_NVoxels,
                                                       I_FreeARTValue_NVoxels,
                                                       places)


class TestFluoComplexCases(ParametricTestCase):
    """the unit test related to the compton projector and debug"""

    # Dimensions of the phantom to test
    phDimX = 41
    phDimY = 41
    phDimZ = 1

    origin = (0.0, 0.0)

    xpos = 20
    ypos = 20
    zpos = 0

    voxelPosInPhantomRef = (xpos, ypos, zpos)
    voxelPosInExpRef = testutils.toExperimentationRef(voxelPosInPhantomRef,
                                                      phDimX,
                                                      phDimY,
                                                      phDimZ)

    # detector properties
    detectorRadius = 10.0*metricsystem.cm
    detectorArea = detectorRadius * 2.0
    detectorWidth = detectorRadius * 2.0

    # we are setting an hight value to get close from the theoretical values
    oversampling = 20
    # For this test case we are skipping the attenuation of the incoming beam and only focusing on the outgoing
    interactionProba = 1.0
    incomingAbsorptionFactor = 0.0
    # The width of the stack to test to make sure the attenuation is well propagated
    width = 5  # nb voxel.
    # The outgoing beam attenuation to consider for this test case
    outgoingAbsorptionFactor = 1.0
    detectorDistance = 1000

    def test_outgoing_beam_absorption_width_voxels_y(self):
        """
        This is the cqse where the incoming ray is hitting a voxel with only an
        interaction probability to 1. At the time the beam haven t been
        attenuated by any material.
        Then the outgoing beam is generated (at xpos, ypos) and going to the
        detector.
        On this path the ray will cross an area with an attenuation of
        outgoingAbsorptionFactor. Throught a distance of
        sqrt(width*width + width*width).
        This test is only verifying that this attenuation for this cqse is well
        taking into account.
        """
        detAngle = numpy.pi / 4.0  # 45 degree detector
        # we are in the trigonometric reference
        detPos = (numpy.sin(detAngle)*self.detectorDistance,
                  numpy.cos(detAngle)*self.detectorDistance,
                  self.zpos)
        detSetup = [(detPos, self.detectorRadius)]

        # RUN the FREE ART EXPERIMENTATION
        # create the simple phantom
        phantom = numpy.zeros((self.phDimX, self.phDimY, self.phDimZ),
                              dtype=numpy.float64)
        absMat = numpy.zeros((self.phDimX, self.phDimY, self.phDimZ),
                             dtype=numpy.float64)
        selfAbsMat = numpy.zeros((self.phDimX, self.phDimY, self.phDimZ),
                                 dtype=numpy.float64)

        phantom[self.ypos, self.xpos, self.zpos] = self.interactionProba

        for delta in numpy.arange(0, self.width, 1):
            selfAbsMat[self.ypos + delta + 2, self.xpos+1:, self.zpos] = self.outgoingAbsorptionFactor

        # Define the option to compute the attenatuion of rays
        methodGBeams = raypointsmethod.withInterpolation
        optionOutgoing = outgoingrayalgorithm.createOneRayPerSamplePoint

        sinogram, angles = reconstrutils.makeFreeARTFluoSinogram(
            phantom, absMat, selfAbsMat, 5, detSetup, self.oversampling, methodGBeams, optionOutgoing)

        # The momentum when we are going trought the n voxel ( n == width )
        I_FreeARTValue_NVoxels = sinogram[0][0][self.xpos]

        # width : because we are in the 45 degree case
        distInMaterialForTheOutgoingBeam = numpy.sqrt(self.width*self.width*2)
        I_theoreticalValue_NVoxels = numpy.exp(-distInMaterialForTheOutgoingBeam*self.outgoingAbsorptionFactor)*testutils.getSolidAngle(self.voxelPosInExpRef, detPos, self.detectorRadius)

        self.assertAlmostEqual(I_theoreticalValue_NVoxels, I_FreeARTValue_NVoxels, 5)


class TestFluoIncomingAndOutgoingBeam(ParametricTestCase):
    """
    the unit test related to the compton projector and constructor
    """

    # detector properties
    detectorRadius = 10.0*metricsystem.cm
    detectorArea = detectorRadius * 2.0
    detectorWidth = detectorRadius * 2.0
    detectorDistance = 1000*metricsystem.cm
    # Dimensions of the phantom to test
    phDimX = 31  # voxel
    phDimY = 31  # voxel
    phDimZ = 1  # voxel

    xpos = 15  # voxel
    ypos = 15  # voxel
    zpos = 0   # voxel

    origin = (0.0, 0.0, 0.0)

    voxelPosInPhantomRef = (xpos, ypos, zpos)
    voxelPosInExpRef = testutils.toExperimentationRef(voxelPosInPhantomRef, phDimX, phDimY, phDimZ)

    # we are setting an hight value to get close from the theoretical values
    oversampling = 20
    interactionProba = 1.0

    def test_absorption_in_a_stack(self):
        """
        Test the attenuation for the outgoing beam.
        with have n lines of material (n == width ) where we are testing over
        different absorption.
        for the incoming beam and for the outgoing beam.
        Then we compare result given by freeART and by the theory
        """
        width = 6

        methodGBeams = raypointsmethod.withInterpolation
        optionOutgoing = outgoingrayalgorithm.createOneRayPerSamplePoint

        for precision in (numpy.float32, numpy.float64):
            for inAbsorbFact in (1.e-5, 2.0):
                for outAbsorbFact in (1.e-5, 2.0):
                    for detAngle in (0, 30.0*numpy.pi/180.0):
                        # we are in the trigonometric reference
                        detPos = (numpy.sin(detAngle)*self.detectorDistance,
                                  numpy.cos(detAngle)*self.detectorDistance,
                                  self.zpos)
                        detSetup = [(detPos, self.detectorRadius)]

                        for voxelSize in [1.0*metricsystem.mm, 1.0*metricsystem.cm]:
                            with self.subTest(precision=precision, incoAbsMat=inAbsorbFact,
                                              outAbsorbFact=outAbsorbFact, detAngle=detAngle,
                                              voxelSize=voxelSize):
                                # create the simple phantom
                                phantom = numpy.zeros((self.phDimX, self.phDimY, self.phDimZ),
                                                      dtype=precision)
                                absMat = numpy.zeros((self.phDimX, self.phDimY, self.phDimZ),
                                                     dtype=precision)
                                selfAbsMat = numpy.zeros((self.phDimX, self.phDimY, self.phDimZ),
                                                         dtype=precision)

                                # dans ce cas dans le repere de freeART les lignes se trouve en (:, -5:-7)
                                for delta in numpy.arange(0, width, 1):
                                    phantom[self.ypos+delta, :, self.zpos] = self.interactionProba
                                    selfAbsMat[self.ypos+delta, :, self.zpos] = outAbsorbFact
                                    absMat[self.ypos+delta, :, self.zpos] = inAbsorbFact

                                sinogram, angles = reconstrutils.makeFreeARTFluoSinogram(phantom=phantom,
                                                                                         absMat=absMat,
                                                                                         selfAbsMat=selfAbsMat,
                                                                                         numAngle=5,
                                                                                         detSetup=detSetup,
                                                                                         oversampling=self.oversampling,
                                                                                         beamCalcMeth=methodGBeams,
                                                                                         outRayPtCalcMeth=optionOutgoing,
                                                                                         voxelSize=voxelSize)

                                # The momentum when we are going trought the n voxel ( n == width )
                                I_FreeARTValue_NVoxels = sinogram[0][0][self.xpos]

                                ### GET THE THEORETICAL VALUES
                                I_theoreticalValue_NVoxels = testutils.getFluoTheoreticalValue(
                                    detPos=detPos,
                                    detectorRadius=self.detectorRadius,
                                    voxelPosInFreeARTRef=self.voxelPosInExpRef,
                                    mu_E0=inAbsorbFact,
                                    mu_EF=outAbsorbFact,
                                    psiIncoming=numpy.pi/2.0,
                                    psiOutgoing=numpy.pi/2.0 - detAngle,
                                    tau_E0=1.0,
                                    distInMat=width*voxelSize
                                )
                                places = 3 if precision is numpy.float32 else 5
                                self.assertAlmostEqual(I_theoreticalValue_NVoxels, I_FreeARTValue_NVoxels, places)


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestFluoIncomingBeam_2D))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestFluoOutgoingBeam_2D))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestFluoComplexCases))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestFluoIncomingAndOutgoingBeam))
    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest="suite")
