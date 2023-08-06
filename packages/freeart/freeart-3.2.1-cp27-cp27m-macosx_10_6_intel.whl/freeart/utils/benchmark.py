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
"""Benchmark file."""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "05/07/2016"

import freeart
from freeart.utils import reconstrutils, exampleutils, outgoingrayalgorithm, raypointsmethod

from silx.gui.plot import Plot2D
from silx.gui import qt

import sys

savingToPdf = False

def benchmark_tx_projection(oversamplings, widthsToTest, nbAngle):
    """
    Create a graph for benchmarking the transmission forward projector

    :param oversamplings: the list of oversamplings to test
    :param widthsToTest: the list of phantom width to test
    :param nbAngle: the number of projection to test
    """
    times = {}
    for oversamp in oversamplings :
        bid = "oversamp=" + str(oversamp)
        times[bid] = {}
        for width in widthsToTest :
            times[bid][width] = exampleutils.produce_tx_SheppLogan_sinogram(oversamp, nbAngle, width, save=False)[2]
            print("tx forward projection - execution time for oversamp = " + str(oversamp) + ", width = " + str(width) + " toke : " + str(times[bid][width]) + " s")

    if savingToPdf :
        title= "tx_benchmatk_for_forward_projection_on_" + str(nbAngle) + "_angles"
        plot = plot2D(title=title )
        for curve in times:
            plot.addCurve(widthsToTest, times[curve].values(), legend=curve )

        plot.legendsDockWidget.show()
        plot.saveGraph(filename=title + '.png', fileFormat='png')
        plot.hide()

def benchmark_tx_reconstruction(oversamplings, widthsToTest, nbAngle, nbIter):
    """
    Create a graph for benchmarking the transmission reconstructor

    :param oversamplings: the list of oversamplings to test
    :param widthsToTest: the list of phantom width to test
    :param nbAngle: the number of projection to test
    :param nbIter: the number of iteration to test (one iteration launch nbAngle back projection)
    """    
    times = {}
    for oversamp in oversamplings :
        bid = "oversamp=" + str(oversamp)
        times[bid] = {}
        for width in widthsToTest :
            sino, angles, time = exampleutils.produce_tx_SheppLogan_sinogram(_oversampling=oversamp, _anglesNb=nbAngle, width=width, save=False )
            times[bid][width] = exampleutils.make_tx_reconstruction(sino, angles, _nbIter=nbIter)[1]
            print("tx reconstruction - execution time for oversamp = " + str(oversamp) + ", width = " + str(width) + " toke : " + str(times[bid][width]) + " s")

    if savingToPdf :
        title = "tx_benchmatk_for_reconstruction_on_" + str(nbAngle) + "_angles_and_" + str(nbIter) + "_iteration"
        plot = plot2D(title=title )
        for curve in times:
            plot.addCurve(widthsToTest, times[curve].values(), legend=curve )

        plot.legendsDockWidget.show()
        plot.saveGraph(filename=(title + ".png"), fileFormat="png")
        plot.hide()


def benchmark_fluo_projection(oversamplings, widthsToTest, nbAngle, outgoingraypointsmethods):
    """
    Benchmark the fluo projection

    :param oversamplings: the list of oversamplings to test
    :param widthsToTest: the list of phantom width to test
    :param nbAngle: the number of projection to test   
    :param outgoingraypointsmethods: the list of outgoingrayalgorithm to test  
    """
    times = {}
    for oversamp in oversamplings :
        for obmc in outgoingraypointsmethods:
            bid = "method="+ str(obmc) + "_oversamp=" + str(oversamp)
            times[bid] = {}
            for width in widthsToTest :
                times[bid][width] = exampleutils.produce_fluo_SheppLogan_sinogram(oversamp, nbAngle, detSetup, width, save=False)[4]
                print("fluo projection - execution time for " + str(oversamp) + " oversampling, with = " + str(width) + " toke : " + str(times[bid][width]))

    if savingToPdf :
        for obmc in outgoingraypointsmethods:
            title = "fluo_benchmark_for_projection_method_" + str(obmc) + "_on_" + str(nbAngle) + "_angles_and_"
            plot = plot2D(title=title )
            for curve in times:
                plot.addCurve(widthsToTest, times[curve].values(), legend=curve )

            plot.legendsDockWidget.show()
            plot.saveGraph(filename=(title + ".png"), fileFormat="png")
            plot.hide()


def benchmark_fluo_reconstruction(oversamplings, widthsToTest, nbAngle, outgoingraypointsmethods, nbIter):
    """
    benchmark the fluo reconstruction

    :param oversamplings: the list of oversamplings to test
    :param widthsToTest: the list of phantom width to test
    :param nbAngle: the number of projection to test    
    :param outgoingraypointsmethods: the list of outgoingrayalgorithm to test  
    :param nbIter: the number of iteration to test (one iteration launch nbAngle back projection)
    """    
    times = {}
    for oversamp in oversamplings :
        for obmc in outgoingraypointsmethods:
            bid = "method="+ str(obmc) + "_oversamp=" + str(oversamp)
            times[bid] = {}
            for width in widthsToTest :
                sinogram, angles, absMat, selfAbsMat, time = exampleutils.produce_fluo_SheppLogan_sinogram(oversamp, nbAngle, detSetup, width, save=False)
                times[bid][width] = exampleutils.make_fluo_reconstruction(sinogram, angles, absMat, selfAbsMat, detSetup, nbIter, oversamp)[1]
                print("fluo reconstruction - execution time for " + str(oversamp) + " oversampling, with = " + str(width) + 
                    ", method = " + str(obmc) + " toke : " + str(times[bid][width]))

    if savingToPdf :
        for obmc in outgoingraypointsmethods:
            title=("fluo_benchmark_for_reconstruction_method_" + str(obmc) + "_on_" + str(nbAngle) + "_angles_and_" + str(nbIter) + "_iteration")
            plot = plot2D(title=title )
            for curve in times:
                plot.addCurve(widthsToTest, times[curve].values(), legend=curve )

            plot.legendsDockWidget.show()
            plot.saveGraph(filename=(title + ".png"), fileFormat="png")
            plot.hide()

if __name__ == "__main__":
    if ('--saving' or '--s') in sys.argv :
        savingToPdf=True

    # benchmark the transmission
    oversamplings = [1, 2, 4, 8]
    widths = [16, 32, 64, 128, 356, 1024]
    methodsBeamsGeneral = [raypointsmethod.withInterpolation ]
    methodsOutgoing = [ outgoingrayalgorithm.rawApproximation,
                outgoingrayalgorithm.createOneRayPerSamplePoint,
                outgoingrayalgorithm.matriceSubdivision]

    if savingToPdf :
        global app  # QApplication must be global to avoid seg fault on quit
        app = qt.QApplication([])

    # TODO : compute mean error
    benchmark_tx_projection(oversamplings, widths, nbAngle = 100)
    benchmark_tx_reconstruction(oversamplings, widths, nbAngle = 100, nbIter=1)

    detPos = (1000, 0, 0)
    detectorRadius = 10 
    detSetup = [(detPos, detectorRadius)]
    
    benchmark_fluo_projection(oversamplings, widths, 100, methodsOutgoing)
    benchmark_fluo_reconstruction(oversamplings, widths, 100, methodsOutgoing, nbIter=1)

    if savingToPdf : 
        app.exec_()  