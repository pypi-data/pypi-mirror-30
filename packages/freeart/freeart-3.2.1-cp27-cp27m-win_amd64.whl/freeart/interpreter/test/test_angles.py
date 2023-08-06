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
__date__ = "01/10/2016"

import os
import tempfile
import unittest
from freeart.interpreter import GlobalConfigInterpreter
import numpy
from freeart.utils import reconstrutils, testutils, genph
import freeart
from freeart.configuration import config, structs, fileInfo
from freeart.configuration.iniConfigIO import IniConfigWriter
from freeart.unitsystem import metricsystem

import numpy as np
import logging
_logger = logging.getLogger("unitests")

class testTxAngle(unittest.TestCase):
    """Test that we are able to generate a valid transmission reconstruction using a cfg file and the interpreter"""
    oversampling = 1
    voxelSize = 5.0*metricsystem.cm
    phantom_width = 56
    dampingFactor = 1.0/float(phantom_width)
    nbAngles = 360

    nbIteration = 1

    def setUp(self):
        
        # deal with files
        self.tempdir = tempfile.mkdtemp()        
        self.cfg_file_min_max = os.path.join(self.tempdir, "tmp_cfg_file_min_max.cfg")    
        self.cfg_file_first_last = os.path.join(self.tempdir, "tmp_cfg_file_first_last.cfg")    
        self.sino_10_30 = os.path.join(self.tempdir, "sino_10_30.edf")    
        self.sino_tx = os.path.join(self.tempdir, "sino_tx.edf")    
        self.phantom_out_tx = os.path.join(self.tempdir, "phantom_out_tx.edf")    

        # create and write a sino file
        phGenerator = genph.PhantomGenerator()
        self.sheppLogan_phantom_tx = phGenerator.get2DPhantomSheppLogan(self.phantom_width)
        # move it to 3D
        self.sheppLogan_phantom_tx.shape = (self.sheppLogan_phantom_tx.shape[0],
                                            self.sheppLogan_phantom_tx.shape[1],
                                            1)

        # build standard sinogram
        al = freeart.TxFwdProjection(self.sheppLogan_phantom_tx,
                                     minAngle=0,
                                     maxAngle=2.0*numpy.pi,
                                     anglesNb=self.nbAngles)
        al.setOverSampling(self.oversampling)
        al.setVoxelSize(self.voxelSize)
        al.setRandSeedToZero(True)
        sinogram = al.makeSinogram()[0]

        sinogram_10_30 = sinogram[:,10:31,]
        assert(sinogram_10_30.shape[1] == 21)

        reconstrutils.saveSinogram(sinogram_10_30, self.sino_10_30)
        reconstrutils.saveSinogram(sinogram, self.sino_tx)
        assert(os.path.isfile(self.sino_10_30))
        assert(os.path.isfile(self.sino_tx))

        # define parameters of reconstruction
        writer = IniConfigWriter()

        conf = config.TxConfig()
        conf.reconsType = "Transmission"
        conf.sinograms = (
            structs.TxSinogram(
                fileInfo=fileInfo.EDFMatrixFileInfo(filePath=self.sino_10_30)),
        )
        conf.oversampling = self.oversampling
        conf.dampingFactor = self.dampingFactor
        conf.includeLastProjection = True
        conf.minAngle = 10.0 * 2.0 * np.pi / 360.0
        conf.maxAngle = 30.0*2.0*np.pi/360.0
        conf.projections = '0:21'
        conf.voxelSize = self.voxelSize
        writer.write(filePath=self.cfg_file_min_max,
                     reconsConfiguration=conf)
        conf.includeLastProjection = False
        conf.minAngle = 0.0
        conf.maxAngle = 2.0*np.pi
        conf.projections = '10:31'
        conf.sinograms = (
            structs.TxSinogram(
                fileInfo=fileInfo.EDFMatrixFileInfo(filePath=self.sino_tx)),
        )
        writer.write(filePath=self.cfg_file_first_last,
                     reconsConfiguration=conf)

        # build the reconstruction of reference
        angles = np.linspace(10.0*2.0*np.pi/360.0, 30.0*2.0*np.pi/360.0, 21)
        checkAngles = np.linspace(0.0, 2.0*np.pi, self.nbAngles)
        checkAngles = checkAngles[:-1]
        assert(len(angles) == 21)
        # assert(np.array_equal(checkAngles[10:30], angles))
        I0 = 1.0
        alRecons = freeart.TxBckProjection(-np.log(sinogram_10_30/I0), angles)
        alRecons.setRandSeedToZero(True)
        alRecons.setOverSampling(self.oversampling)
        alRecons.setVoxelSize(self.voxelSize)
        alRecons.setDampingFactor(self.dampingFactor)
        # make the reconstruction
        self.refReconstruction = alRecons.iterate(self.nbIteration)

    def tearDown(self):
        # clean cfg
        if os.path.isfile(self.cfg_file_min_max):
            os.unlink(self.cfg_file_min_max)

        if os.path.isfile(self.cfg_file_first_last):
            os.unlink(self.cfg_file_first_last)

        # clean edf
        if os.path.isfile(self.sino_10_30):
            os.unlink(self.sino_10_30)

        if os.path.isfile(self.sino_tx):
            os.unlink(self.sino_tx)            

    def testMinAndMaxAngle(self):
        interpreter = GlobalConfigInterpreter(self.cfg_file_min_max)
        interpreter.setRandSeedToZero(True)
        interpreter.iterate(self.nbIteration)
        k0 = list(interpreter.getReconstructionAlgorithms().keys())[0]
        phantom = interpreter.getReconstructionAlgorithms()[k0].getPhantom()
        
        sino = interpreter.interpreter.getSinograms()[0]
        self.assertTrue(len(interpreter.interpreter.angles) == 21)

        self.assertAlmostEqual(interpreter.interpreter.angles[0], 10.0*2.0*np.pi/360.0)
        self.assertAlmostEqual(interpreter.interpreter.angles[-1], 30.0*2.0*np.pi/360.0)

    def testFirstAndLastProjection(self):
        # pass
        interpreter = GlobalConfigInterpreter(self.cfg_file_first_last)
        interpreter.setRandSeedToZero(True)
        interpreter.iterate(self.nbIteration)
        k0 = list(interpreter.getReconstructionAlgorithms().keys())[0]
        phantom = interpreter.getReconstructionAlgorithms()[k0].getPhantom()

        sino = interpreter.interpreter.getSinograms()[0]
        self.assertTrue(len(interpreter.interpreter.angles) == 21)
        self.assertAlmostEqual(interpreter.interpreter.angles[0], 10.0*2.0*np.pi/360.0)
        self.assertAlmostEqual(interpreter.interpreter.angles[-1], 30.0*2.0*np.pi/360.0)


