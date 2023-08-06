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
__date__ = "24/05/2016"

from silx.gui import qt
import os
import silx
import sys
import tempfile
import numpy
import tomogui
import tomogui.gui
import tomogui.utils as utils
from tomogui.configuration import config as tomoguiconfig
from tomogui.gui.datasource.QDataSourceWidget import QDataSourceWidget
from tomogui.gui.normalization.NormWidget import NormWidget
from tomogui.gui.reconsparam.ReconsParamWidget import ReconsParamWidget
from tomogui.gui.reconstruction import ReconsManager
from tomogui.gui.utils import guiutils
from tomogui.gui.utils import icons as tomoguiIcons
from tomogui.gui.utils.QFileManagement import ConfigurationMenu, QGiveFilePathOrSave
from tomogui.gui.utils.QFileManagement import H5_FILTER, EDF_FILTER
from tomogui.third_party.dialog.ImageFileDialog import ImageFileDialog
from tomogui.gui.datasource.tomoguiFileTypeCB import TomoGUIFileTypeCB
try:
    import freeart
    from freeart.configuration import config as freeartconfig
    from freeart.configuration import read, save, fileInfo, structs
    from freeart.configuration.config import retrieveInfoFile
    from freeart.utils.reconstrutils import decreaseMatSize
    from tomogui.gui.datasource.QDataSourceWidget import QDataSourceFluoWidget
    from tomogui.gui.materials.QSampleComposition import SampleCompositionTab
    hasfreeart = True
except ImportError:
    hasfreeart = False
    from tomogui.third_party.configuration import config as freeartconfig
    from tomogui.third_party.configuration import read, save, fileInfo, structs
    from tomogui.third_party.configuration.config import retrieveInfoFile
    from tomogui.third_party.edfutils import decreaseMatSize
import logging

_logger = logging.getLogger(__name__)


