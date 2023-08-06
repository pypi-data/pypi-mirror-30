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
"""Create the link between freeart and a configuration file. Basically set up
a reconstruction
"""
__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "23/10/2017"

from freeart.configuration import config, structs
import freeart
import os
import sys
import freeart.utils
import freeart.utils.reconstrutils as reconstrutils
import freeart.utils.physicalelmts as physicalelmts
from freeart.utils import sinogramselection
import numpy as np
import logging
import fisx
from threading import Thread
from fisx import Detector
from fabio.edfimage import edfimage
from freeart.configuration import read
import numpy
import copy
_logger = logging.getLogger("freeARTInterpreter")
logging.basicConfig(level=logging.INFO)

elementInstance = None


class AbsConfInterpreter(object):
    """Abstract class from which each interpreter (fluorescence, tx...)
    should inherit"""

    def __init__(self, filePath, _config):
        assert not (filePath is None and _config is None)

        self.filePath = filePath
        if filePath:
            self.config = read(self.filePath)
        else:
            self.config = copy.deepcopy(_config)

        assert(self.config.precision in config._ReconsConfig.PRECISION_TO_TYPE)
        self.precisionType = config._ReconsConfig.PRECISION_TO_TYPE[self.config.precision]
        self.setTheoreticalSampSize()
        self.setLimitParallelReconstruction(-1)
        self.setLimitVoxels(-1)
        self.config.fillSinogramNames()
        self.angles = None
        if self.config.useAFileForI0:
            self.config.I0.loadData(refFile=None)
            assert self.config.I0.data is not None
            self.config.I0.data = self.adaptSinogramData(data=self.config.I0.data,
                                                         isI0=True)

    def resetAngles(self):
        """Reset all angles """
        self.angles = None

    def setTheoreticalSampSize(self):
        raise NotImplementedError('AbsConfInterpreter is a pure virtual class')

    def iterate(self):
        """
        Iterate on the reconstruction. Each iteration generate a backward
        projection for each angle of acquisition (in a random order).
        """
        raise NotImplementedError('AbsConfInterpreter is a pure virtual class')

    def _reduceSinogram(self, matrix):
        """Reduce the data according to the DefinitionReductionfactor and the
        ProjectionReductionFactor

        :param matrix: the matrix to reduce
        :return: the matrix reduced
        """
        if self.config.definitionReduction is None:
            self.config.definitionReduction = 1

        matrix = self._reduceXData(matrix, self.config.definitionReduction)

        if self.config.projectionNumberReduction is None:
            self.config.projectionNumberReduction = 1

        return self._reduceNbAnglesData(matrix)

    def _adaptMatToReduction(self, data):
        """
        Reduce the matrix in x and y according to the requested configuration.
        Take into account the projection reduction and the definition reduction.

        :param data: the matrix to reduce.
        :return: a reduced matrix
        """
        if data.shape[1] != self._getTheoreticalSampSize():
            if self.config.definitionReduction is None:
                self.dataXReduction = self.config.definitionReduction
            res = None
            reduction = self.config.definitionReduction
            if len(data.shape) == 3:
                res = data[:, ::reduction, ::reduction]

            if len(data.shape) == 2:
                res = data[::reduction, ::reduction]

            if res is None:
                raise RuntimeError("Unvalid matrix dimension")
            else:
                return res
        else:
            return data

    def _getTheoreticalSampSize(self):
        # return the size of the reconstructed sample
        return self._thSampSize

    def _getFirstFluoSino(self):
        if self.config.sinograms is None or len(self.config.sinograms) is 0:
            return None
        else:
            return self.config.sinograms[0]

    def _getAngles(self, nbAngles, selection):
        """
        Compute nbAngle homogeneous angle between minAngle and maxAngle.
        Take into account if the last angle should be equal to the first angle
        from the config file (LastAngleEqualFirstAngle option)

        :param nbAngles: the number of angle we want to generate
        :return: the angle for homogeneous angle between each acquisition
        """
        def getMinAngle():
            if self.config.minAngle is None:
                err = "can't find information about min angle in the .cfg file"
                raise IOError(err)

            return self.config.minAngle

        def getMaxAngle():
            if self.config.maxAngle is None:
                err = "can't find information about max angle in the .cfg file"
                raise IOError(err)

            return self.config.maxAngle

        # if specify that the last angle in the sinogram == first angle in the
        # sinogram
        if self.config.includeLastProjection is None:
            self.config.includeLastProjection = False

        minAngle = getMinAngle()
        maxAngle = getMaxAngle()

        if minAngle > maxAngle:
            raise RuntimeError("minAngle > maxAngle, can't process")

        if minAngle < -2.1*np.pi or minAngle > 2.1*np.pi or maxAngle < -2.1*np.pi or maxAngle > 2.1*np.pi:
            err = """Angles should be defined in radians. We for minAngle and
                maxAngle at least one angle < -2*pi or > 2.pi """
            raise RuntimeError(err)

        return sinogramselection.getAngles(minAngle=minAngle,
                                           maxAngle=maxAngle,
                                           selection=selection,
                                           acquiInverted=self.config.acquiInverted,
                                           lastAngleEqualFirst=self.config.includeLastProjection,
                                           nbAngles=nbAngles)

    def _reduceNbAnglesData(self, data):
        """
        Reduce the number of angles in the data of a factor factorReduction

        :param data: the matrix to reduce
        :param factorReduction: the factor of reduction to apply
        :return: the matrix reduced

        .. warning:: the matrix should be a 2D numpy array
        """
        return data[::self.config.projectionNumberReduction, ]

    def _reduceXData(self, data, factorReduction):
        """
        Reduce the number of projection in the data of a factor factorReduction

        :param data: the matrix to reduce
        :param factorReduction: the factor of reduction to apply
        :return: the matrix reduced

        .. warning:: the matrix should be a 2D numpy array
        """
        return data[:, ::factorReduction]

    def _centerSinogram(self, data, center):
        """Simple function to center the sinogram

        :param data: the sinogram to center
        :param center: The new center of rotation
        """
        assert(len(data.shape) == 2)
        width = min(abs(data.shape[1]-center), center)
        if width > 0:
            return data[:, center-width:center+width]
        else:
            _logger.info("can t center the sinogram. Centering avoid")
            return data

    def getSinograms(self):
        """

        :return: A dictionnary of the sinograms to treat"""
        err = 'getSinograms not implemented. '
        err += 'AbsConfInterpreter is a pure virtual class'
        raise NotImplementedError(err)

    def getFile(self):
        """

        :return: the current configuratioin file """
        return self.filePath

    def setLimitParallelReconstruction(self, val):
        """
        Limit the number of parallel reconstruction we can run

        :param val: the new limitation of parallel reconstructions to run
        """
        if val > 0:
            self.limitParaRecon = val
        if val == -1:
            self.limitParaRecon = sys.maxsize

    def setLimitVoxels(self, val):
        """
        Limit the maximal number of voxel we can run during one iteration

        :param val: the maximal number of voxel to run during one step.
        """
        if val > 0:
            self.limitVoxel = val
        if val == -1:
            self.limitVoxel = sys.maxsize

    def _normalizeRawData(self, sinogram):
        """Normalization of raw data. Apply the new center of rotation, reduce
        data if needed and normalize fron I0 value.

        :param sinogram: the sinogram to normalize
        """
        assert sinogram.ndim is 2
        if self.config.useAFileForI0 is True:
            assert self.config.I0.data is not None
            sI0 = reconstrutils.decreaseMatSize(self.config.I0.data).shape
            if (sI0 != sinogram.shape):
                err = """I0 sinogram (%s) and sinogram (%s) have different
                                    shapes""" % (sI0, sinogram.shape)
                raise ValueError(err)
            else:
                sinogram = sinogram / reconstrutils.decreaseMatSize(self.config.I0.data)
        elif self.config.I0 is not None:
            if not isinstance(self.config.I0, numpy.ndarray) and self.config.I0 <= 0.0:
                raise ValueError("invalid I0 value given")
            else:
                sinogram = sinogram / self.config.I0

        return sinogram

    def adaptSinogramData(self, data, isI0=False):
        """
        center, reduce sinogram (X definition and number of projection) and
        pick the range of projection requested.

        :param data:
        :param computeAngles: If true then compute `self.angles`
        :return: data adapted to constrain
        """
        data = reconstrutils.decreaseMatSize(data)

        # step 0: get angles
        selection = self.config.projections
        if isI0 is False:
            self.angles = self._getAngles(nbAngles=data.shape[0],
                                          selection=selection)
            self.angles = self._reduceNbAnglesData(self.angles)
            self.angles = numpy.ascontiguousarray(self.angles)

        # step 1 : normalization of the sinogram
        if self.config.center:
            data = self._centerSinogram(data, self.config.center)

        # step 2: get the selected sinogram
        data = sinogramselection.getSelection(selection=selection,
                                              projections=data)

        # step 3 : deal with data reduction.
        # Rule : do not reduce data when the target is to produce an absMat.
        # Simplify a lot stuff (specially when loading fluo config file)
        data = self._reduceSinogram(data)

        # step 4 : normalize from I0
        if isI0 is False:
            data = self._normalizeRawData(data)

        # step 5 : move it to 3D
        if data.ndim is 2:
            data.shape = (1,
                          data.shape[0],
                          data.shape[1])
        return data

    def getSinograms(self):
        """

        :return: A dictionnary of the sinograms to treat
        """
        return self.config.sinograms


