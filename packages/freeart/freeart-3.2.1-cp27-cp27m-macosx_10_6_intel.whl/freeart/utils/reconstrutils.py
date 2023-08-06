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
"""group some functions used for reconstruction """


__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "01/09/2016"


import numpy as np
import os
import freeart
from freeart.unitsystem import metricsystem
from freeart.utils import outgoingrayalgorithm
from fabio.edfimage import edfimage
from fisx import Material
import logging
_logger = logging.getLogger("reconstrutils")


def decreaseMatSize(mat):
    """
    will decrease the matrice size if possible where one dimension has only
    one element
    """
    if(len(mat.shape) == 3):
        if(mat.shape[0] == 1):
            mat.shape = (mat.shape[1], mat.shape[2])
        elif (mat.shape[2] == 1):
            mat.shape = (mat.shape[0], mat.shape[1])

    if(len(mat.shape) == 4):
        if(mat.shape[0] == 1):
            mat.shape = (mat.shape[1], mat.shape[2], mat.shape[3])
        if(mat.shape[3] == 1):
            mat.shape = (mat.shape[0], mat.shape[1], mat.shape[2])

    return mat


def increaseMatSize(mat, firstPos):
    """
    Simple function which will add a dimension to the current matrice

    :param mat: the matrice for which we want to remove a dimension
    :param firstPos: if true remove the first position else remove the last
    """
    if(len(mat.shape) == 2):
        if(firstPos):
            mat.shape = (1, mat.shape[0], mat.shape[1])
        else:
            mat.shape = (mat.shape[0], mat.shape[1], 1)

    return mat


def saveMatrix(data, fileName, overwrite=False):
    """
    will create an edf file to store the given data

    :param data: the data to save
    :param fileName: the localisation to know where to save the data
    """
    savePhantom(data, fileName, overwrite)


def saveSinogram(data, fileName, overwrite=False):
    """
    will create an edf file to store the given data

    :param data: the data to save
    :param fileName: the localisation to know where to save the data
    """
    savePhantom(data, fileName, overwrite)


def savePhantom(data, fileName, overwrite=False):
    """
    will create an edf file to store the given data

    :param data: the data to save
    :param fileName: the localisation to know where to save the data
    """
    if(os.path.isfile(fileName)):
        if overwrite is True:
            _logger.info("overxtriting the file : " + str(fileName))
        else:
            _logger.info("file " + str(fileName) + "already exists")
            return

    phantomToSave = data.copy()
    phantomToSave = decreaseMatSize(phantomToSave)
    edf_writer = edfimage(data=phantomToSave)
    edf_writer.write(fileName)
    edf_writer = None


def LoadEdf_2D(fName, frame=0):
    """
    Load data from the given edf file

    :param fName: the name of the file
    :param frame: if multiple frame file, will use theis parameter to load a
                  specific frame
    """
    edfreader = edfimage()
    edfreader.read(fName)
    if edfreader.nframes == 1:
        return edfreader.getData()
    else:
        return edfreader.getframe(frame).data


def readSinoFile(fname):
    """
    Read the sinogram contained in a simple file (txt)

    :return:
        * sinoData : numpy array of float 64 loaded fron the file
        * sinoAngles: list of angles of acquisition
    """
    ind = 0
    fi = open(fname)
    slicesNb = int(fi.readline())
    anglesNb = int(fi.readline())
    pixelsNb = int(fi.readline())

    angles = fi.readline().split()
    sinoAngles = np.array(angles, dtype=np.float64)

    sinoData = np.zeros((slicesNb, anglesNb, pixelsNb), np.float64)

    for line in fi:
        oneLineDat = line.split()
        sinoData[0, ind, :] = oneLineDat
        ind = ind + 1

    _logger.info("sliceNb =" + slicesNb)
    _logger.info("anglesNb =" + anglesNb)
    _logger.info("pixelsNb =" + pixelsNb)

    return (sinoData, sinoAngles)


def savePhantomToTxt(fname, x, fmt="%1.6e", delimiter=' '):
    saveMatrixToTxt(fname, x, fmt, delimiter)


def saveSinogramToTxt(fname, x, fmt="%1.6e", delimiter=' '):
    assert(len(x.shape) in [2, 3])

    with open(fname, 'w') as fh:
        assert(len(x.shape) == 3)
        assert(x.shape[0] == 1)
        fh.write("%d\n" % x.shape[0])

        fh.write("%d\n" % x.shape[1])
        fh.write("%d\n" % x.shape[2])

        nbrow = len(x)
        currentLine = 0
        for row in x[0]:
            line = ' '
            line = line + delimiter.join(fmt % value for value in row)
            if(currentLine != (nbrow-1)):
                fh.write(line + '\n')
            else:
                # write the last line of the file
                fh.write(line)

            currentLine += 1


def saveMatrixToTxt(fname, x, fmt="%1.6e", delimiter=' '):
    """
    will store the data to a file
    """
    assert(len(x.shape) in [2, 3])

    with open(fname, 'w') as fh:
        fh.write("%d\n" % x.shape[0])
        fh.write("%d\n" % x.shape[1])
        if(len(x.shape) > 2):
            assert(x.shape[2] == 1)
            fh.write("%d\n" % x.shape[2])

        nbrow = len(x)
        currentLine = 0
        for row in x:
            line = ' '
            line = line + delimiter.join(fmt % value for value in row)
            if(currentLine != (nbrow-1)):
                fh.write(line + '\n')
            else:
                # write the last line of the file
                fh.write(line)

            currentLine += 1


