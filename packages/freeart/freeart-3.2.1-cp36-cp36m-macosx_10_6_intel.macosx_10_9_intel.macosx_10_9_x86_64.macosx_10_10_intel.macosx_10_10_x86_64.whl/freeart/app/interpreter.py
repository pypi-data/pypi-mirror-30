#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from freeart.interpreter import GlobalConfigInterpreter
from freeart.utils.reconstrutils import decreaseMatSize
from silx.gui.plot import Plot2D
from silx.gui import qt
import argparse
import logging

_logger = logging.getLogger(__name__)

def getinputinfo():
    return "freeart interpreter [projectfile.cfg] [nbIteration]"


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'configuration_file',
        help='File containing the configuration of the reconstruction')
    parser.add_argument(
        'nb_iteration',
        help='number of iteration to execute on the reconstruction')
    parser.add_argument(
        '--debug',
        dest="debug",
        action="store_true",
        default=False,
        help='Set logging system in debug mode')

    options = parser.parse_args(argv[1:])

    cfgFile = options.configuration_file
    nbIteration = options.nb_iteration

    _logger.info('create the freeart interpreter to run reconstruction')
    interpreter = GlobalConfigInterpreter(filePath=cfgFile)
    _logger.info('start iterations')
    interpreter.iterate(nbIteration)
    _logger.info('iterations finished')

    global app  # QApplication must be global to avoid seg fault on quit
    app = qt.QApplication([])

    for algo in interpreter.getReconstructionAlgorithms():
        reconsPh = interpreter.getReconstructionAlgorithms()[algo].getPhantom()
        plot = Plot2D(parent=None)
        plot.addImage(decreaseMatSize(reconsPh))
        plot.show()

    app.exec_()
    exit(0)

if __name__ == "__main__":
    main(sys.argv)
