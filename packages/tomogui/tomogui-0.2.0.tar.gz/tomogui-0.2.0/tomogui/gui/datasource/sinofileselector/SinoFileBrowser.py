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
__date__ = "08/08/2017"


from silx.gui import qt
from tomogui.third_party.dialog.ImageFileDialog import ImageFileDialog
from tomogui.gui.datasource.tomoguiFileTypeCB import TomoGUIFileTypeCB
from tomogui.gui.datasource.QMessageGroupFiles import QMessageGroupFiles
import numpy
import os
try:
    from freeart.configuration import structs, config as freeartconfig
    from freeart.utils.reconstrutils import tryToFindPattern
except ImportError:
    from tomogui.third_party.configuration import structs, config as freeartconfig
    from tomogui.third_party.pymcautils import tryToFindPattern


class BaseSinoFileBrowser(qt.QWidget):
    """
    This class allow to select a set of file containing fluorescence sinograms
    to be treated
    """
    sigSinogramHasBeenRemoved = qt.Signal(object)
    sigSinogramHasBeenAdded = qt.Signal(object)
    sigSinogramSelectedChanged = qt.Signal(object)

    def __init__(self, parent=None):
        def getToolTip():
            return "register all files containing fluorescence sinograms to be treated"

        qt.QWidget.__init__(self, parent)
        self.sinograms = {}
        """Associate a file to a dict of uri and uri to sinograms"""

        self.dictFileToItem = {}
        """Associate the top level items for each file"""
        self.listFiles = []
        """Registred files"""

        layout = qt.QVBoxLayout()
        layout.addWidget(self._buildViewAndModel())
        layout.addWidget(self._buildButtons())
        self.setLayout(layout)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setToolTip(getToolTip())

    def keyPressEvent(self, event):
        """Deal with keys event
            - del : remove the current file
        """
        # if the key pressed is delete :
        if type(event) == qt.QKeyEvent and event.key() == qt.Qt.Key_Delete:
            self._removeFileCallback()

    def _buildButtons(self):
        """Build the buttons to manage the list of files"""
        group = qt.QWidget(self)

        layout = qt.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        # spacer
        spacer = qt.QWidget()
        spacer.setSizePolicy(qt.QSizePolicy.Expanding,
                             qt.QSizePolicy.Minimum)
        layout.addWidget(spacer)

        layoutTreatedGroupButtons = qt.QVBoxLayout()
        layoutTreatedGroupButtons.addWidget(spacer)

        self._qpbRemoveFile = qt.QPushButton("Remove")
        self._qpbRemoveFile.clicked.connect(self._removeFileCallback)
        self._qpbRemoveFile.setAutoDefault(True)
        self._qpbAddFile = qt.QPushButton("Add")
        self._qpbAddFile.clicked.connect(self._addFileCallback)
        self._qpbAddFile.setAutoDefault(True)

        layout.addWidget(self._qpbRemoveFile)
        layout.addWidget(self._qpbAddFile)
        group.setLayout(layout)
        return group

    def _buildViewAndModel(self):
        """Build the view and the model of the Tree"""
        self.view = qt.QTreeWidget()
        self.view.setColumnCount(2)
        self.view.setHeaderLabels(('file', 'uri'))
        self.view.clicked[qt.QModelIndex].connect(self.currentChanged)

        return self.view

    def _addFileCallback(self):
        """Function callback when a file is added"""
        raise NotImplementedError('Abstract class')

    def addSinogram(self, sinogram, signalIt=True):
        """
        add the file to the tree
        If the file is in an new folder, will create the folder.
        Set the file has a child of her foler
        """
        assert sinogram
        if sinogram.fileInfo:
            assert(os.path.isfile(sinogram.fileInfo.getFile()))
            filePath = sinogram.fileInfo.getFile()
        else:
            filePath = 'unknow'

        if filePath not in self.listFiles:
            self.listFiles.append(filePath)

        if filePath is None:
            groupFiles = groupType = None
        else:
            groupFiles, groupType = tryToFindPattern(filePath)

            # ask the user if he want to group those files
            if len(groupFiles) > 0:
                dialog = QMessageGroupFiles(groupFiles, groupType, self)
                if dialog.exec_() == qt.QMessageBox.No:
                    groupType = None

        self._addFileToList(sinogram)
        assert(filePath in self.dictFileToItem)
        if signalIt:
            self.sigSinogramHasBeenAdded.emit(sinogram)

    def _addFileToList(self, sinogram):
        """
        add the given folder as a top level item
        """
        assert sinogram
        if sinogram.fileInfo:
            filePath = sinogram.fileInfo.getFile()
            uri = sinogram.fileInfo.getUri()
        else:
            filePath = 'unknow'
            uri = sinogram.name or ''

        # Add file item
        if filePath not in self.dictFileToItem:
            folderItem = qt.QTreeWidgetItem([filePath])
            self.dictFileToItem[filePath] = folderItem
            self.view.addTopLevelItem(self.dictFileToItem[filePath])
            self.sinograms[filePath] = {}
        else:
            folderItem = self.dictFileToItem[filePath]

        # add uri item
        assert filePath in self.sinograms
        if uri not in self.sinograms[filePath]:
            uriItem = qt.QTreeWidgetItem(['', uri])
            folderItem.addChild(uriItem)
            self.sinograms[filePath][uri] = sinogram

    def _removeFileCallback(self):
        """
        Remove selected items
        """
        def removeSinogram(fileName, uri):
            rmSinogram = self.sinograms[fileName][uri]
            self.sigSinogramHasBeenRemoved.emit(rmSinogram)
            del self.sinograms[fileName][uri]
            if len(self.sinograms[fileName]) is 0:
                del self.sinograms[fileName]
                del self.dictFileToItem[fileName]

        selectedItems = self.view.selectedItems()
        for selectedItem in selectedItems:
            # if we want to remove an entire file:
            isAFile = self.view.indexOfTopLevelItem(selectedItem) != -1
            # in the case we want to remove the entire file
            if isAFile or selectedItem.parent().childCount() == 1:
                if isAFile:
                    topLevelItem = selectedItem
                else:
                    topLevelItem = selectedItem.parent()
                fileName = topLevelItem.data(0, 0)

                for iChild in numpy.arange(0, topLevelItem.childCount()):
                    uri = topLevelItem.child(iChild).data(1, 0)
                    removeSinogram(fileName, uri)
                self.view.takeTopLevelItem(self.view.indexOfTopLevelItem(topLevelItem))
            else:
                # in the case we want to remove the only child
                fileName = selectedItem.parent().data(0, 0)
                uri = selectedItem.data(1, 0)
                removeSinogram(fileName, uri)
                selectedItem.parent().takeChild(
                    selectedItem.parent().indexOfChild(selectedItem))

    def clean(self):
        self.view.clear()
        self.sinograms = {}
        self.dictFileToItem = {}

    def currentChanged(self):
        """
        Function called when a new item is clicked.
        Will ask to the QFileInspector to update the file inspected from a
        signal
        """
        selectedItem = self.view.selectedItems()[0]
        isAFile = self.view.indexOfTopLevelItem(selectedItem) != -1
        if isAFile:
            self.sigSinogramSelectedChanged.emit(None)
        else:
            topLevelItem = selectedItem.parent()
            filePath = topLevelItem.data(0, 0)
            uri = selectedItem.data(1, 0)
            self.sigSinogramSelectedChanged.emit(self.sinograms[filePath][uri])

    def _itemIsAFolderItem(self, item):
        """Return True if the item represents a folder"""
        return (item in self.dictFileToItem)


