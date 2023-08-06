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
Contains the fileInfo classes. They allow the definition of information
to retrieve data from .h5 and .edf files
"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "26/10/2017"


import os
import h5py
import numpy
import logging
try:
    from freeart.utils.reconstrutils import LoadEdf_2D
except:
    from ..edfutils import LoadEdf_2D
import silx
if silx._version.MINOR < 7:
    from tomogui.third_party import dictdump_0_7 as dictdump
else:
    from silx.io import dictdump

logger = logging.getLogger(__name__)


class MatrixFileInfo(object):
    """
    class defining potential information for a file sinogram contained in
    a file. And a load function to retrieve the data associated with this
    information

    :param str filePath: file path
    :param str location: location of the dataset in the file
    """

    def __init__(self, filePath=None, location=None):
        self.filePath = filePath
        self.location = location or ''

    def __str__(self):
        return "file path is %s, location is %s \n" % (str(self.filePath), str(self.location))

    def __eq__(self, other):
        if not isinstance(other, MatrixFileInfo):
            return False
        return self.filePath == other.filePath

    def getFile(self):
        """

        :return: the file location
        :rtype: str
        """
        return self.filePath

    def load(self, refFile):
        """
        load the data. First from the file set. If None register in infoFile
        then it will use the reffile.

        :param refFile: needed for the H5MatrixFileInfo which the file
                        containing the reconstruction parameters. Bad design
                        but no time to do better
        :return: the data contained
        """
        if self.filePath is None:
            return None
        assert(os.path.isfile(self.filePath))
        if self.filePath.lower().endswith('.npy'):
            return numpy.load(self.filePath)
        elif self.filePath.lower().endswith('.dict') or \
            self.filePath.lower().endswith('.ini'):
            return dictdump.load(self.filePath)
        else:
            raise ValueError('extension of file %s not managed by freeart' % os.path.basename(self.filePath))

    def getUri(self):
        return self.filePath + '::' + str(self.location)

    def setUri(self, uri):
        stps = uri.split('::')
        self.location = stps[1] if len(stps) == 2 else None
        self.filePath = stps[0]

class EDFMatrixFileInfo(MatrixFileInfo):
    """FileInfo for edf file"""
    def __init__(self, filePath, index=0):
        MatrixFileInfo.__init__(self, filePath, location=index)
        if self.location == "":
            self.location = 0

    def load(self, refFile):
        assert os.path.isfile(self.getFile())
        return LoadEdf_2D(self.getFile(), self.location)

    def getIndex(self):
        return self.location


class H5MatrixFileInfo(MatrixFileInfo):
    """FileInfo for hdf5 file"""
    def __init__(self, filePath):
        if filePath is not None:
            assert ('::' in filePath)
            stps = filePath.split('::')
            location = stps[1]
            fp = stps[0]
        else:
            location = None
            fp = None
        MatrixFileInfo.__init__(self, fp, location)

    def getH5Location(self):
        return self.location

    def load(self, refFile):
        assert (
            os.path.isfile(self.getFile() or refFile))
        file = h5py.File(self.getFile() or refFile,
                         mode='r')
        data = None
        key = self.getH5Location()
        assert key
        assert key != ''
        try:
            node = file[key]
        except KeyError:
            logger.error(
                'fail to load data, key %s not found in %s' % (
                    key, self.getFile()))
            file.close()
        else:
            if isinstance(node, h5py.Dataset):
                data = node[...]
                file.close()
                # Bad hack : if no data recorded then will be set to an empty string
                if str(data) == "":
                    data = None

            elif isinstance(node, h5py.Group):
                file.close()
                data = dictdump.h5todict(h5file=self.getFile() or refFile,
                                         path=self.getH5Location())
            else:
                file.close()
                logger.error('can\'t deal with this type of h5py container')

        return data
