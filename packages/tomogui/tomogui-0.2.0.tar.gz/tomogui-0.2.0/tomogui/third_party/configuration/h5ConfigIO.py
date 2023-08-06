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
import h5py
from . import config as configmod
import logging
import copy
try:
    from freeart import version
except:
    version = ''
import time
import silx
if silx._version.MINOR < 7:
    from tomogui.third_party import dictdump_0_7 as dictdump
else:
    from silx.io import dictdump

logger = logging.getLogger(__name__)


class H5Struct():
    PROCESS_NAME = "freeart"
    RECONSTRUCTION_GRP_ID = 'reconstruction'
    CONFIGURATION_GRP_ID = 'configuration'

    def getOrCreateGroup(self, topLevelNode, group):
        def _getOrCreateNext(topLevelNode, nextGrp):
            if nextGrp in topLevelNode.keys():
                return topLevelNode[nextGrp]
            else:
                return topLevelNode.create_group(nextGrp)

        if group is None or group == "":
            return topLevelNode
        splits = group.lstrip('/').split('/')
        remainingPath, nextGrp = '/'.join(splits[1:]), splits[0]
        if len(splits) == 1:
            return _getOrCreateNext(topLevelNode, nextGrp)
        else:
            return self.getOrCreateGroup(
                topLevelNode=_getOrCreateNext(topLevelNode, nextGrp),
                group='/'.join(splits[1:]))

    def _h5FilePathIsValid(self, filePath):
        if filePath is None:
            return False
        splits = filePath.split("::")
        return len(splits) is 2 and len(splits[1]) > 0


class H5ConfigWriter(configIO.ConfigWriter, H5Struct):
    def write(self, filePath, reconsConfiguration, overwrite=False,
              merge=False):
        assert(isinstance(reconsConfiguration, configmod._ReconsConfig))
        confToSave = copy.copy(reconsConfiguration)
        if merge is True:
            confToSave.setFileInfoToH5File(filePath, save=True)

        file = h5py.File(filePath, mode='a')

        reconsGrp = self.getOrCreateGroup(file, self.RECONSTRUCTION_GRP_ID)
        reconsGrp.attrs['program'] = self.PROCESS_NAME
        reconsGrp.attrs['version'] = version
        reconsGrp.attrs['date'] = str(time.strftime("%d/%m/%Y"))

        # prepare configuration
        configGrp = self.getOrCreateGroup(reconsGrp, self.CONFIGURATION_GRP_ID)
        configGrp.attrs['format'] = 'ini'
        path = configGrp.name

        if overwrite is True:
            index = 0
            key = path + '/sino_file_' + str(index)
            while key in file:
                del file[key]
                index = index + 1
                key = path + '/sino_file_' + str(index)

        file.close()

        dictdump.dicttoh5(treedict=confToSave.toDict(),
                          h5file=filePath,
                          h5path=path,
                          mode='r+',
                          overwrite_data=overwrite)


class H5ConfigReader(configIO.ConfigReader, H5Struct):

    def read(self, filePath):
        dict = dictdump.load(filePath, fmat="hdf5")
        if not (self.RECONSTRUCTION_GRP_ID in dict \
                        or self.CONFIGURATION_GRP_ID in dict[self.RECONSTRUCTION_GRP_ID]):
            raise IOError('structure of the hdf5 not recognize, can\'t retrieve the configuration')

        configurationDict = dict[self.RECONSTRUCTION_GRP_ID][self.CONFIGURATION_GRP_ID]

        if 'general_settings' not in configurationDict:
            logger.warning('impossible to read reconstruction configuration,'
                           '`general_settings` not defined.'
                           'File structure is not valid')
            return None

        if 'reconstruction_type' not in configurationDict['general_settings']:
            logger.warning(
                'impossible to read reconstruction configuration,'
                '`general_settings/reconstruction_type` not defined.'
                'File structure is not valid')
            return None

        reconsType = configurationDict['general_settings']['reconstruction_type']
        if type(reconsType) is not str:
            reconsType = str(reconsType.tostring().decode())
        if reconsType not in self.dictReconsTypeToReconsConf:
            logger.error(
                'reconstruction type requested is not defined (%s)' % reconsType)
            return None
        conf = self.dictReconsTypeToReconsConf[reconsType]()._fromDict(configurationDict)

        self._reloadDatasets(config=conf, filePath=filePath)
        return conf
