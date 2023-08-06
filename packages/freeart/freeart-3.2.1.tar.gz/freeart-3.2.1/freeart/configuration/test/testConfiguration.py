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
"""test that the TxConfig and FluoConfig class are correct
"""


__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "18/10/2017"

import unittest
from freeart.configuration import config, structs, fileInfo
import numpy


class TestConfigurationClasses(unittest.TestCase):
    """Make sure the configuration classes are correctly instanciated"""
    def testBaseClass(self):
        """Test the Base class conditions : _ReconsConfig"""
        l = config._ReconsConfig(reconsType=config._ReconsConfig.TX_ID,
                                 projections='2:6',
                                 minAngle=0,
                                 maxAngle=numpy.pi)

        with self.assertRaises(ValueError):
            l = config._ReconsConfig(reconsType=config._ReconsConfig.TX_ID,
                                     projections='2:6',
                                     minAngle=0,
                                     maxAngle=3*numpy.pi)

        l = config._ReconsConfig(reconsType=config._ReconsConfig.TX_ID,
                                 projections='2:6',
                                 minAngle=0,
                                 maxAngle=numpy.pi,
                                 I0=1)
        self.assertTrue(l.useAFileForI0 is False)

        l = config._ReconsConfig(reconsType=config._ReconsConfig.TX_ID,
                                 projections='2:6',
                                 minAngle=0,
                                 maxAngle=numpy.pi,
                                 I0='dsadsda')
        self.assertTrue(l.useAFileForI0 is True)

    def testItRecons(self):
        "test _ItReconsConfig class"
        l = config._ItReconsConfig(reconsType=config._ReconsConfig.TX_ID,
                                 projections='2:6',
                                 minAngle=0,
                                 maxAngle=numpy.pi,
                                 dampingFactor=1.,
                                 precision='double')
        self.assertTrue(l.reconsType == config._ReconsConfig.TX_ID)
        self.assertTrue(l.projections == '2:6')
        self.assertTrue(l.dampingFactor == 1.)
        self.assertTrue(l.precision == 'double')

    def testTxConfig(self):
        "test TxConfig class"
        l = config.TxConfig(sinograms=None,
                            projections='2:6',
                            minAngle=0,
                            maxAngle=numpy.pi,
                            dampingFactor=1.,
                            precision='simple')
        self.assertTrue(l.reconsType == config._ReconsConfig.TX_ID)
        self.assertTrue(l.projections == '2:6')
        self.assertTrue(l.dampingFactor == 1.)
        self.assertTrue(l.computeLog is True)
        self.assertTrue(l.precision == 'simple')
        l.addSinogram(structs.TxSinogram(name='sino1',
                                         data=numpy.zeros((10, 10))))
        l.addSinogram(structs.TxSinogram(name='sino2',
                                         data=numpy.zeros((10, 10))))
        self.assertTrue(len(l.sinograms) is 2)

    def testFluoConfig(self):
        """test FluoConfig class"""
        detector = structs.Detector(x=1, y=2, z=3, width=0.1)
        l = config.FluoConfig(outBeamCalMethod=None,
                              sinoI0=None,
                              absMat=None,
                              isAbsMatASinogram=True,
                              detector=detector,
                              minAngle=0,
                              maxAngle=numpy.pi,
                              dampingFactor=1.)
        self.assertTrue(l.reconsType == config._ReconsConfig.FLUO_ID)
        self.assertTrue(l.projections == None)
        self.assertTrue(l.dampingFactor == 1.)
        self.assertTrue(l.absMat == structs.AbsMatrix())
        self.assertTrue(l.detector == detector)


class TestConfigToDict(unittest.TestCase):
    """Make sure the toDict function of the reconstruction configuration are
    working"""
    def testBaseClass(self):
        """Test the Base class conditions : _ReconsConfig"""
        l = config._ReconsConfig(reconsType=config._ReconsConfig.TX_ID,
                                 projections='2:6',
                                 minAngle=0,
                                 maxAngle=numpy.pi,
                                 includeLastProjection=True,
                                 oversampling=12)
        l.toDict()

    def testItRecons(self):
        "test _ItReconsConfig class"
        l = config._ItReconsConfig(reconsType=config._ReconsConfig.TX_ID,
                                   projections='2:6',
                                   minAngle=0,
                                   maxAngle=numpy.pi,
                                   dampingFactor=1.,
                                   solidAngleOff=True)
        l.toDict()

    def testTxConfig(self):
        "test TxConfig class"
        filePath = 'test.edf'
        sinograms = [
            structs.TxSinogram(
                fileInfo=fileInfo.EDFMatrixFileInfo(filePath=filePath)),
            structs.TxSinogram(
                fileInfo=fileInfo.EDFMatrixFileInfo(filePath=filePath))
        ]
        conf = config.TxConfig(sinograms=sinograms,
                               projections='2:6',
                               minAngle=0,
                               maxAngle=numpy.pi,
                               dampingFactor=1.)
        conversion = conf.toDict()
        self.assertTrue(conf == config.TxConfig()._fromDict(conversion))

    def testFluoConfig(self):
        """test FluoConfig class"""
        filePath = 'test.edf'
        sinoTest = structs.FluoSino(
            fileInfo=fileInfo.EDFMatrixFileInfo(index=1,
                                                filePath=filePath),
            name='mySinogram',
            physElmt='O',
            ef=12,
            selfAbsMat=None)
        detector = structs.Detector(x=1, y=2, z=3, width=0.1)

        conf = config.FluoConfig(outBeamCalMethod=None,
                                 sinoI0=None
                                 ,
                                 absMat=None,
                                 isAbsMatASinogram=True,
                                 detector=detector,
                                 minAngle=0,
                                 maxAngle=numpy.pi,
                                 dampingFactor=1.,
                                 centerOfRotation=6.,
                                 acquiInverted=True)
        conf.addSinogram(sinoTest)
        conversion = conf.toDict()
        self.assertTrue(conf == config.FluoConfig()._fromDict(conversion))

        conf = config.FluoConfig(outBeamCalMethod=None,
                                 sinoI0=None,
                                 absMat=None,
                                 isAbsMatASinogram=True,
                                 detector=detector,
                                 minAngle=0,
                                 maxAngle=numpy.pi,
                                 dampingFactor=1.,
                                 centerOfRotation=6.,
                                 acquiInverted=True,
                                 sinograms={filePath: sinoTest})
        conversion = conf.toDict()
        self.assertTrue(conf == config.FluoConfig()._fromDict(conversion))


def suite():
    test_suite = unittest.TestSuite()
    for t in (TestConfigurationClasses, TestConfigToDict):
        test_suite.addTest(unittest.defaultTestLoader.loadTestsFromTestCase(t))

    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest="suite")
