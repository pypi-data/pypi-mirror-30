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
"""Test two steps.
The first one is the interpretation of a cfg file.
The second one is the reconstruction using the freeart core (ART algorithm)
and the python layer dealing with interaction probability and sample materials.
"""


__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "01/09/2016"

import logging
import os
import tempfile
import unittest
import shutil
import numpy
import numpy as np
import freeart
from freeart.configuration.iniConfigIO import IniConfigWriter
from freeart.configuration import config, structs, fileInfo
from freeart.interpreter import GlobalConfigInterpreter
from freeart.unitsystem import metricsystem
from freeart.utils import reconstrutils, testutils, genph
import silx
if silx._version.MINOR < 7:
    from silx.test.utils import ParametricTestCase
else:
    from silx.utils.testutils import ParametricTestCase
import copy

_logger = logging.getLogger("unitests")


class TestConfigInterpreterTx(unittest.TestCase):
    """
    Test that we are able to generate a valid transmission reconstruction using
    a cfg file and the interpreter
    """
    oversampling = 6
    dampingFactor = 0.04
    voxelSize = 2.5*metricsystem.cm
    phantom_width = 56
    nbAngles = 360

    def setUp(self):
        # deal with files
        self.tempdir = tempfile.mkdtemp()
        self.cfg_file_tx = os.path.join(self.tempdir, "tmp_cfg_file_tx.cfg")
        self.cfg_file_tx_2 = os.path.join(self.tempdir, "tmp_cfg_file_tx_2.cfg")
        self.sino_tx = os.path.join(self.tempdir, "sino_tx.edf")
        self.phantom_out_tx = os.path.join(self.tempdir, "phantom_out_tx.edf")

        # create and write a sino file
        phGenerator = genph.PhantomGenerator()
        self.sheppLogan_phantom_tx = phGenerator.get2DPhantomSheppLogan(self.phantom_width)
        # move it to 3D
        self.sheppLogan_phantom_tx.shape = (self.sheppLogan_phantom_tx.shape[0],
                                            self.sheppLogan_phantom_tx.shape[1],
                                            1)

        al = freeart.TxFwdProjection(self.sheppLogan_phantom_tx,
                                     minAngle=0,
                                     maxAngle=2.0*numpy.pi,
                                     anglesNb=self.nbAngles)
        al.setOverSampling(self.oversampling)
        al.setVoxelSize(self.voxelSize)
        al.setRandSeedToZero(True)
        sinogram = al.makeSinogram()[0]

        reconstrutils.saveSinogram(sinogram, self.sino_tx)
        assert(os.path.isfile(self.sino_tx))

        writer = IniConfigWriter()
        # define parameters of reconstruction
        conf = config.TxConfig()
        conf.reconsType = "Transmission"
        conf.sinograms = (
            structs.TxSinogram(
                fileInfo=fileInfo.EDFMatrixFileInfo(self.sino_tx)),
        )
        conf.voxelSize = self.voxelSize
        conf.oversampling = self.oversampling
        conf.dampingFactor = self.dampingFactor
        conf.minAngle = 0.0
        conf.maxAngle = 2.0*np.pi
        conf.projections = str(0) + ":" + str(self.nbAngles-1)
        writer.write(self.cfg_file_tx, conf)

        conf.definitionReduction = 2
        writer.write(self.cfg_file_tx_2, conf)

    def tearDown(self):
        # tx files
        if os.path.isfile(self.cfg_file_tx):
            os.unlink(self.cfg_file_tx)

        if os.path.isfile(self.sino_tx):
            os.unlink(self.sino_tx)

    def testTxFromConfig(self):
        # pass
        interpreter = GlobalConfigInterpreter(self.cfg_file_tx)
        # for unit tests, reset the random generator
        interpreter.setRandSeedToZero(True)
        interpreter.iterate(2)
        k0 = list(interpreter.getReconstructionAlgorithms().keys())[0]
        phantom = interpreter.getReconstructionAlgorithms()[k0].getPhantom()
        numpy.testing.assert_allclose(phantom,
                                      self.sheppLogan_phantom_tx,
                                      rtol=0.5,
                                      atol=3e-3)

    def testIteration(self):
        """
        Make sure that when we call iterate start from the current state
        """
        interpreter = GlobalConfigInterpreter(self.cfg_file_tx)
        # for unit tests, reset the random generator
        interpreter.setRandSeedToZero(True)
        interpreter.iterate(1)
        k0 = list(interpreter.getReconstructionAlgorithms().keys())[0]
        phantomIter1 = interpreter.getReconstructionAlgorithms()[k0].getPhantom().copy()

        interpreter.iterate(1)
        phantomIter2 = interpreter.getReconstructionAlgorithms()[k0].getPhantom()

        self.assertFalse(numpy.allclose(phantomIter1, phantomIter2))

    def testReductionData(self):
        """
        Test that the request for reduction data will be well take into account
        """
        interpreter = GlobalConfigInterpreter(self.cfg_file_tx_2)
        # for unit tests, reset the random generator
        interpreter.setRandSeedToZero(True)
        interpreter.iterate(2)
        k0 = list(interpreter.getReconstructionAlgorithms().keys())[0]
        phantom = interpreter.getReconstructionAlgorithms()[k0].getPhantom()
        self.assertTrue(phantom.shape[1] == self.sheppLogan_phantom_tx.shape[1] / 2)


