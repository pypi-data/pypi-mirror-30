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


import logging
import os
from silx.gui import qt
from silx.gui.plot import Plot2D
from tomogui.third_party.dialog.ImageFileDialog import ImageFileDialog
from tomogui.gui.datasource.tomoguiFileTypeCB import TomoGUIFileTypeCB
from tomogui.gui.utils import icons
try:
    from freeart.configuration import fileInfo, structs
    from freeart.configuration.config import retrieveInfoFile
    found_freeart = True
except ImportError:
    from tomogui.third_party.configuration import fileInfo, structs
    from tomogui.third_party.configuration.config import retrieveInfoFile
    found_freeart = False

_logger = logging.getLogger("Inputs")


EDF_FILTER = 'EDF (*.edf)'

H5_FILTER = 'hdf5 file *.h5 *.hdf *.hdf5'

CFG_FILTER = 'CFG *.cfg *.ini'


class QFileSelection(qt.QWidget):
    """
    A simple widget including a QButton and a QLineEdit to get a filePath
    Behavior : whenn the user press the QpushButton then a dialog to get the
    file is displayed.
    Once the user have selected a file, the path will be register to the
    QLineEdit
    """

    sigFileSelected = qt.Signal(object)
    """signal emitted when the file is changed"""

    def __init__(self, parent, buttonText="Select file", horizontalLayout=True):
        """
        Constructor
        :param parent: The parent of the widget
        :param buttonText: The text to set to the QPushButton
        :param horizontalLayout: True if we want to set the QPushButton and the
                                 QLineEdit in an horizontal layout. If False
                                 will be stored in a vertical layout.
        """
        # TODO : should also be able to select a sinogram in an hdf5 file
        super(QFileSelection, self).__init__(parent)
        if horizontalLayout:
            layout = qt.QHBoxLayout()
        else:
            layout = qt.QVBoxLayout()

        self._fileName = "::"

        self._qtbSelectFile = qt.QPushButton(buttonText)
        self._qtbSelectFile.setAutoDefault(True)
        self._qtbSelectFile.clicked.connect(self.selectFile)
        self._qteFileSelected = qt.QLineEdit(self._fileName)
        self._qteFileSelected.text = ''

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._qteFileSelected)
        layout.addWidget(self._qtbSelectFile)
        self.data = None

        self.setLayout(layout)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.setToolTip("Select file")

    def selectFile(self):
        """
        The callback when the user will press SelectFile button.
        if a file is sected then the event "newFileSelected" will be emitted
        """
        dialog = ImageFileDialog(self)
        dialog.setFileType(TomoGUIFileTypeCB(dialog))

        result = dialog.exec_()
        if not result:
            return

        s = str(dialog.selectedPath()).split('::')
        uri = '0'
        assert len(s) <= 2
        if len(s) == 2:
            uri = s[1]
        filePath = s[0]
        self.setFileSelected(fileSelected=filePath, uri=uri)

    def getFileInfo(self):
        spts = str(self._qteFileSelected.displayText()).split('::')
        filePath = spts[0]
        uri = '' if len(spts) is 1 else spts[1]
        return retrieveInfoFile(file=filePath, index=uri)

    def getFileSelected(self):
        """

        :return: the path of the file selected
        """
        spts = str(self._qteFileSelected.displayText()).split('::')
        filePath = spts[0]
        return filePath

    def setFileSelected(self, fileSelected, uri):
        """
        set the file selected path

        :param fileSelected: the path we want to set
        """
        self._qteFileSelected.setText(fileSelected + "::" + str(uri))
        if os.path.isfile(fileSelected):
            # emit signal that file has changed
            self.setToolTip(fileSelected)
            ddict = {}
            ddict['event'] = "fileSelected"
            ddict['filePath'] = str(fileSelected)
            ddict['uri'] = str(uri)
            self.sigFileSelected.emit(ddict)
        else:
            # Notice the user that is file doesn't exists
            info = 'File %s setted does not exists.' % fileSelected
            _logger.info(info)

    def setText(self, txt):
        """
        Set the text to the QPushButton

        :param txt: The new text if the QPushButton, must be str
        """
        assert(type(txt) == str)
        self._qtbSelectFile.setText(txt)

    def clean(self):
        self._fileName = "::"
        self._qteFileSelected.setText(self._fileName)


