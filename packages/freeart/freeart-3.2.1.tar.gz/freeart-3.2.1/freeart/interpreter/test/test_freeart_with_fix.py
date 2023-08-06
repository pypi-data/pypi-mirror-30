# # coding: utf-8
# # /*##########################################################################
# #
# # Copyright (c) 2016 European Synchrotron Radiation Facility
# #
# # Permission is hereby granted, free of charge, to any person obtaining a copy
# # of this software and associated documentation files (the "Software"), to deal
# # in the Software without restriction, including without limitation the rights
# # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# # copies of the Software, and to permit persons to whom the Software is
# # furnished to do so, subject to the following conditions:
# #
# # The above copyright notice and this permission notice shall be included in
# # all copies or substantial portions of the Software.
# #
# # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# # THE SOFTWARE.
# #
# # ###########################################################################*/
# __authors__ = ["H. Payno"]
# __license__ = "MIT"
# __date__ = "01/09/2016"

# import unittest
# import os
# import tempfile
# import sys
# if sys.version < '3.0':
#     import ConfigParser as configparser
# else:
#     import configparser

# from freeart.interpreter import GlobalConfigInterpreter
# import numpy
# from freeart.utils import reconstrutils, testutils, physicalelmts, genph, raypointsmethod, outgoingrayalgorithm
# import freeart
# from freeart.interpreter.config import Config
# from freeart.unitsystem import metricsystem

# from fisx import Material

# import numpy as np
# import logging
# _logger = logging.getLogger("unitests")

# class testConfigInterpreterFluo(unittest.TestCase):
#     """Test that we are able to generate a valid fluorescence reconstruction using a cfg file and the interpreter"""

#     def setUp(self):
#         materialSteel = {'Comment':"No comment",
#                  'CompoundList':['Cr', 'Fe', 'Ni'],
#                  'CompoundFraction':[18.37, 69.28, 12.35],
#                  'Density':1.0,
#                  'Thickness':1.0}

#         materialTeflon = {'Comment':"No comment",
#                  'CompoundList':['C1', 'F1'],
#                  'CompoundFraction':[0.240183, 0.759817],
#                  'Density':1.0,
#                  'Thickness':1.0}

#         materials = {"Steel":materialSteel, "Teflon":materialTeflon}
#         sheppLoganPartID = {"Steel":3, "Teflon":2}
#         densities = {"Steel":0.5, "Teflon":0.2}
#         EF2 = {"Steel":1.5e5, "Teflon":2.4e4}

#         self.experimentationTwoMat = testutils.FluorescenceExperimentationExWithFisx(materials, densities, 
#             oversampling=20, dampingFactor=0.02, E0=1.0e6, EF=EF2, nbAngles=400, sinoElmts=['Cl', 'Fe', 'Ni'])
#         self.experimentationTwoMat.setUp()
#         self.experimentationTwoMat.voxelSize = 3.0*metricsystem.cm

#     def testWithFisx(self):
#         exp = self.experimentationTwoMat
#         interpreter = GlobalConfigInterpreter(exp.cfg_fluo_file)
#         # for unit tests, reset the random generator
#         interpreter.setRandSeedToZero(True)
#         interpreter.iterate(3)

#         algos = interpreter.getReconstructionAlgorithms()
#         # check parameters from the first algorithm
#         for material in algos :
#             reconstructed_phantom = algos[material].getPhantom()
#             assert(material in exp.phantoms)
#             numpy.testing.assert_allclose(reconstructed_phantom, exp.phantoms[material], rtol=0.3, atol=5e-2)  

#     def tearDown(self):
#         self.experimentationSteel.tearDown()
#         self.experimentationTwoMat.tearDown()
#         del self.experimentationSteel
#         del self.experimentationTwoMat


# def suite():
#     test_suite = unittest.TestSuite()
#     test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(testWithFisx))
    
#     return test_suite

# if __name__ == '__main__':
#     unittest.main(defaultTest="suite")        