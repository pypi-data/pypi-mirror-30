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
__date__ = "15/11/2017"


from silx.gui import qt
from numpy.random import randint
from tomogui.gui.materials.MaterialEditor import MaterialGUI


class MaterialDialog(qt.QMessageBox):
    """
    Simple dialog to get a physical material from the user

    :param plot: the plot widget to be linked with
    """
    def __init__(self, parent=None, materialName=None, material=None):
        qt.QMessageBox.__init__(self, parent)

        self.layout().addWidget(qt.QLabel("Please select a material"), 0, 0)

        # Material Editor
        self.materialGUI = MaterialGUI(self)
        if material is not None:
            assert isinstance(material, dict)
            self.materialGUI._current = material
            if materialName is not None:
                self.materialGUI._nameLine.setText(materialName)
                self.disableNameEdition(True)
            self.materialGUI._fillValues()
            self.materialGUI._updateCurrent()
        self.layout().addWidget(self.materialGUI, 1, 0)
        self.color = qt.QColor(randint(0, 255), randint(0, 255), randint(0, 255))

        # color button
        self.qbChangeColor = qt.QPushButton("color")
        self._updateIconColorBt()
        # self.qbChangeColor.setAutoDefault(True)
        self.qbChangeColor.clicked.connect(self._changeColor)
        self.layout().addWidget(self.qbChangeColor, 2, 0)

        self.okButton = self.addButton(qt.QMessageBox.Ok)
        self.okButton.setToolTip(
            "You can't validate the material until all the components are valid.")
        self.cancelButton = self.addButton(qt.QMessageBox.Cancel)

        # rearange the QMesageBox button
        self.layout().removeWidget(self.okButton)
        self.layout().removeWidget(self.cancelButton)
        self.layout().addWidget(self.okButton, 3, 0)
        self.layout().addWidget(self.cancelButton, 3, 1)

        self.okButton.setEnabled(False)

        self.materialGUI._table.itemChanged.connect(self._updateOkButton)
        self.materialGUI._nameLine.textChanged.connect(self._updateOkButton)

    def getSelectedMaterial(self):
        """Return the physical material selected by the user"""
        return self.materialGUI.getMaterialName(), self.materialGUI.getMaterial()

    def _changeColor(self):
        """call back of the color button"""
        self.color = qt.QColorDialog().getColor()
        self._updateIconColorBt()

    def getColor(self):
        """return the color selected by the user"""
        return self.color

    def _updateIconColorBt(self):
        """
        Update the background color of the color button to fit with actual
        selected color
        """
        pixmap = qt.QPixmap(10, 10)
        pixmap.fill(self.color)
        icon = qt.QIcon(pixmap)
        self.qbChangeColor.setIcon(icon)

    def _updateOkButton(self):
        """Update the enable status of the ok button"""
        if self.materialGUI.hasMaterial() and self.materialGUI.materialIsValid() and self.materialGUI.isMaterialNamed():
            self.okButton.setEnabled(True)
        elif (not self.materialGUI.hasMaterial()) or (not self.materialGUI.materialIsValid()) and self.materialGUI.isMaterialNamed():
            self.okButton.setEnabled(False)

    def disableNameEdition(self, b):
        self.materialGUI._nameLine.setReadOnly(b)