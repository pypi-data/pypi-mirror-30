###########################################################################
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
#############################################################################

__author__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "23/11/2017"


from tomogui.gui.datasource.QDataSourceBaseWidget import QDataSourceBaseWidget
from tomogui.gui.datasource.sinofileselector.QSinoFileTxSelector import _QSinoTxSelector
from silx.gui import qt
from tomogui.gui.utils.QFileManagement import QFileSelection
from tomogui import utils
import os
try:
    from freeart.configuration import structs, fileInfo
except ImportError:
    from tomogui.third_party.configuration import structs, fileInfo


class QDataSourceTxWidget(QDataSourceBaseWidget):
    """
    QDataSourceTxWidget is the widget dedicated to get the input from the user
    to get file paths for a Transmission reconsparam.
    This include :
        - the sinogram to reconstruct
        - the file to save the sinogram
    """
    def __init__(self, parent=None, sinograms=None):
        """
        Constructor
        """
        QDataSourceBaseWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())
        self.txSinogramSelector = _QSinoTxSelector(parent=self)
        self.txSinogramSelector.fileSelector.sigSinogramHasBeenAdded.connect(
            self._sinogramRefHasChanged)
        self.layout().addWidget(self.txSinogramSelector)

        self.setToolTip(self.getTransmissionInputsHelp())
        self.addSinogram(sinograms)

    def clean(self):
        self.txSinogramSelector.clean()

    def addSinograms(self):
        for sinogram in sinograms:
            self.addSinogram(sinogram)

    def addSinogram(self, sinogram):
        assert sinogram is None or isinstance(sinogram, structs.DataStored)
        if sinogram:
            if sinogram.fileInfo:
                val = sinogram.fileInfo.getFile()
                if isinstance(sinogram.fileInfo, fileInfo.H5MatrixFileInfo):
                    uri = str(sinogram.fileInfo.getH5Location())
                elif isinstance(sinogram.fileInfo, fileInfo.EDFMatrixFileInfo):
                    uri = str(sinogram.fileInfo.location)
                else:
                    uri = ''
                sinogram.loadData(refFile=None)

            if sinogram.data is not None:
                self.sigSinoRefChanged.emit(sinogram.data)
                self.sigSinoRefDimChanged.emit(sinogram.data.shape)
                self.sigI0MightChanged.emit(sinogram.data.max())
            self.txSinogramSelector.addSinogram(sinogram)

    def getTransmissionInputsHelp(self):
        res = "<html> The transmission reconsparam need as input files : <ul>"
        res = res + utils.addHTMLLine(self.getHTMLItHelp())
        res = res + "</ul></html>"
        return res

    def getHTMLItHelp(self):
        return "The It sinogram"

    def saveConfiguration(self, config, refFile):
        """
        dump information in a configuration file

        :param config: the configuration to save information
        """
        self.txSinogramSelector.saveConfiguration(config, refFile)

    def loadConfiguration(self, config):
        """
        load input file information fron a cfg file

        :param config: the configuration to load information
        """
        for sinogram in config.sinograms:
            self.addSinogram(sinogram)
