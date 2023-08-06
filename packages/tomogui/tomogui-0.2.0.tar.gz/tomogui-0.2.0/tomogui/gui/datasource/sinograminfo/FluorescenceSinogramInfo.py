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
__date__ = "06/11/2017"


from silx.gui import qt
from fabio.edfimage import edfimage
from tomogui.gui.datasource.ElementSelector import ElementSelector
try:
    import freeart.utils.physicalelmts as physicalElement
    from freeart.configuration import fileInfo, structs, config as freeartconfig
    found_freeart = True
except:
    from tomogui.third_party.configuration import fileInfo, structs, config as freeartconfig
    found_freeart = False
import numpy
from tomogui.third_party.dialog.ImageFileDialog import _ImagePreview, ImageFileDialog
from tomogui.gui.datasource.tomoguiFileTypeCB import TomoGUIFileTypeCB
from tomogui.gui.datasource.sinograminfo.TxSinogramInfo import TxSinogramInfo
import logging
import os

_logger = logging.getLogger(__name__)


class FluorescenceSinogramInfo(TxSinogramInfo):
    """
    This widget will display information about one fluorescence sinogram
    """
    iSino = 0

    def __init__(self, sinogram, parent=None):
        """
        Constructor
        """
        TxSinogramInfo.__init__(self, sinogram=sinogram, parent=parent)
        widget_EF_Elmt = qt.QWidget(self)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(2)
        widget_EF_Elmt.setLayout(qt.QHBoxLayout())
        widget_EF_Elmt.layout().addWidget(self._getEFGUI(widget_EF_Elmt))
        widget_EF_Elmt.layout().addWidget(self._getPhysElmtGUI(widget_EF_Elmt))
        widget_EF_Elmt.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(widget_EF_Elmt)
        self.layout().addWidget(self._getSelfAbsGUI(self))

        # move the preview at the end
        self.layout().removeWidget(self._previewLabel)
        self.layout().removeWidget(self.sinoPreview)
        self.layout().addWidget(self._previewLabel)
        self.layout().addWidget(self.sinoPreview)

        if self.sinogram:
            self.setSinogram(sinogram)

        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def clean(self):
        TxSinogramInfo.clean(self)
        self._physElmtSel.setEnabled(False)
        self._qlSelfAbsMat.setText('')
        self._qlSelfAbsMat.setEnabled(False)
        self._qleEF.setText('')
        self._qleEF.setEnabled(False)

    def setSinogram(self, sinogram):
        if sinogram is None:
            return
        assert(isinstance(sinogram, structs.FluoSino))
        TxSinogramInfo.setSinogram(self, sinogram)

        # set EF
        self._qleEF.setText(str(self.sinogram.EF))
        self._qleEF.setEnabled(True)
        # set physElmt
        if self.sinogram.physElmt is None or self.sinogram.physElmt not in physicalElement.elementInstance.getElementNames():
            self.sinogram.physElmt = self._tryGuessingElementName()
        self._physElmtSel.setSelection(str(self.sinogram.physElmt))
        self._physElmtSel.setEnabled(True)
        # set self abs mat
        if self.sinogram.selfAbsMat and self.sinogram.selfAbsMat.fileInfo:
            txt = self.sinogram.selfAbsMat.fileInfo.getUri()
            enable = True
        else:
            txt = ''
            enable = False
        self._qlSelfAbsMat.setText(txt)
        self._qpbViewSelfAbsMat.setEnabled(enable)

    def _getEFGUI(self, parent):
        widget = qt.QWidget(parent)
        widget.setLayout(qt.QHBoxLayout())
        widget.layout().addWidget(qt.QLabel('EF (kev)', parent=widget))
        self._qleEF = qt.QLineEdit(text='',
                                   parent=widget)
        self._qleEF.textChanged.connect(self._updateEF)
        widget.layout().addWidget(self._qleEF)
        widget.layout().setContentsMargins(0, 0, 0, 0)
        return widget

    def _updateEF(self, EF):
        if self.sinogram:
            self.sinogram.EF = float(EF)

    def showEF(self, visible):
        self._qleEF.setVisible(visible)

    def _getPhysElmtGUI(self, parent):
        widget = qt.QWidget(parent)
        widget.setLayout(qt.QHBoxLayout())
        widget.layout().addWidget(qt.QLabel('Element', parent=widget))
        self._physElmtSel = ElementSelector(parent=widget)
        self._physElmtSel.periodicTable.sigElementClicked.connect(self._physElmtChanged)
        widget.layout().addWidget(self._physElmtSel)
        widget.layout().setContentsMargins(0, 0, 0, 0)
        return widget

    def _physElmtChanged(self, selection):
        if self.sinogram:
            self.sinogram.physElmt = selection[0]

    def _getSelfAbsGUI(self, parent):
        self._selfAbsMatWid = qt.QWidget(parent)
        self._selfAbsMatWid.setLayout(qt.QHBoxLayout())
        self._selfAbsMatWid.layout().addWidget(
            qt.QLabel('self attenuation matrix:'))
        self._qlSelfAbsMat = qt.QLabel(text='', parent=self._selfAbsMatWid)
        self._selfAbsMatWid.layout().addWidget(self._qlSelfAbsMat)
        self._qpbViewSelfAbsMat = qt.QPushButton(text='view',
                                                 parent=self._selfAbsMatWid)
        self._qpbViewSelfAbsMat.setEnabled(False)
        self._selfAbsMatWid.layout().addWidget(self._qpbViewSelfAbsMat)
        self._qpbSelSelfAbsMat = qt.QPushButton(text='select',
                                                parent=self._selfAbsMatWid)
        self._selfAbsMatWid.layout().addWidget(self._qpbSelSelfAbsMat)
        self._qpbViewSelfAbsMat.pressed.connect(self._showSelfAbsMat)
        self._qpbSelSelfAbsMat.pressed.connect(self._selectSelfAbsMat)
        return self._selfAbsMatWid

    def setSelfAbsMatVisible(self, visible):
        self._selfAbsMatWid.setVisible(visible)

    def _showSelfAbsMat(self):
        self.viewWindow = qt.QMainWindow()
        widget = _ImagePreview(parent=None)
        self.sinogram.selfAbsMat.loadData(None)
        widget.setImage(self.sinogram.selfAbsMat.data)
        widget.setWindowTitle('Self abs mat view' + self.sinogram.selfAbsMat.fileInfo.getUri())
        self.viewWindow.setCentralWidget(widget)
        self.viewWindow.show()

    def _selectSelfAbsMat(self):
        dialog = ImageFileDialog(parent=self)
        dialog.setFileType(TomoGUIFileTypeCB(dialog))

        result = dialog.exec_()
        if result:
            s = str(dialog.selectedPath()).split('::')
            index = '0'
            assert len(s) <= 2
            if len(s) == 2:
                index = s[1]

            fi = freeartconfig.retrieveInfoFile(file=s[0],
                                                index=index)
            self.sinogram.selfAbsMat = structs.SelfAbsMatrix(fileInfo=fi)
            self._qlSelfAbsMat.setText(str(dialog.selectedPath()))
            self._qpbViewSelfAbsMat.setEnabled(True)

    def _tryGuessingElementName(self):
        """
        For files like edf file saved using pymca we can find the pattern to
        get the element type
        """
        if isinstance(self.sinogram.fileInfo, structs.EDFMatrixFileInfo):
            edfReader = edfimage()
            edfReader.read(self.sinogram.fileInfo.getFile())
            header = edfReader.getframe(int(self.sinogram.fileInfo.location)).getHeader()

            if not self.__shouldSkipSino(header):
                name = self._guessSinoName(sinoHeader=header,
                                           useFileName=(edfReader.nframes == 1),
                                           fileName=self.sinogram.fileInfo.getFile())

            if name.lower()[-2:] in ["-k", "-l", "-m", " k", " l", " m"]:
                name = name[:-2]
            if name not in physicalElement.elementInstance.getElementNames():
                # default element value
                name = "H"
        else:
            name = 'H'

        return name

    def __shouldSkipSino(self, sinoHeader):
        """
        skip the pymca errors sinograms.
        Those are under the synthax s(...)
        """
        name = self._guessSinoName(sinoHeader)
        if name is not None:
            return name.lower().startswith("s(") and name.lower().endswith(")")
        else:
            return False

    def _guessSinoName(self, sinoHeader, useFileName=False, fileName=None):
        """
        Simple function to get a default name for a sinogram

        :param sinoHeader: the header in the edf file for this sinogram
        :param useFileName: if no name found can we try to find a pattern from
                            the file name
        :param fileName: the file name
        """
        if 'Title' in sinoHeader:
            return sinoHeader['Title']

        if 'title' in sinoHeader:
            return sinoHeader['title']

        if useFileName and fileName is not None:
            name = os.path.basename(fileName)
            if name.lower().endswith('.edf'):
                name = name[:-4]

            return name
        return None


if __name__ == '__main__':
        global app  # QApplication must be global to avoid seg fault on quit
        app = qt.QApplication([])

        sino = structs.FluoSino(name='fluoSino',
                                fileInfo=fileInfo.H5MatrixFileInfo('test.h5::dsad'),
                                physElmt='O',
                                ef='89',
                                selfAbsMat=None,
                                data=numpy.arange(100).reshape(10, 10))

        mainWindow = FluorescenceSinogramInfo(sinogram=sino)

        mainWindow.setAttribute(qt.Qt.WA_DeleteOnClose)
        mainWindow.show()

        app.exec_()