class ProjectWindow(qt.QMainWindow):
    """
    This is the main window to deal with a freeART reconsparam

    :param parent: the parent of the widget in the Qt hierarchy
    """
    def __init__(self, parent=None, cfgFile=None):
        qt.QMainWindow.__init__(self, parent)

        # menu bar
        self.menuBar = qt.QMenuBar()
        self.projectMenu = ConfigurationMenu(self.menuBar, fileCFGPath=cfgFile)

        # status bar
        self.statusBar().showMessage("welcome to freeart gui", 20000)

        # main widget
        self.mainWidget = MainWidget(self, self.statusBar())
        self.setCentralWidget(self.mainWidget)
        self._connectMenuBar()

        # tool bar
        self._buildToolBar()

        # load data if some existing
        if cfgFile is not None:
            self.setConfFile(cfgFile)

        # window properties
        self.show()

    def clean(self):
        self.mainWidget.clean()

    def setConfFile(self, cfgFile):
        assert(os.path.isfile)
        assert(ConfigurationMenu.isAValidConfigFile(cfgFile))

        self.projectMenu.setFileCFGPath(filePath=cfgFile, merge=False)
        self.mainWidget.loadConfigurationFromFile(cfgFile)
        self.saveAction.setEnabled(True)

    def _buildToolBar(self):
        """
        Build the toolbar
        """
        self.toolbar = qt.QToolBar('ToolBar')

        self.saveAction = self.projectMenu._menuBar.saveAction
        self.saveAsAction = self.projectMenu._menuBar.saveAsAction
        self.loadAction = self.projectMenu._menuBar.loadAction
        self.exitAction = qt.QAction('Exit', self)
        self.exitAction.setIcon(tomoguiIcons.getQIcon('exit'))
        self.exitAction.setShortcut(qt.QKeySequence.Quit)
        self.exitAction.triggered.connect(self.close)

        self.toolbar.addAction(self.loadAction)
        self.toolbar.addAction(self.saveAction)
        self.toolbar.addAction(self.saveAsAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.exitAction)

        self.addToolBar(qt.Qt.TopToolBarArea, self.toolbar)

        self.setWindowTitle('FreeART reconsparam configuration')
        self.show()

        # By default save is unvailable. Need a signal
        # ( from the Configuration Menu to be activated )
        self._updateSaveAction(False)
        self.projectMenu.sigSaveAvailable.connect(self._updateSaveAction)

    def _updateSaveAction(self, enable):
        """
        Deal with the enable param of the saveAction
        """
        self.saveAction.setEnabled(enable)
        if enable is True:
            self.saveAction.setShortcut(qt.QKeySequence.Save)
            self.saveAsAction.setShortcut(qt.QKeySequence())
        else:
            self.saveAction.setShortcut(qt.QKeySequence())
            self.saveAsAction.setShortcut(qt.QKeySequence.Save)

    def _connectMenuBar(self):
        """
        Connect the menu bar (project save/load) with the main widget
        """
        self.projectMenu.sigFileLoading.connect(
            self.mainWidget._loadConfiguration)
        self.projectMenu.sigFileSaving.connect(
            self.mainWidget._saveConfiguration)

    def filterOtherThan(self, id):
        """
        set the widget on for the given reconsparam type.

        :param id:
        :return:
        """
        self.mainWidget._tabWidget.dataSourceWidget.setReconstructionType(id)
        self.setWindowTitle(id)
        self.mainWidget._tabWidget.dataSourceWidget.qcbReconstructionType.hide()

    def setReconsFluoMode(self, opt):
        """
        Set the reconsparam from fluo to be made from albsorption files
        directly or from I0 and It

        :param opt: the reconsparam we want. Should be in
                    QDataSourceFluoWidget.RECONS_MODE
        :return:
        """
        assert opt in QDataSourceFluoWidget.RECONS_MODE
        self.mainWidget.getDataSourceWidget().qdsFluo.setFluoReconsMode(opt)

    def setSinoToRecons(self, reconsType, sinograms, names):
        self.mainWidget.setSinoToRecons(reconsType, sinograms, names)

    def setIt(self, it, name=None):
        self.mainWidget.setIt(it, name=name)

    def setI0(self, i0, name=None):
        self.mainWidget.setI0(i0, name=name)

    def setLogRecons(self, isLogRecons):
        """Set reconstruction mode for transmission reconstruction"""
        self.mainWidget.setLogRecons(isLogRecons)


