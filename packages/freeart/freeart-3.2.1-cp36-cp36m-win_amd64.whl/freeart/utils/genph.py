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
"""Tool to provide Shepp-Logan phantoms."""
__authors__ = ["N. Vigano"]
__license__ = "MIT"
__date__ = "01/09/2014"

import sys
import numpy

class PhantomGenerator(object):
    '''
    Class for generating different Phantoms
    '''
    class Ellipsoid:
        def __init__(self, a, b, c, x0, y0, z0, alpha, mu):
            self.a = a; self.b = b; self.c = c
            self.x0 = x0; self.y0 = y0; self.z0 = z0
            self.alpha = alpha * numpy.pi / 180.0; self.mu = mu
            self.cosAlpha = numpy.cos(self.alpha)
            self.sinAlpha = numpy.sin(self.alpha)
    
    sheppLogan = [
        #         a       b      c       x0     y0      z0     alpha  mu
        Ellipsoid(0.69,   0.92,  0.90,   0.0,   0.0,    0.0,    0.0,  0.10),
        Ellipsoid(0.6624, 0.874, 0.88,   0.0,  -0.02,   0.0,    0.0, -0.08),
        Ellipsoid(0.11,   0.31,  0.21,   0.22, -0.0,    0.0,  -18.0, -0.02),
        Ellipsoid(0.16,   0.41,  0.22,  -0.22,  0.0,   -0.25,  18.0, -0.02),
        Ellipsoid(0.21,   0.25,  0.35,   0.0,   0.35,  -0.25,   0.0,  0.03),
        Ellipsoid(0.046,  0.046, 0.046,  0.0,   0.10,  -0.25,   0.0,  0.01),
        Ellipsoid(0.046,  0.046, 0.02,   0.0,  -0.10,  -0.25,   0.0,  0.01),
        Ellipsoid(0.046,  0.023, 0.02,  -0.08, -0.605, -0.25,   0.0,  0.01),
        Ellipsoid(0.023,  0.023, 0.10,   0.0,  -0.605, -0.25,   0.0,  0.01),
        Ellipsoid(0.023,  0.046, 0.10,   0.06, -0.605, -0.25,   0.0,  0.01)
    ]

    metalPhantom = [
        #         a       b      c       x0       y0      z0     alpha  mu
        Ellipsoid(0.95,   0.95,  0.95,   0.0,     0.0,    0.0,    0.0,  0.02),
        Ellipsoid(0.15,   0.15,  0.15,   0.0,     0.6,    0.0,    0.0,  0.08),
        Ellipsoid(0.10,   0.10,  0.10,   0.4242,  0.4242, 0.0,    0.0,  0.08),
        Ellipsoid(0.05,   0.05,  0.05,   0.6,     0.0,    0.0,    0.0,  0.08),
        Ellipsoid(0.02,   0.02,  0.02,   0.4242, -0.4242, 0.0,    0.0,  0.08),
        Ellipsoid(0.15,   0.15,  0.15,   0.0,    -0.6,    0.0,    0.0,  0.88),
        Ellipsoid(0.10,   0.10,  0.10,  -0.4242, -0.4242, 0.0,    0.0,  0.88),
        Ellipsoid(0.05,   0.05,  0.05,  -0.6,     0.0,    0.0,    0.0,  0.88),
        Ellipsoid(0.02,   0.02,  0.02,  -0.4242,  0.4242, 0.0,    0.0,  0.88)
    ]

    def __init__(self):
        pass

    def get3DPhantomSheppLogan(self, n):
        """
        :param n: The width (and height) of the phantom to generate 
        :return: A numpy array of dimension n*n fit with the sheppLogan phantom
        """
        volume = numpy.ndarray(shape=(n, n, n))
        volume.fill(0.)
        
        count = 0
        for ell in PhantomGenerator.sheppLogan:
            count = count+1
            # print("Ellisse n: %d con mu: %f" % (count, ell.mu))
            squareZ = self._getSquareZ(n, ell)
            squareZ.shape = (1,n)
            for x in range(n):
                sumSquareXandY = self._getSquareXandYsum(n, x, ell)
                sumSquareXandY.shape = (n,1)
                sumSquareXYZ = numpy.add(squareZ, sumSquareXandY)
                indices = sumSquareXYZ <= 1
                volume[x,indices] = ell.mu
        indices = numpy.abs(volume) > 0
        volume[indices] = numpy.multiply(volume[indices] + 0.1, 5)
        return volume

    def get2DPhantomSheppLogan(self, n, ellipsoidID=None):
        """
        :param n: The width (and height) of the phantom to generate 
        :param ellipsoidID: The Id of the ellipsoid to pick. If None will produce all the ellipsoid
        """
        assert(ellipsoidID is None or (ellipsoidID >=0 and ellipsoidID < len(PhantomGenerator.sheppLogan)))
        if ellipsoidID is None :
            area = self._get2DPhantom(n, PhantomGenerator.sheppLogan)
        else :
            area = self._get2DPhantom(n, [PhantomGenerator.sheppLogan[ellipsoidID]])

        indices = numpy.abs(area) > 0
        area[indices] = numpy.multiply(area[indices] + 0.1, 5)
        return area / 100.0

    def get2DPhantomMetal(self, n, ellipsoidID=None):
        """
        :param n: The width (and height) of the phantom to generate 
        :param ellipsoidID: The Id of the ellipsoid to pick. If None will produce all the ellipsoid
        """        
        assert(ellipsoidID is None or (ellipsoidID >=0 and ellipsoidID < len(PhantomGenerator.metalPhantom)))
        if ellipsoidID is None :
            area = self._get2DPhantom(n, PhantomGenerator.metalPhantom)
        else :
            area = self._get2DPhantom(n, [PhantomGenerator.metalPhantom[ellipsoidID]])
        area = numpy.multiply(area, 10)
        return area / 100.0

    def _get2DPhantom(self, n, phantomSpec):
        area = numpy.ndarray(shape=(n, n))
        area.fill(0.)

        count = 0
        for ell in phantomSpec:
            count = count+1
            for x in range(n):
                sumSquareXandY = self._getSquareXandYsum(n, x, ell)
                indices = sumSquareXandY <= 1
                area[indices, x] = ell.mu
        return area

    def _getSquareXandYsum(self, n, x, ell):
        div = lambda x, y: numpy.divide(x, y)
        mul = lambda x, y: numpy.multiply(x, y)
        sub = lambda x, y: numpy.subtract(x, y)
        add = lambda x, y: numpy.add(x, y)
        pow2 = lambda x: numpy.power(x, 2)

        supportX1 = numpy.ndarray(shape=(n, ))
        supportX2 = numpy.ndarray(shape=(n, ))
        support_consts = numpy.ndarray(shape=(n, ))

        xScaled = float(2*x-n)/float(n)
        xCos =  xScaled*ell.cosAlpha
        xSin = -xScaled*ell.sinAlpha
        supportX1.fill(xCos)
        supportX2.fill(xSin)

        supportY1 = numpy.arange(n)
        support_consts.fill(2.)
        supportY1 = mul(support_consts, supportY1)
        support_consts.fill(n)
        supportY1 = sub(supportY1, support_consts)
        support_consts.fill(n)
        supportY1 = div(supportY1, support_consts)
        supportY2 = numpy.array(supportY1)

        support_consts.fill(ell.sinAlpha)
        supportY1 = add(supportX1, mul(supportY1, support_consts))
        support_consts.fill(ell.cosAlpha)
        supportY2 = add(supportX2, mul(supportY2, support_consts))

        support_consts.fill(ell.x0)
        supportY1 = sub(supportY1, support_consts)
        support_consts.fill(ell.y0)
        supportY2 = sub(supportY2, support_consts)

        support_consts.fill(ell.a)
        supportY1 = pow2(div(supportY1, support_consts))
        support_consts.fill(ell.b)
        supportY2 = pow2(div(supportY2, support_consts))

        return add(supportY1, supportY2)

    def _getSquareZ(self, n, ell):
        div = lambda x, y: numpy.divide(x, y)
        mul = lambda x, y: numpy.multiply(x, y)
        sub = lambda x, y: numpy.subtract(x, y)
        pow2 = lambda x: numpy.power(x, 2)

        supportZ1 = numpy.arange(n)
        support_consts = numpy.ndarray(shape=(n, ))
        support_consts.fill(2.)
        supportZ1 = mul(support_consts, supportZ1)
        support_consts.fill(n)
        supportZ1 = sub(supportZ1, support_consts)
        support_consts.fill(n)
        supportZ1 = div(supportZ1, support_consts)

        support_consts.fill(ell.z0)
        supportZ1 = sub(supportZ1, ell.z0)

        support_consts.fill(ell.c)
        return pow2(div(supportZ1, support_consts))

    def print2DPhantomToPlainTxt(self, ph, file="output.txt"):
        f = open(file,"w")
        shp = ph.shape
        f.write("%d\n" % shp[0])
        f.write("%d\n" % shp[1])
        f.write("1\n")
        for y in range(shp[1] - 1,0,-1):
            for x in range(shp[0]):
                f.write("%1.7e " % ph[y,x])
                if (x >= (shp[0]-1)):
                    f.write("\n")
        f.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("genph usage: genph <Phantom file name>")
        sys.exit(-1)

    phgen = PhantomGenerator()
    phantom = phgen.get2DPhantomSheppLogan(256)
    phgen.print2DPhantomToPlainTxt(phantom,sys.argv[1])