class TxSinoFileBrowser(BaseSinoFileBrowser):
    iSinoName = 0
    def __init__(self, parent):
        BaseSinoFileBrowser.__init__(self, parent)

    def _addFileCallback(self):
        """Function callback when a file is added"""
        dialog = ImageFileDialog(self)
        dialog.setFileType(TomoGUIFileTypeCB(dialog))

        result = dialog.exec_()
        if result:
            s = str(dialog.selectedPath()).split('::')
            index = '0'
            assert len(s) <= 2
            if len(s) == 2:
                index = s[1]
            sinogram = structs.TxSinogram(
                fileInfo=freeartconfig.retrieveInfoFile(file=s[0],
                                                        index=index)
                )
            sinogram.name = 'sinogram_' + str(FluoSinoFileBrowser.iSinoName)
            FluoSinoFileBrowser.iSinoName += 1
            self.addSinogram(sinogram=sinogram)


class FluoSinoFileBrowser(BaseSinoFileBrowser):
    iSinoName = 0
    def __init__(self, parent):
        BaseSinoFileBrowser.__init__(self, parent)

    def _addFileCallback(self):
        """Function callback when a file is added"""
        dialog = ImageFileDialog(self)
        dialog.setFileType(TomoGUIFileTypeCB(dialog))

        result = dialog.exec_()
        if result:
            s = str(dialog.selectedPath()).split('::')
            index = '0'
            assert len(s) <= 2
            if len(s) == 2:
                index = s[1]
            sinogram = structs.FluoSino(
                fileInfo=freeartconfig.retrieveInfoFile(file=s[0],
                                                        index=index),
                physElmt='H',
                ef=1.0,
                selfAbsMat=None,
                name='sinogram_' + str(FluoSinoFileBrowser.iSinoName)
                )
            FluoSinoFileBrowser.iSinoName += 1

            self.addSinogram(sinogram=sinogram)