class TestConfigInterpreterCompton(unittest.TestCase):
    """
    Test that we are able to generate a valid fluorescence reconstruction
    using a cfg file and the interpreter
    """
    materialName = "Steel"
    material = {
        'Comment': "No comment",
        'CompoundList': ['Cr', 'Fe', 'Ni'],
        'CompoundFraction': [18.37, 69.28, 12.35],
        'Density': 1.0,
        'Thickness': 1.0
    }

    materials = {materialName: material}
    sheppLoganPartID = {materialName: 2}
    densities = {materialName: 1.0}

    elements = ['K']

    experimentation = testutils.ComptonExperimentationExample(elements,
                                                              materials,
                                                              sheppLoganPartID,
                                                              densities,
                                                              oversampling=20,
                                                              dampingFactor=0.02,
                                                              nbAngles=360)

    def setUp(self):
        self.experimentation.setUp()

    def tearDown(self):
        self.experimentation.tearDown()

    def testFluoFromConfig(self):
        interpreter = GlobalConfigInterpreter(self.experimentation.cfg_fluo_file)
        # for unit tests, reset the random generator
        interpreter.setRandSeedToZero(True)
        interpreter.iterate(5)

        algos = interpreter.getReconstructionAlgorithms()
        # check parameters from the first algorithm
        for material in algos:
            reconstructed_phantom = algos[material].getPhantom()
            assert(material in self.experimentation.phantoms)
            numpy.testing.assert_allclose(reconstructed_phantom,
                                          self.experimentation.phantoms[material],
                                          rtol=0.5,
                                          atol=5e-2)


