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
import numpy
from freeart.unitsystem import metricsystem
from freeart.utils import testutils
import silx
if silx._version.MINOR < 7:
    from silx.test.utils import ParametricTestCase
else:
    from silx.utils.testutils import ParametricTestCase

class SheppLoganReconstructionTest(ParametricTestCase):
    """
    This is the unit test class to run a simple projection on the SheppLogan and then make his reconstruction to make sure we find back the same values
    """
    detectorRadius = 10 * metricsystem.cm

    nbIterations = 3
    oversampling = 4

    def test_SheppLogam(self):
        """
        The main function of the SheppLoganReconstruction unit test
        """
        for precision in (numpy.float32, numpy.float64):
            for voxelSize in (2.0*metricsystem.cm, 0.5*metricsystem.mm):
                with self.subTest(precision=precision, voxelSize=voxelSize):
                    rtol = 0.2 if precision is numpy.float64 else 0.3
                    shepLogan = testutils.SheppLoganReconstruction()
                    detPos = (1000 * metricsystem.cm, 0, 0)
                    detSetup = [(detPos, self.detectorRadius)]
                    sino, angles, absMat, selfAbsMat, initialPhantom = shepLogan.produce_SheppLogan_sinogram(32,
                                                                                                             _oversampling=self.oversampling,
                                                                                                             _anglesNb=360,
                                                                                                             _detSetup=detSetup,
                                                                                                             _voxelSize=voxelSize)
                    reconstructedPhantom = shepLogan.make_reconstruction(_sinogram=sino.astype(precision),
                                                                         _angles=angles,
                                                                         _absMat=absMat.astype(precision),
                                                                         _selfAbsMat=selfAbsMat.astype(precision),
                                                                         _detSetup=detSetup,
                                                                         _nbIter=self.nbIterations,
                                                                         _oversampling=self.oversampling,
                                                                         _dampingFactor=0.2,
                                                                         _voxelSize=voxelSize)

                    numpy.testing.assert_allclose(reconstructedPhantom,
                                                  initialPhantom,
                                                  rtol=rtol,
                                                  atol=1e-3)


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(SheppLoganReconstructionTest))
    return test_suite


if __name__ == '__main__' and __package__ is None:
    unittest.main(defaultTest="suite")
