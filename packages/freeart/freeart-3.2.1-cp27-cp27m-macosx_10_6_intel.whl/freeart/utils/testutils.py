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

..warning :: those example have been created before the existance of the
             :class: Txconfig and :class: configuration.config.FluoConfig
             classes.
             Due to lake of time I couldn't rewrote them but they are certainly
             not an easy access to understand the configuration and how a
             reconstruction is created even if the name migh tlet understand
             differently.
             If you have a configuration to write you better look at the
             configuration.config module.
"""
__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "01/09/2016"


import os
import tempfile

import fabio
import numpy as np
from silx.io import configdict
import freeart
from freeart.configuration import iniConfigIO, config, structs, fileInfo
from freeart.interpreter import configinterpreter
from freeart.unitsystem import metricsystem
from freeart.utils import getDistance, getDistance_2D, getAngle
from freeart.utils import physicalelmts, genph, reconstrutils, raypointsmethod, \
    outgoingrayalgorithm
from freeart.utils import h5utils
from silx.io import configdict
from collections import OrderedDict
import silx
if silx._version.MINOR < 7:
    from freeart.utils import dictdump_0_7 as dictdump
else:
    from silx.io import dictdump

def toExperimentationRef(pt, phDimx, phDimy, phDimz):
    """
    Transform the point pt to the FreeART reference for the according giving
    phantom dimesions

    ..Note:: For freeART the center of the universe is the medium voxel
    """
    return (pt[0]-phDimx//2, pt[1]-phDimy//2, pt[2]-phDimz//2)


def getAngleBetweenVec_DetectorVoxel_Vec_x(detPos, voxPos):
    """
    Return the angle made between the vector detPosVoxPos and the X vector.
    Which can be see as the vector of each voxel. And be used to know the
    angle of incidence of a ray with the voxel.
    """
    vectorX = (1.0, 0.0, 0.0)
    vectorDetVox = (detPos[0] - voxPos[0], detPos[1] - voxPos[1], detPos[2] - voxPos[2])
    return getAngle(vectorX, vectorDetVox)


def getSinAngleDetectorVoxel(detPos, voxPos):
    """Return the sinus of the angle between detPos and voxPos"""
    return np.sin(getAngleBetweenVec_DetectorVoxel_Vec_x(detPos, voxPos))


def getSolidAngle(voxelPosInFreeARTRef, detPos, detectorRadius):
    """
    Compute detector efficiency according to detector position and voxel
    position
    """
    distDetectorPoint = getDistance(voxelPosInFreeARTRef, detPos)
    # get the angle between the vectors (detcent, origin) and (voxelpos, origin)
    cosAlpha = distDetectorPoint / np.sqrt(distDetectorPoint*distDetectorPoint + detectorRadius*detectorRadius)
    return 0.5*(1-cosAlpha)


def getRawSumTheoreticalFluoValue(detPos, detectorRadius, voxelPosInFreeARTRef,
                                  mu_E0, mu_EF, psiIncoming, psiOutgoing,
                                  widths, I0=1.0):

    signalSum = 0
    for lWidth in widths:
        signalSum += getRawTheoreticalFluoValue(detPos=detPos,
                                                detectorRadius=detectorRadius,
                                                voxelPosInFreeARTRef=voxelPosInFreeARTRef,
                                                mu_E0=mu_E0,
                                                mu_EF=mu_EF,
                                                psiIncoming=psiIncoming,
                                                psiOutgoing=psiOutgoing,
                                                material_width=lWidth+1.0,
                                                I0=I0)

    return signalSum


def getRawTheoreticalFluoValue(detPos, detectorRadius, voxelPosInFreeARTRef,
                               mu_E0, mu_EF, psiIncoming, psiOutgoing,
                               material_width, I0=1.0):

    detectorEfficiency = getSolidAngle(voxelPosInFreeARTRef,
                                       detPos,
                                       detectorRadius)

    sinPsiIncoming = np.sin(psiIncoming)
    sinPsiOutgoing = np.sin(psiOutgoing)

    incomingBeamAttenuation = np.exp(-mu_E0*material_width / sinPsiIncoming)
    outgoingBeamAttenuation = np.exp(-mu_EF*material_width / sinPsiOutgoing)
    return I0 * incomingBeamAttenuation * outgoingBeamAttenuation * detectorEfficiency


def getFluoTheoreticalValue(detPos, detectorRadius, voxelPosInFreeARTRef,
                            mu_E0, mu_EF, psiIncoming, psiOutgoing, tau_E0,
                            distInMat, I0=1.0, Ci=1.0, Wis=1.0, Ris_EF=1.0):
    """
    Return the theoretical I value for a voxel according to fluorescence theory
    The intensity get for the Energy EF
    We are looking for fluoresence photon emitted by the element i
    This work for a beam and an homogeneous material.

    :param detPos : The position of the detector
    :param voxelPosInFreeARTRef : the position of the computed voxel in the
                                  freeart Reference
    :param mu_E0: the mass attenuation of the incoming beam at energy E0
    :param mu_EF: the mass attenuation of the outgoing beam at energy EF
    :param psiIncoming: the angle of entry of the incoming beam in the material
    :param psiOutgoing: the conjuge of the angle between the incoming beam and
                        the voxel-detector vector
    :param tau_E0: Probability to create a vacancy
    :param I0 : Intensity of the incoming beam
    :param Ci : mass fraction of the element i
    :param Wis: probqbility for beeing in the atomic shell s ?
    :param Ris_EF : Probability of generating an element i ?
    """

    detectorEfficiency = getSolidAngle(voxelPosInFreeARTRef,
                                       detPos,
                                       detectorRadius)

    # Compute the theoretical value
    proba_emitting_photon_element_i = Ci*Wis*Ris_EF

    # if no absorption
    if (mu_E0 == 0) and (mu_EF == 0):
        return proba_emitting_photon_element_i*detectorEfficiency

    sinPsiIncoming = np.sin(psiIncoming)
    sinPsiOutgoing = np.sin(psiOutgoing)

    Fact_1 = tau_E0 / (mu_E0 + mu_EF*sinPsiIncoming/sinPsiOutgoing)
    expCalculation = -(mu_E0/sinPsiIncoming + mu_EF/sinPsiOutgoing) * distInMat
    return I0 * proba_emitting_photon_element_i * Fact_1 * (1.0 - np.exp(expCalculation)) * detectorEfficiency


def getFluoTheoreticalValueForTransmission(detPos, detectorRadius,
                                           voxelPosInFreeARTRef, mu_E0, mu_EF,
                                           psiIncoming, psiOutgoing, tau_E0,
                                           distInMat, I0=1.0, Ci=1.0, Wis=1.0,
                                           Ris_EF=1.0):
    """
    Return the theoretical I value for a voxel according to fluorescence theory

    ..Warning:: : we made the assumption that rays are parallel.
    We are looking for fluoresence photon emitted by the element i
    This work for a beam and an homogeneous material.

    :param detPos : The position of the detector
    :param voxelPosInFreeARTRef : the position of the computed voxel in the
                                  freeart reference
    :param mu_E0: the mass attenuation of the incoming beam at energy E0
    :param mu_EF: the mass attenuation of the outgoing beam at energy EF
    :param psiIncoming: the angle of entry of the incoming beam in the material
    :param psiOutgoing: the conjuge of the angle between the incoming beam and
                        the voxel-detector vector
    :param tau_E0: Probability to create a vacancy
    :param I0 : Intensity of the incoming beam
    :param Ci : mass fraction of the element i
    :param Wis: probability for beeing in the atomic shell s ?
    :param Ris_EF : Probability of generating an element i ?
    """

    detectorEfficiency = getSolidAngle(voxelPosInFreeARTRef, detPos, detectorRadius)

    proba_emitting_photon_element_i = Ci*Wis*Ris_EF

    sinPsiIncoming = np.sin(psiIncoming)
    sinPsiOutgoing = np.sin(psiOutgoing)

    Fact_1 = tau_E0 / (mu_E0 - mu_EF*sinPsiIncoming/sinPsiOutgoing)
    expCalculationE = -(mu_E0/sinPsiIncoming) * distInMat
    expCalculationF = -(mu_EF/sinPsiOutgoing) * distInMat

    return I0 * proba_emitting_photon_element_i * Fact_1 * \
           (np.exp(expCalculationF) - np.exp(expCalculationE)) * detectorEfficiency


def removeAvoidVoxel(phantom, replacementValue=0.0):
    """
    Set all voxel which aren't in the higher circle contained by the phantom to
    zero.
    This function can be used to ignore voxel which were not in the area
    treated by the freeART reconstruction algorithm.
    """
    circleCenter = (phantom.shape[0]//2, phantom.shape[1]//2)
    circleRadius = min(phantom.shape[0], phantom.shape[1])//2
    for z in np.arange(0, phantom.shape[2], 1):
        for x in np.arange(0, phantom.shape[0], 1):
            for y in np.arange(0, phantom.shape[1], 1):
                if getDistance_2D(circleCenter, (x, y)) > circleRadius:
                    phantom[x, y, z] = replacementValue

    return phantom


class SheppLoganReconstruction():
    """
    Test of the generation of a sinogram and of the reconstruction of it
    """
    methodGBeams = raypointsmethod.withInterpolation

    optionOutgoing = outgoingrayalgorithm.createOneRayPerSamplePoint

    def produce_SheppLogan_sinogram(self, dim, _oversampling, _anglesNb,
                                    _detSetup,
                                    _voxelSize=1.0*metricsystem.centimeter):
        """
        Example of the generation of a simple 2D sinogram.
        :param _oversampling: the number of oversampling number we want o take
                              per mm covered by the ray
        :param _anglesNb: the number of angle we want to make an acquisition
                          for.
        """
        # generate the phantom
        phGenerator = genph.PhantomGenerator()
        sheppLogan_phantom = phGenerator.get2DPhantomSheppLogan(dim)
        sheppLogan_phantom.shape = (sheppLogan_phantom.shape[0],
                                    sheppLogan_phantom.shape[1],
                                    1)

        # generate absMat and selfAnsMat
        absMat = sheppLogan_phantom * 20.0
        selfAbsMat = sheppLogan_phantom / 10.0

        # run the sinogram generation
        sinogram, angles = reconstrutils.makeFreeARTFluoSinogram(
            sheppLogan_phantom,
            absMat,
            selfAbsMat,
            _anglesNb,
            _detSetup,
            _oversampling,
            self.methodGBeams,
            self.optionOutgoing,
            voxelSize=_voxelSize)

        return sinogram, angles, absMat, selfAbsMat, sheppLogan_phantom

    def make_reconstruction(self, _sinogram, _angles, _absMat, _selfAbsMat,
                            _detSetup, _nbIter, _oversampling,
                            _voxelSize=1.0*metricsystem.cm,
                            _dampingFactor=0.005, _turnOffSolidAngle=False):
        """
        Example of the reconstruction from a sinogram and related data.

        :param _sinogram: the sinogram to use for the reconstruction
        :param _angles: the angles of acquisition registred on the sinogram
        :param _nbIter: the number of iteration to execute for the
                       reconstruction
        """

        alRecons = freeart.FluoBckProjection(sinoDat=_sinogram,
                                             sinoAngles=_angles,
                                             expSetUp=_detSetup,
                                             absorp=_absMat,
                                             selfAbsorp=_selfAbsMat)

        alRecons.setOverSampling(_oversampling)
        alRecons.setDampingFactor(_dampingFactor)
        alRecons.setRayPointCalculationMethod(self.methodGBeams)
        alRecons.setOutgoingRayAlgorithm(self.optionOutgoing)
        # alRecons.setRandSeedToZero(True)
        alRecons.setVoxelSize(_voxelSize)
        alRecons.turnOffSolidAngle(_turnOffSolidAngle)

        return alRecons.iterate(_nbIter)


class FluorescenceExperimentationExample(object):
    """
    A simple fluorescence experimentation example

    :param buildFromSinogram: if True then we will build the absorption matrix
                              from a sinogram
    :param elements: the list of element for which we want to generate a
                     sinogram
    :param materials: The list of the materials to consider
    :param sheppLoganPartIDs: Dictionnary that for each material attribute an
                              area of the shepplogan
    :param densities: For each material the density of the material.
                      Should be between 0 and 1
    :param oversampling: the oversampling per step to run
    :param dampingFactor: the relaxation factor to apply
    :param nbAngles: the number of projection
    :param buildFromSinogram: if True then we will set the sinogram file in
                              the config file
    :param E0:
    :param EF:
    :param matrixWidth:
    :param minAngle: the angle of the last projection.
    :param maxAngle: the angle of the last projection.
    :param firstProjection: the index of the first projection to include for
                            the reconstruction.
    :param lastProjection: the index of the last projection to include for the
                           reconsutruction.
    :param setProbaEmissionToOne: if True, skip the call to fisx to compute the
                                  probaility of emission
    """
    voxelSize = 1.0 * metricsystem.cm
    detectorRadius = 1.0 * metricsystem.cm
    det = structs.Detector(x=0., y=1000.0 * metricsystem.cm, z=0.,
                           width=1.0 * metricsystem.cm)
    detPos = (0.0, 1000.0*metricsystem.cm, 0.0)
    detSetup = [(detPos, detectorRadius)]

    def __init__(self, elements, materials, sheppLoganPartIDs, densities,
                 oversampling, dampingFactor, EF, nbAngles=360,
                 buildFromSinogram=False, E0=1.0e6, matrixWidth=56,
                 minAngle=0.0, maxAngle=2.0*np.pi, firstProjection=0,
                 lastProjection=None, includeLastProjection=False,
                 setProbaEmissionToOne=False, turnOffSolidAngle=False):

        # check given densitites and interaction probabilities
        for mat in materials:
            if mat not in densities:
                err = 'Density is not given for %s' % mat
                raise ValueError(err)
            if densities[mat] < 0 or densities[mat] > 1:
                err = 'Density for %s is not in [0, 1], non sense' % mat
                raise ValueError(err)

        self.materials = materials
        self.elements = elements
        self.densities = densities
        self.E0 = E0
        self.EF = EF
        self._buildFromSinogram = buildFromSinogram
        self.minAngle = minAngle
        self.maxAngle = maxAngle
        self.firstProjection = firstProjection
        self.lastProjection = lastProjection
        self.includeLastProjection = includeLastProjection
        self.setProbaEmissionToOne = setProbaEmissionToOne

        self.sheppLoganPartIDs = sheppLoganPartIDs

        self.selfAbsorptionMatrices = {}
        self.sinos = {}
        self.phantoms = {}
        self.oversampling = oversampling
        self.dampingFactor = dampingFactor
        self.nbAngles = nbAngles
        self.matWidth = matrixWidth
        self.turnOffSolidAngle = turnOffSolidAngle

    def setUp(self):
        """
        Main function of the setUp
        """
        self.tempdir = tempfile.mkdtemp()
        self.setUpMaterialsIntoFisx()
        self.setUpElementsMatrice()
        self.setUpDensityMatrice()
        self.setUpAbsMat()
        self.setUpInteractionMatrice(self.setProbaEmissionToOne)
        self.setUpSelfAbs()
        sinosFilesInfo = self.setUpFluorescenceSinograms()
        conf = self.setUpConfigFile(sinosFilesInfo)
        self.writeConfigFile(conf)
        self.outputdir = tempfile.mkdtemp()

    def setUpMaterialsIntoFisx(self):
        """Register all needed material into fisx"""
        import fisx
        from fisx import Elements
        self.fisxElements = Elements()
        self.fisxMaterials = {}

        for material in self.materials:
            mat = fisx.Material(material,
                                self.materials[material]['Density'], self.materials[material]['Thickness'])
            mat.setComposition(
                dict(zip(self.materials[material]['CompoundList'], self.materials[material]['CompoundFraction'])))
            self.fisxElements.addMaterial(mat)
            self.fisxMaterials[material] = mat

    def setUpElementsMatrice(self):
        """
        Create the matrice for the sample that set for each voxel the material

        ..Note:: a voxel can contain only one material
        """
        phGenerator = genph.PhantomGenerator()
        self.matOfPhysElmts = np.ndarray(shape=(self.matWidth, self.matWidth),
                                         dtype='S10')
        # basic behavior : a voxel is limited to one material
        for materialName in self.materials:
            partMaterial = phGenerator.get2DPhantomSheppLogan(self.matWidth,
                                                              self.sheppLoganPartIDs[materialName])
            self.matOfPhysElmts[partMaterial != 0.0] = materialName

    def setUpDensityMatrice(self):
        """
        Create the density matrix (material densities)
        """
        self.densityMat = np.zeros(shape=(self.matWidth, self.matWidth), dtype='float64')
        # basic behavior : a voxel is limited to one material
        for materialName in self.materials:
            condition = np.in1d(self.matOfPhysElmts.ravel(), materialName).reshape(self.matOfPhysElmts.shape)
            self.densityMat[condition] = self.densities[materialName]

        self.densityMat.shape = (self.densityMat.shape[0],
                                 self.densityMat.shape[1],
                                 1)

    def setUpAbsMat(self):
        """
        Generate the absorption matrix (absorption of the incoming beams)
        """
        self.absorption_matrix_file = os.path.join(self.tempdir,
                                                   "absorption_matrix.edf")
        self.absorption_matrix_value = np.zeros(shape=(self.matWidth, self.matWidth),
                                                dtype=np.float64)
        self.absMat = structs.AbsMatrix(data=self.absorption_matrix_value,
                                        fileInfo=fileInfo.EDFMatrixFileInfo(self.absorption_matrix_file))

        physicalelmts.elementInstance.removeMaterials()

        for materialName in self.materials:
            physicalelmts.elementInstance.addMaterial(reconstrutils.convertToFisxMaterial(materialName,
                                                                                          self.materials[materialName]))

            absValue = physicalelmts.elementInstance.getElementMassAttenuationCoefficients(materialName,
                                                                                           self.E0)
            condition = np.in1d(self.matOfPhysElmts.ravel(), materialName).reshape(self.absorption_matrix_value.shape)
            self.absorption_matrix_value[condition] = absValue['total']

        if self._buildFromSinogram:
            self.absorption_matrix_value.shape = (self.absorption_matrix_value.shape[0],
                                                  self.absorption_matrix_value.shape[1],
                                                  1)
            al = freeart.TxFwdProjection(self.absorption_matrix_value,
                                         minAngle=self.minAngle,
                                         maxAngle=self.maxAngle,
                                         anglesNb=self.nbAngles)
            al.setOverSampling(5)
            sinogram, angles = al.makeSinogram()
            sinogram.shape = (sinogram.shape[1], sinogram.shape[2])
            reconstrutils.saveSinogram(sinogram, self.absorption_matrix_file)
            self.sinogramTx = sinogram
        else:
            reconstrutils.saveMatrix(self.absorption_matrix_value,
                                     self.absorption_matrix_file)
            self.absorption_matrix_value.shape = (self.absorption_matrix_value.shape[0],
                                                  self.absorption_matrix_value.shape[1],
                                                  1)

    def setUpInteractionMatrice(self, setProbaEmissionToOne):
        """
        This will compute the interaction matrice.
        This is for each voxel the probability of emission of the element for
        the material multiply by the density of the material

        .. Note: density of the each material is suppossed homogeneous in the
                 sample.

        :param setProbaEmissionToOne: if True, skip the call to fisx to compute
                                      the probaility of emission
        """
        self.interaction_matrix_file = {}
        self.interaction_matrix_value = {}
        for element in self.elements:
            fName = "interaction_matrix_" + element + ".edf"
            self.interaction_matrix_file[element] = os.path.join(self.tempdir, fName)
            self.interaction_matrix_value[element] = np.zeros(shape=(self.matWidth, self.matWidth),
                                                              dtype=np.float64)

            for materialName in self.materials:
                if setProbaEmissionToOne is False:
                    probabilityOfEmission = configinterpreter.FluoConfInterpreter.getProbabilityOfEmission(fisxMat=self.fisxMaterials[materialName],
                                                                                                           energy=self.E0,
                                                                                                           element=element,
                                                                                                           fisxElements=self.fisxElements,
                                                                                                           shell=None)
                else:
                    probabilityOfEmission = 1.0

                condition = np.in1d(self.matOfPhysElmts.ravel(), materialName).reshape(self.interaction_matrix_value[element].shape)
                self.interaction_matrix_value[element][condition] = probabilityOfEmission

            reconstrutils.saveMatrix(self.interaction_matrix_value[element],
                                     self.interaction_matrix_file[element])

            s0 = self.interaction_matrix_value[element].shape[0]
            s1 = self.interaction_matrix_value[element].shape[1]
            self.interaction_matrix_value[element].shape = (s0, s1, 1)

    def setUpFluorescenceSinograms(self):
        """
        Produce fluorescence sinograms
        """
        def buildElementSelfAbsMat(element):
            selfAbsMat = np.zeros(shape=(self.matWidth, self.matWidth),
                                  dtype=np.float64)
            for materialName in self.materials:
                condition = np.in1d(self.matOfPhysElmts.ravel(), materialName).reshape(selfAbsMat.shape)
                selfAbsMat[condition] = physicalelmts.elementInstance.getElementMassAttenuationCoefficients(
                    materialName, self.EF[element])['total'][0]

            selfAbsMat.shape = (selfAbsMat.shape[0], selfAbsMat.shape[1], 1)

            return selfAbsMat

        self.sinogramsdir = tempfile.mkdtemp()
        self.sino_file = os.path.join(self.sinogramsdir, "sinograms_fluo.edf")

        for element in self.elements:
            ph_value = self.interaction_matrix_value[element]*self.densityMat
            selfAbsMat = buildElementSelfAbsMat(element)

            sino_value = reconstrutils.makeFreeARTFluoSinogram(ph_value,
                                                               self.absorption_matrix_value,
                                                               selfAbsMat,
                                                               minAngle=self.minAngle,
                                                               maxAngle=self.maxAngle,
                                                               numAngle=self.nbAngles,
                                                               detSetup=self.detSetup,
                                                               oversampling=self.oversampling,
                                                               beamCalcMeth=raypointsmethod.withInterpolation,
                                                               outRayPtCalcMeth=outgoingrayalgorithm.rawApproximation,
                                                               turnOffSolidAngle=self.turnOffSolidAngle)[0]

            self.sinos[element] = sino_value
            self.phantoms[element] = ph_value
        edf_writer = None

        i = 0
        for element in self.elements:
            self.sinos[element] = reconstrutils.decreaseMatSize(self.sinos[element])
            if not edf_writer:
                edf_writer = fabio.edfimage.EdfImage(data=self.sinos[element],
                                                     header={"tata": "toto"})
            else:
                edf_writer.appendFrame(self,
                                       data=self.sinos[element],
                                       header={"tata": "toto"})
            i = i + 1

        edf_writer.write(self.sino_file)

        return {self.sino_file: self.sinos}

    def setUpSelfAbs(self):
        """
        Generate the self absorption matrice (matrice of absorption for the
        outgoing beams)
        """
        # save the sample composition
        self.self_absorption_matrix_file = os.path.join(self.tempdir,
                                                        "sample_composition.npy")
        np.save(self.self_absorption_matrix_file, self.matOfPhysElmts)
        # save the materials
        self.materials_file = os.path.join(self.tempdir, "materials_file.ini")
        configDict = configdict.ConfigDict(defaultdict=self.materials)
        configDict.write(self.materials_file)

    def setUpConfigFile(self, sinoFiles):
        """
        Create the .cfg file in order to use the config interpreter
        """
        self.cfg_fluo_file = os.path.join(self.tempdir, "fluo_cfg.cfg")

        conf = config.FluoConfig()
        # general stuff, absMat and interactionMat
        conf.isAbsMatASinogram = self._buildFromSinogram
        conf.absMat = self.absMat
        conf.materials = structs.Materials(
            matComposition=structs.MatComposition(
                fileInfo=fileInfo.MatrixFileInfo(filePath=self.self_absorption_matrix_file)
            ),
            materials=structs.MaterialsDic(
                fileInfo=fileInfo.MatrixFileInfo(filePath=self.materials_file))
        )
        conf.minAngle = self.minAngle
        conf.maxAngle = self.maxAngle
        conf.projections = str(self.firstProjection) + ':' + str(self.lastProjection)
        conf.includeLastProjection = self.includeLastProjection

        # fluo sinograms path and info
        for filePath in sinoFiles:
            iSino = 0
            sinograms = []
            for element in sinoFiles[filePath]:
                conf.addSinogram(structs.FluoSino(
                    name=element,
                    fileInfo=fileInfo.EDFMatrixFileInfo(
                        filePath=filePath,
                        index=iSino),
                    physElmt=element,
                    ef=self.EF[element],
                    selfAbsMat=None,
                ))
                iSino = iSino + 1

        # FreeART params
        conf.voxelSize = self.voxelSize
        conf.oversampling = self.oversampling
        conf.dampingFactor = self.dampingFactor
        conf.detector = self.det
        conf.E0 = self.E0

        return conf

    def writeConfigFile(self, conf):
        # write the cfg file
        writer = iniConfigIO.IniConfigWriter()
        writer.write(self.cfg_fluo_file, conf)

    def tearDown(self):
        self.tearDownConfigFile()
        self.tearDownAbsMat()
        self.tearDownInteractionMatrice()
        self.tearDownFluorescenceSinograms()

    def tearDownConfigFile(self):
        if os.path.isfile(self.cfg_fluo_file):
            os.unlink(self.cfg_fluo_file)

    def tearDownAbsMat(self):
        if os.path.isfile(self.absorption_matrix_file):
            os.unlink(self.absorption_matrix_file)

    def tearDownInteractionMatrice(self):
        for element in self.elements:
            if os.path.isfile(self.interaction_matrix_file[element]):
                os.unlink(self.interaction_matrix_file[element])

    def tearDownFluorescenceSinograms(self):
        if os.path.isfile(self.sino_file):
            os.unlink(self.sino_file)

    def tearDownMaterialFile(self):
        if os.path.isfile(self.materials_file):
            os.unlink(self.materials_file)


class ComptonExperimentationExample(FluorescenceExperimentationExample):
    """
    A simple compton experimentation example
    """
    def __init__(self, elements, materials, sheppLoganPartID, densities,
                 oversampling, dampingFactor, nbAngles=360,
                 buildFromSinogram=False, E0=1.0e6, matrixWidth=56,
                 minAngle=0.0, maxAngle=2.0*np.pi, firstProjection=0,
                 lastProjection=-1, includeLastProjection=False):

        EF = {}
        for element in elements:
            EF[element] = E0

        FluorescenceExperimentationExample.__init__(
            self,
            elements,
            materials,
            sheppLoganPartID,
            densities,
            oversampling,
            dampingFactor,
            buildFromSinogram=buildFromSinogram,
            E0=E0,
            EF=EF,
            matrixWidth=matrixWidth,
            nbAngles=nbAngles,
            minAngle=minAngle,
            maxAngle=maxAngle,
            firstProjection=firstProjection,
            lastProjection=lastProjection,
            includeLastProjection=includeLastProjection)

    def writeConfigFile(self, conf):
        conf.reconsType = config._ReconsConfig.COMPTON_ID
        FluorescenceExperimentationExample.writeConfigFile(self, conf)


def createConfigTx(tempdir, sinoI0=None):
    txSinoFile = os.path.join(tempdir, 'txSino.edf')
    sinoData = np.arange(100).reshape(10, 10) + 1.0
    sino = structs.TxSinogram(data=sinoData,
                              fileInfo=fileInfo.EDFMatrixFileInfo(
                                  filePath=txSinoFile),
                              name='TxSinogram')
    sino.save()
    txConf = config.TxConfig(
        sinograms=(sino,),
        projections='2:6',
        minAngle=0.0,
        maxAngle=1.2,
        dampingFactor=1.,
        I0=sinoI0)

    return txConf


def createConfigFluo(tempdir, addAbsMat=False, addSelfAbsMat=False,
                     selfAbsMat=None, withMaterials=False, fileExtension='.h5',
                     fileExtensionMat='.h5', sinoI0=None):
    NBFluoSino = 5
    outFileFluo = os.path.join(tempdir, 'fluo.h5')

    detector = structs.Detector(x=1, y=2, z=3, width=0.1)
    absMat = None
    if addAbsMat is True:
        fileName = 'AbsmatMatrix.edf'
        sourceFile = os.path.join(tempdir, fileName)
        file_info = fileInfo.EDFMatrixFileInfo(filePath=sourceFile)
        absMat = structs.AbsMatrix(data=np.arange(100).reshape(10, 10) + 1.0,
                                   fileInfo=file_info)
        absMat.save()
    conf = config.FluoConfig(outBeamCalMethod=None,
                             I0=sinoI0,
                             absMat=absMat,
                             isAbsMatASinogram=False,
                             detector=detector,
                             minAngle=0.0,
                             maxAngle=1.2,
                             dampingFactor=1.,
                             centerOfRotation=6.,
                             acquiInverted=True)

    def _addFluoSinograms(fileExtension, addSelfAbsMat=False,
                          selfAbsMat=None):
        def createFileInfo(fileExtension, name, data):
            if fileExtension is None:
                # TODO : try with official one
                # in this case all data are stored in the same .h5 file
                sourceFile = None
                path = "/data/" + name + str(iSino)
                file_info = fileInfo.H5MatrixFileInfo(
                    filePath=outFileFluo + "::" + path)
                sourceFile = outFileFluo

                h5utils.createH5WithDataSet(filePath=sourceFile,
                                            h5path=path,
                                            data=dataSino,
                                            mode='a')

            elif fileExtension in ('.h5', '.hdf5'):
                # generate a new h5 file
                fileName = name + 'File' + str(iSino) + '.h5'
                sourceFile = os.path.join(tempdir, fileName)

                path = "/data/" + name + str(iSino)
                h5utils.createH5WithDataSet(filePath=sourceFile,
                                            h5path=path,
                                            data=dataSino)
                file_info = fileInfo.H5MatrixFileInfo(
                    filePath=sourceFile + "::" + path)
            elif fileExtension.lower() == '.edf':
                fileName = name + 'File' + str(iSino) + '.edf'
                sourceFile = os.path.join(tempdir, fileName)

                file_info = fileInfo.EDFMatrixFileInfo(filePath=sourceFile)
                reconstrutils.saveMatrix(data=dataSino, fileName=sourceFile)
            else:
                raise NotImplementedError('Not managed for other types')

            return file_info, sourceFile

        for iSino in range(NBFluoSino):
            dataSino = np.arange(100).reshape(10, 10)
            selfAbsMat = None

            fileInfoSino, sourceFileSino = createFileInfo(fileExtension,
                                                          'fluoSino',
                                                          dataSino)
            if addSelfAbsMat is True:
                dataSelfAbsMat = dataSino
                fileInfoSAM, sourceFileSAM = createFileInfo(fileExtension,
                                                            'selfAbsMat',
                                                            dataSelfAbsMat)
                selfAbsMat = structs.SelfAbsMatrix(fileInfo=fileInfoSAM,
                                                   data=dataSelfAbsMat)
            sinogram = structs.FluoSino(fileInfo=fileInfoSino,
                                        data=dataSino,
                                        name='Sinogram_' + str(iSino),
                                        physElmt='O',
                                        ef=12.0,
                                        selfAbsMat=selfAbsMat)
            conf.addSinogram(sinogram)

    def _addMaterials(fileExtensionMat, filePath):
        composition = np.ndarray((100, 100), dtype='S10')
        composition[:, :] = ''
        composition[20:25, :] = 'mat1'
        composition[:10, 10:23] = 'mat2'
        materials = {
            'mat1':
                OrderedDict({
                    'CompoundList': ['H', 'O'],
                    'CompoundFraction': [0.42, 0.36],
                    'Density': 1.0,
                    'Thickness': 1.0,
                    'Comment': 'wothout'
                }),
            'mat2':
                OrderedDict({
                    'CompoundList': ['Y', 'O'],
                    'CompoundFraction': [0.42, 0.0],
                    'Density': 0.2,
                    'Thickness': 0.5,
                    'Comment': ''
                }),
        }
        if fileExtensionMat is None:
            # save composition
            h5utils.createH5WithDataSet(filePath=filePath,
                                        h5path=structs.MatComposition.MAT_COMP_DATASET.lstrip(
                                            "::"),
                                        data=composition,
                                        mode='a')

            dictdump.dicttoh5(h5file=filePath,
                              treedict=materials,
                              h5path=structs.MaterialsDic.MATERIALS_DICT.lstrip(
                                  "::"),
                              mode='a')

            file_info_dict = fileInfo.H5MatrixFileInfo(
                filePath + structs.MaterialsDic.MATERIALS_DICT)
            file_info_comp = fileInfo.H5MatrixFileInfo(
                filePath + structs.MatComposition.MAT_COMP_DATASET)
        elif fileExtensionMat == '.h5':
            # Then both materials and materials composition are stored in the same .h5
            h5File = os.path.join(tempdir, 'matCompo.h5')
            path = "/data/matCompositions"
            h5utils.createH5WithDataSet(filePath=h5File,
                                        h5path=path,
                                        data=composition)
            file_info_comp = fileInfo.H5MatrixFileInfo(h5File + "::" + path)

            h5File = os.path.join(tempdir, 'matDict.h5')
            path = '/materials'
            dictdump.dicttoh5(h5file=h5File,
                              treedict=materials,
                              h5path=path)

            file_info_dict = fileInfo.H5MatrixFileInfo(h5File + "::" + path)

        elif fileExtensionMat == '.npy':
            npzFile = os.path.join(tempdir, 'matCompo.npy')
            file_info_comp = fileInfo.MatrixFileInfo(npzFile)
            np.save(npzFile, composition)

            dicFile = os.path.join(tempdir, 'matDict.dict.ini')
            tmp = configdict.ConfigDict(materials)
            tmp.write(dicFile)

            assert os.path.isfile(dicFile)
            p = dictdump.load(dicFile)
            assert (p == tmp)
            file_info_dict = fileInfo.MatrixFileInfo(dicFile)
        else:
            raise ValueError('Extansion not managed')

        conf.materials = structs.Materials(
            materials=structs.MaterialsDic(fileInfo=file_info_dict,
                                           data=materials),
            matComposition=structs.MatComposition(fileInfo=file_info_comp,
                                                  data=composition)
        )

    _addFluoSinograms(fileExtension, addSelfAbsMat, selfAbsMat)
    if withMaterials:
        _addMaterials(fileExtensionMat, outFileFluo)

    return conf