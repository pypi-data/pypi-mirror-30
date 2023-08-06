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
__date__ = "24/07/2016"

import numpy as np
from numpy.random import randint
from silx.gui import qt
from silx.gui.plot import PlotWindow, MaskToolsWidget
from silx.gui.plot.Colormap import Colormap
from silx.io import configdict
from tomogui.gui.materials.MaterialsFileDialog import MaterialDialog
from tomogui.gui.materials.MaterialEditor import MaterialGUI
from tomogui.gui.utils.QFileManagement import QFileSelection
from tomogui.gui.utils.ConfigurationActor import ConfigurationActor
import collections
import numpy
try:
    from silx.opencl.backprojection import Backprojection
    has_silx_fbp = True
except ImportError:
    has_silx_fbp = False
import sys
import os
import logging
try:
    from freeart.utils import reconstrutils
    from freeart.configuration import structs, fileInfo
    from freeart.utils import h5utils
    from freeart.configuration import config as freeartconfig
    from freeart.utils import sinogramselection
except ImportError:
    raise RuntimeWarning("freeart not found")

_logger = logging.getLogger("QSampleComposition")


class SampleCompDialog(qt.QDialog):
    """The dialog to edit the materials of a sample

    :param parent: the parent widget if any
    :param FluoConfig config: the configuration containing the materials to
                              edit.
    """

    def __init__(self, parent=None, config=None, materials=None):
        qt.QDialog.__init__(self, parent)
        self.setWindowTitle('Definition of the sample composition')
        self.setWindowFlags(qt.Qt.Widget)
        types = qt.QDialogButtonBox.Save | qt.QDialogButtonBox.Open | qt.QDialogButtonBox.Ok | qt.QDialogButtonBox.Cancel
        _buttons = qt.QDialogButtonBox(parent=self)
        _buttons.setStandardButtons(types)
        assert(materials is None or isinstance(materials, structs.Materials))
        assert(config is None or isinstance(config, freeartconfig.FluoConfig))
        self.mainWindow = QSampleComposition(parent=self,
                                             materials=materials,
                                             config=config)
        _buttons.button(qt.QDialogButtonBox.Open).clicked.connect(self.load)
        _buttons.button(qt.QDialogButtonBox.Save).clicked.connect(self.mainWindow.save)
        _buttons.button(qt.QDialogButtonBox.Ok).clicked.connect(self.accept)
        _buttons.button(qt.QDialogButtonBox.Cancel).clicked.connect(self.reject)

        self.setLayout(qt.QVBoxLayout())
        self.layout().addWidget(self.mainWindow)
        self.layout().addWidget(_buttons)

    def setMaterials(self, materials):
        self.mainWindow.setMaterials(materials)

    def load(self):
        self.mainWindow.load()

    def saveTo(self, outputFile):
        self.mainWindow.saveTo(outputFile)

    def _quit(self):
        """callback of the validate button"""
        self.close()

    def getMaterials(self, refFile):
        return self.mainWindow.getMaterials(refFile)