class Q2DDataSelection(qt.QWidget):

    sigDataStoredChanged = qt.Signal()
    """Signal emitted when the sinogram change"""

    def __init__(self, text, parent=None):
        qt.QWidget.__init__(self, parent)
        self.dataStored = structs.DataStored()
        self._plot = None
        self.setLayout(qt.QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(4)

        self._nameAndViewWidget = qt.QWidget(parent=self)
        self._nameAndViewWidget.setLayout(qt.QHBoxLayout())
        self._nameAndViewWidget.layout().setSpacing(4)
        self._nameAndViewWidget.layout().setContentsMargins(0, 0, 0, 0)

        self.layout().addWidget(self._nameAndViewWidget)

        self._nameLabel = qt.QLabel('', parent=self._nameAndViewWidget)
        self._nameAndViewWidget.layout().addWidget(self._nameLabel)
        spacer = qt.QWidget()
        spacer.setSizePolicy(qt.QSizePolicy.Expanding,
                             qt.QSizePolicy.Minimum)
        self._nameAndViewWidget.layout().addWidget(spacer)
        self._viewButton = qt.QPushButton('view',
                                          parent=self._nameAndViewWidget)

        self._viewButton.setSizePolicy(qt.QSizePolicy.Preferred,
                                       qt.QSizePolicy.Preferred)
        self._nameAndViewWidget.layout().addWidget(self._viewButton)

        self._fileSelection = QFileSelection(parent=self, buttonText=text)
        self.layout().addWidget(self._fileSelection)

        self._viewButton.pressed.connect(self.plotSinogram)

        self._fileSelection.sigFileSelected.connect(self._updateFileInfo)

    def setDataStored(self, dataStored):
        if dataStored is None:
            return
        self.dataStored = dataStored
        if dataStored.fileInfo is not None:
            self._fileSelection.setFileSelected(dataStored.fileInfo.getFile(),
                                                dataStored.fileInfo.location)
        else:
            self._fileSelection.setFileSelected('','')
        if dataStored.name is not None:
            self._nameLabel.setText(dataStored.name)

        self.sigDataStoredChanged.emit()

    def getDataStored(self):
        return self.dataStored

    def plotSinogram(self):
        if self.dataStored:
            if self.dataStored.data is None:
                self.dataStored.loadData(refFile=None)
            if self.dataStored.data is not None:
                assert self.dataStored.data.ndim is 2
                self._getPlot().addImage(self.dataStored.data)
                if self.dataStored.name is not None:
                    self._getPlot().setWindowTitle(self.dataStored.name)
                self._getPlot().show()

    def _getPlot(self):
        if self._plot is None:
            self._plot = Plot2D(parent=None)
        return self._plot

    def _updateFileInfo(self):
        self.dataStored.fileInfo = self._fileSelection.getFileInfo()

    def setText(self, txt):
        self._fileSelection.setText(txt)


class QFolderSelection(qt.QWidget):
    """
    As QFileSelection but for folders
    """
    sigFolderSelected = qt.Signal(object)

    def __init__(self, parent, buttonText="Select folder",
                 horizontalLayout=True):
        super(QFolderSelection, self).__init__(parent)
        if horizontalLayout:
            layout = qt.QHBoxLayout()
        else:
            layout = qt.QVBoxLayout()

        self._fileName = ""

        self._qtbSelectFolder = qt.QPushButton(buttonText)
        self._qtbSelectFolder.setAutoDefault(True)
        self._qtbSelectFolder.clicked.connect(self.selectFolder)
        self._qteFolderSelected = qt.QLineEdit(self._fileName)
        self._qteFolderSelected.text = ''

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        if horizontalLayout:
            layout.addWidget(self._qteFolderSelected)
            layout.addWidget(self._qtbSelectFolder)
        else:
            layout.addWidget(self._qtbSelectFolder)
            layout.addWidget(self._qteFolderSelected)

        self.data = None

        self.setLayout(layout)

        self.setToolTip("select folder")

    def selectFolder(self):
        """
        Function called when the QPushButton has been pressed
        """
        dialog = qt.QFileDialog(self)
        dialog.setFileMode(qt.QFileDialog.DirectoryOnly)

        if not dialog.exec_():
            dialog.close()
            return

        folderSelected = dialog.selectedFiles()[0]
        self.setFolderSelected(folderSelected)

    def getFolderSelected(self):
        """

        :return: the path of the folder selected

        .. note:: display text should be the same value as text but in one case
                  failed. haven t look further, now using displayText.
        """
        return str(self._qteFolderSelected.displayText())

    def setFolderSelected(self, folderPath):
        """
        Set the path of the folder selected
        :param folderPath: the path of the folder
        """
        self._qteFolderSelected.setText(folderPath)
        if os.path.exists(folderPath):
            # emit signal that file has changed
            ddict = {}
            ddict['event'] = "folderSelected"
            ddict['filePath'] = str(folderPath)
            self.sigFolderSelected.emit(ddict)
        else:
            # Notice the user that is file doesn't exists
            info = 'Folder %s setted does not exists.' % folderPath
            _logger.info(info)


class QProjectFileDialog(qt.QFileDialog):
    """
    Dialog to select the file to save the project.
    Contains also an option to save all the dataset in the file (if .h5 only)
    """
    def __init__(self, parent, defaultMerge=False, showMergeOpt=True,
                 nameFilters=None):
        qt.QFileDialog.__init__(self, parent)
        self.setAcceptMode(qt.QFileDialog.AcceptSave)
        self.setWindowTitle("Save project")
        self.setModal(1)
        self.setLayout(qt.QVBoxLayout())

        _nameFilters = nameFilters
        if _nameFilters is None:
            _nameFilters = [H5_FILTER, CFG_FILTER]
        self.setNameFilters(_nameFilters)

        self._qcheckBoxGroupDataset = qt.QCheckBox('Save all dataset in the project file',
                                                   parent=self)
        self._qcheckBoxGroupDataset.setToolTip('If this option is activate then the file will be '
                                               'fully containing the reconstruction data')
        self._qcheckBoxGroupDataset.setChecked(defaultMerge)
        self._qcheckBoxGroupDataset.setVisible(showMergeOpt)
        self.layout().addWidget(self._qcheckBoxGroupDataset)
        self.filterSelected.connect(self.changeOpt)

    def changeOpt(self, filter):
        self._qcheckBoxGroupDataset.setVisible(filter == H5_FILTER)

    def isDataSetShouldBeMerged(self):
        return self.selectedNameFilter() == H5_FILTER and self._qcheckBoxGroupDataset.isChecked()


class ConfigurationMenu(qt.QObject):
    """
    class to create a ToolBar containing some simple actions :
        - open project : open a configuration file
        - save project
        - save project as

    ..Note :: this is a simple class which only create needed action and emit
              signals
    """

    sigFileLoading = qt.Signal(object)
    """emitted when a new file is loaded"""
    sigFileSaving = qt.Signal(object)
    """emitted when a new file is loaded"""
    sigSaveAvailable = qt.Signal(object)
    """emitted to notice that the save action is available or not"""

    def __init__(self, menuBar, parent=None, fileCFGPath=None):
        """Constructor"""
        qt.QObject.__init__(self, parent)
        self._menuBar = menuBar
        self.fileCFG = fileCFGPath
        self.merge = False

        self._setCFGProjectMenu()

        self.setFileCFGPath(self.fileCFG, createIfNeeded=True, merge=self.merge)

    def _setCFGProjectMenu(self):
        """
        Setup the menu bar to include the project tab
        """
        menu = self._menuBar.addMenu("&Project")

        self._menuBar.loadAction = qt.QAction(
            icons.getQIcon('document-open'),
            'load', None)
        self._menuBar.loadAction.setToolTip(
            'Load a project saved in a cfg file')
        self._menuBar.loadAction.triggered.connect(self._loadActionTriggered)
        menu.addAction(self._menuBar.loadAction)

        self._menuBar.saveAction = qt.QAction(
            icons.getQIcon('document-save'),
            'save', None)
        self._menuBar.saveAction.setToolTip(
            'Save the project to the current cfg file')
        self._menuBar.saveAction.triggered.connect(self._saveActionTriggered)
        menu.addAction(self._menuBar.saveAction)

        self._menuBar.saveAsAction = qt.QAction(
            icons.getQIcon('document-save-as'),
            'save_as', None)
        self._menuBar.saveAsAction.setToolTip(
            'Save the project to the cfg given by the user')
        self._menuBar.saveAsAction.triggered.connect(self._saveAsActionTriggered)
        menu.addAction(self._menuBar.saveAsAction)

        return menu

    def _saveActionTriggered(self):
        """
        called when the save action is triggered.
        Behavior: simply emit a sigFileSaving signal and let the connected
        class/function do the work
        """
        assert(os.path.isfile(self.fileCFG))
        # emit signal that we can save this project
        ddict = {}
        ddict['event'] = "savingProject"
        ddict['filePath'] = self.fileCFG
        ddict['merge'] = self.mergeData
        self.sigFileSaving.emit(ddict)

    def _saveAsActionTriggered(self):
        """
        called when the save as action is triggered.
        Behavior: if no file as been registred to save the configuration ask
        one to the user.
        Then act as if the saveAction as been triggered
        """
        # request the user the new file to save stuff
        dialog = QProjectFileDialog(self._menuBar)

        if not dialog.exec_():
            dialog.close()
            return

        newFile = dialog.selectedFiles()[0]
        fn, file_extension = os.path.splitext(newFile)
        if file_extension.lower() not in ('.cfg', '.ini', '.h5', '.hdf5'):
            newFile = newFile + '.h5'

        mergeOpt = dialog.isDataSetShouldBeMerged()
        # set the new path
        if self.setFileCFGPath(filePath=newFile,
                               createIfNeeded=True,
                               merge=mergeOpt) is True:
            self._saveActionTriggered()
            self.sigSaveAvailable.emit(True)

    def _loadActionTriggered(self):
        """
        called when the load action is triggered.
        Behavior : check that the given file is correct then emit a
        sigFileLoading signal
        """
        # Open a dialog and get the new file and path
        dialog = qt.QFileDialog(self._menuBar)
        dialog.setAcceptMode(qt.QFileDialog.AcceptOpen)
        dialog.setFileMode(qt.QFileDialog.AnyFile)
        dialog.setNameFilters(['HDF5 file *.h5 *.hdf *.hdf5',
                               "CFG *.cfg *.ini"])

        if not dialog.exec_():
            dialog.close()
            return

        newFile = dialog.selectedFiles()[0]

        # Check file is correct
        if not os.path.isfile(newFile):
            _logger.warning('Can\'t load this file, does not exists.')
            return

        # setting this file as the new current file project
        if self.setFileCFGPath(newFile, merge=False, createIfNeeded=False) is False:
            return

        # emit the loading signal and the new path to it
        ddict = {}
        ddict['event'] = "loadingProject"
        ddict['filePath'] = self.fileCFG
        self.sigFileLoading.emit(ddict)

    def _activeSaveAction(self, active):
        self._menuBar.saveAction.setEnabled(active)
        if active is True:
            self._menuBar.saveAction.setShortcut(qt.QKeySequence.Save)
            self._menuBar.saveAsAction.setShortcut(qt.QKeySequence())
        else:
            self._menuBar.saveAsAction.setShortcut(qt.QKeySequence.Save)
            self._menuBar.saveAction.setShortcut(qt.QKeySequence())

    def setFileCFGPath(self, filePath, merge, createIfNeeded=True):
        """
        set the new path if this file is an existing cfg file

        :param filePath: the path of the configuration file
        :param merge: if True then the different dataset will be merged in the
                      configuration file (the file must be a .h5)
        :param createIfNeeded: If true then if the file doesn't exists we will
                               create it
        """
        if filePath:
            self.mergeData = merge
            fn, file_extension = os.path.splitext(filePath)
            # if the extension is correct
            if file_extension.lower() in ('.cfg', '.ini', '.h5', '.hdf5'):
                if os.path.isfile(filePath):
                    self._activeSaveAction(True)
                    self.fileCFG = filePath
                    return True

                # if we need to create the file and the extension is correct
                if createIfNeeded:
                    _logger.info("Creating the file " + filePath)
                    open(filePath, 'w+').close()
                    self.fileCFG = filePath
                    self._activeSaveAction(True)
                    return True

            # if we need to create the file and the extension is incorrect
            if createIfNeeded:
                _logger.info("Creating the file " + filePath)
                open(filePath, 'w+').close()
                self.fileCFG = filePath
                self._activeSaveAction(True)
                return True

        self._menuBar.saveAction.setEnabled(False)
        if filePath is not None:
            if createIfNeeded:
                warn = "Can't set the file %s as the current project." % filePath
                warn += "Unable to create file"
                _logger.warning(warn)
            else:
                warn = "Can't set the file %s as the current project. " % filePath
                warn += "File does not exists"
                _logger.warning(warn)

        self.sigSaveAvailable.emit(False)
        return False

    def hasAValidFile(self):
        """

        :return: true if the current file self.fileCFG is valid
        """
        return self.fileCFG and self.isAValidConfigFile(self.fileCFG)

    @staticmethod
    def isAValidConfigFile(file):
        """

        :param file: the file path we want to check
        :return: True if the given file is considered has valid
        """
        fn, file_extension = os.path.splitext(file)
        if file:
            return (os.path.isfile(file) and file_extension.lower() in ('.cfg', '.h5', '.hdf5', '.ini'))
        else:
            return False


class QGiveFilePathOrSave(qt.QDialog):
    """
    Dialog to ask the user the path to a given dataset or a file to
    save the dataset
    """
    SAVE_VAL = 100
    GIVE_VAL = 101

    def __init__(self, title, info):
        qt.QDialog.__init__(self)
        self.setWindowTitle(title)
        self.setLayout(qt.QVBoxLayout())
        if info is not None and info != '':
            self.layout().addWidget(qt.QLabel(info, parent=self))

        widgetBtns = qt.QWidget(parent=self)
        widgetBtns.setLayout(qt.QHBoxLayout())
        self.layout().addWidget(widgetBtns)

        self._qpbGivePath = qt.QPushButton('Give path to dataset', widgetBtns)
        self._qpbGivePath.clicked.connect(self._requestGivePath)
        widgetBtns.layout().addWidget(self._qpbGivePath)

        self._qpbSaveDataset = qt.QPushButton('Save dataset', widgetBtns)
        self._qpbSaveDataset.clicked.connect(self._requestSave)
        widgetBtns.layout().addWidget(self._qpbSaveDataset)

        self._qpbCancel = qt.QPushButton('Skip', widgetBtns)
        self._qpbCancel.clicked.connect(self.reject)
        widgetBtns.layout().addWidget(self._qpbCancel)

    def _requestSave(self):
        self.done(self.SAVE_VAL)

    def _requestGivePath(self):
        self.done(self.GIVE_VAL)

if __name__ == '__main__':
    app = qt.QApplication([])
    t = QGiveFilePathOrSave('this is the title', 'this is the informative text')
    print(t.exec_())