class TestFluoAngle(unittest.TestCase):
    """Test that we are able to generate a valid fluorescence reconstruction using a cfg file and the interpreter"""

    def setUp(self):
        materialSteel = {'Comment':"No comment",
                 'CompoundList':['Cr', 'Fe', 'Ni'],
                 'CompoundFraction':[18.37, 69.28, 12.35],
                 'Density':1.0,
                 'Thickness':1.0}

        materials1 = {"Steel":materialSteel}
        sheppLoganPartID1 = {"Steel":2}
        densities = {"Steel":1.0}
        
        EF = {"Ni":2.0e6}
        self.elements=['Ni']
        E0 = 1.0e7

        matrixWidth = 56
        dampingFactor = float(matrixWidth) / 1.0
        self.experimentation1 = testutils.FluorescenceExperimentationExample(
            self.elements, materials1, sheppLoganPartID1, densities,
            oversampling=20, dampingFactor=dampingFactor, E0=E0, EF=EF, nbAngles=360,
            minAngle=0.0, maxAngle=2.0*np.pi, firstProjection=10, lastProjection=30, 
            includeLastProjection=False, matrixWidth=matrixWidth)
        self.experimentation1.setUp()
        self.experimentation1.voxelSize = 0.2*metricsystem.mm

        self.experimentation2 = testutils.FluorescenceExperimentationExample(
            self.elements, materials1, sheppLoganPartID1, densities,
            oversampling=20, dampingFactor=dampingFactor, E0=E0, EF=EF,
            nbAngles=21, minAngle=10.0*np.pi*2.0/360.0,
            maxAngle=30.0*np.pi*2.0/360.0, firstProjection=0,
            lastProjection=20, includeLastProjection=True)
        self.experimentation2.setUp()
        self.experimentation2.voxelSize = 0.2 * metricsystem.mm

    def testAngle(self):
        exp1 = self.experimentation1
        interpreter1 = GlobalConfigInterpreter(exp1.cfg_fluo_file)
        interpreter1.setRandSeedToZero(True)
        interpreter1.iterate(1)

        exp2 = self.experimentation2
        interpreter2 = GlobalConfigInterpreter(exp2.cfg_fluo_file)
        interpreter2.setRandSeedToZero(True)
        interpreter2.iterate(1)        
        
        algos1 = interpreter1.getReconstructionAlgorithms()
        algos2 = interpreter2.getReconstructionAlgorithms()

        sinoI1 = interpreter1.interpreter.getSinograms()[0]
        sinoI2 = interpreter2.interpreter.getSinograms()[0]
        self.assertTrue(sinoI1.data.shape == sinoI2.data.shape)
        self.assertTrue(sinoI1.data.shape[1] == 20)
        assert('Ni' in algos1 and 'Ni' in algos2)
        numpy.testing.assert_allclose(algos1['Ni'].getPhantom(), algos2['Ni'].getPhantom(), atol=1e-20 )

    def tearDown(self):
        self.experimentation1.tearDown()
        self.experimentation2.tearDown()
        del self.experimentation1
        del self.experimentation2


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(testTxAngle))
    test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(TestFluoAngle))
    
    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest="suite")