class QSampleComposition(qt.QWidget, ConfigurationActor):
    """
    Widget enabling to define the materials contained in a matrix

    :param parent: the Qt Parent of the widget
    :param Materials materials: state of the materials to edit 
    """

    LEGEND_IMAGE = "BCK_IMG"

    def __init__(self, parent=None, materials=None, config=None):
        assert materials is None or isinstance(materials, structs.Materials)
        qt.QWidget.__init__(self, parent)
        self.materials = None
        self.config = None
        self.setLayout(qt.QVBoxLayout())
        self.plot = PlotWindow(self,
                               position=False,
                               print_=False,
                               roi=False,
                               save=False,
                               control=False,
                               curveStyle=False,
                               copy=False,
                               logScale=False,
                               mask=False,
                               colormap=True)
        self.plot.setDefaultColormap(Colormap(name='viridis',
                                              normalization='linear',
                                              vmin=None,
                                              vmax=None))

        self.layout().addWidget(self.plot)
        self.maskToolWidget = MaterialMaskToolWidget(self.plot, self)
        self.layout().addWidget(self.maskToolWidget)

        self.fileSelection = QFileSelection(self,
                                            "Change background image")
        self.fileSelection.setToolTip('The background image should be the same '
                                      'dimension of the sample (original size) or after reduction.'
                                      'But those data has to be coherent otherwise we won\'t be able to run a reconstruction.'
                                      'The initial background is the selfAbsorption matrix if exists.'
                                      'Otherwise if silx FBP is available this is the FBP reconstruction of the absMat sinogram')
        self.fileSelection.sigFileSelected.connect(self._imageChanged)
        self.layout().addWidget(self.fileSelection)

        if config is not None:
            self.setConfig(config)
        else:
            self.setMaterials(materials)

    def clean(self):
        self.materials = None
        self.config = None
        self.plot.clear()
        self.fileSelection.clean()
        self.maskToolWidget.reset()

    def setConfig(self, config):
        assert(config is not None)
        assert (isinstance(config, freeartconfig.FluoConfig))
        self.config = config
        self.materials = config.materials
        self.setMaterials(self.materials)

        if self.config.absMat is not None and self.config.absMat.data is not None:
            if self.config.isAbsMatASinogram:
                self.tryToGuessBackground()
            else:
                self.addImage(numpy.zeros(self.config.absMat.data.shape))

    def tryToGuessBackground(self):
        # try to use the silx FBP to run a background image reconstruction
        try:
            if self.config.absMat is not None:
                if self.config.isAbsMatASinogram:
                    sino = self.config.absMat
                    if sino.data is None:
                        sino.loadData(refFile=None)
                    if sino.data is not None and has_silx_fbp is True:
                        assert sino.data.ndim is 2
                        nbAngles = sino.data.shape[0]
                        angles = numpy.linspace(self.config.minAngle,
                                                self.config.maxAngle,
                                                nbAngles)

                        sinoForRebuid = sinogramselection.getSelection(
                            projections=sino.data,
                            selection=self.config.projections)

                        angles = sinogramselection.getSelection(projections=angles,
                                                                selection=self.config.projections)

                        fbp = Backprojection(sino_shape=sinoForRebuid.shape,
                                             slice_shape=None,
                                             axis_position=self.config.center,
                                             angles=angles,
                                             filter_name=None,
                                             ctx=None,
                                             devicetype="all",
                                             platformid=None,
                                             deviceid=None,
                                             profile=False)
                        bckImg = fbp.filtered_backprojection(sinoForRebuid)
                        self.addImage(bckImg)
                else:
                    sino = self.config.absMat
                    if sino.data is None:
                        sino.loadData(refFile=None)
                    assert sino.data.ndim is 2
                    if sino.data is not None:
                        self.addImage(sino.data)
        except:
            _logger.warning(
                'failed to reconstruct the background image. Please enter it manually')

    def load(self):
        dialog = qt.QFileDialog(self)
        dialog.setAcceptMode(qt.QFileDialog.AcceptOpen)
        dialog.setWindowTitle("Select a file to load materials")
        dialog.setModal(1)
        dialog.setNameFilters(['HDF5 file *.h5 *.hdf *.hdf5'])

        if not dialog.exec_():
            dialog.close()
            return

        filePath = dialog.selectedFiles()[0]

        try:
            config = read(filePath)
            materials = config.materials
        except:
            _logger.info('fail to open the file as a fluoconfiguration file.'
                         'Try to open it as a simple materials file')
            materials = None
            config = None

        file_info_dict = fileInfo.H5MatrixFileInfo(
            filePath + structs.MaterialsDic.MATERIALS_DICT)
        file_info_comp = fileInfo.H5MatrixFileInfo(
            filePath + structs.MatComposition.MAT_COMP_DATASET)

        if materials is None:
            materials = structs.Materials(
                materials=structs.MaterialsDic(fileInfo=file_info_dict),
                matComposition=structs.MatComposition(fileInfo=file_info_comp))
            try:
                materials.loadData(filePath=filePath)
            except IOError:
                raise ValueError('Fail to open data, are you sure file exists')
            except KeyError:
                raise ValueError(
                    'Materials definition and the sample composition '
                    'can\'t be loaded seems like they are not existing '
                    'or set at uncommon location')
        if config is not None:
            self.setConfig(config)
        else:
            self.setMaterials(materials)

    def getShortToolTip(self):
        toTi = "In order to run a fluorescence reconstruction we need to get "
        toTi += "the self attenuation. if you can't furnish this information "
        toTi += "then we can deduce it frmo the absorption matrix and the "
        toTi += "sample composition"
        return toTi

    def setMaterials(self, materials):
        self.materials = materials
        if materials is not None:
            self.materials.loadData(filePath=None)
            if materials.materials.data is not None and \
                            materials.matComposition.data is not None:
                self.maskToolWidget.loadSampleComposition(self.materials)

    def getMaterials(self, h5File):
        if self.materials is None:
            self.materials = structs.Materials(
                materials=structs.MaterialsDic(data=None, fileInfo=None),
                matComposition=structs.MatComposition(data=None, fileInfo=None))

        self.materials.matComposition.data = self.maskToolWidget.buildCurrentMaterialMatrix()
        self.materials.materials.data = self.maskToolWidget.materials

        if h5File is not None:
            if self.materials.matComposition.fileInfo is None:
                self.materials.matComposition.fileInfo = fileInfo.H5MatrixFileInfo(
                    h5File + structs.MatComposition.MAT_COMP_DATASET)
            if self.materials.materials.fileInfo is None:
                self.materials.materials.fileInfo = fileInfo.H5MatrixFileInfo(
                    h5File + structs.MaterialsDic.MATERIALS_DICT)

        return self.materials

    def addImage(self, data):
        """
        Add the background image in the silx plot

        :param data: the data to display in the background
        """
        if len(data.shape) == 3:
            self.plot.addImage(data=reconstrutils.decreaseMatSize(data),
                               legend=self.LEGEND_IMAGE)
        else:
            self.plot.addImage(data=data, legend=self.LEGEND_IMAGE)

    def _imageChanged(self, event):
        """call back function when the file selection is called"""
        assert(event['event'] == "fileSelected")
        self.loadFile(event['filePath'])

    def loadFile(self, filePath):
        """
        Load the given file in the background of the widget
        """
        self.addImage(data=reconstrutils.LoadEdf_2D(filePath))

    def getMatDict(self):
        """Return the materials dictionary"""

    def saveTo(self, outputFile):
        assert(outputFile is not None)
        self.getMaterials(outputFile).saveTo(outputFile)

    def askForH5File(self):
        dialog = qt.QFileDialog()
        dialog.setAcceptMode(qt.QFileDialog.AcceptSave)
        dialog.setWindowTitle(
            "Select a file to store the sample composition")
        dialog.setModal(1)
        dialog.setNameFilters(['HDF5 file *.h5 *.hdf *.hdf5'])

        if not dialog.exec_():
            dialog.close()
            return

        output = dialog.selectedFiles()[0]
        ol = output.lower()
        if not (ol.endswith('.h5') or ol.endswith('.hdf5') or ol.endswith('.hdf')):
            output = output + '.h5'

        return output

    def save(self):
        """
        callback of the validate button
        """
        outputFile = self.askForH5File()

        # save data
        if outputFile is None:
            _logger.info('no output file has been given, material definition '
                         'will not be saved')
            return
        else:
            return self.saveTo(outputFile)

    def setAbsMat(self, absMat):
        if self.config is None:
            self.config = freeartconfig.FluoConfig(materials=self.materials)
        self.config.absMat = absMat

    def setIsAbsMatASino(self, isAbsMatASino):
        if self.config is None:
            self.config = structs.FluoConfig(materials=self.materials)
        self.config.isAbsMatASinogram = isAbsMatASino

    def setFluoSinograms(self, sinograms):
        if self.config is None:
            self.config = structs.FluoConfig(materials=self.materials)
        self.config.sinograms = sinograms

    def setReconsParam(self, center, minAngle, maxAngle, projections):
        if self.config is None:
            self.config = structs.FluoConfig(materials=self.materials)
        self.config.center = center
        self.config.minAngle = minAngle
        self.config.maxAngle = maxAngle
        self.config.projections = projections

    def loadConfiguration(self, config):
        self.setConfig(config)

    def saveConfiguration(self, config, refFile):
        outFile = refFile
        if refFile is not None:
            fn, file_extension = os.path.splitext(refFile)
            if file_extension.lower() not in ('.h5', '.hdf5', '.hdf'):
                m = self.getMaterials(None)
                needFileToStoreMaterials = m.materials.fileInfo is None or m.matComposition.fileInfo is None
                if needFileToStoreMaterials:
                    outFile = self.askForH5File()
                    if outFile is None:
                        _logger.warning('No file specify for materials and sample '
                                        'composition, won\'t be store')

        config.materials = self.getMaterials(outFile)
        config.materials.save()


