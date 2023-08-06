# /*##########################################################################
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
import numpy
from tomogui.third_party.dialog.ImageFileDialog import _ImagePreview
import logging
try:
    from freeart.configuration import fileInfo, structs, config as freeartconfig
    found_freeart = True
except:
    from tomogui.third_party.configuration import fileInfo, structs, config as freeartconfig
    found_freeart = False

_logger = logging.getLogger(__name__)


class TxSinogramInfo(qt.QWidget):
    """
    Widget used to display information about a Transmission sinogram.
    """
    iSino = 0

    def __init__(self, sinogram, parent=None):
        """
        Constructor
        """
        qt.QWidget.__init__(self, parent)
        self.sinogram = None
        self.setLayout(qt.QVBoxLayout())

        self.layout().addWidget(self._getURIGUI(self))
        self.layout().addWidget(self._getNameGUI(self))

        self._previewLabel = qt.QLabel('preview', parent=self)
        self.layout().addWidget(self._previewLabel)
        self.layout().addWidget(self._getDataGUI(self))
        self.layout().addWidget(self._getImageshape(self))

        self.setSinogram(sinogram)
        self.setContentsMargins(0, 0, 0, 0)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def setSinogram(self, sinogram):
        if sinogram is None:
            return
        assert(isinstance(sinogram, structs.Sinogram))

        self.sinogram = sinogram
        # set file
        uri = ''
        if self.sinogram.fileInfo:
            self.sinogram.fileInfo.getUri()
        self._qleUri.setText(uri)
        # set sino name
        if self.sinogram.name == '' or self.sinogram.name is None:
            self.sinogram.name = 'sino_' + str(self.iSino)
            self.iSino = self.iSino + 1
        self._qleName.setText(str(self.sinogram.name))
        self._qleName.setEnabled(True)

        # set image data
        self.sinogram.loadData(refFile=None)
        self.sinoPreview.setImage(self.sinogram.data)
        self._shapeLabel.setText('shape: ' + str(sinogram.data.shape))

    def clean(self):
        self.sinogram = None
        self._qleUri.setText('')
        self._qleName.setText('')
        self._shapeLabel.setText('')
        self._qleName.setEnabled(False)

    def _getDataGUI(self, parent):
        self.sinoPreview = _ImagePreview(parent=parent)
        return self.sinoPreview

    def _getURIGUI(self, parent):
        widget = qt.QWidget(parent)
        widget.setLayout(qt.QHBoxLayout())
        widget.layout().addWidget(qt.QLabel('file', parent=parent))
        self._qleUri = qt.QLabel(text='', parent=widget)
        widget.layout().addWidget(self._qleUri)
        widget.layout().setContentsMargins(0, 0, 0, 0)
        return widget

    def _getNameGUI(self, parent):
        widget = qt.QWidget(parent)
        widget.setLayout(qt.QHBoxLayout())
        widget.layout().addWidget(qt.QLabel('name', parent=widget))
        self._qleName = qt.QLineEdit(text='', parent=widget)
        self._qleName.textChanged.connect(self._updateName)
        widget.layout().addWidget(self._qleName)
        widget.layout().setContentsMargins(0, 0, 0, 0)
        return widget

    def _getImageshape(self, parent):
        self._shapeLabel = qt.QLabel('')
        return self._shapeLabel

    def _updateName(self, name):
        if self.sinogram:
            self.sinogram.name = name


if __name__ == '__main__':
    global app  # QApplication must be global to avoid seg fault on quit
    app = qt.QApplication([])

    sino = structs.TxSino(name='fluoSino',
                          fileInfo=fileInfo.H5MatrixFileInfo(
                                'test.h5::dsad'),
                          data=numpy.arange(100).reshape(10, 10))

    mainWindow = TxSinogramInfo(sinogram=sino)
    mainWindow.setAttribute(qt.Qt.WA_DeleteOnClose)
    mainWindow.show()

    app.exec_()