class TxConfInterpreter(AbsConfInterpreter):
    """
    Interpreter for tx reconstruction

    :param filePath: the path of the cfg file
    """
    def __init__(self, filePath, _config=None):
        AbsConfInterpreter.__init__(self, filePath=filePath, _config=_config)
        if _config:
            assert(isinstance(_config, config.TxConfig))
        self.txRecons = {}
        # make sure data is here
        self._setUpTxReconstruction()

    def getReconstructionAlgorithms(self):
        """

        :return: the dictionay of the freeart reconstruction.
        """
        return self.txRecons

    def setTheoreticalSampSize(self):
        def checkSinograms():
            shape = None
            for sinogram in self.config.sinograms:
                assert isinstance(sinogram, structs.Sinogram)
                assert (sinogram.data is not None)
                assert (sinogram.data.ndim is 2)

                if shape is None:
                    shape = sinogram.data.shape
                elif sinogram.data.shape != shape:
                    raise ValueError('At least two sinograms to reconstruct'
                                     ' have different dimension. Case not'
                                     ' managed by the freeart interpreter')

        assert(self.config.sinograms)
        sinogram = self.config.sinograms[0]
        sinogram.loadData(refFile=self.filePath)
        checkSinograms()
        width = sinogram.data.shape[1]
        if self.config.center not in (None, -1):
            hwidth = self.config.center if self.config.center <= width / 2 else width - self.config.center
            width = hwidth * 2
        mod = width % self.config.definitionReduction
        mod = 1 if mod > 0 else 0
        self._thSampSize = int(width / self.config.definitionReduction) + mod

    def _setUpTxReconstruction(self):
        """
        Setup the FreeART Tx algorithm to fit with the self.configuration file
        """
        # deal with I0
        if self.config.useAFileForI0 is True:
            assert(isinstance(self.config.I0, structs.I0Sinogram))
            if self.config.I0.data is None:
                self.config.I0.loadData(refFile=self.filePath)

        for sinogram in self.config.sinograms:
            self.txRecons[sinogram.name] = self._buildAlgoTx(sinogram=sinogram)

    def _buildAlgoTx(self, sinogram):
        """
        Build a transmission ART algorithm for the given algorithm and given
        self.configuration file
        """
        assert sinogram.data is not None
        sinogram.data = self.adaptSinogramData(sinogram.data,
                                               isI0=False)

        # if some values of the sinogram are negative and the sinogram is I
        # (and not -log(I))
        if self.config.computeLog and (True in (sinogram.data < 0.0)):
            err = """given sinogram has negative values. Can't process
                  the reconstruction"""
            raise RuntimeError(err)

        # create the adapted ARTAlgorithm
        if self.config.computeLog is True:
            logVal = -np.log(sinogram.data)
        else:
            logVal = sinogram.data
        assert(np.nan not in logVal)

        txAlgo = freeart.TxBckProjection(logVal.astype(self.precisionType),
                                         self.angles)

        if self.config.voxelSize:
            txAlgo.setVoxelSize(self.config.voxelSize * self.config.definitionReduction)

        if self.config.oversampling:
            txAlgo.setOverSampling(self.config.oversampling)

        if self.config.I0 is not None:
            if self.config.useAFileForI0 is False:
                txAlgo.setI0(float(self.config.I0))

        if self.config.beamCalcMethod:
            txAlgo.setRayPointCalculationMethod(self.config.beamCalcMethod)

        if self.config.dampingFactor:
            txAlgo.setDampingFactor(self.config.dampingFactor)

        return txAlgo

    def iterate(self, nbIteration):
        """
        Iterate on the reconstruction. Each iteration generate a backward
        projection for each angle of acquisition (in a random order).
        """
        if self.txRecons is None:
            err = "No ART algorithm defined"
            raise ValueError(err)
        threads = []
        for algoID in self.txRecons:
            assert(not self.txRecons[algoID] is None)
            threads.append(Thread(target=self.txRecons[algoID].iterate,
                                  args=(nbIteration,)))

        [thread.start() for thread in threads]
        [thread.join() for thread in threads]

    def setRandSeedToZero(self, b):
        if self.txRecons is None:
            err = "No ART algorithm defined"
            raise ValueError(err)
        for algo in self.txRecons:
            self.txRecons[algo].setRandSeedToZero(b)