class SampleCompositionTab(qt.QWidget, ConfigurationActor):
    """Contains the `QSample composition` with some control button
    """
    def __init__(self, parent=None, materials=None, config=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QVBoxLayout())
        self.mainWindow = QSampleComposition(parent=self, config=config, materials=materials)
        self.layout().addWidget(self.mainWindow)
        self._qpbTryGuessBack = qt.QPushButton('Try to guess background',
                                               parent=self)
        self._qpbTryGuessBack.setToolTip('we can try to deduce a raw shape of '
                                         'the sample. By using the absorption '
                                         'matrix if given or trying to '
                                         'reconstruct it using FBP')
        self.layout().addWidget(self._qpbTryGuessBack)
        self._qpbTryGuessBack.clicked.connect(self.mainWindow.tryToGuessBackground)

        widgetLoadSave = qt.QWidget(parent=self)
        self.layout().addWidget(widgetLoadSave)
        widgetLoadSave.setLayout(qt.QHBoxLayout())
        spacer = qt.QWidget()
        spacer.setSizePolicy(qt.QSizePolicy.Expanding,
                             qt.QSizePolicy.Minimum)
        widgetLoadSave.layout().addWidget(spacer)

        self._qpbLoadMat = qt.QPushButton('load', parent=widgetLoadSave)
        self._qpbLoadMat.setToolTip('Load materials definition contained in '
                                    'an other file')
        self._qpbLoadMat.clicked.connect(self.mainWindow.load)
        widgetLoadSave.layout().addWidget(self._qpbLoadMat)

        self._qpbSaveMat = qt.QPushButton('save', parent=widgetLoadSave)
        self._qpbSaveMat.setToolTip('Save materials definition into another '
                                    'file')
        self._qpbSaveMat.clicked.connect(self.mainWindow.save)
        widgetLoadSave.layout().addWidget(self._qpbSaveMat)

    def getShortToolTip(self):
        return self.mainWindow.getShortToolTip()

    def loadConfiguration(self, config):
        if not isinstance(config, freeartconfig.FluoConfig):
            _logger.info('SampleComposition not loaded because configuration '
                         'file is not fluo or compton')
            return
        self.mainWindow.loadConfiguration(config)

    def saveConfiguration(self, config, filePath):
        self.mainWindow.saveConfiguration(config, filePath)

    def clean(self):
        self.mainWindow.clean()