def readMatrix2D(fname, fmt="%1.6e", delimiter=' '):
    """
    read a 2D matrix stored on a txt file
    """
    with open(fname) as fi:
        # get the matrice dimension from the header
        x_shape = int(fi.readline())
        y_shape = int(fi.readline())
        z_shape = int(fi.readline())
        assert(z_shape == 1)

        matrice = np.ndarray(shape=(x_shape, y_shape, z_shape))

        # read the matrice and affecte the readed value
        x = 0
        for line in fi:
            values = line.split()
            y = 0
            for val in values:
                matrice[x][y][0] = np.float64(val)
                y = y+1

            x = x+1

        return matrice


def makeFreeARTFluoSinogram(phantom, absMat, selfAbsMat, numAngle, detSetup,
                            oversampling, beamCalcMeth, outRayPtCalcMeth,
                            minAngle=0.0, maxAngle=2.0 * np.pi,
                            subdivisionValue=3, turnOffSolidAngle=False,
                            I0=1.0, voxelSize=1.0*metricsystem.centimeter):
    """
    Generate the fluorescence sinogram

    :param phantom: The initial phantom (density * probability of emission of photon...)
    :param absMat: absorption of the incoming. Aka :math:`{\mu}_{E_0}{\\rho}x`

    :return:
        * sinogram (numpy array of float64 )
        * angles list of angles of projection

    .. warning:: all angle values must be given in rad
    """
    assert(len(phantom.shape) == len(absMat.shape))
    assert(len(phantom.shape) == len(selfAbsMat.shape))
    assert(len(phantom.shape) == 3)
    assert(phantom.shape[2] == 1)
    assert(absMat.shape[2] == 1)
    assert(selfAbsMat.shape[2] == 1)
    # create the sinogram
    al = freeart.FluoFwdProjection(phMatr=phantom,
                                   expSetUp=detSetup,
                                   absorpMatr=absMat,
                                   selfAbsorpMatrix=selfAbsMat,
                                   angleList=None,
                                   minAngle=minAngle,
                                   maxAngle=maxAngle,
                                   anglesNb=numAngle)

    al.setOverSampling(oversampling)
    al.setRayPointCalculationMethod(beamCalcMeth)
    al.setOutgoingRayAlgorithm(outRayPtCalcMeth)
    al.turnOffSolidAngle(turnOffSolidAngle)
    al.setVoxelSize(voxelSize)

    if outRayPtCalcMeth == outgoingrayalgorithm.matriceSubdivision:
        al.setSubdivisionSelfAbsMat(subdivisionValue)
    al.setI0(I0)
    # Make sure we can assure repeatability. This will set the seed to 0
    al.setRandSeedToZero(True)

    sinogram = None
    sinogram, angles = al.makeSinogram()

    return sinogram, angles


def convertToFisxMaterial(materialName, material):
    """
    convert a material defined in a dictionnary (from tomoGUI for example.
    Used to be saved and loaded ) in a fisx Material. Won't do the registration

    :param materialName: the name to attribute to the fisx material
    :param material: the material defined in a dictionary

    :return: the fisx material

    initial material structure looks like :
    materialName = "My_mat"
    material = {'Comment':"No comment",
             'CompoundList':['Cr', 'Fe', 'Ni'],
             'CompoundFraction':[18.37, 69.28, 12.35],
             'Density':1.0,
             'Thickness':1.0}

    Final structure is a fisx Material :
    steel = {"Cr":18.37,
         "Fe":69.28, # calculated by subtracting the sum of all other elements
         "Ni":12.35 }
    material = Material("My_mat", 1.0, 1.0)
    material.setComposition(steel)
    """
    assert('CompoundList' in material)
    assert('CompoundFraction' in material)
    assert('Density' in material)
    assert('Thickness' in material)
    # if we have only one CompoundList
    if type(material['CompoundList']) is str:
        composition = {}
        composition[material['CompoundList']] = material['CompoundFraction']

    else:
        assert(len(material['CompoundList']) == len(material['CompoundFraction']))
        composition = {}
        for iCompound in np.arange(0, len(material['CompoundList'])):
            composition[material['CompoundList'][iCompound]] = material['CompoundFraction'][iCompound]
        if len(composition) is 0:
            raise ValueError('Material with empry composition found. '
                             'Can\'t convert material to fisx')

    material = Material(materialName,
                        material['Density'],
                        material['Thickness'])
    material.setComposition(composition)

    return material


def getFisxMatName(materialName):
    """Small hack to make sure the given material name is not existing yet on
    fisx"""
    return '_' + materialName


def tryToFindPattern(filePath, groupType=None):
    """Basically try to fit with pymca output files

    :param filePath: the file we want to find pattern for.

    :return: the files we can group and the type of group we can process
    """

    # try to fit with pymca files
    if not groupType or groupType == 'pymca':
        pattern = 'ANALYSIS/det'
        if pattern in filePath:
            pymcaFiles = []
            if filePath.count(pattern) > 1:
                mess = """found more than one pattern in the folder path.
                    Can t determine any"""
                _logger.info(mess)
                return

            assert(len(pattern) < len(filePath)+2)
            indexPattern = filePath.find(pattern)
            # get detxx value
            detPatternStart = indexPattern+len(pattern)-3
            detPatternEnd = indexPattern+len(pattern)+2
            currentDet = filePath[detPatternStart: detPatternEnd]
            # try replacing det xx by all possible values
            for iDet in range(100):
                if iDet < 10:
                    detID = 'det0' + str(iDet)
                else:
                    detID = 'det' + str(iDet)

                potentialFileID = filePath.replace(currentDet, detID)
                if os.path.isfile(potentialFileID):
                    pymcaFiles.append(potentialFileID)

            if len(pymcaFiles) > 0:
                return pymcaFiles, 'pymca'

    return [], None
