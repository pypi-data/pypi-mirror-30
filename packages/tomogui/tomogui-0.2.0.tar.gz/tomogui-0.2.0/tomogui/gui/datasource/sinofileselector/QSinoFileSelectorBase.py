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


from tomogui.gui.utils.ConfigurationActor import ConfigurationActor
from tomogui.gui.datasource.sinofileselector.SinoFileBrowser import BaseSinoFileBrowser
from silx.gui import qt
import logging

_logger = logging.getLogger(__file__)


class QSinoFileSelectorBase(qt.QGroupBox, ConfigurationActor):
    """
    Main widget for fluorescence datasource.
    Contains a QFileSelector and a QFileInspector which are connected one to
    the other
    """
    def __init__(self, parent=None):
        qt.QGroupBox.__init__(self, parent)

        self.setTitle(self._getTitle())
        self.setLayout(qt.QVBoxLayout())

        # crete fileSelector
        self.fileSelector = self.getSinoFileBrowser()
        self.layout().addWidget(self.fileSelector)
        self.sinoInfo = self.getSinogramInfoWidget()
        scrollArea = qt.QScrollArea(self)
        scrollArea.setWidget(self.sinoInfo)
        scrollArea.setWidgetResizable(True)
        self.layout().addWidget(scrollArea)

        # connect widgets
        self.fileSelector.sigSinogramHasBeenAdded.connect(self._updateSinoInfo)
        self.fileSelector.sigSinogramSelectedChanged.connect(self._updateSinoInfo)
        self.fileSelector.sigSinogramHasBeenRemoved.connect(self._cleanSinoInfo)

    def addSinogram(self, sinogram):
        self.fileSelector.addSinogram(sinogram)

    def getSinoFileSelectorWidget(self):
        raise NotImplementedError('Abstract class')

    def loadConfiguration(self, config):
        raise NotImplementedError('Abstract class')

    def saveConfiguration(self, config, refFile):
        raise NotImplementedError('Abstract class')

    def _getTitle(self):
        raise NotImplementedError('Abstract class')

    def getSinoFileBrowser(self):
        raise NotImplementedError('Abstract class')

    def getSinograms(self):
        sinograms = []
        for sinoFile in self.fileSelector.sinograms:
            for uri in self.fileSelector.sinograms[sinoFile]:
                sinogram = self.fileSelector.sinograms[sinoFile][uri]
                sinograms.append(sinogram)
        return sinograms

    def _updateSinoInfo(self, sinogram):
        if sinogram:
            self.sinoInfo.setSinogram(sinogram)
        else:
            self.sinoInfo.clean()

    def _cleanSinoInfo(self):
        self.sinoInfo.clean()

    def clean(self):
        self.fileSelector.clean()
        self.sinoInfo.clean()
