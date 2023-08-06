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
"""A simple example of a fluorescence projection and reconstruction."""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "01/06/2016"

from freeart.utils import reconstrutils, exampleutils as ex
from freeart.unitsystem import metricsystem

if __name__ == "__main__":
    
    detPos = (1000*metricsystem.cm, 0, 0) # 90 degree detector
    detectorRadius = 10*metricsystem.cm
    detSetup = [(detPos, detectorRadius)]
    oversampling = 4

    sino, angles, absMat, selfAbsMat, execTime = ex.produce_fluo_SheppLogan_sinogram(_oversampling=oversampling,
                                                                                     _anglesNb=360,
                                                                                     _detSetup=detSetup,
                                                                                     _width=256 )
    reconstrutils.savePhantom(sino, "sinogram.edf")
    reconstructedPhantom, execTime = ex.make_fluo_reconstruction(_sinogram=sino,
                                                                 _angles=angles,
                                                                 _absMat=absMat,
                                                                 _selfAbsMat=selfAbsMat,
                                                                 _detSetup=detSetup,
                                                                 _nbIter=5,
                                                                 _oversamp=oversampling)

    reconstrutils.savePhantom(reconstructedPhantom, "recons_sheppLogan_64.edf")
