#/*##########################################################################
# Copyright (C) 20016-2017 European Synchrotron Radiation Facility
#
# This file is part of tomogui. Interface for tomography developed at
# the ESRF by the Software group.
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
#############################################################################*/

__author__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "08/08/2017"


from silx.gui import qt
import numpy
import os
import logging
from tomogui.gui.datasource.sinofileselector.QSinoFileSelectorBase import QSinoFileSelectorBase
from tomogui.gui.datasource.sinograminfo.TxSinogramInfo import TxSinogramInfo
from tomogui.gui.datasource.sinofileselector.SinoFileBrowser import TxSinoFileBrowser
try:
    from freeart.configuration import fileInfo, config as freeartconfig
except ImportError:
    from tomogui.third_party.configuration import fileInfo, config as freeartconfig

_logger = logging.getLogger(__file__)


class _QSinoTxSelector(QSinoFileSelectorBase):
    """
    Main widget for fluorescence datasource.
    Contains a QFileSelector and a QFileInspector which are connected one to
    the other
    """
    def __init__(self, parent=None):
        QSinoFileSelectorBase.__init__(self, parent)

    def _getTitle(self):
        return 'Transmission sinograms'

    def getSinogramInfoWidget(self):
        return TxSinogramInfo(parent=self, sinogram=None)

    def loadConfiguration(self, config):
        assert isinstance(config, freeartconfig._SimpleSinoConfig)
        for sinogram in config.sinograms:
            self.fileSelector.addSinogram(sinogram)

    def saveConfiguration(self, config, refFile):
        def fillEmptyFillInfo(sinograms):
            fn, file_extension = os.path.splitext(refFile)
            if file_extension.lower() not in ('.h5', '.hdf', '.hdf5'):
                return sinograms

            for sinogram in sinograms:
                if sinogram.fileInfo is None:
                    sinogram.fileInfo = fileInfo.H5MatrixFileInfo(
                        refFile + sinogram.h5defaultPath
                    )
                    sinogram.save()
            return sinograms

        config.sinograms = self.getSinograms()
        if refFile is not None:
            config.sinograms = fillEmptyFillInfo(config.sinograms)

    def getSinoFileBrowser(self):
        return TxSinoFileBrowser(self)

if __name__ == '__main__':
    import tempfile
    import shutil
    from freeart.utils import h5utils, testutils as freeart_testutils
    from freeart.configuration import fileInfo, structs
    tempdir = tempfile.mkdtemp()
    config = freeart_testutils.createConfigTx(tempdir)

    # add some sinogram in the same .h5 file
    fileName = 'multiSino' + '.h5'
    sourceFile = os.path.join(tempdir, fileName)

    sinograms = []
    for iSino in (1, 3, 5):
        path = "/data/sino___" + str(iSino)
        h5utils.createH5WithDataSet(filePath=sourceFile,
                                    h5path=path,
                                    data=numpy.arange(100).reshape(10, 10),
                                    mode='a')
        file_info = fileInfo.H5MatrixFileInfo(
            filePath=sourceFile + "::" + path)

        config.sinograms.append(
            structs.TxSinogram(fileInfo=file_info,
                               data=None,
                               name='Sinogram_' + str(iSino),)
        )

    app = qt.QApplication([])
    widget = _QSinoTxSelector()
    widget.loadConfiguration(config)
    widget.show()
    app.exec_()
    shutil.rmtree(tempdir)
