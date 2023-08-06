# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2015-2016 European Synchrotron Radiation Facility
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
"""
"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "07/08/2017"


import unittest
from .test_angles import suite as test_angle_suite
from .test_config import suite as test_config_suite
from .test_configinterpreter import suite as test_configinterpreter_suite
from .test_fluooutgoingray import suite as test_fluooutgoingray_suite
from .test_fluoprojector import suite as test_fluoprojector_suite
from .test_fluoreconstruction import suite as test_fluoreconstruction_suite
from .test_fluosa import suite as test_fluosa_suite
from .test_rayparameters import suite as test_rayparameters_suite
from .test_tx import suite as test_tx_suite


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTests(
        [test_angle_suite(),
         test_config_suite(),
         test_configinterpreter_suite(),
         test_fluooutgoingray_suite(),
         test_fluoprojector_suite(),
         test_fluoreconstruction_suite(),
         test_fluosa_suite(),
         test_rayparameters_suite(),
         test_tx_suite()])
    return test_suite