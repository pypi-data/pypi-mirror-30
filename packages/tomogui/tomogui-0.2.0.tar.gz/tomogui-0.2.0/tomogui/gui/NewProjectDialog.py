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
__date__ = "22/10/2017"

from silx.gui import qt
from tomogui.gui.ProjectWidget import ProjectWindow
from tomogui.configuration import config as tomoguiconfig
import numpy
try:
    import freeart
    from freeart.configuration import config as freeartconfig
    has_freeart = True
except:
    has_freeart = False


class NewProjectDialog(qt.QDialog):
    """
    Launch a dialog to select the type of reconstruction to run for the
    given numpy array
    
    :param numpy.ndarray data: the data to reconstruct
    """
    FBP_REQ = 1000
    """Value set if an FBP reconstruction is requested"""

    TX_REQ = 1001
    """Value set if an TX reconstruction is requested"""

    FLUO_REQ = 1010
    """Value set if an FLUO reconstruction is requested"""

    COMPTON_REQ = 1011
    """Value set if an COMPTON reconstruction is requested"""

    def __init__(self):
        qt.QDialog.__init__(self)
        self.setWindowTitle('Sinogram reconstruction')
        self.setLayout(qt.QVBoxLayout())

        self.layout().addWidget(
            qt.QLabel('What kind of reconstruction do you want to run'))
        _buttons = qt.QDialogButtonBox(parent=self)

        self._qpbFBP = qt.QPushButton('FBP', _buttons)
        self._qpbFBP.setToolTip('Filtered back projection reconstruction from silx')
        self._qpbFBP.clicked.connect(self.setFBPRecons)
        _buttons.layout().addWidget(self._qpbFBP)

        if has_freeart:
            self._qpbTX = qt.QPushButton('TX', _buttons)
            _buttons.layout().addWidget(self._qpbTX)
            self._qpbTX.setToolTip('Transmission reconstruction from freeart')
            self._qpbTX.clicked.connect(self.setTXRecons)

            self._qpbFluo = qt.QPushButton('Fluo', _buttons)
            _buttons.layout().addWidget(self._qpbFluo)
            self._qpbFluo.setToolTip('Fluorescence reconstruction from freeart')
            self._qpbFluo.clicked.connect(self.setFluoRecons)

            self._qpbCompton = qt.QPushButton('Compton', _buttons)
            _buttons.layout().addWidget(self._qpbCompton)
            self._qpbCompton.setToolTip('Compton reconstruction from freeart')
            self._qpbCompton.clicked.connect(self.setComptonRecons)

        self.layout().addWidget(_buttons)

    def setFBPRecons(self):
        self.done(self.FBP_REQ)

    def setTXRecons(self):
        self.done(self.TX_REQ)

    def setFluoRecons(self):
        self.done(self.FLUO_REQ)

    def setComptonRecons(self):
        self.done(self.COMPTON_REQ)

    def run(self):
        self.mainWindow = ProjectWindow()
        self.mainWindow.setSinoToRecons(
            reconsType=tomoguiconfig.FBPConfig.FBP_ID,
            sinograms=[self.data])

        mainWindow.show()

    @staticmethod
    def resToRtype(resType):
        if resType == NewProjectDialog.FBP_REQ:
            return tomoguiconfig.FBPConfig.FBP_ID
        if has_freeart is True:
            if resType == NewProjectDialog.TX_REQ:
                return freeartconfig._ReconsConfig.TX_ID
            elif resType == NewProjectDialog.FLUO_REQ:
                return freeartconfig._ReconsConfig.FLUO_ID
            elif resType == NewProjectDialog.COMPTON_REQ:
                return freeartconfig._ReconsConfig.COMPTON_ID
        return None


if __name__ == '__main__':
    app = qt.QApplication.instance() or qt.QApplication([])
    diag = NewProjectDialog(data=numpy.arange(100).reshape(10, 10))
    diag.exec_()