class FluoConfInterpreter(AbsConfInterpreter):
    """
    FreeART interpreter for fluorescence reconstruction.
    Basicall y take a .cfg file containing the description of the
    reconstruction in input and create all corresponding ARTAlgorithm for such
    reconstructions

    :param filePath: the configuration file to be interpreted.
    """
    def __init__(self, filePath, _config=None):
        AbsConfInterpreter.__init__(self, filePath=filePath, _config=_config)

        if _config:
            assert (isinstance(_config, config.FluoConfig))

        self.fisxMaterials = {}
        """Dict to associate at each material in the sample the corresponding
        fisx materials"""
        self.selfAbsMatFile = {}
        """File where to get the selfAbsMat file in case the user give them"""
        self.absMatrixFile = None
        """The file of the absorption matrix file"""
        self.fluoSinogramsAlgorithms = {}
        "all the art algorithm to fit the configuration file"
        self.fluoSinograms = {}
        "sinograms to treat"
        self.interactionMatrice = {}
        "the interaction matrices"
        self._sinoElemt = {}

        self._setUpFluoReconstruction()
        self._buildAlgorithms()

    def setTheoreticalSampSize(self):
        sino = self._getFirstFluoSino()
        assert(sino)
        assert isinstance(sino, structs.FluoSino)
        assert(sino.data.ndim is 2)

        width = sino.data.shape[1]
        if self.config.center not in (None, -1):
            hwidth = self.config.center if self.config.center <= width / 2 else width - self.config.center
            width = hwidth * 2
        mod = width % self.config.definitionReduction
        mod = 1 if mod > 0 else 0

        self._thSampSize = int(width / self.config.definitionReduction) + mod

    def _setUpFluoReconstruction(self):
        """
        Setup the FreeART Fluo algorithm to fit with the self.configuration
        file
        """
        if len(self.config.sinograms) < 1:
            raise ValueError("No fluorescence sinograms given")

        if self.config.absMat is None or (self.config.absMat.fileInfo is None and self.config.absMat.data is None):
            raise ValueError('Absorption matrix not defined')

        if self.config.absMat.data is None and not os.path.isfile(self.config.absMat.fileInfo.getFile()):
            err = self.config.absMat + " absorption file setted does not exist"
            raise ValueError(err)

        # in the case we need to build the absorption matrice from ourself
        if self.config.isAbsMatASinogram is True:
            mess = """The interpreter is not able to reconstruct by himself the
                absorption matrix. Please build it first, then give if back to
                the freeart interpreter"""
            raise RuntimeError(mess)
        elif self.config.absMat.data is None:
            self.config.absMat.loadData(self.filePath)
        self.config.absMat.data = self._adaptMatToReduction(self.config.absMat.data)
        if self.config.absMat.data.shape[1] != self._getTheoreticalSampSize():
            s1 = self.config.absMat.data.shape[1]
            s2 = self._getTheoreticalSampSize()
            err = 'The absorption matrix has invalid dimensions (%s).' \
                  'When in theory it should be (%s, %s). This error can occur' \
                  'if the absorption matrix have been reconstructed with a ' \
                  'different center of rotation for example.' % (s1, s2, s2)
            raise ValueError(err)

        self.config.absMat.data.shape = (self.config.absMat.data.shape[0],
                                         self.config.absMat.data.shape[1],
                                         1)

        self.__prepareMaterials()

    def __prepareMaterials(self):
        """
        prepare materials for fisx
        """
        if self.config.materials is None or self.config.materials.materials is None or \
            self.config.materials.matComposition is None or \
            self.config.materials.materials.fileInfo is None or \
                        self.config.materials.matComposition.fileInfo is None:
            return
        else:
            assert(self.config.materials.materials is not None)
            assert(self.config.materials.materials.fileInfo is not None)
            assert(self.config.materials.matComposition is not None)
            assert(self.config.materials.matComposition.fileInfo is not None)
            assert(os.path.isfile(self.config.materials.materials.fileInfo.filePath))
            self.config.materials.loadData(self.filePath)
            materials = self.config.materials.materials.data

            physicalelmts.elementInstance.removeMaterials()
            for materialName in materials:
                uniqMatName = reconstrutils.getFisxMatName(materialName)
                self.fisxMaterials[uniqMatName] = reconstrutils.convertToFisxMaterial(
                    uniqMatName,
                    materials[materialName])
                physicalelmts.elementInstance.addMaterial(
                    self.fisxMaterials[uniqMatName])

    def __getFisxDetector(self):
        """

        :return: the fisx detector to compute the interaction matrix
        """
        # TODO : get the material of the detector
        # pb : in this case we will take twice the effect of the solid angle.
        # Something that we don't want to...
        detector = Detector("Si1", 2.33, 1.0)
        detector.setDiameter(self.config.detector.width)

    @staticmethod
    def getProbabilityOfEmission(fisxMat, energy, element, fisxElements,
                                 shell=None):
        """
        compute the probability of emission of the element for a specific
        energy and material.

        :param fisxMat: the fisx material of the interaction
        :param energy: the nergy of the incomng beam
        :param element: the generated element
        :param shell: the targetted shell of the interaction.

        :return: the probability of emission of the element for a specific
                 energy and material.
        """
        if not type(fisxMat) is fisx.Material:
            raise TypeError('material should be a fisx.Material')
        if(len(fisxMat.getComposition()) is 0):
            raise TypeError('Issue with fisx Material, not correctly registred')

        excitations = fisxElements.getExcitationFactors(element, [energy])

        if sys.version_info[1] > 2:
            photonelectricMassAttenuation = fisxElements.getMassAttenuationCoefficients(fisxMat.getComposition(), [energy])[b'photoelectric']
        else:
            photonelectricMassAttenuation = fisxElements.getMassAttenuationCoefficients(fisxMat.getComposition(), [energy])['photoelectric']

        if shell is None:
            rate = 0.
            for excitation in excitations:
                rate += excitations[excitation]['rate'] * photonelectricMassAttenuation[0]
            return rate
        else:
            if shell not in excitations:
                raise ValueError('Required shell is not existing for the elemnt')
            else:
                return excitations[element]['rate'][shell] * photonelectricMassAttenuation

    def _resetFluoSinograms(self):
        """Reset all fluorescence sinograms """
        self.fluoSinogramsAlgorithms = {}
        self.fluoSinograms = {}
        self.interactionMatrice = {}

    def _resetSinoElemt(self):
        """
        Reset the sinogram element
        """
        self._sinoElemt = {}

    def _buildAlgorithms(self):
        """
        will setup one ART algorithm per fluo sinogram
        """
        self._resetFluoSinograms()
        self.resetAngles()

        [self._buildAlgorithm(sinogram) for sinogram in self.config.sinograms]

    def __getTitle(self, header):
        """return the title of the header"""
        if 'title' in header:
            return header['title']
        if 'Title' in header:
            return header['Title']
        return None

    def __getMeanData(self, edfReader, groupFiles, indexDataToTreat, referenceName):
        """Simply create a mean sinogram from a list of files and check that
        each sinogram of the file as the same ID (referenceName)

        :param edfReader: the edfReader for the file
        :param groupFiles: the list of file definig the group
        :param indexDataToTreat: index of the sinogram in the file
        :param referenceName: The 'title' of the reference sinogram
        """
        sino = None

        for file in groupFiles:
            # check that titles are the same as the reference file. otherwise
            # through an error
            if edfReader.nframes == 1:
                if self.__getTitle(edfReader.getHeader()) != referenceName:
                    raise ValueError('incoherent title name between sinogram to compute the mean')

                if sino is None:
                    sino = edfReader.getData()
                else:
                    sino += edfReader.getData()

            else:
                if self.__getTitle(edfReader.getframe(int(indexDataToTreat)).getHeader()) != referenceName:
                    raise ValueError('incoherent title name between sinogram to compute the mean')

                if sino is None:
                    sino = edfReader.getframe(int(indexDataToTreat)).getData()
                else:
                    sino += edfReader.getframe(int(indexDataToTreat)).getData()

        return sino / len(groupFiles)

    def _buildAlgorithm(self, sinogram):
        """build the algorithm for the givem file path"""

        # read the file
        if sinogram.data is None:
            err = "sinogram %s has empty data" + sinogram.name
            raise IOError(err)

        if sinogram.fileInfo:
            datasets = self.config.getSinogramsFileDict()[sinogram.fileInfo.getFile()]
            gf, groupType = reconstrutils.tryToFindPattern(sinogram.fileInfo.getFile())
            if groupType == 'pymca':
                try:
                    self.__treatAsAPymcaGroupFiles(sinogram.fileInfo.getFile(),
                                                   datasets)
                    return
                except ValueError:
                    err = """Found incoherence in the files or in sinograms, unable
                        to associate pymca group files"""
                    _logger.info(err)
        self.__treatAsAStandardFile(sinogram)

    def __treatAsAPymcaGroupFiles(self, filePath, sinograms):
        """
        create all the algorithm from getting the mean file from the pymca
        """
        groupFiles = reconstrutils.tryToFindPattern(filePath, 'pymca')
        assert(len(groupFiles) > 0)
        if (len(groupFiles) < 2):
            err = "file can't be associated with any other pymca file"
            raise ValueError(err)

        edfReader = edfimage()
        edfReader.read(filePath)

        for sino in sinograms:
            assert(isinstance(sino, structs.FluoSino))
            name = sino.name
            self._sinoElemt[name] = sino.physElmt
            EF = sino.EF

            refName = None
            if edfReader.nframes == 1:
                refName = self.__getTitle(edfReader.getHeader())
            else:
                refName = self.__getTitle(
                    edfReader.getframe(int(sino.index)).getHeader())

                sino.data = self.__getMeanData(edfReader=edfReader,
                                               groupFiles=groupFiles,
                                               indexDataToTreat=sino.index,
                                               referenceName=refName)
            self._addFluoARTAlgorithm(sino)

    def __treatAsAStandardFile(self, sinogram):
        """
        create all the algorithm at the standard way
        """
        assert(isinstance(sinogram, structs.FluoSino))
        self._sinoElemt[sinogram.name] = sinogram.physElmt
        self._addFluoARTAlgorithm(sinogram)

    def _updateSelfAbsMat(self, fluoSinogram):
        """

        """
        assert(isinstance(fluoSinogram, structs.FluoSino))
        if self.config.reconsType == config._ReconsConfig.COMPTON_ID:
            # compton case
            assert(self.config.absMat.data is not None)
            return self.config.absMat.data
        else:
            # fluo case
            if fluoSinogram.selfAbsMat is not None:
                # use given self abs mat
                fluoSinogram.selfAbsMat.loadData(self.filePath)
                return fluoSinogram.selfAbsMat.data
            else:
                # create the self abs mat
                if fluoSinogram.EF is None:
                    err = "No EF given. Can't process the fluorescence reconstruction"
                    raise ValueError(err)

                assert(fluoSinogram.EF > 0.0)
                # In the case of the fluorescence
                selfAbsMatrix = np.zeros(self.config.absMat.data.shape, dtype=np.float64)
                sampleComposition = self.config.materials.matComposition.data
                E0 = self.config.E0
                for materialName in self.fisxMaterials:
                    EI = physicalelmts.elementInstance
                    cross_section_EF_mat = EI.getElementMassAttenuationCoefficients(materialName,
                                                                                    [fluoSinogram.EF])
                    cross_section_E0_mat = EI.getElementMassAttenuationCoefficients(materialName,
                                                                                    [E0])
                    # Note : energy is in keV in freeart AND in physx. So no need for conversion

                    condition = np.in1d(sampleComposition.ravel(), materialName[1:]).reshape(selfAbsMatrix.shape)
                    selfAbsMatrix[condition] = self.config.absMat.data[condition] * cross_section_EF_mat['total'][0] / cross_section_E0_mat['total'][0]

                # reduce the sample composition if needed (if sinogram definition
                # is reduced )
                assert(selfAbsMatrix.ndim == 3)
                selfAbsMatrix = self._adaptMatToReduction(selfAbsMatrix)
                if selfAbsMatrix.shape[1] != self._getTheoreticalSampSize():
                    s1 = selfAbsMatrix.shape[1]
                    s2 = self._getTheoreticalSampSize()
                    err = 'The self absorption matrix for (%s, %s) has invalid dimensions (%s).' \
                          'When in theory it should be (%s, %s).' % (s1, s1, s2, s2)
                    raise ValueError(err)

                assert(self.config.absMat.data.shape == selfAbsMatrix.shape)
                fluoSinogram.selfAbsMat = structs.SelfAbsMatrix(data=selfAbsMatrix)
                return selfAbsMatrix

    def _addFluoARTAlgorithm(self, fluoSinogram):
        """
        Add an ART algorithm to the set of algorithm

        :param fluoSinogram: the sinogram for which we want to build an ART
                             algorithm
        """
        assert(isinstance(fluoSinogram, structs.FluoSino))
        assert(fluoSinogram.data is not None)
        _logger.info('create the algorithm for ' + fluoSinogram.physElmt)

        selection = self.config.projections
        self.angles = self._getAngles(nbAngles=fluoSinogram.data.shape[0],
                                      selection=selection)

        fluoSinogram.data = self.adaptSinogramData(fluoSinogram.data,
                                                   isI0=False)

        # Do not do this, already managed in the freeart core process
        # if self.angles[0] != 0.0:
        #     # rotate the detector position from the origon of a certain angle
        #     self.detPos = tuple(freeart.utils.computeDetectorPosition(
        #         detPos=self.detPos,
        #         angle=self.angles[0]))
        #     self.detSetup = [(self.detPos, self.detWidth)]
        #
        #     info = 'Updating detector position for the first projection.'
        #     info += 'New position is %s' % str(self.detPos)
        #     _logger.info(info)

        # for now in compton Mode
        if not fluoSinogram.data.shape[2] == self.config.absMat.data.shape[1]:
            error = "can't run the reconstruction, width of the sinogram (%s)" \
                    "and the absorption matrix dim (%s) are differente" \
                     % (fluoSinogram.data.shape[2], self.config.absMat.data.shape[1])
            raise ValueError(error)

        selfAbsMatrix = self._updateSelfAbsMat(fluoSinogram)
        selfAbsMatrix = self._adaptMatToReduction(selfAbsMatrix)
        self.config.absMat.data = self.__checkAbsMatDim(self.config.absMat.data)
        selfAbsMatrix = self.__checkAbsMatDim(selfAbsMatrix)

        if not self.config.absMat.data.shape == selfAbsMatrix.shape:
            error = "can't run the reconstruction, shapes of the absorption " \
                    "matrix (%s )" % str(self.config.absMat.data.shape)
            error += "and shape of the self absorption matrix are not fitting" \
                     " (%s )" % str(selfAbsMatrix.shape)
            _logger.error(error)
            raise ValueError(error)

        # creating the ART algorithm
        detector = self.config.detector
        detSetup = [(detector.getPosition(), detector.width)]
        alRecons = freeart.FluoBckProjection(sinoDat=fluoSinogram.data.astype(self.precisionType),
                                             sinoAngles=self.angles,
                                             expSetUp=detSetup,
                                             absorp=self.config.absMat.data.astype(self.precisionType),
                                             selfAbsorp=selfAbsMatrix.astype(self.precisionType))

        if self.config.voxelSize:
            alRecons.setVoxelSize(self.config.voxelSize * self.config.definitionReduction)

        if self.config.oversampling:
            alRecons.setOverSampling(self.config.oversampling)

        if self.config.useAFileForI0 is False:
            alRecons.setI0(self.config.I0)

        if self.config.beamCalcMethod:
            alRecons.setRayPointCalculationMethod(self.config.beamCalcMethod)

        if self.config.outBeamCalMethod:
            alRecons.setOutgoingRayAlgorithm(self.config.outBeamCalMethod)

        if self.config.solidAngleOff:
            alRecons.turnOffSolidAngle(self.config.solidAngleOff)

        if self.config.dampingFactor:
            alRecons.setDampingFactor(self.config.dampingFactor)

        self.fluoSinogramsAlgorithms[fluoSinogram.name] = alRecons
        self.fluoSinograms[fluoSinogram.name] = fluoSinogram

        # create the interaction matrice
        self.interactionMatrice[fluoSinogram.physElmt] = self.__computeInteractionMatrice(fluoSinogram.physElmt)

    def __checkAbsMatDim(self, mat):
        if mat.ndim != 3:
            assert(mat.ndim is 2)
            mat = mat.reshape(mat.shape[0], mat.shape[1], 1)

        return mat

    def __computeInteractionMatrice(self, name):
        """Return the interaction matrice according to the materials in the
        sample and the element

        :param name: the id of the element for which we want to compute the
        interaction matrix
        """
        if self.config.reconsType == 'Compton':
            interactionMatrice = np.ones((self.config.absMat.data.shape[0],
                                          self.config.absMat.data.shape[1]),
                                          dtype=np.float64)
        else:
            interactionMatrice = np.zeros((self.config.absMat.data.shape[0],
                                           self.config.absMat.data.shape[1]),
                                          dtype=np.float64)
            materialsDict = self.config.materials.materials.data
            if materialsDict is not None:
                sampleComposition = self.config.materials.matComposition.data

                for materialName in materialsDict:
                    uniqMatName = reconstrutils.getFisxMatName(materialName)
                    probabilityOfEmission = FluoConfInterpreter.getProbabilityOfEmission(
                                                fisxMat=self.fisxMaterials[uniqMatName],
                                                energy=self.config.E0,
                                                element=name,
                                                fisxElements=physicalelmts.elementInstance,
                                                shell=None)
                    condition = np.in1d(sampleComposition.ravel(),
                                        materialName).reshape(interactionMatrice.shape)
                    interactionMatrice[condition] = probabilityOfEmission

            interactionMatrice.shape = (interactionMatrice.shape[0],
                                        interactionMatrice.shape[1],
                                        1)

        return interactionMatrice

    def getReconstructionAlgorithms(self):
        """
        :return: all the algorithm created for reconstructions
        """
        return self.fluoSinogramsAlgorithms

    def iterate(self, nbIteration):
        """
        Iterate on the reconstruction. Each iteration generate a backward
        projection for each angle of acquisition (in a random order).
        """
        threads = []
        nbVoxel = 0

        for index, sinogram in enumerate(self.config.sinograms):
            if index % self.limitParaRecon == 0 or (nbVoxel > self.limitVoxel):
                [thread.start() for thread in threads]
                [thread.join() for thread in threads]
                threads = []

            assert(not self.fluoSinogramsAlgorithms[sinogram.name] is None)
            threads.append(Thread(target=self.fluoSinogramsAlgorithms[sinogram.name].iterate,
                                  args=(nbIteration,)))
            nbVoxel = self.fluoSinograms[sinogram.name].data.shape[1] * self.fluoSinograms[sinogram.name].data.shape[1]

        [thread.start() for thread in threads]
        [thread.join() for thread in threads]

    def setRandSeedToZero(self, b):
        for sinogramName in self.fluoSinogramsAlgorithms:
            assert(self.fluoSinogramsAlgorithms[sinogramName] is not None)
            self.fluoSinogramsAlgorithms[sinogramName].setRandSeedToZero(b)

    def getDensityPhantoms(self):
        """
        Return the phantom taking into account the probability of generation
        of the physical element
        """
        res = {}
        for element in self.fluoSinogramsAlgorithms:
            ph = np.zeros(self.interactionMatrice[element].shape)
            if self.interactionMatrice[element] is not None:
                probInter = self.fluoSinogramsAlgorithms[element].getPhantom()[self.interactionMatrice[element] > 0.0] / \
                                                            self.interactionMatrice[element][self.interactionMatrice[element] > 0.0]
                ph[self.interactionMatrice[element] > 0.0] = probInter
            res[element] = ph

        return res

    def getInteractionPhantoms(self):
        return self.interactionMatrice
