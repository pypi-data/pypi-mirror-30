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
from unittest.util import safe_repr

class testPercentage(unittest.TestCase): 
    """A class to make test from percentage of error between elemets.
    Will redefine some assert from unittest.TestCase"""

    def __init__(self, methodName='runTest'):
        """Create an instance of the class that will use the named test
           method when executed. Raises a ValueError if the instance does
           not have a method with the specified name.
        """
        self._testMethodName = methodName
        self._outcome = None
        self._testMethodDoc = 'No test'
        try:
            testMethod = getattr(self, methodName)
        except AttributeError:
            if methodName != 'runTest':
                # we allow instantiation with no explicit method name
                # but not an *incorrect* or missing method name
                raise ValueError("no such test method in %s: %s" %
                      (self.__class__, methodName))
        else:
            self._testMethodDoc = testMethod.__doc__
        self._cleanups = []
        self._subtest = None

    def getError(self, first, second) :
        meanVal = (first + second) /2.0
        return (abs(first - second) / meanVal) * 100.0

    def assertErrorPercentageAlmostEqual(self, first, second, acceptableErrorPercentage) :
        """Fail if the percentage of the difference between first and second is higher than acceptableErrorPercentage"""
        if(first == second) :
            # shortcut
            return

        error = self.getError(first, second)

        if(error > acceptableErrorPercentage ) :
            msg = '%s differ from %s with more than %s %% : %s %%' % (safe_repr(first),
                                                          safe_repr(second),
                                                          acceptableErrorPercentage,
                                                          error)
            raise self.failureException(msg)
        else :
            return