class _MainTabWidget(qt.QTabWidget):
    """
    This is the tab widget used for the freeART reconsparam
    Tabs are :
       - dataSource : input for the file to treat
       - normalization : inputs used for the normalization
                         (as center of mass definition)
       - reconsparam parameters : the parameters of the reconsparam such
                                     as oversampling, number of iterations...
    """
    def __init__(self, parent=None):
        """
        Constructor

        :param parent: the parent of the widget in the Qt hierarchy
        """
        qt.QTabWidget.__init__(self, parent)

        self.dataSourceWidget = QDataSourceWidget(self)
        self.normWidget = NormWidget(self)
        self.reconsParamWidget = ReconsParamWidget(self)
        dataSources = [self.dataSourceWidget.qdsTx]
        if hasfreeart is True:
            self.materialsWidget = SampleCompositionTab(self)
            self.materialsWidget.isDisplayed = False

            self.normWidget.centeringWidget.groupRotationWidget.sigCenterchanged.connect(
                self.setMaterialsWidgetVisibility
            )
            self.dataSourceWidget.qdsFluo.sigRequireMaterials.connect(self.setMaterialsWidgetVisibility)
            self.reconsParamWidget.sigInfoForMaterialsChanged.connect(
                self.setMaterialsWidgetVisibility
            )
            dataSources.append(self.dataSourceWidget.qdsFluo)
            self.dataSourceWidget.qdsFluo.sigReconsModeChanged.connect(self._updateMatInfo)
        else:
            self.materialsWidget = None

        # is selected
        for dataSource in dataSources:
            dataSource.sigSinoRefChanged.connect(
                self.normWidget.centeringWidget.updateData)
            dataSource.sigSinoRefChanged.connect(
                self.reconsParamWidget._projectionSelector.setSinogram)
            dataSource.sigI0MightChanged.connect(
                self.normWidget.I0Normalization.setI0)
            dataSource.sigSinoRefDimChanged.connect(
                self.reconsParamWidget._sinogramDim_haschanged)

        # type of reconsparam
        self.dataSourceWidget.sigReconstructionTypeChanged.connect(
            self.reconsParamWidget._setReconstructionType)
        self.dataSourceWidget.sigReconstructionTypeChanged.connect(
            self.normWidget.reconstructionTypeChanged)
        self.dataSourceWidget.sigReconstructionTypeChanged.connect(
            self._reconstructionTypeChanged)

        # tab 0 : data source
        self.setTabToolTip(self.addTab(self.dataSourceWidget, "data source"),
                           self.dataSourceWidget.getShortToolTip())

        # tab 1 : centering
        self.setTabToolTip(self.addTab(self.normWidget, "normalization"),
                           self.normWidget.getShortToolTip())
        # tab 2 : reconsparam
        self._reconsParamScrollArea = qt.QScrollArea(parent=self)
        self._reconsParamScrollArea.setWidget(self.reconsParamWidget)
        self._reconsParamScrollArea.setWidgetResizable(True)
        self.setTabToolTip(self.addTab(self._reconsParamScrollArea, "reconstruction parameters"),
                           self.reconsParamWidget.getShortToolTip())

        self.setMaterialsWidgetVisibility(True)

        # will at least emit a signal to update other widgets
        self.dataSourceWidget._reconsTypeChanged()

    def _reconstructionTypeChanged(self, reconsType):
        if reconsType != freeartconfig._ReconsConfig.FLUO_ID:
            self.setMaterialsWidgetVisibility(False)

    def setMaterialsWidgetVisibility(self, visible):
        if hasfreeart is False:
            return
        if visible is True and self.materialsWidget.isDisplayed is False:
            self.dataSourceWidget.qdsFluo.sigInfoForMaterialsChanged.connect(
                self._updateMatInfo
            )
            self.materialsWidget.isDisplayed = True
            self.setTabToolTip(
                self.addTab(self.materialsWidget, "sample comsposition"),
                self.materialsWidget.getShortToolTip())
        if visible is False and self.materialsWidget.isDisplayed is True:
            self.removeTab(3)
            self.dataSourceWidget.qdsFluo.sigInfoForMaterialsChanged.disconnect(
                self._updateMatInfo
            )
            self.materialsWidget.isDisplayed = False

    def _updateMatInfo(self):
        """ this function is used to update information about materials
        information if there is a self abs or a fluorescence sinogram to deduce
        the backgroundimage"""
        if self.materialsWidget.isDisplayed is True:
            self.materialsWidget.mainWindow.setAbsMat(
                self.dataSourceWidget.qdsFluo.getAbsMat())
            self.materialsWidget.mainWindow.setIsAbsMatASino(
                self.dataSourceWidget.qdsFluo.isAbsMatASino())
            self.materialsWidget.mainWindow.setFluoSinograms(
                self.dataSourceWidget.qdsFluo.getSinograms())
            self.materialsWidget.mainWindow.setReconsParam(
                center=self.normWidget.centeringWidget.groupRotationWidget.getCenter(),
                minAngle=self.reconsParamWidget.getMinAngle(),
                maxAngle=self.reconsParamWidget.getMaxAngle(),
                projections=self.reconsParamWidget.getProjections(),
            )


