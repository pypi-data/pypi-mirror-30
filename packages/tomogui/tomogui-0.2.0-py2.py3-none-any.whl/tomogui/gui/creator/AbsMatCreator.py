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
__date__ = "21/07/2017"


import logging
import numpy
import os
from silx.gui import qt
from tomogui.third_party.dialog.ImageFileDialog import ImageFileDialog
from tomogui.gui.datasource.tomoguiFileTypeCB import TomoGUIFileTypeCB
from tomogui.gui.materials.QSampleComposition import QSampleComposition

try:
    from freeart.utils import physicalelmts, reconstrutils
except ImportError:
    raise RuntimeWarning("freeart not found")


class AbsMatCreator(qt.QMainWindow):
    """Creator widget to define an absorption matrix
    """

    def __init__(self, parent=None):
        qt.QMainWindow.__init__(self, parent=parent)
        widget = qt.QWidget()
        self.setCentralWidget(widget)
        widget.setToolTip(
            """in order to generate an absorption matrix you should :
                  - load a background image/matrix of the sample you want to define
                  - define materials contained in the sample
                  - draw each materials on the mask
                  - save for each energy a file with the energy
            """)

        widget.setLayout(qt.QVBoxLayout())
        widget.layout().addWidget(self._createLoader())
        widget.layout().addWidget(self._createMainWindow())
        widget.layout().addWidget(self._createMaterialManager())
        widget.layout().addWidget(self._createConverter())

    def _createLoader(self):
        widget = qt.QWidget()
        widget.setLayout(qt.QHBoxLayout())
        self._loadBckImgBt = qt.QPushButton(parent=widget,
                                            text='load background image')
        self._loadBckImgBt.pressed.connect(self._load)
        widget.layout().addWidget(self._loadBckImgBt)
        return widget

    def _createMainWindow(self):
        self._mainWidget = QSampleComposition(parent=self)
        return self._mainWidget

    def _load(self):
        dialog = ImageFileDialog(self)
        dialog.setFileType(TomoGUIFileTypeCB(dialog))

        result = dialog.exec_()
        if not result:
            return

        self._mainWidget.addImage(dialog.selectedImage())

    def _createMaterialManager(self):
        widget = qt.QWidget(parent=self)
        self._saveBt = qt.QPushButton(parent=widget, text='Save')
        self._saveBt.pressed.connect(self.saveMaterials)
        widget.setLayout(qt.QHBoxLayout())
        widget.layout().addWidget(self._saveBt)

        self._loadBt = qt.QPushButton(parent=widget, text='Load')
        self._loadBt.pressed.connect(self.loadMaterials)
        widget.setLayout(qt.QHBoxLayout())
        widget.layout().addWidget(self._loadBt)
        return widget

    def _createConverter(self):
        widget = qt.QGroupBox(parent=self, title='Generate absorption matrix')
        widget.setLayout(qt.QVBoxLayout())

        energyWidget = qt.QWidget(parent=widget)
        energyWidget.setLayout(qt.QHBoxLayout())
        energyWidget.layout().addWidget(qt.QLabel('E (keV) = '))
        self._energyQLE = qt.QLineEdit(text=str(1), parent=energyWidget)
        energyWidget.layout().addWidget(self._energyQLE)
        widget.layout().addWidget(energyWidget)

        generateWidget = qt.QWidget(parent=widget)
        generateWidget.setLayout(qt.QHBoxLayout())
        spacer = qt.QWidget(parent=generateWidget)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        generateWidget.layout().addWidget(spacer)
        self._generateBt = qt.QPushButton(parent=generateWidget,
                                          text='Generate')
        self._generateBt.pressed.connect(self.exportAbsMatrices)
        generateWidget.layout().addWidget(self._generateBt)
        widget.layout().addWidget(generateWidget)
        return widget

    def saveMaterials(self):
        self._mainWidget.save()

    def loadMaterials(self):
        materialsFile = self._getMaterialsFile()
        if materialsFile is None:
            return
        self._mainWidget.maskToolWidget.loadSampleComposition(materialsFile)

    def _getMaterialsFile(self):
        dialog = qt.QFileDialog(self)
        dialog.setWindowTitle(
            "Select the file defining the sample composition")
        dialog.setModal(1)
        dialog.setNameFilters(['hdf5 file *.h5 *.hdf *.hdf5'])

        if not dialog.exec_():
            dialog.close()
            return None

        return dialog.selectedFiles()[0]

    def selectFolder(self):
        """
        Function called when the QPushButton has been pressed
        """
        dialog = qt.QFileDialog(self)
        dialog.setFileMode(qt.QFileDialog.DirectoryOnly)

        if not dialog.exec_():
            dialog.close()
            return None

        return dialog.selectedFiles()[0]

    def exportAbsMatrices(self):
        """
        Callback to generate absorption matrices for the materials definitions
        (composition, density) and the required density
        """
        outputFolder = self.selectFolder()
        if outputFolder is None:
            return

        try:
            energy = float(self._energyQLE.text())
        except ValueError:
            logger.warning("Can't convert ernergy to a float")
            return

        data = self._mainWidget.maskToolWidget.plot.getImage(QSampleComposition.LEGEND_IMAGE).getData().shape
        selfAbsMatrix = numpy.zeros(data, dtype=numpy.float64)

        for materialName, materialDef in self._mainWidget.maskToolWidget.materials.items():
            physicalelmts.elementInstance.removeMaterials()
            # print(type(materialName))
            physMat = reconstrutils.convertToFisxMaterial(str(materialName),
                                                          materialDef)
            physicalelmts.elementInstance.addMaterial(physMat)

            cross_section_E_mat = physicalelmts.elementInstance.getElementMassAttenuationCoefficients(
                materialName, energy)

            composition = self._mainWidget.maskToolWidget.buildCurrentMaterialMatrix()
            # Note : energy is in keV in freeart AND in physx. So no need for conversion
            condition = numpy.in1d(composition.ravel(), materialName).reshape(composition.shape)

            selfAbsMatrix[condition] = cross_section_E_mat['total'][0] * materialDef['Density']

        fileName = 'absMat_' + str(energy) + 'keV.edf'
        outfile = os.path.join(outputFolder, fileName)
        reconstrutils.saveMatrix(data=selfAbsMatrix,
                                 fileName=outfile,
                                 overwrite=True)
