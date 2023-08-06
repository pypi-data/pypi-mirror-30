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
"""Simple functions for fluorescence and transmission projections and reconstructions."""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "22/09/2016"

import freeart
from freeart.utils import genph, reconstrutils
import time
import numpy

############  Tx example #################


def produce_tx_SheppLogan_sinogram(_oversampling, _anglesNb, width, save=False):
    """Example of the generation of a simple 2D sinogram.
    parameters :
        - _oversampling : the number of oversampling number we want o take per mm covered by the ray
        - _anglesNb : the number of angle we want to make an acquisition for"""

    phGenerator = genph.PhantomGenerator()
    sheppLogan_phantom = phGenerator.get2DPhantomSheppLogan(n=width)
    if save:
        reconstrutils.savePhantom(sheppLogan_phantom, "ph_sheppLogan_256.edf")

    sheppLogan_phantom.shape = (sheppLogan_phantom.shape[0], sheppLogan_phantom.shape[1], 1)

    start_time = time.time()
    al = freeart.TxFwdProjection(sheppLogan_phantom, minAngle=0,
                                 maxAngle=2.0*numpy.pi, anglesNb=_anglesNb)
    al.setOverSampling(_oversampling)
    sinogram, angles = al.makeSinogram()

    if save:
        reconstrutils.saveSinogram(sinogram, "sino_sheppLogan_256.edf")

    execution_time = time.time() - start_time

    return sinogram, angles, execution_time

def make_tx_reconstruction(_sinogram, _angles, _nbIter, dampingFactor=0.02):
    """Example of the reconstruction from a sinogram and related data.
    parameters :
       - _sinogram : the sinogram to use for the reconstruction
       - _angles : the angles of acquisition registred on the sinogram
       - _nbIter : the number of iteration to execute for the reconstruction"""

    start_time = time.time()
    al = freeart.TxBckProjection(_sinogram, _angles)
    al.setDampingFactor(dampingFactor)

    res = al.iterate(_nbIter)
    execution_time = time.time() - start_time

    return res, execution_time

############  Fluo example #################


def produce_fluo_SheppLogan_sinogram(_oversampling, _anglesNb, _detSetup, _width, save=True):
    """Example of the generation of a simple 2D sinogram.
    parameters :
        - _oversampling : the number of oversampling number we want o take per mm covered by the ray
        - _anglesNb : the number of angle we want to make an acquisition for"""
    #generate the phantom
    phGenerator = genph.PhantomGenerator()
    sheppLogan_phantom = phGenerator.get2DPhantomSheppLogan(_width)
    sheppLogan_phantom.shape = (sheppLogan_phantom.shape[0], sheppLogan_phantom.shape[1], 1)

    start_time = time.time()

    #generate absMat and selfAnsMat
    absMat     = sheppLogan_phantom / 20.0 
    selfAbsMat = sheppLogan_phantom / 20.0 

    # rune the sinogram generation
    sinogram, angles = reconstrutils.makeFreeARTFluoSinogram(
        sheppLogan_phantom, absMat, selfAbsMat, _anglesNb, _detSetup, 10, True, False );

    if save :
        reconstrutils.savePhantom(sheppLogan_phantom, "ph_sheppLogan_64.edf")
        reconstrutils.savePhantom(absMat, "AM_sheppLogan_64.edf")
        reconstrutils.savePhantom(selfAbsMat, "SAM_sheppLogan_64.edf")

    execution_time = time.time() - start_time

    return sinogram, angles, absMat, selfAbsMat, execution_time


def make_fluo_reconstruction(_sinogram, _angles, _absMat, _selfAbsMat, _detSetup, _nbIter, _oversamp, _dampingFactor=0.05):
    """Example of the reconstruction from a sinogram and related data.
    parameters :
       - _sinogram : the sinogram to use for the reconstruction
       - _angles : the angles of acquisition registred on the sinogram
       - _nbIter : the number of iteration to execute for the reconstruction"""
    
    alRecons = freeart.FluoBckProjection(sinoDat=_sinogram,
                                         sinoAngles=_angles,
                                         expSetUp=_detSetup,
                                         absorp=_absMat,
                                         selfAbsorp=_selfAbsMat)

    alRecons.setOverSampling(_oversamp)
    alRecons.setDampingFactor(_dampingFactor)
    
    start_time = time.time()
    res = alRecons.iterate(_nbIter)
    execution_time = time.time() - start_time

    return res, execution_time