class TestConfigInterpreterReconstructionFluo(unittest.TestCase):
    """
    Test that the reconstructions for fluorescence
    (densities*interactionMatrix) are correct
    """

    def setUp(self):
        materialSteel = {
            'Comment': "No comment",
            'CompoundList': ['Cr', 'Fe', 'Ni'],
            'CompoundFraction': [18.37, 69.28, 12.35],
            'Density': 1.0,
            'Thickness': 1.0
        }

        materialTeflon = {
            'Comment': "No comment",
            'CompoundList': ['C1', 'F1'],
            'CompoundFraction': [0.240183, 0.759817],
            'Density': 1.0,
            'Thickness': 1.0
        }

        self.elements = ['Ni', 'K']

        materials = {
            "Steel": materialSteel,
            "Teflon": materialTeflon
        }
        sheppLoganPartID = {
            "Steel": 3,
            "Teflon": 2
        }
        densities = {
            "Steel": 0.5,
            "Teflon": 0.2
        }
        EF = {
            "Ni": 1.0e7,
            "K": 2.0e7
        }
        self.experimentationTwoMat = testutils.FluorescenceExperimentationExample(
            self.elements,
            materials,
            sheppLoganPartID,
            densities,
            oversampling=20,
            dampingFactor=0.02,
            E0=1.0e6,
            EF=EF,
            nbAngles=400)
        self.experimentationTwoMat.setUp()
        self.experimentationTwoMat.voxelSize = 3.0*metricsystem.cm

    def testFluoFromConfigTwoMats(self):
        exp = self.experimentationTwoMat
        interpreter = GlobalConfigInterpreter(exp.cfg_fluo_file)
        # for unit tests, reset the random generator
        interpreter.setRandSeedToZero(True)
        interpreter.iterate(3)

        algos = interpreter.getReconstructionAlgorithms()
        # check parameters from the first algorithm
        for material in algos:
            reconstructed_phantom = algos[material].getPhantom()
            assert(material in exp.phantoms)
            numpy.testing.assert_allclose(reconstructed_phantom,
                                          exp.phantoms[material],
                                          rtol=0.3,
                                          atol=5e-2)

    def tearDown(self):
        self.experimentationTwoMat.tearDown()
        del self.experimentationTwoMat


class TestConfigInterpreterDensitiesFluo(unittest.TestCase):
    """
    Test that the materials densities reconstructed from the fluorescence
    SART are correct.
    """

    def _generateMaterials(self):
        materialSteel = {
            'Comment': "No comment",
            'CompoundList': ['Cr', 'Fe', 'Ni'],
            'CompoundFraction': [18.37, 69.28, 12.35],
            'Density': 1.0,
            'Thickness': 1.0
        }

        self.sheppLogan = {"Steel": 2}
        """this sheppLogan will be sued to generate concentrations"""

        import fisx
        from fisx import Elements
        elements = Elements()

        matSteel = fisx.Material('Steel',
                                 materialSteel['Density'],
                                 materialSteel['Thickness'])
        matSteel.setComposition(dict(zip(materialSteel['CompoundList'],
                                         materialSteel['CompoundFraction'])))
        elements.addMaterial(matSteel)

        self.materials = {"Steel": materialSteel}
        self.densities = {"Steel": 1.0}

        self.elements = ['K']

    def setUp(self):
        self.E0 = 1.0e6
        self._generateMaterials()

        EF2 = {"K": 1.0e7}
        self.experimentationTwoMat = testutils.FluorescenceExperimentationExample(
                                        elements=self.elements,
                                        materials=self.materials,
                                        sheppLoganPartIDs=self.sheppLogan,
                                        densities=self.densities,
                                        oversampling=20,
                                        dampingFactor=0.03,
                                        E0=self.E0,
                                        EF=EF2,
                                        nbAngles=400)
        self.experimentationTwoMat.setUp()
        self.experimentationTwoMat.voxelSize = 3.0*metricsystem.cm

    def testFluoFromConfigTwoMats(self):
        exp = self.experimentationTwoMat
        interpreter = GlobalConfigInterpreter(exp.cfg_fluo_file)
        # for unit tests, reset the random generator
        interpreter.setRandSeedToZero(True)
        interpreter.iterate(3)
        reconstructions = interpreter.interpreter.getDensityPhantoms()

        # check parameters from the first algorithm
        for element in reconstructions:
            reconstructed_phantom = reconstructions[element]
            assert(element in exp.phantoms)
            numpy.testing.assert_allclose(
                reconstructed_phantom, exp.densityMat, rtol=0.25, atol=5e-2)

    def tearDown(self):
        self.experimentationTwoMat.tearDown()
        del self.experimentationTwoMat


