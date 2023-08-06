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

"""
Outgoing beam calculation method
This define the way the OUTGOING ray values are computed
This apply only for the fluorescence mode

rawApproximation : in this case we are making the evaluation of the outgoing ray the faster as possible
                   by computing for each rotation the mean value of some outgoing rays and taking it as the value
                   of the voxel

createOneRayPerSamplePoint : in this version we are creating the real outgoing ray for each sample point on the incoming ray
                    and computing the 'real' outgoing absorption of the ray by sampling voxels           
matriceSubdivision : this is the raw approximation case but by subdividing the voxels for the outgoing rays
                     we are reducing the noise of the "raw" approximation.
"""

rawApproximation = 0
createOneRayPerSamplePoint = 1
matriceSubdivision = 2

