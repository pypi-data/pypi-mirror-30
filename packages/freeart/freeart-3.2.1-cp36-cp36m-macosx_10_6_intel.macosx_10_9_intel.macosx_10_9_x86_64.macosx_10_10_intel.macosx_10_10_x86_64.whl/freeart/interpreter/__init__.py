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
"""
Python module to build and run a freeart reconstruction from a configuraton
file (.cfg file).
"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "23/05/2016"


from freeart.configuration import read as readConfig
from .configinterpreter import TxConfInterpreter, FluoConfInterpreter
import freeart.utils.reconstrutils as reconstrutils
from threading import Thread
import os
import logging

_logger = logging.getLogger(__name__)


class GlobalConfigInterpreter():
    """
    This is hte main class of the module.
    The Global interpreter will call other interpreters in order to interpret a
    configuration file into a transmission or a fluorescence reconstruction.

    :param filePath: the file path of th ecfg file
    :param config: the `_ReconsConfig` if already exists
    :param force: if True, will force the interpreter to be created even if the
                  cfg file is invalid. This parameter is used for example in
                  the case that the we have a fluorescence reconstruction and
                  that we want to build a transmission reconstruction first
    """

    interpreter = None
    """The interpreter used to convert a .cfg file into a freeart
    reconstruction"""

    def __init__(self, filePath, config=None, force=False):
        self.filePath = filePath
        if self.filePath is not None:
            self._checkFileIsCorrect()

        if config is None:
            self._config = readConfig(self.filePath)
        else:
            self._config = config

        if self.isATxReconstruction():
            inf = """Transmission reconstruction file detected. Creating the
                reconstruction algorithm"""
            _logger.info(inf)
            self.interpreter = TxConfInterpreter(filePath, self._config)
        elif self._config.isAbsMatASinogram is True:
            inf = """In order to run the fluorescence reconstruction the
             absorption matrix need to be reconstructed first. Please run
             this reconstruction first.
             """
            raise ValueError(inf)
        elif self.isAFluoOrComptonReconstruction():
            inf = """Fluorescence reconstruction file detected. Creating the
                reconstruction algorithm"""
            _logger.info(inf)
            self.interpreter = FluoConfInterpreter(filePath, self._config)

    def getConfig(self):
        return self.interpreter.config

    config = property(getConfig)

    def getReconstructionAlgorithms(self):
        """
        Return one ART algorithm for each sinogram we want to reconstruct
        """
        if self.interpreter:
            return self.interpreter.getReconstructionAlgorithms()
        else:
            inf = "No interpreter found during construction for the given file"
            _logger.info(inf)
            return None

    def isATxReconstruction(self):
        """

        :return: True if the given file is set up for a transmission
        reconstruction"""
        return self._config.reconsType == 'Transmission'

    def isAFluoOrComptonReconstruction(self):
        """

        :return: True if the given file is set up for a fluorescence or
        compton reconstruction"""
        return self._config.reconsType in ('Fluorescence', 'Compton')

    def _checkFileIsCorrect(self):
        """chack that the givem cfg file is correct"""
        if not type(self.filePath) is str:
            err = "%s should be a string" % self.filePath
            raise TypeError(err)
        if not os.path.isfile(self.filePath):
            err = "%s should be an existing file" % self.filePath
            raise ValueError(err)

    def iterate(self, nbIteration):
        """
        Run nb Iteration, if possible in parallel

        :param nbIteration: the number of iteration we want to run
            (one iteration will execute a backward projection from each angle
                of acquisition)
        """
        t = Thread(target=self.interpreter.iterate, args=(nbIteration,))

        t.start()
        t.join()

    def setRandSeedToZero(self, b):
        self.interpreter.setRandSeedToZero(True)

    def saveCurrentReconstructionsTo(self, folderPath):
        """
        save one file per reconstruction to the given folder

        :param folderPath: the path we want to save under
        """
        assert(self.interpreter is not None)
        assert(os.path.isdir(folderPath))
        folderPath = folderPath + "/"
        algos = self.getReconstructionAlgorithms()
        for algoName in algos:
            outputFile = folderPath + 'recons_' + algoName
            if not outputFile.lower().endswith('.edf'):
                outputFile = outputFile + '.edf'
            reconstrutils.savePhantom(algos[algoName].getPhantom(), outputFile)

    def setOversampling(self, val):
        """
        Set the given oversampling to all the ART algorithms of the interpreter

        :param val: the new oversampling value.
        """
        assert(type(val) == int)
        assert(type(val) > 0)
        ARTAglos = self.interpreter.getReconstructionAlgorithms()
        for algo in ARTAglos:
            ARTAglos[algo].setOverSampling(val)

    def setDampingFactor(self, val):
        """
        Set the given dampingFactor to all the ART algorithms of the
        interpreter

        :param val: the new dampingFactor value.
        """
        assert(type(val) == float)
        assert(val > 0)
        assert(val <= 1.0)
        ARTAglos = self.interpreter.getReconstructionAlgorithms()
        for algo in ARTAglos:
            ARTAglos[algo].setDampingFactor(val)

    def setRayPointCalculationMethod(self, methodID):
        """
        Set the given dampingFactor to all the ART algorithms of the
        interpreter

        :param methodID: the new method to compute the ray points values
            (with or without interpolation).
        """
        ARTAglos = self.interpreter.getReconstructionAlgorithms()
        for algo in ARTAglos:
            ARTAglos[algo].setRayPointCalculationMethod(methodID)

    def setOutgoingRayAlgorithm(self, algorithmID):
        """
        Set the given dampingFactor to all the ART algorithms of the
        interpreter

        :param algorithmID: the new algorithmID value.
        """
        ARTAglos = self.interpreter.getReconstructionAlgorithms()
        for algo in ARTAglos:
            ARTAglos[algo].setOutgoingRayAlgorithm(algorithmID)

    def getReconstructionType(self):
        """

        :return: the type of reconstruction we want to run
        """
        return self.interpreter.config.reconsType

    def getE0(self):
        """

        :return: the energy of the incoming rays. Units of Energy is keV
        """
        return self.config.E0

    def setE0(self, E0):
        """
        Set the energy of the incoming rays. This is needed for fluorescence
        reconstruction.

        :param E0: the energy of the incoming rays. In keV
        """
        self.config.E0 = E0
