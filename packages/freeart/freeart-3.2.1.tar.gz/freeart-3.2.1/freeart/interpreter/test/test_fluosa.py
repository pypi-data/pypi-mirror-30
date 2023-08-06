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
__date__ = "20/10/2016"

import unittest
import numpy

import freeart
from freeart.unitsystem import metricsystem
from freeart.utils import genph

import logging
_logger = logging.getLogger("unitests")

class testTxVsFluo(unittest.TestCase):
    """A simple unit tests to  make sure that if the interaction probability and the self absorption is null 
    then we found back the same stuff for compton and transmission"""

    detectorAngles = [0.0, 60*numpy.pi/180.0, numpy.pi, -numpy.pi/2.0, 1.3*numpy.pi]
    detectorRadius = 1.0
    nbAngles = 20

    def setUp(self):
        phGenerator = genph.PhantomGenerator()
        self.sheppLogan_phantom = phGenerator.get2DPhantomSheppLogan(56)
        self.sheppLogan_phantom.shape = (self.sheppLogan_phantom.shape[0], self.sheppLogan_phantom.shape[1], 1)

        self.probaInteraction = self.sheppLogan_phantom.copy()
        self.probaInteraction[self.probaInteraction!=0.0] = 1.0
        self.selfAbsMat = numpy.zeros(self.sheppLogan_phantom.shape)

    def phantomFluoSinogram(self, withSA, detSetup):
        # define reconstruction parameters
        al = freeart.FluoFwdProjection(
            phMatr           = self.probaInteraction, 
            expSetUp         = detSetup,
            absorpMatr       = self.sheppLogan_phantom,
            selfAbsorpMatrix = self.selfAbsMat,
            angleList        = None, 
            minAngle         = 0, 
            maxAngle         = numpy.pi, 
            anglesNb         = self.nbAngles )

        al.setOverSampling(2)
        al.turnOffSolidAngle(withSA)
        # create the sinogram
        sino, angles = al.makeSinogram()  
        return sino

    def testPhantomReconstruction_withoutSA(self):
        """
        Test that all generated sinogram with a null self absorption is equal no matter the detector position
        """
        sinograms = {}
        for detAngle in self.detectorAngles:
            detPos = (numpy.sin(detAngle)*1000.0, numpy.cos(detAngle)*1000.0, 0.0)
            detSetup = [(detPos, self.detectorRadius)]

            sinograms[detAngle]=self.phantomFluoSinogram(True, detSetup)

        ref = sinograms[0.0]
        for detAngle in self.detectorAngles:
            numpy.testing.assert_allclose(ref, sinograms[detAngle])

    def testPhantomReconstruction_withSA(self):
        """
        Test that all generated sinogram with a null self absorption is equal no matter the detector position
        """
        sinograms = {}
        for detAngle in self.detectorAngles:
            detPos = (numpy.sin(detAngle)*10e5, numpy.cos(detAngle)*10e5, 0.0)
            detSetup = [(detPos, self.detectorRadius)]

            sinograms[detAngle]=self.phantomFluoSinogram(False, detSetup)

        ref = sinograms[0.0]
        for detAngle in self.detectorAngles:
            numpy.testing.assert_allclose(ref, sinograms[detAngle], rtol=5e-4)


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(testTxVsFluo))
    return test_suite

if __name__ == '__main__' and __package__ is None :
    unittest.main(defaultTest="suite")