class TestXYReduction(ParametricTestCase):
    """
    Test that the configinterpreter is correctly dealing with the
    reduction of the sinogram
    """

    def setUp(self):
        ParametricTestCase.setUp(self)
        self.sinoI0 = structs.I0Sinogram(data=np.arange(100).reshape(10, 10) + 1.0)
        self.tempdir = tempfile.mkdtemp()
        self.confTx = testutils.createConfigTx(self.tempdir,
                                               sinoI0=copy.copy(self.sinoI0))
        self.txSinograms = self.confTx.sinograms

        self.confFluo = testutils.createConfigFluo(self.tempdir,
                                                   sinoI0=copy.copy(self.sinoI0),
                                                   addSelfAbsMat=True,
                                                   addAbsMat=True)
        self.confFluo.minAngle = 0.2
        self.confFluo.maxAngle = 0.8
        self.fluoSinograms = self.confFluo.sinograms

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        ParametricTestCase.tearDown(self)

    def testTx(self):
        for center in (2, 5, 7):
            for selection in (':', '1:6', '0:2; 4:6'):
                for reductionX in (1, 2, 3, 6):
                    for reductionY in (1, 2, 3, 6):
                        with self.subTest(selection=selection,
                                          reductionDefinition=reductionX,
                                          reductionAngle=reductionY,
                                          center=center):
                            txConf = config.TxConfig(
                                sinograms=copy.deepcopy(self.txSinograms),
                                projections='2:6',
                                minAngle=0.0,
                                maxAngle=1.2,
                                dampingFactor=1.,
                                I0=copy.deepcopy(self.sinoI0))

                            txConf.projections = selection
                            txConf.definitionReduction = reductionX
                            txConf.projectionNumberReduction = reductionY
                            txConf.center = center
                            gci = GlobalConfigInterpreter(filePath=None,
                                                          config=txConf)
                            gci.iterate(1)

    def testFluo(self):
        for center in (2, 5, 7):
            for selection in (':', '1:6', '0:2; 4:6'):
                for reductionX in (1, 2, 3, 6):
                    w = center if center < 5 else 10 - center
                    currentWidth = w * 2
                    mod = currentWidth % reductionX
                    mod = 1 if mod > 0 else 0
                    matWidth = int(currentWidth / reductionX) + mod
                    absMatData = numpy.arange(matWidth*matWidth).reshape(matWidth,
                                                                         matWidth)
                    absMat = structs.AbsMatrix(data=copy.copy(absMatData))
                    selfAbsMat = structs.SelfAbsMatrix(data=copy.copy(absMatData))
                    for reductionY in (1, 2, 3, 6):
                        with self.subTest(selection=selection,
                                          reductionDefinition=reductionX,
                                          reductionAngle=reductionY,
                                          center=center):
                            fluoConf = self.confFluo
                            fluoConf.setI0(copy.deepcopy(self.sinoI0))
                            fluoConf.sinograms = copy.deepcopy(self.fluoSinograms)
                            fluoConf.absMat = copy.deepcopy(absMat)
                            assert fluoConf.absMat.data.shape == (matWidth, matWidth)
                            for sino in fluoConf.sinograms:
                                sino.selfAbsMat = copy.deepcopy(selfAbsMat)
                                assert sino.selfAbsMat.data.shape == (matWidth, matWidth)
                            fluoConf.projections = selection
                            fluoConf.definitionReduction = reductionX
                            fluoConf.projectionNumberReduction = reductionY
                            fluoConf.center = center
                            # absorption and self absorption matrices have to
                            # be of the correct shape
                            gci = GlobalConfigInterpreter(filePath=None,
                                                          config=fluoConf)
                            gci.iterate(1)


def suite():
    test_suite = unittest.TestSuite()
    for test in (TestConfigInterpreterTx, TestConfigInterpreterCompton,
                 TestConfigInterpreterCompton,
                 TestConfigInterpreterReconstructionFluo,
                 TestConfigInterpreterDensitiesFluo,
                 TestXYReduction):
        test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(test))

    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest="suite")
