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
"""module to define material, taking from PymCa"""

__author__ = "V. Armando Sole - ESRF Data Analysis"
__contact__ = "sole@esrf.fr"
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"

import sys
import copy

from silx.gui import qt
from silx.gui.plot import PlotWindow
from tomogui.physics import Elements

ScanWindow = PlotWindow

if hasattr(qt, "QString"):
    QString = qt.QString
else:
    QString = str

DEBUG = 0


class MaterialGUI(qt.QWidget):

    sigMaterialMassAttenuationSignal = qt.pyqtSignal(object)
    sigMaterialTransmissionSignal = qt.pyqtSignal(object)

    def __init__(self, parent=None, name="New Material", default={},
                 comments=False, height=10, toolmode=False):
        qt.QWidget.__init__(self, parent)
        self.setWindowTitle(name)
        self._default = default
        self._setCurrentDefault()
        for key in default.keys():
            if key in self._current:
                self._current[key] = self._default[key]
        self.__lastRow = None
        self.__lastColumn = None
        self.__fillingValues = True
        self.__toolMode = toolmode
        if toolmode:
            self.buildToolMode(comments, height)
        else:
            self.build(comments, height)

    def _setCurrentDefault(self):
        self._current = {
            'Comment': "New Material",
            'CompoundList': [],
            'CompoundFraction': [1.0],
            'Density': 1.0,
            'Thickness': 1.0
        }

    def build(self, comments="True", height=3):
        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.__comments = comments
        commentsHBox = qt.QWidget(self)
        layout.addWidget(commentsHBox)
        commentsHBoxLayout = qt.QHBoxLayout(commentsHBox)
        commentsHBoxLayout.setContentsMargins(0, 0, 0, 0)
        commentsHBoxLayout.setSpacing(0)

        tableContainer = qt.QWidget(commentsHBox)
        commentsHBoxLayout.addWidget(tableContainer)
        tableContainerLayout = qt.QVBoxLayout(tableContainer)
        tableContainerLayout.setContentsMargins(0, 0, 0, 0)
        tableContainerLayout.setSpacing(0)
        self.__hboxTableContainer = qt.QWidget(tableContainer)
        hbox = self.__hboxTableContainer
        tableContainerLayout.addWidget(hbox)
        hboxLayout = qt.QHBoxLayout(hbox)
        hboxLayout.setContentsMargins(0, 0, 0, 0)
        hboxLayout.setSpacing(0)
        numberLabel = qt.QLabel(hbox)
        hboxLayout.addWidget(numberLabel)
        numberLabel.setText("Number of elements:")
        numberLabel.setAlignment(qt.Qt.AlignVCenter)
        self.__numberSpin = qt.QSpinBox(hbox)
        hboxLayout.addWidget(self.__numberSpin)
        self.__numberSpin.setMinimum(1)
        self.__numberSpin.setMaximum(100)
        self.__numberSpin.setValue(1)
        self._table = qt.QTableWidget(tableContainer)
        self._table.setRowCount(1)
        self._table.setColumnCount(2)
        tableContainerLayout.addWidget(self._table)
        self._table.setMinimumHeight(
            (height) * self._table.horizontalHeader().sizeHint().height())
        self._table.setMaximumHeight(
            (height) * self._table.horizontalHeader().sizeHint().height())
        self._table.setMinimumWidth(1 * self._table.sizeHint().width())
        self._table.setMaximumWidth(1 * self._table.sizeHint().width())

        labels = ["Material", "Mass Fraction"]
        for i in range(len(labels)):
            item = self._table.horizontalHeaderItem(i)
            if item is None:
                item = qt.QTableWidgetItem(labels[i], qt.QTableWidgetItem.Type)
            self._table.setHorizontalHeaderItem(i, item)
        self._table.setSelectionMode(qt.QTableWidget.NoSelection)
        if self.__comments:
            vbox = qt.QWidget(commentsHBox)
            commentsHBoxLayout.addWidget(vbox)
            vboxLayout = qt.QVBoxLayout(vbox)

            # default thickness and density
            self.__gridVBox = qt.QWidget(vbox)
            grid = self.__gridVBox
            vboxLayout.addWidget(grid)
            gridLayout = qt.QGridLayout(grid)
            gridLayout.setContentsMargins(11, 11, 11, 11)
            gridLayout.setSpacing(4)

            spacer = qt.QWidget(self)
            spacer.setSizePolicy(qt.QSizePolicy.Minimum,
                                 qt.QSizePolicy.Expanding)
            vboxLayout.addWidget(spacer)

        # name line
        nameHBox = qt.QWidget(self)
        nameHBoxLayout = qt.QHBoxLayout(nameHBox)
        nameLabel = qt.QLabel(nameHBox)
        nameHBoxLayout.addWidget(nameLabel)
        nameLabel.setText("Material name :")
        nameLabel.setToolTip("The name of the material we are defining")
        nameLabel.setAlignment(qt.Qt.AlignVCenter)
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
        nameHBoxLayout.addWidget(spacer)

        self._nameLine = qt.QLineEdit(nameHBox)
        nameHBoxLayout.addWidget(self._nameLine)
        layout.insertWidget(0, nameHBox)

        if self.__comments:
            # comment
            commentHBox = qt.QWidget(self)
            commentHBoxLayout = qt.QHBoxLayout(commentHBox)
            commentLabel = qt.QLabel(commentHBox)
            commentHBoxLayout.addWidget(commentLabel)
            commentLabel.setText("Comment :")
            commentLabel.setAlignment(qt.Qt.AlignVCenter)
            spacer = qt.QWidget(self)
            spacer.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Minimum)
            commentHBoxLayout.addWidget(spacer)

            self._commentLine  = qt.QLineEdit(commentHBox)
            self._commentLine.editingFinished[()].connect(self._commentLineSlot)
            commentHBoxLayout.addWidget(self._commentLine)
            self._commentLine.setReadOnly(False)
            longtext="En un lugar de La Mancha, de cuyo nombre no quiero acordarme ..."
            self._commentLine.setFixedWidth(self._commentLine.fontMetrics().width(longtext))
            layout.insertWidget(1, commentHBox)

        self.__numberSpin.valueChanged[int].connect(self.__numberSpinChanged)
        self._table.cellChanged[int, int].connect(self._tableSlot)
        self._table.cellEntered[int, int].connect(self._tableSlot2)

    def buildToolMode(self, comments="True", height=3):
        layout = qt.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.__comments = comments
        grid = qt.QWidget(self)
        gridLayout = qt.QGridLayout(grid)
        gridLayout.setContentsMargins(11, 11, 11, 11)
        gridLayout.setSpacing(4)
        numberLabel = qt.QLabel(grid)
        numberLabel.setText("Number  of  Compounds:")
        numberLabel.setAlignment(qt.Qt.AlignVCenter)
        self.__numberSpin  = qt.QSpinBox(grid)
        self.__numberSpin.setMinimum(1)
        self.__numberSpin.setMaximum(30)
        self.__numberSpin.setValue(1)

        tableContainer = qt.QWidget(self)
        tableContainerLayout = qt.QVBoxLayout(tableContainer)
        tableContainerLayout.setContentsMargins(0, 0, 0, 0)
        tableContainerLayout.setSpacing(0)
        self._tableContainer = tableContainer

        self._table = qt.QTableWidget(tableContainer)
        self._table.setRowCount(1)
        self._table.setColumnCount(2)
        tableContainerLayout.addWidget(self._table)
        self._table.setMinimumHeight((height)*self._table.horizontalHeader().sizeHint().height())
        self._table.setMaximumHeight((height)*self._table.horizontalHeader().sizeHint().height())
        self._table.setMinimumWidth(1*self._table.sizeHint().width())
        self._table.setMaximumWidth(1*self._table.sizeHint().width())
        labels = ["Material", "Mass Fraction"]
        for i in range(len(labels)):
            item = self._table.horizontalHeaderItem(i)
            if item is None:
                item = qt.QTableWidgetItem(str(labels[i]), qt.QTableWidgetItem.Type)
            self._table.setHorizontalHeaderItem(i, item)
        self._table.setSelectionMode(qt.QTableWidget.NoSelection)

        densityLabel = qt.QLabel(grid)
        densityLabel.setText("Density (g/cm3):")
        densityLabel.setAlignment(qt.Qt.AlignVCenter)
        self.__densityLine = qt.QLineEdit(grid)
        self.__densityLine.setText("1.0")
        validator = qt.QDoubleValidator(self.__densityLine)
        self.__densityLine.setValidator(validator)
        self.__densityLine.setReadOnly(False)

        thicknessLabel = qt.QLabel(grid)
        thicknessLabel.setText("Thickness  (cm):")
        thicknessLabel.setAlignment(qt.Qt.AlignVCenter)
        self.__thicknessLine = qt.QLineEdit(grid)
        self.__thicknessLine.setText("0.1")
        validator = qt.QDoubleValidator(self.__thicknessLine)
        self.__thicknessLine.setValidator(validator)
        self.__thicknessLine.setReadOnly(False)

        self.__transmissionButton = qt.QPushButton(grid)
        self.__transmissionButton.setText('Material Transmission')
        self.__massAttButton = qt.QPushButton(grid)
        self.__massAttButton.setText('Mass Att. Coefficients')
        self.__transmissionButton.setAutoDefault(False)
        self.__massAttButton.setAutoDefault(False)

        nameHBox = qt.QWidget(grid)
        nameHBoxLayout = qt.QHBoxLayout(nameHBox)
        nameHBoxLayout.setContentsMargins(0, 0, 0, 0)
        nameHBoxLayout.setSpacing(0)
        nameLabel = qt.QLabel(nameHBox)
        nameLabel.setText("Name:")
        nameLabel.setAlignment(qt.Qt.AlignVCenter)
        self._commentLine = qt.QLineEdit(nameHBox)
        self._commentLine.setReadOnly(False)
        if self.__toolMode:
            toolTip = "Type your material name and press the ENTER key.\n"
            toolTip += "Fitting materials cannot be defined or redefined here.\n"
            toolTip += "Use the material editor of the advanced fit for it.\n"
            self._commentLine.setToolTip(toolTip)

        nameHBoxLayout.addWidget(nameLabel)
        nameHBoxLayout.addWidget(self._commentLine)
        gridLayout.addWidget(nameHBox, 0, 0, 1, 2)
        gridLayout.addWidget(numberLabel, 1, 0)
        gridLayout.addWidget(self.__numberSpin, 1, 1)
        gridLayout.addWidget(self._tableContainer, 2, 0, 1, 2)
        gridLayout.addWidget(densityLabel, 3, 0)
        gridLayout.addWidget(self.__densityLine, 3, 1)
        gridLayout.addWidget(thicknessLabel, 4, 0)
        gridLayout.addWidget(self.__thicknessLine, 4, 1)
        gridLayout.addWidget(self.__transmissionButton, 5, 0)
        gridLayout.addWidget(self.__massAttButton, 5, 1)
        layout.addWidget(grid)

        # build all the connections
        self._commentLine.editingFinished[()].connect(self._commentLineSlot)

        self.__numberSpin.valueChanged[int].connect(self.__numberSpinChanged)

        self._table.cellChanged[int, int].connect(self._tableSlot)
        self._table.cellEntered[int, int].connect(self._tableSlot2)

        self.__densityLine.editingFinished[()].connect(self.__densitySlot)

        self.__thicknessLine.editingFinished[()].connect(self.__thicknessSlot)

        self.__transmissionButton.clicked.connect(self.__transmissionSlot)

        self.__massAttButton.clicked.connect(self.__massAttSlot)

    def setCurrent(self, matkey0):
        if DEBUG:
            print("setCurrent(self, matkey0) ", matkey0)
        matkey = Elements.getMaterialKey(matkey0)
        if matkey is not None:
            if self.__toolMode:
                # make sure the material CANNOT be modified
                self._current = copy.deepcopy(Elements.Material[matkey])
                if self._table.isEnabled():
                    self.__disableInput()
            else:
                self._current = Elements.Material[matkey]
        else:
            self._setCurrentDefault()
            if not self.__toolMode:
                Elements.Material[matkey0] = self._current
        self.__numberSpin.setFocus()
        try:
            self._fillValues()
            self._updateCurrent()
        finally:
            if self.__toolMode:
                self._commentLine.setText("%s" % matkey)
            self.__fillingValues = False

    def _fillValues(self):
        if DEBUG:
            print("fillValues(self)")
        self.__fillingValues = True
        if self.__comments:
            self._commentLine.setText("%s" % self._current['Comment'])
            try:
                self.__densityLine.setText("%.5g" % self._current['Density'])
            except:
                self.__densityLine.setText("")
            if 'Thickness' in self._current.keys():
                try:
                    self.__thicknessLine.setText("%.5g" % self._current['Thickness'])
                except:
                    self.__thicknessLine.setText("")

        self.__numberSpin.setValue(max(len(self._current['CompoundList']), 1))
        row = 0
        for compound in self._current['CompoundList']:
            item = self._table.item(row, 0)
            if item is None:
                item = qt.QTableWidgetItem(str(compound), qt.QTableWidgetItem.Type)
                self._table.setItem(row, 0, item)
            else:
                item.setText(compound)
            item = self._table.item(row, 1)
            if item is None:
                item = qt.QTableWidgetItem("%.5g" % float(str(self._current['CompoundFraction'][row])),
                                           qt.QTableWidgetItem.Type)
                self._table.setItem(row, 1, item)
            else:
                item.setText("%.5g" % self._current['CompoundFraction'][row])
            row += 1
        self.__fillingValues = False

    # http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=666503
    def _updateCurrent(self):
        if DEBUG:
            print("updateCurrent(self)")
            print("self._current before = ", self._current)

        self._current['CompoundList'] = []
        self._current['CompoundFraction'] = []
        for i in range(self._table.rowCount()):
            item = self._table.item(i, 0)
            if item is None:
                item = qt.QTableWidgetItem("",
                                           qt.QTableWidgetItem.Type)
            txt0 = str(item.text())
            item = self._table.item(i, 1)
            if item is None:
                item = qt.QTableWidgetItem("",
                                           qt.QTableWidgetItem.Type)
            txt1 = str(item.text())
            if (len(txt0) > 0) and (len(txt1) > 0):
                self._current['CompoundList'].append(txt0)
                self._current['CompoundFraction'].append(float(txt1))
        self.__densitySlot(silent=True)
        self.__thicknessSlot(silent=True)
        if DEBUG:
            print("self._current after = ", self._current)

    def __densitySlot(self, silent=False):
        try:
            qstring = self.__densityLine.text()
            text = str(qstring)
            if len(text):
                value = float(str(qstring))
                self._current['Density'] = value
        except:
            if silent:
                return
            msg = qt.QMessageBox(self.__densityLine)
            msg.setIcon(qt.QMessageBox.Critical)
            msg.setText("Invalid Float")
            msg.exec_()
            self.__densityLine.setFocus()

    def __thicknessSlot(self, silent=False):
        try:
            qstring = self.__thicknessLine.text()
            text = str(qstring)
            if len(text):
                value = float(text)
                self._current['Thickness'] = value
        except:
            if silent:
                return
            msg=qt.QMessageBox(self.__thicknessLine)
            msg.setIcon(qt.QMessageBox.Critical)
            msg.setText("Invalid Float")
            msg.exec_()
            self.__thicknessLine.setFocus()

    def __transmissionSlot(self):
        ddict = {}
        ddict.update(self._current)
        ddict['event'] = 'MaterialTransmission'
        self.sigMaterialTransmissionSignal.emit(ddict)

    def __massAttSlot(self):
        ddict = {}
        ddict.update(self._current)
        ddict['event'] = 'MaterialMassAttenuation'
        self.sigMaterialMassAttenuationSignal.emit(ddict)

    def _commentLineSlot(self):
        if DEBUG:
            print("_commentLineSlot(self)")
        qstring = self._commentLine.text()
        text = str(qstring)
        if self.__toolMode:
            if len(text):
                matkey = Elements.getMaterialKey(text)
            if matkey is not None:
                self.setCurrent(matkey)
                # Disable everything
                self.__disableInput()
            elif text in Elements.ElementList:
                self.__disableInput()
                name = Elements.Element[text]['name']
                self._current['Comment'] = name[0].upper() + name[1:]
                self._current['CompoundList'] = [text+"1"]
                self._current['CompoundFraction'] = [1.0]
                self._current['Density'] = Elements.Element[text]['density']
                self._fillValues()
                self._updateCurrent()
                self._commentLine.setText("%s" % text)
            else:
                self._current['Comment'] = text
                self.__numberSpin.setEnabled(True)
                self._table.setEnabled(True)
                self.__densityLine.setEnabled(True)
                self.__thicknessLine.setEnabled(True)
        else:
            self._current['Comment'] = text

    def __disableInput(self):
        self.__numberSpin.setEnabled(False)
        self._table.setEnabled(False)
        self.__densityLine.setEnabled(False)
        self.__thicknessLine.setEnabled(True)

    def __numberSpinChanged(self, value):
        self._table.setRowCount(value)
        rheight = self._table.horizontalHeader().sizeHint().height()
        nrows = self._table.rowCount()
        for idx in range(nrows):
            self._table.setRowHeight(idx, rheight)
        if len(self._current['CompoundList']) > value:
            self._current['CompoundList'] = self._current['CompoundList'][0:value]
        if len(self._current['CompoundFraction']) > value:
            self._current['CompoundFraction'] = self._current['CompoundFraction'][0:value]

    def _tableSlot(self, row, col):
        if self.__fillingValues:
            return
        item = self._table.item(row, col)
        if item is not None:
            if DEBUG:
                print("table item is None")
            qstring = item.text()
        else:
            qstring = ""
        if col == 0:
            compound = str(qstring)
            if Elements.isValidFormula(compound):
                pass
            else:
                matkey = Elements.getMaterialKey(compound)
                if matkey is not None:
                    item.setText(matkey)
                else:
                    msg = qt.QMessageBox(self._table)
                    msg.setIcon(qt.QMessageBox.Critical)
                    msg.setText("Invalid Formula %s" % compound)
                    msg.exec_()
                    self._table.setCurrentCell(row, col)
                    return
        else:
            try:
                float(str(qstring))
            except:
                msg = qt.QMessageBox(self._table)
                msg.setIcon(qt.QMessageBox.Critical)
                msg.setText("Invalid Float")
                msg.exec_()
                self._table.setCurrentCell(row, col)
                return
        self._updateCurrent()

    def _tableSlot2(self, row, col):
        if self.__fillingValues:
            return
        if self.__lastRow is None:
            self.__lastRow = row

        if self.__lastColumn is None:
            self.__lastColumn = col

        item = self._table.item(self.__lastRow,
                                self.__lastColumn)
        if item is None:
            item = qt.QTableWidgetItem("", qt.QTableWidgetItem.Type)
            self._table.setItem(self.__lastRow,
                                self.__lastColumn,
                                item)
        qstring = item.text()

        if self.__lastColumn == 0:
            compound = str(qstring)
            if Elements.isValidFormula(compound):
                pass
            else:
                matkey = Elements.getMaterialKey(compound)
                if matkey is not None:
                    item = self._table.item(self.__lastRow,
                                            self.__lastColumn)
                    if item is None:
                        item = qt.QTableWidgetItem(matkey,
                                                   qt.QTableWidgetItem.Type)
                        self._table.setItem(self.__lastRow,
                                            self.__lastColumn,
                                            item)
                    else:
                        item.setText(matkey)
                else:
                    msg = qt.QMessageBox(self._table)
                    msg.setIcon(qt.QMessageBox.Critical)
                    msg.setText("Invalid Formula %s" % compound)
                    msg.exec_()
                    self._table.setCurrentCell(self.__lastRow, self.__lastColumn)
                    return
        else:
            try:
                float(str(qstring))
            except:
                msg = qt.QMessageBox(self._table)
                msg.setIcon(qt.QMessageBox.Critical)
                msg.setText("Invalid Float")
                msg.exec_()
                self._table.setCurrentCell(self.__lastRow, self.__lastColumn)
                return
        self._updateCurrent()

    def materialIsValid(self):
        mat = self.getMaterial()
        for compound in mat['CompoundList']:
            if Elements.isValidFormula(compound) is False:
                return False

        return True

    def hasMaterial(self):
        mat = self.getMaterial()
        return len(mat['CompoundList']) > 0

    def isMaterialNamed(self):
        return self.getMaterialName() != ''

    def getMaterial(self):
        """Return the current material defined by the user"""
        self._updateCurrent()
        return self._current

    def getMaterialName(self):
        return self._nameLine.text()


if __name__ == "__main__":
    app = qt.QApplication([])
    app.lastWindowClosed.connect(app.quit)
    if len(sys.argv) > 1:
        demo = MaterialGUI(toolmode=True)
    else:
        demo = MaterialGUI()
    demo.show()
    app.exec_()
