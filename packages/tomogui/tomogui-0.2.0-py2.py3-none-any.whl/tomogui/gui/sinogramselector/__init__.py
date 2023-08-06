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
__date__ = "18/09/2017"

from silx.gui import qt
from .QSinoProjSelectorMask import QSinoProjSelectorMask
try:
    from freeart.utils import sinogramselection
except ImportError:
    from tomogui.third_party import sinogramselection
import logging

logger = logging.getLogger(__name__)


class QSinoProjSelector(qt.QWidget):
    """
    Widget helping the selection of the projection to select for reconsparam
    """

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self._interactSelWidget = None

        self.setLayout(qt.QVBoxLayout())

        self.layout().addWidget(qt.QLabel("projections used"))
        self.projectionsUsed = qt.QLineEdit("", parent=self)
        self.layout().addWidget(self.projectionsUsed)

        self.interactiveModeBtn = qt.QPushButton("interactive mode",
                                                 parent=self)
        self.layout().addWidget(self.interactiveModeBtn)
        self.interactiveModeBtn.pressed.connect(self.launchInteractiveSel)

    def setSinogram(self, data):
        """

        :param data: todo
        :warning: this will reset the selection
        """
        self.getInteractiveSelWidget().setImage(data)
        self.setSelection(str(0) + ':' + str(data.shape[0]))

    def setSelection(self, selection):
        if sinogramselection.selectionIsValid(str(selection)):
            self.getInteractiveSelWidget().setSelection(selection)
            self.projectionsUsed.setText(selection)
        else:
            raise ValueError("Given selection is invalid")

    def getSelection(self):
        return str(self.projectionsUsed.text())

    def launchInteractiveSel(self):
        if not hasattr(self._interactSelWidget, "_mask"):
            mess = "no sinogram setted, can't use the selection tool"
            logger.warning(mess)
            qt.QMessageBox.warning(self,
                                   'Selection tool not available',
                                   mess)
        else:
            self._interactSelWidget._mask.setSelection(
                self.projectionsUsed.text())
            self.getInteractiveSelWidget().show()

    def getInteractiveSelWidget(self):
        if self._interactSelWidget is None:
            self._interactSelWidget = QSinoProjSelectorMask(parent=self)
            self._interactSelWidget._mask.sigSelectionChanged.connect(
                self.setSelection
            )

        return self._interactSelWidget


if __name__ == "__main__":
    global app  # QApplication must be global to avoid seg fault on quit
    app = qt.QApplication.instance() or qt.QApplication([])
    import numpy

    data = numpy.random.random((48, 100))

    mainWindow = QSinoProjSelector()
    mainWindow.setSinogram(data)
    mainWindow.setAttribute(qt.Qt.WA_DeleteOnClose)
    mainWindow.show()

    app.exec_()
