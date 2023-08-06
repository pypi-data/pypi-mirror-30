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
__date__ = "10/08/2017"


import logging
import os
import shutil
import tempfile
import unittest
import numpy as np
import h5py
import numpy
from freeart.utils import testutils
from freeart.configuration import config, structs, fileInfo
from freeart.interpreter.configinterpreter import FluoConfInterpreter
from freeart.interpreter.test import utils
from freeart.utils import reconstrutils

_logger = logging.getLogger("unitests")


class TestConfig(unittest.TestCase):
    """Test that Config functions are working"""

    def setUp(self):
        self.setValidConfigFiles()
        self.setUnvalidConfigFiles()

        # write valid files
        self.writeValidTx(self.configfile_valid_tx)
        self.writeFluoFileValid(self.configfile_valid_fluo_file)
        self.writeFluoFolderValid(self.configfile_valid_fluo_folder)

        # write unvalid files
        self.writeUnvalidTx(self.configfile_unvalid_1)
        self.writeUnvalidFluo2(self.configfile_unvalid_3)

    def setValidConfigFiles(self):
        self.tempdir = tempfile.mkdtemp()
        self.configfile_valid_fluo_file = os.path.join(self.tempdir,
                                                       "tmp_config_valid_fluo_1.cfg")
        self.configfile_valid_fluo_folder = os.path.join(self.tempdir,
                                                         "tmp_config_valid_fluo_2.cfg")
        self.configfile_valid_tx = os.path.join(self.tempdir,
                                                "tmp_config_valid_tx.cfg")

    def setUnvalidConfigFiles(self):
        self.tempdir = tempfile.mkdtemp()
        self.configfile_unvalid_1 = os.path.join(self.tempdir,
                                                 "tmp_config_unvalid_1.cfg")
        self.configfile_unvalid_3 = os.path.join(self.tempdir,
                                                 "tmp_config_unvalid_3.cfg")

    def tearDown(self):
        self.removeValidConfigFiles()
        self.removeUnvalidConfigFiles()

    def removeUnvalidConfigFiles(self):
        if os.path.isfile(self.configfile_unvalid_1):
            os.unlink(self.configfile_unvalid_1)

    def removeValidConfigFiles(self):
        if os.path.isfile(self.configfile_valid_fluo_file):
            os.unlink(self.configfile_valid_fluo_file)

        if os.path.isfile(self.configfile_valid_fluo_folder):
            os.unlink(self.configfile_valid_fluo_folder)

        if os.path.isfile(self.configfile_valid_tx):
            os.unlink(self.configfile_valid_tx)


class TestDatasetToH5(unittest.TestCase):
    """
    class to test the validity of `setFileInfoToH5File` function in the 
    _ReconsConfig
    """
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

        self.confFluo = testutils.createConfigFluo(self.tempdir,
                                                  fileExtension='.edf',
                                                  withMaterials=True,
                                                  addAbsMat=True,
                                                  fileExtensionMat='.npy',
                                                  addSelfAbsMat=True)
        self.confTx = testutils.createConfigTx(self.tempdir)
        i0 = structs.I0Sinogram(fileInfo=fileInfo.EDFMatrixFileInfo(os.path.join(self.tempdir, 'io.edf')),
                                data=numpy.zeros(100).reshape(10, 10))
        self.confTx.I0 = self.confFluo.I0 = i0
        self.h5File = os.path.join(self.tempdir, 'configFile.h5')

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def testTxNotSaving(self):
        self.confTx.setFileInfoToH5File(refFile=self.h5File, save=False)
        self.assertFalse(os.path.isfile(self.h5File))

    def testTxSaving(self):
        self.confTx.setFileInfoToH5File(refFile=self.h5File, save=True)
        file = h5py.File(self.h5File, mode='r')
        self.assertTrue(structs.TxSinogram.TX_SINOGRAM_DATASET.strip('::') in file)
        self.assertTrue(structs.I0Sinogram.I0_DATASET.strip('::') in file)

    def testFluoSaving(self):
        self.confFluo.setFileInfoToH5File(refFile=self.h5File, save=False)
        self.assertFalse(os.path.isfile(self.h5File))

    def testFluoNotSaving(self):
        self.confFluo.setFileInfoToH5File(refFile=self.h5File, save=True)
        file = h5py.File(self.h5File, mode='r')
        self.assertTrue(structs.I0Sinogram.I0_DATASET.strip('::') in file)
        self.assertTrue(structs.MaterialsDic.MATERIALS_DICT.strip('::') in file)
        self.assertTrue(structs.MatComposition.MAT_COMP_DATASET.strip('::') in file)
        self.assertTrue(structs.AbsMatrix.ABS_MAT_INDEX.strip('::') in file)
        self.assertTrue((structs.FluoSino.SINO_DATASET.strip('::') + '1') in file)
        self.assertTrue((structs.SelfAbsMatrix.MATERIALS_DICT.strip('::') + '1') in file)

class TestFluoCFGFile(unittest.TestCase):
    """
    Test that some cfg file are correctly parsed and interpreted
    """

    MATRIX_DIM = 10

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.configFile = os.path.join(self.tempdir + 'conf.cfg')
        self.absFile = os.path.join(self.tempdir + 'absMatFile.edf')
        self.selfAbsFile = os.path.join(self.tempdir + 'selfAbsMatFile.edf')
        reconstrutils.saveMatrix(
            np.random.rand(self.MATRIX_DIM, self.MATRIX_DIM),
            self.absFile
        )

        reconstrutils.saveMatrix(
            np.random.rand(self.MATRIX_DIM, self.MATRIX_DIM),
            self.selfAbsFile
        )

        utils.writeGeneralSettings(f=self.configFile,
                                   reconsType=config._ReconsConfig.FLUO_ID)
        utils.writeFluoGeneral(f=self.configFile,
                               absFileIsASino=False,
                               absFile=self.absFile,
                               sampComposition=None,
                               materialsFile=None)

        utils.addSinoFile(f=self.configFile,
                          dim=self.MATRIX_DIM,
                          nToAdd=2,
                          physElmts=['H', 'O'],
                          selfAbsPath=self.selfAbsFile,
                          tempdir=self.tempdir)

        utils.addNormalization(f=self.configFile,
                               rotCenter=5,
                               normI0FrmFile=False,
                               i0=1.0,
                               computeMinusLog=True)

        utils.addReconsProperties(f=self.configFile,
                                  voxelSize=1.0,
                                  oversampling=2,
                                  relaxationFactor=0.23)

        utils.addReductionData(f=self.configFile)
        utils.addProjInfo(f=self.configFile,
                          startProj=0,
                          endProj=self.MATRIX_DIM-1)
        utils.addDetectorInfo(f=self.configFile,
                              detWidth=10,
                              detX=10.0,
                              detY=0.0,
                              detZ=0.0)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def testFluo(self):
        interpreter = FluoConfInterpreter(self.configFile)


def suite():
    test_suite = unittest.TestSuite()
    for ui in (TestConfig, TestFluoCFGFile):
        test_suite.addTest(
            unittest.defaultTestLoader.loadTestsFromTestCase(ui))

    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest="suite")
