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
__date__ = "07/08/2017"

import unittest
from freeart import utils
import numpy

import logging
_logger = logging.getLogger("unitests")


class testUtils(unittest.TestCase):
    """
    Test some function of test_utils
    """
    DET_POS = numpy.array((1000, 0, 0))

    def testChangeDetectorPosition(self):
        self.assertTrue(
            numpy.allclose(utils.computeDetectorPosition(self.DET_POS,
                                                         0.0),
                           self.DET_POS))
        self.assertTrue(
            numpy.allclose(utils.computeDetectorPosition(self.DET_POS,
                                                         numpy.pi / 2.0),
                           (0, -1000, 0)))
        self.assertTrue(
            numpy.allclose(utils.computeDetectorPosition(self.DET_POS,
                                                         numpy.pi),
                           (-1000, 0, 0)))


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(testUtils))

    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest="suite")