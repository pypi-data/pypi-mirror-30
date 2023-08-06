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
__date__ = "27/10/2017"


import h5py
import os


def createH5WithDataSet(filePath, h5path, data, mode='w-', overwrite=True):
    """Create a simple file with one data set at the location path"""
    def _getOrCreateNext(topLevelNode, nextGrp):
        if nextGrp in topLevelNode.keys():
            return topLevelNode[nextGrp]
        else:
            return topLevelNode.create_group(nextGrp)

    # there is an hack for dict, we have to go through dictdump.dicttoh5
    if isinstance(data, dict):
        dictdump.dicttoh5(h5file=filePath,
                          treedict=data,
                          h5path=h5path,
                          mode='a',
                          overwrite_data=overwrite)
    else:
        file = h5py.File(name=filePath, mode=mode)
        grps = h5path.lstrip('::').lstrip('/').split('/')
        datasetname = grps[-1]
        grps=grps[:-1]
        node = file
        for grp in grps:
            node = _getOrCreateNext(node, grp)

        if not datasetname in node:
            node.create_dataset(name=datasetname, data=data)
        elif overwrite is True:
            del node[datasetname]
            node[datasetname] = data
        else:
            raise IOError('Unable to create link (Name already exists)')
        file.close()
        assert (os.path.isfile(filePath))
