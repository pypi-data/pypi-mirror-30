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
__date__ = "01/09/2016"


import os
import tempfile

import numpy

from freeart.configuration import config
from freeart.utils import reconstrutils


def writeGeneralSettings(f, reconsType):
    with open(f, 'a') as myFile:
        myFile.write("[general_settings]\n")
        myFile.write("reconstruction_type = " + config._ReconsConfig.FLUO_ID+ "\n")
        myFile.write("freeart_version = 3.0.0\n")
        myFile.write("precision = double\n")


def writeFluoGeneral(f, absFileIsASino, absFile, sampComposition,
                     materialsFile):
    assert type(absFileIsASino) is bool
    assert type(absFile) is str

    with open(f, 'a') as myFile:
        myFile.write("[data_source_fluo]\n")
        myFile.write("absorption_file_is_a_sinogram = " + str(absFileIsASino) + "\n")
        myFile.write("absorption_file = " + absFile + "\n")
        myFile.write("absorption_file_index = 0\n")
        _sam = sampComposition
        if _sam is None:
            _sam = ''
        myFile.write("samp_composition_file = " + _sam + "\n")
        myFile.write("samp_composition_file_index = 0\n")
        _mat = materialsFile
        if _mat is None:
            _mat = ''
        myFile.write("materials_file = " + _mat + "\n")
        myFile.write('materials_file_index = 0\n')
        myFile.write("\n")


def addSinoFile(f, dim, nToAdd, physElmts, selfAbsPath, tempdir=None):
    """
    Simulate a fluorescence sinogram to reconstruct.
    
    :param f: 
    :param nToAdd: 
    :param physelmt: 
    :return:
    """
    _tempdir = tempdir
    if _tempdir is None:
        _tempdir = tempfile.mkdtemp()

    with open(f, 'a') as myFile:
        for i in range(nToAdd):
            myFile.write("[fluo_sino_file_" + str(i) + "]\n")
            sinoPath = os.path.join(tempdir, 'selfAbsMat_' + str(i) + ".edf")
            reconstrutils.saveMatrix(numpy.random.rand(dim, dim),
                                     sinoPath)
            myFile.write("file_path =  " + sinoPath + "\n")
            myFile.write("data_set_index_0 = 0\n")
            myFile.write("data_name_0 = " + physElmts[i] + "\n")
            myFile.write("data_physical_element_0 = " + physElmts[i] + "\n")
            myFile.write("ef_0 = 1.0\n")
            myFile.write("self_absorption_file_0 = " + selfAbsPath + "\n")
            myFile.write('\n')

    return tempdir


def addNormalization(f, rotCenter, normI0FrmFile, i0, computeMinusLog):
    with open(f, 'a') as myFile:
        myFile.write("[normalization]\n")
        myFile.write("rotation_center = " + str(rotCenter) + "\n")
        myFile.write("normalizei0fromafile = " + str(normI0FrmFile) + "\n")
        myFile.write("i0 = " + str(i0) + "\n")
        myFile.write("computeminuslog = " + str(computeMinusLog) + "\n")
        myFile.write('\n')


def addReconsProperties(f, voxelSize=1.0, oversampling=2, relaxationFactor=1,
                        beamCalMeth=0, outBeamCalc=0, solidAngOff=False,
                        includeLatAng=False, e0=1):
    with open(f, 'a') as myFile:
        myFile.write("[reconstruction_properties]\n")
        myFile.write("voxel_size = " + str(voxelSize) + "\n")
        myFile.write("oversampling = " + str(oversampling) + "\n")
        myFile.write("relaxation_factor = " + str(relaxationFactor) + "\n")
        myFile.write("bean_calculation_method = " + str(beamCalMeth) + "\n")
        myFile.write("outgoing_bean_calculation_method = " + str(outBeamCalc) + "\n")
        myFile.write("solid_angle_is_off = " + str(solidAngOff) + "\n")
        myFile.write("include_last_angle = " + str(includeLatAng) + "\n")
        myFile.write("e0 = " + str(e0) + "\n")
        myFile.write('\n')


def addReductionData(f, definReduc=1, projReduct=1):
    with open(f, 'a') as myFile:
        myFile.write("[reduction_data]\n")
        myFile.write("definition_reducted_by = " + str(definReduc) + "\n")
        myFile.write("projection_number_reducted_by = " + str(projReduct) + "\n")
        myFile.write('\n')


def addProjInfo(f, startProj, endProj, minAngle=0, maxAngle=numpy.pi*2.0, invertAcqui=False):
    with open(f, 'a') as myFile:
        myFile.write("[projection_information]\n")
        myFile.write("min_angle = " + str(minAngle) + "\n")
        myFile.write("max_angle = " + str(maxAngle) + "\n")
        myFile.write("projections_sel = " + str(startProj) + ":" +str(endProj) + "\n")
        myFile.write("acqui_inv = " + str(invertAcqui) + "\n")
        myFile.write('\n')


def addDetectorInfo(f, detWidth, detX, detY, detZ):
    with open(f, 'a') as myFile:
        myFile.write("[detector_setup]\n")
        myFile.write("det_pos_x = " + str(detWidth) + "\n")
        myFile.write("det_pos_y = " + str(detX) + "\n")
        myFile.write("det_pos_z = " + str(detY) + "\n")
        myFile.write("det_width = " + str(detY) + "\n")
        myFile.write('\n')
