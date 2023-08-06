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
from silx.gui.widgets import PeriodicTable

class ElementSelector(qt.QPushButton):
    """
    Simple connection with the silx PeriodicTable in order to select an
    element
    """
    DEFAULT_ELEMENT = 'H'

    def __init__(self, elmt=DEFAULT_ELEMENT, parent=None):
        qt.QPushButton.__init__(self, parent=parent)
        self.setText(elmt)
        self.setAutoDefault(True)
        self.setFlat(False)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 100);")

        self.widget = qt.QWidget(None)
        layout = qt.QVBoxLayout()
        self.widget.setLayout(layout)
        self.periodicTable = PeriodicTable.PeriodicTable(self.widget)
        self.periodicTable.setSelection([elmt])

        self.clicked.connect(self._switchPTView)
        buttonClose = qt.QPushButton(text='close', parent=self.widget)
        layout.addWidget(self.periodicTable)
        layout.addWidget(buttonClose)
        buttonClose.setAutoDefault(True)
        buttonClose.clicked.connect(self.widget.hide)

        self.widget.hide()

        self.periodicTable.sigElementClicked.connect(self._changeElement)

    def _switchPTView(self):
        if self.widget.isVisible():
            self.widget.hide()
        else:
            self.widget.show()

    def getElement(self):
        return self.text()

    def setSelection(self, elmt):
        self.periodicTable.setSelection([elmt])
        self.setText(elmt)

    def _changeElement(self, selection):
        self.setText(selection[0])