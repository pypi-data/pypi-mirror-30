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

from . import configIO
from . import config
import logging
import silx
if silx._version.MINOR < 7:
    from freeart.utils import dictdump_0_7 as dictdump
else:
    from silx.io import dictdump

logger = logging.getLogger(__name__)


class IniConfigWriter(configIO.ConfigWriter):
    def write(self, filePath, reconsConfiguration, overwrite=False,
              merge=False):
        assert isinstance(reconsConfiguration, config._ReconsConfig)
        if merge is True:
            logger.warning('the `includeDatasetInFile` option is not managed'
                           'by the IniConfigWriter')
        dictdump.dicttoini(ddict=reconsConfiguration.toDict(),
                           inifile=filePath,
                           mode="w" if overwrite is True else 'a')


class IniConfigReader(configIO.ConfigReader):

    def read(self, filePath):
        dict = dictdump.load(filePath)
        if 'general_settings' not in dict:
            logger.warning('impossible to read reconstruction configuration,'
                           '`general_settings` not defined.'
                           'File structure is not valid')
            return None

        if 'reconstruction_type' not in dict['general_settings']:
            logger.warning(
                'impossible to read reconstruction configuration,'
                '`general_settings/reconstruction_type` not defined.'
                'File structure is not valid')
            return None

        reconsType = dict['general_settings']['reconstruction_type']
        if type(reconsType) is not str:
            reconsType = str(reconsType.tostring().decode())
        if reconsType not in self.dictReconsTypeToReconsConf:
            logger.error(
                'reconstruction type requested is not defined (%s)' % reconsType)
            return None
        conf = self.dictReconsTypeToReconsConf[reconsType]()._fromDict(dict)

        self._reloadDatasets(config=conf, filePath=filePath)
        return conf