class MainWidget(qt.QWidget):
    """
    This is the main widget for a freeART reconsparam.

    :param parent: the parent of the widget in the Qt hierarchy
    """
    def __init__(self, parent=None, statusBar=None):
        qt.QWidget.__init__(self, parent)

        self._parentStatusBar = statusBar

        layout = qt.QVBoxLayout()

        # add the tabWidget
        self._tabWidget = _MainTabWidget(self)
        layout.addWidget(self._tabWidget)

        # add the buttons to move between tabs
        self._qgbbuttons = qt.QGroupBox(self)
        layoutButtons = qt.QHBoxLayout()

        self._qbPreviousTab = qt.QPushButton("previous")
        self._qbPreviousTab.setIcon(tomoguiIcons.getQIcon('arrow_left'))
        self._qbPreviousTab.setAutoDefault(True)
        self._qbPreviousTab.clicked.connect(self._previousTabCallBack)
        layoutButtons.addWidget(self._qbPreviousTab)

        self._qbNextTab = qt.QPushButton("next")
        self._qbNextTab.setIcon(tomoguiIcons.getQIcon('arrow_right'))
        self._qbNextTab.setAutoDefault(True)
        self._qbNextTab.clicked.connect(self._nextTabCallBack)
        layoutButtons.addWidget(self._qbNextTab)

        self._updateNextAndPreviousEnable()
        self._tabWidget.currentChanged.connect(
            self._updateNextAndPreviousEnable)

        spacer = qt.QWidget()
        spacer.setSizePolicy(qt.QSizePolicy.Expanding,
                             qt.QSizePolicy.Minimum)

        layoutButtons.addWidget(spacer)

        self._qbReconstruct = qt.QPushButton("Run reconstruction")
        self._qbReconstruct.setToolTip(
            "Start the reconsparam from the given parameters")
        self._qbReconstruct.setIcon(tomoguiIcons.getQIcon('run'))
        self._qbReconstruct.setAutoDefault(True)
        f = self._qbReconstruct.font()
        f.setBold(True)
        f.setPointSize(12)
        self._qbReconstruct.setFont(f)
        self._qbReconstruct.clicked.connect(self._reconstruct)
        layoutButtons.addWidget(self._qbReconstruct)

        self._qgbbuttons.setFlat(True)
        self._qgbbuttons.setLayout(layoutButtons)
        layout.addWidget(self._qgbbuttons)

        self.setLayout(layout)

    def clean(self):
        self.getDataSourceWidget().clean()
        self.getNormalizationWidget().clean()
        self._tabWidget.materialsWidget.clean()

    def setSinoToRecons(self, reconsType, sinogramsData, names=None):
        """
        Set the GUI to run the reconstruction of the given sinograms in the
        given mode.

        .. note:: for Tx and FBP reconstruction we can now only deal with one
                  reconstruction. Multiple sinogram reconstruction is only
                  managed for fluorescence and compton.

        :param str reconsType: the type of reconstruction to run
        :param list sinogramsData: list of numpy arrays to reconstruct. Numpy
                                   nd arrays should be 2D.
        :param names: list of the names of the sinograms
        """
        def getFirstSinogram():
            if len(sinogramsData) > 0:
                return sinogramsData[0]
            return None

        def convertNdArayToFluoSino(arrays):
            res = []
            for iArray, array in enumerate(arrays):
                sino = structs.FluoSino(name='',
                                        fileInfo=None,
                                        physElmt=None,
                                        ef=1.0,
                                        selfAbsMat=None,
                                        data=decreaseMatSize(array))
                name = sino.h5defaultPath
                if names is not None:
                    name = names[iArray]
                sino.name = name
                res.append(sino)
            return res

        def convertNdArayToTxSino(arrays):
            res = []
            for iArray, array in enumerate(arrays):
                sino = structs.TxSinogram(name=names[iArray],
                                          data=decreaseMatSize(array))
                name = sino.h5defaultPath + '_' + str(iArray)
                if names is not None:
                    name=names[iArray]
                sino.name = name
                res.append(sino)
            return res

        if len(sinogramsData) is 0:
            _logger.info('list of sinogram is empty')
            return

        for sino in sinogramsData:
            assert isinstance(sino, numpy.ndarray)
            assert sino.ndim in (2, 3)

        if names:
            assert(type(names) in (list, tuple))
            if len(names) != len(sinogramsData):
                raise ValueError('names and sinogramsData have different length')
        else:
            names = []
            for i in range(len(sinogramsData)):
                names.append('sinogram_' + str(i))

        conf = None
        if reconsType == tomoguiconfig.FBPConfig.FBP_ID:
            conf = tomoguiconfig.FBPConfig()
            conf.sinograms = convertNdArayToTxSino(sinogramsData)
            conf.dampingFactor = 1.0/float(conf.sinograms[0].data.shape[0])
        elif hasfreeart is True:
            if reconsType == freeartconfig._ReconsConfig.TX_ID:
                conf = freeartconfig.TxConfig()
                conf.sinograms = convertNdArayToTxSino(sinogramsData)
                conf.dampingFactor = 1.0 / float(conf.sinograms[0].data.shape[0])
            elif reconsType in (freeartconfig._ReconsConfig.FLUO_ID,
                                freeartconfig._ReconsConfig.COMPTON_ID):
                conf = freeartconfig.FluoConfig()
                conf.reconsType = reconsType
                conf.sinograms = convertNdArayToFluoSino(sinogramsData)
                conf.dampingFactor = 1.0 / float(decreaseMatSize(getFirstSinogram()).shape[0])

        if conf is None:
            raise ValueError('Requested reconstruction type is not recognized')

        self.loadConfiguration(conf)

    def setIt(self, it, name=None):
        _it = structs.Sinogram(data=it,
                               name=name if name is not None else 'ItSinogram')
        self.getDataSourceWidget().qdsFluo.setIt(_it)

    def setI0(self, i0, name=None):
        assert isinstance(i0, numpy.ndarray)
        _i0 = structs.I0Sinogram(data=i0,
                                 name=name if name is not None else 'I0Sinogram')
        self.getNormalizationWidget().I0Normalization.setI0(_i0)

    def setLogRecons(self, isLog):
        self.getNormalizationWidget().I0Normalization._computeMinusLog.setChecked(isLog)

    def getReconsParamWidget(self):
        return self._tabWidget.reconsParamWidget

    def getNormalizationWidget(self):
        return self._tabWidget.normWidget

    def getDataSourceWidget(self):
        return self._tabWidget.dataSourceWidget

    def _updateNextAndPreviousEnable(self):
        """
        Deal with enable state for buttons next and previous
        """
        if self._tabWidget.currentIndex() == self._tabWidget.count() - 1:
            self._qbNextTab.setEnabled(False)
        else:
            self._qbNextTab.setEnabled(True)

        if self._tabWidget.currentIndex() == 0:
            self._qbPreviousTab.setEnabled(False)
        else:
            self._qbPreviousTab.setEnabled(True)

    def _nextTabCallBack(self):
        """
        Function called when the \'next\' button is preset
        """
        if self._tabWidget.currentIndex() < self._tabWidget.count() - 1:
            self._tabWidget.setCurrentIndex(self._tabWidget.currentIndex() + 1)
            self._updateNextAndPreviousEnable()

    def _previousTabCallBack(self):
        """
        Function called when the \'previous\' button is preset
        """
        if self._tabWidget.currentIndex() > 0:
            self._tabWidget.setCurrentIndex(self._tabWidget.currentIndex() - 1)
            self._updateNextAndPreviousEnable()

    def _saveConfiguration(self, event):
        """
        Callback function used when the user will press the saveConfiguration
        button.
        This will create a file containing every information needed to run a
        freeart reconsparam.

        :param event: the event received. Must be \'savingProject\' event
        """
        assert(event['event'] == "savingProject")
        if self._parentStatusBar:
            self._parentStatusBar.clearMessage()
            self._parentStatusBar.showMessage("saving project...", 1000)

        self.saveConfiguration(event['filePath'], event['merge'])

    def saveConfiguration(self, filePath, merge):
        """
        Save the current configuration to the given file paths
        """
        conf = self.getConfiguration(filePath)
        self._checkUnsavedData(conf, filePath)
        save(configuration=conf, filePath=filePath, overwrite=True, merge=merge)

        if self._parentStatusBar:
            self._parentStatusBar.clearMessage()
            self._parentStatusBar.showMessage("project saved", 1000)

    def _checkUnsavedData(self, conf, filePath):
        # check if some missing information according to the configuration file
        # If some missing ask to save data or give path to those data
        fn, file_extension = os.path.splitext(filePath)
        if file_extension.lower() in ('.h5', '.hdf', '.hdf5'):
            # Im this case data with missing fileInfo will be saved in the
            # config file
            return
        if hasattr(conf, 'sinograms') and conf.sinograms is not None:
            for sinogram in conf.sinograms:
                assert isinstance(sinogram, structs.Sinogram)
                if sinogram.data is not None and sinogram.fileInfo is None:
                    sinogram.fileInfo = self._askUserToSetInfoFile(sinogram)

    def _askUserToSetInfoFile(self, data):
        """
        Ask to the user where is the file associated to this data or create a data set

        :param data:
        """
        def getTitle():
            if isinstance(data, structs.Sinogram):
                return 'Request file information for sinogram %s' % data.name
            else:
                raise NotImplementedError('')

        def getInfo():
            if isinstance(data, structs.Sinogram):
                return 'Some data are not associated to any file information. \n' \
                       'In order to be able to retrieve all information please : \n' \
                       '   - give the path to the sinogram %s \n' \
                       '   - save the sinogram to a new file' % data.name
            else:
                raise NotImplementedError('')

        def getUnsaveWarning():
            if isinstance(data, structs.Sinogram):
                return 'Information concerning sinogram %s will not be saved' \
                       'So those data won\'t be loaded next time you load this' \
                       'configuration file' % data.name
            else:
                raise NotImplementedError('')

        assert isinstance(data, structs.DataStored)
        assert data.data is not None
        assert data.fileInfo is None
        dialog = QGiveFilePathOrSave(title=getTitle(),
                                     info=getInfo())
        if not dialog.exec_():
            _logger.warning(getUnsaveWarning())
            return None

        if dialog.result() == QGiveFilePathOrSave.SAVE_VAL:
            dialog = qt.QFileDialog(self)
            dialog.setAcceptMode(qt.QFileDialog.AcceptSave)
            dialog.setFileMode(qt.QFileDialog.AnyFile)

            dialog.setNameFilters([EDF_FILTER,
                                   H5_FILTER])
            if not dialog.exec_():
                dialog.close()
                return None

            outputFile = dialog.selectedFiles()[0]

            fn, file_extension = os.path.splitext(outputFile)
            if file_extension == '':
                if dialog.selectedNameFilter() == EDF_FILTER:
                    outputFile += '.edf'
                    file_extension = '.edf'
                elif dialog.selectedNameFilter() == H5_FILTER:
                    outputFile += '.h5'
                    file_extension = '.h5'

            if file_extension.lower().endswith('.edf'):
                index = 0
            else:
                index = data.h5defaultPath
            data.fileInfo = retrieveInfoFile(str(outputFile), index)
            data.save()
            return data
        else:
            assert dialog.result() == QGiveFilePathOrSave.GIVE_VAL
            dialogOpen = ImageFileDialog(self)
            dialogOpen.setFileType(TomoGUIFileTypeCB(dialog))

            result = dialogOpen.exec_()
            if not result:
                return
            s = str(dialogOpen.selectedPath()).split('::')
            uri = '0'
            assert len(s) <= 2
            if len(s) == 2:
                uri = s[1]
            filePath = s[0]
            data.fileInfo = fileInfo.H5MatrixFileInfo(filePath + '::' + uri)
            return data

    def getConfiguration(self, configFile):
        if self.getReconstructionType() is tomoguiconfig.FBPConfig.FBP_ID:
            conf = tomoguiconfig.FBPConfig()
        elif hasfreeart is True:
            if self.getReconstructionType() in (freeartconfig._ReconsConfig.COMPTON_ID,
                                               freeartconfig._ReconsConfig.FLUO_ID):
                conf = freeartconfig.FluoConfig()
            elif self.getReconstructionType() == freeartconfig._ReconsConfig.TX_ID:
                conf = freeartconfig.TxConfig()
            else:
                raise ValueError('reconsparam type not recognized')
        else:
            raise NotImplementedError('reconsparam type not managed')

        conf.reconsType = self.getReconstructionType()
        conf.softReconsVersion = {}
        if self.getReconstructionType() is tomoguiconfig.FBPConfig.FBP_ID:
            conf.softReconsVersion['silx'] = silx.version
        else:
            conf.softReconsVersion['freeart'] = freeart.version

        conf.softReconsVersion['tomogui'] = tomogui.version

        self.getDataSourceWidget().saveConfiguration(conf, refFile=configFile)
        self.getNormalizationWidget().saveConfiguration(conf)
        self._tabWidget.reconsParamWidget.saveConfiguration(conf)
        if hasfreeart is True and self._tabWidget.materialsWidget.isDisplayed is True:
            self._tabWidget.materialsWidget.saveConfiguration(conf, configFile)
        return conf

    def setReconstructionType(self, reconsType):
        self.getDataSourceWidget().setReconstructionType(reconsType)

    def loadConfigurationFromFile(self, filePath):
        """
        Update the widget fron a configuraton file
        :param filePath: The path of the configuration file.
                         Warning: This must be a '.cfg' file
        """
        config = read(filePath)
        self.loadConfiguration(config)

    def loadConfiguration(self, config):
        # bad hack : we are looking for the reconsparam type.
        # Silx configparser as the freeart configparser are able to get it
        # since it is the same structure used for this option
        self.setReconstructionType(config.reconsType)
        self.getDataSourceWidget().loadConfiguration(config)
        self.getNormalizationWidget().loadConfiguration(config)
        self._tabWidget.reconsParamWidget.loadConfiguration(config)
        if hasfreeart is True:
            self._tabWidget.materialsWidget.loadConfiguration(config)

    def _loadConfiguration(self, event):
        """
        Callback function for the \'loadingProject event'\.
        :param event: The event received. Must be a \'loadingProject\' event
        """
        if self._parentStatusBar:
            self._parentStatusBar.clearMessage()
            self._parentStatusBar.showMessage("loading project...", 5000)
        assert(event['event'] == "loadingProject")
        filePath = event['filePath']

        self.loadConfigurationFromFile(filePath)
        if self._parentStatusBar:
            self._parentStatusBar.clearMessage()
            self._parentStatusBar.showMessage("load completed", 5000)

    def getReconstructionType(self):
        return self.getDataSourceWidget().getReconstructionType()

    def _reconstruct(self):
        """
        Callback of the reconstruct event
        """
        # save current configuration in a tmp file
        tempDir = tempfile.mkdtemp()
        cfgFile = tempDir + "tomogui_to_freeart.h5"

        if guiutils.checkCanReconstructDialog(self.getConfiguration(cfgFile)):
            self.saveConfiguration(cfgFile, merge=False)
            plaformId, deviceId = self.getReconsParamWidget().getOpenCLDevice()
            ReconsManager.runReconstruction(self.getConfiguration(cfgFile),
                                            platformId=plaformId,
                                            deviceId=deviceId)


if __name__ == "__main__":
    """
    TODO
    """
    global app  # QApplication must be global to avoid seg fault on quit
    app = qt.QApplication([])

    splash = utils.getMainSplashScreen()
    app.processEvents()

    cfgFile = None
    if len(sys.argv) > 1 and sys.argv[1].endswith(".cfg"):
        cfgFile = sys.argv[1]

    mainWindow = ProjectWindow(cfgFile=cfgFile)
    mainWindow.show()
    splash.finish(mainWindow)

    app.exec_()
