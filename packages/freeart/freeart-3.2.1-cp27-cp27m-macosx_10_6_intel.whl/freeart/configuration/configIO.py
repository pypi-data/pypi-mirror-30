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

"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "18/10/2017"

import os
from . import structs
from . import config as configmod


class _ConfigIO():
    """Class able to read and write configuration"""
    VALID_FILE_EXTENSIONS = None

    def isAValidFileName(self, filePath):
        fn, file_extension = os.path.splitext(filePath)
        return file_extension in self.VALID_FILE_EXTENSIONS


class ConfigReader(_ConfigIO):
    """Base class of the configuration reader"""
    dictReconsTypeToReconsConf = {
        configmod._ReconsConfig.TX_ID: configmod.TxConfig,
        configmod._ReconsConfig.FLUO_ID: configmod.FluoConfig,
        configmod._ReconsConfig.COMPTON_ID: configmod.FluoConfig
    }
    """Dictionary used to associate a reconstruction type and a configuration
    class"""

    def read(self, filePath):
        """

        :param filePath: path of the file to read
        :return: an instance of configuration. Might be FluoConfiguration or
                 TxConfiguration depending on the file read.
        """
        raise NotImplementedError("Config is an abstract class")

    def _reloadDatasets(self, config, filePath):
        """Load all dataset contained in the configuration"""
        self._loadI0(config, filePath)
        self._loadSinograms(config, filePath)
        if isinstance(config, configmod.FluoConfig):
            self._loadAbsMat(config, filePath)
            self._loadMaterials(config, filePath)
        return config

    def _loadSinograms(self, config, filePath):
        for sinogram in config.sinograms:
            assert(isinstance(sinogram, structs.DataStored))
            sinogram.loadData(filePath)
            if hasattr(sinogram, 'selfAbsMat') and sinogram.selfAbsMat:
                sinogram.selfAbsMat.loadData(filePath)

    def _loadAbsMat(self, config, filePath):
        if config.absMat is not None:
            assert isinstance(config.absMat, structs.AbsMatrix)
            config.absMat.loadData(filePath)

    def _loadMaterials(self, config, filePath):
        if config.materials:
            assert isinstance(config.materials, structs.Materials)
            config.materials.loadData(filePath)

    def _loadI0(self, config, filePath):
        if isinstance(config.I0, structs.DataStored):
            config.I0.loadData(filePath)


class ConfigWriter(_ConfigIO):
    """Class to write a configuration into a config file
    
    :param filePath: output file
    :param :class:`_ReconsConfig` reconsConfiguration: configuration to write
    :param bool overwrite: if True overwrite contains if file exists
    :param bool merge: include all the dataset of the
                                      configuration in the file.
    """
    def write(self, filePath, reconsConfiguration, overwrite=False,
              merge=False):
        """"""
        raise NotImplementedError("Config is an abstract class")