class MaterialMaskToolWidget(MaskToolsWidget.MaskToolsWidget):
    """
    The MaterialMaskToolWidget allow to draw on an image to define different
    materials inside a sample

    :param plot: the plot widget to be linked with
    :param parent: the parent widget if any
    """
    masks = {}  # link a mask of the MaskToolsWidget to a material
    items = {}  # link each item of the QList with his material
    materials = {}
    ALPHA = 8

    nextFreeMaskId = 1  # counter on the mask id attributed
    sampleComposition = None

    DEFAULT_DENSITY = 1.0

    def __init__(self, plot, parent=None):
        def hideUneededMaskTools():
            """Hide all widgets we don't want the user to used from the
            original MaskToolsWidget"""
            self.transparencyWidget.hide()
            self.levelWidget.hide()
            self.loadSaveWidget.hide()

        def initPhysicalMaterials():
            "Build the group box relative to the physical material selection"
            self.gbMaterials = qt.QGroupBox(self)
            layout = qt.QVBoxLayout()

            self.gbMaterials.setSizePolicy(qt.QSizePolicy.Expanding,
                                           qt.QSizePolicy.Expanding)
            self.qpbAddMaterial = qt.QPushButton("Add Material",
                                                 self.gbMaterials)
            self.qpbAddMaterial.setToolTip(
                "Define a new material in the sample")
            self.qpbAddMaterial.clicked.connect(self._addMaterialCallBck)
            self.qpbAddMaterial.setAutoDefault(True)
            layout.addWidget(self.qpbAddMaterial)
            # add the list of the material knowed
            self.listOfMasks = qt.QTableWidget(self)
            self.listOfMasks.setColumnCount(2)
            self.listOfMasks.setSelectionBehavior(
                qt.QAbstractItemView.SelectRows)
            self.listOfMasks.setHorizontalHeaderLabels(["Name", "Density (g.cm-3)"])
            self.listOfMasks.setSelectionMode(
                qt.QAbstractItemView.SingleSelection)
            self.listOfMasks.currentItemChanged.connect(
                self._currentItemChanged)
            layout.addWidget(self.listOfMasks)
            self.listOfMasks.itemDoubleClicked.connect(self._editMaterial)

            self.gbMaterials.setLayout(layout)
            self.layout().insertWidget(0, self.gbMaterials)

        super(MaterialMaskToolWidget, self).__init__(parent, plot)
        self.reset()

        # hide some functionality
        hideUneededMaskTools()

        # build the specificities of the widget (physical stuff)
        initPhysicalMaterials()

        layout = qt.QVBoxLayout()
        m = qt.QWidget(self)
        m.setLayout(self.layout())
        layout.addWidget(m)
        self.setLayout(layout)

        self.transparencySlider.setValue(self.ALPHA)

    def _editMaterial(self, item):
        matName = item.data(qt.Qt.DisplayRole)
        if matName not in self.materials:
            logger.warning('can\'t find back the material definition of %s' % matName)
            return

        materialName = item.data(qt.Qt.DisplayRole)
        material = self.materials[materialName].copy()
        msg = MaterialDialog(parent=None, material=material,
                             materialName=materialName)
        if msg.exec_() == qt.QMessageBox.Ok:
            materialName, material = msg.getSelectedMaterial()
        self.materials[item.data(qt.Qt.DisplayRole)] = material

    def reset(self):
        self.masks = {}
        self.items = {}
        self.materials = {}
        self.nextFreeMaskId = 1

    def loadSampleComposition(self, materials):
        """Load the mask from a sample composition"""
        assert isinstance(materials, structs.Materials)
        self.listOfMasks.clear()
        self.listOfMasks.setRowCount(0)

        if materials.matComposition.data is None:
            raise ValueError('Fail to load sample composition')
        if materials.materials.data is None:
            raise ValueError('Fail to load materials definition')

        self.reset()
        mask = np.zeros(materials.matComposition.data.shape, dtype=np.uint8)
        for materialName in materials.materials.data:
            assert materialName in materials.materials.data
            # for now the color is not saved in the file so we create a new one
            color = qt.QColor(randint(0, 255), randint(0, 255), randint(0, 255))
            self._addMask(materialName, materials.materials.data[materialName], color)
            mask[materials.matComposition.data == bytes(materialName.encode('utf-8'))] = self.nextFreeMaskId - 1

        self._mask.reset(shape=mask.shape)
        self.setSelectionMask(mask, copy=False)

    def _addMaterialCallBck(self):
        """Callback function when the add material is called"""
        msg = MaterialDialog()
        if msg.exec_() == qt.QMessageBox.Ok:
            materialName, material = msg.getSelectedMaterial()
            material['Density'] = self.DEFAULT_DENSITY
            self._addMask(materialName, material, msg.getColor())

    def _addMask(self, materialName, material, color):
        """Add a mask for the given physical material"""
        assert('Comment' in material)
        assert(type(color == qt.QColor))

        def createItem():
            itemMatName = qt.QTableWidgetItem(materialName,
                                              qt.QTableWidgetItem.Type)
            itemMatName.setFlags(qt.Qt.ItemIsSelectable | qt.Qt.ItemIsEnabled)
            rowCount = self.listOfMasks.rowCount()
            self.listOfMasks.setRowCount(rowCount+1)
            self.listOfMasks.setItem(rowCount, 0, itemMatName)

            itemMatDensity = qt.QLineEdit(str(material['Density']),
                                          parent=self.listOfMasks)
            itemMatDensity.setValidator(qt.QDoubleValidator(bottom=0.0))
            itemMatDensity.editingFinished.connect(self._updateMaterialDensity)

            self.listOfMasks.setCellWidget(rowCount,
                                           1,
                                           itemMatDensity)

            self.items[materialName] = itemMatName
            elemt = itemMatName.text()
            # convert the color
            silxColor = [
                color.red() / 255.0,
                color.green() / 255.0,
                color.blue() / 255.0
            ]
            self.setMaskColors(silxColor, self.masks[elemt])
            # add the corresponding color icon
            pixmap = qt.QPixmap(100, 100)
            pixmap.fill(color)
            icon = qt.QIcon(pixmap)
            itemMatName.setIcon(icon)

            self.listOfMasks.selectRow(rowCount)

            return itemMatName, itemMatDensity

        if materialName in self.masks:
            msg = qt.QMessageBox()
            msg.setText("A material under this name has already a mask")
            msg.exec_()
            return self.setCurrentMask(materialName)

        if self.nextFreeMaskId > self._maxLevelNumber:
            msg = qt.QMessageBox()
            msg.setText("You can t add no more mask, maximal number has been reach (255)")
            return msg.exec_()

        self.masks[materialName] = self.nextFreeMaskId
        self.materials[materialName] = collections.OrderedDict(material)

        createItem()
        self.nextFreeMaskId = self.nextFreeMaskId + 1

    def _currentItemChanged(self, item):
        """
        Callback when the user is selected an other material in the list
        (cf a different material)
        """
        if item:
            maskLevel = self.masks[item.text()]
            self.levelSpinBox.setValue(maskLevel)

    def _updateMaterialDensity(self):
        editedMaterial = self.listOfMasks.item(self.listOfMasks.currentRow(), 0).text()
        self.materials[editedMaterial]['Density'] = float(self.listOfMasks.cellWidget(self.listOfMasks.currentRow(), 1).text())

    def setCurrentMask(self, materialName):
        """
        set the current mask to the given materialName
        """
        if materialName in self.items:
            self.listOfMasks.setCurrentItem(self.items[materialName],
                                            qt.QItemSelectionModel.Select)

    def buildCurrentMaterialMatrix(self):
        """Create the matrice of materials from set of masks"""
        # for now : bad hack, change each time the mask
        mask = self.getSelectionMask()
        res = np.ndarray(shape=mask.shape, dtype='S10')
        # default value
        res[:] = ''
        # check color for all materials
        for material in self.masks:
            res[mask == self.masks[material]] = material

        return res


if __name__ == "__main__":
    import tempfile
    import shutil
    from freeart.utils import testutils as freeart_testutils

    tempdir = tempfile.mkdtemp()
    fluoConfig = freeart_testutils.createConfigFluo(tempdir,
                                                    addAbsMat=True,
                                                    withMaterials=True)
    global app  # QApplication must be global to avoid seg fault on quit
    app = qt.QApplication([])
    SampleCompDialog(config=fluoConfig).exec_()
    shutil.rmtree(tempdir)

