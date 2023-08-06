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
__date__ = "24/09/2017"

import unittest
from ..sinogramselection import getSelection, getAngles, selectionIsValid
import numpy

import logging
_logger = logging.getLogger("unitests")


class testSinogramSelection(unittest.TestCase):
    """
    Test some function of test_utils
    """
    def testSelectionIsValid(self):
        """Make sure the selectionIsValid function is working"""
        self.assertTrue(selectionIsValid("3"))
        self.assertTrue(selectionIsValid("3; 7"))
        self.assertTrue(selectionIsValid("23:56"))
        self.assertTrue(selectionIsValid(":3"))
        self.assertTrue(selectionIsValid("2:3; 5:89"))
        self.assertTrue(selectionIsValid("1:3;:6"))
        self.assertTrue(selectionIsValid("1:3;"))

    def testSelection(self):
        p = numpy.arange(10)
        self.assertTrue(
            numpy.array_equal(getSelection(projections=p, selection='2; 4; 5'),
                              numpy.append(numpy.append(p[2], p[4]), p[5]))
        )

        self.assertTrue(
            numpy.array_equal(getSelection(projections=p, selection='1:3'),
                              p[1:3])
        )
        self.assertTrue(
            numpy.array_equal(getSelection(projections=p, selection='3:6; 7:9'),
                              numpy.append(p[3:6], p[7:9]))
        )

        with self.assertRaises(Exception):
            getSelection(projections=None, selection='0')

        with self.assertRaises(Exception):
            getSelection(projections=p, selection='20')

    def testGetAngles(self):
        minAngle = 0
        maxAngle = numpy.pi
        nbAngles = 20

        self.assertTrue(
            numpy.array_equal(getAngles(minAngle=minAngle,
                                        maxAngle=maxAngle,
                                        nbAngles=nbAngles,
                                        selection='',
                                        lastAngleEqualFirst=True,
                                        acquiInverted=False),
                              numpy.linspace(minAngle, maxAngle, nbAngles)
                              )
        )

        self.assertTrue(
            numpy.array_equal(getAngles(minAngle=minAngle,
                                        maxAngle=maxAngle,
                                        nbAngles=nbAngles,
                                        selection='',
                                        lastAngleEqualFirst=False,
                                        acquiInverted=False),
                              numpy.linspace(minAngle, maxAngle, nbAngles+1)[:-1]
                              )
        )

        self.assertTrue(
            numpy.array_equal(getAngles(minAngle=minAngle,
                                        maxAngle=maxAngle,
                                        nbAngles=nbAngles,
                                        selection='0:10',
                                        lastAngleEqualFirst=True,
                                        acquiInverted=False),
                              numpy.linspace(minAngle, maxAngle, nbAngles)[0:10]
                              )
        )


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(testSinogramSelection))

    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest="suite")
