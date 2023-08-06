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
"""Python utils for freeart."""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "23/05/2016"

import numpy


def computeDetectorPosition(detPos, angle):
    """
    Rotate the detector position along the origin of the given angle

    :param float angle: the angle of rotation (in rad)
    """
    vectorX = (0.0, 1.0, 0.0)
    detectorDis = numpy.sqrt(detPos[0] * detPos[0] + detPos[1] * detPos[1])
    currentAngle = getAngle(vectorX, detPos)
    rotAngle = currentAngle + angle
    return numpy.array((numpy.sin(rotAngle) * detectorDis,
                        numpy.cos(rotAngle) * detectorDis,
                        detPos[2]))


def getDistance(pt1, pt2):
    """
    Return the distance between two points
    """
    return numpy.sqrt((pt1[0]-pt2[0])*(pt1[0]-pt2[0]) + (pt1[1]-pt2[1])*(pt1[1]-pt2[1]) + (pt1[2]-pt2[2])*(pt1[2]-pt2[2]))


def getDistance_2D(pt1, pt2):
    """"
    Return the distance between two points
    """
    return numpy.sqrt((pt1[0]-pt2[0])*(pt1[0]-pt2[0]) + (pt1[1]-pt2[1])*(pt1[1]-pt2[1]))


def dotproduct(v1, v2):
    """
    Return the dot product of v1 qnd v2
    """
    return sum((a*b) for a, b in zip(v1, v2))


def length(v):
    """
    Return the length of the vector v
    """
    return numpy.sqrt(dotproduct(v, v))


def getAngle(v1, v2):
    """
    Return the angle between v1 and v2
    """
    return numpy.arccos(dotproduct(v1, v2) / (length(v1) * length(v2)))
