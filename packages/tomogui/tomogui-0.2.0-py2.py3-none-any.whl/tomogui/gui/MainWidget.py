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
__date__ = "07/08/2017"

import numpy
from silx.gui import qt
from tomogui import utils
from tomogui.configuration import config as tomoguiconfig
from tomogui.gui.ProjectWidget import ProjectWindow
from tomogui.gui.datasource.QDataSourceWidget import QDataSourceWidget
try:
    from freeart.configuration import config as freeartconfig
    from tomogui.gui.creator.AbsMatCreator import AbsMatCreator
    from tomogui.gui.datasource.QDataSourceWidget import QDataSourceFluoWidget
    freeart_missing = False
except ImportError:
    freeart_missing = True


class TomoguiMainWindow(qt.QWidget):
    """
    Window proposing all the possibility to use tomogui
    """

    LAYOUT_INDEX_LIMIT = 100

    def __init__(self, showOnlyReconsOpt=False, mockNoFreeart=False):
        qt.QWidget.__init__(self)

        self.mainWindow = None
        """The tomogui project main window"""
        self.creator = None
        """The tomogui absorption matrix creator"""

        self.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.setLayout(qt.QGridLayout())

        self.__addBuildAbsMatOpt()
        self.__addReconstructionOpt(mockNoFreeart=mockNoFreeart)
        self.__addLoadCfgOpt()

        spacer = qt.QWidget(parent=self)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding,
                             qt.QSizePolicy.Expanding)
        self.layout().addWidget(spacer,
                                self.LAYOUT_INDEX_LIMIT,
                                self.LAYOUT_INDEX_LIMIT)

        if showOnlyReconsOpt is True:
            self._qpbBuildAbsMat.hide()
            self._qpbLoadCfgFile.hide()
            self._qpbRunReconstruction.setChecked(True)
            self._qpbRunReconstruction.hide()

    def __addBuildAbsMatOpt(self):
        self._qpbBuildAbsMat = qt.QPushButton('Build absorption matrix',
                                              parent=self)
        self._qpbBuildAbsMat.setAutoDefault(True)
        self.layout().addWidget(self._qpbBuildAbsMat, 0, 0)
        self._qpbBuildAbsMat.pressed.connect(self.launchAbsMatCreator)

    def __addReconstructionOpt(self, mockNoFreeart):
        self._qpbRunReconstruction = qt.QPushButton('Run reconstruction',
                                                    parent=self)
        self._qpbRunReconstruction.setCheckable(True)
        self.layout().addWidget(self._qpbRunReconstruction, 1, 0)
        self._qpbRunReconstruction.setAutoDefault(True)
        self.__addSubReconsOpt(mockNoFreeart)

        self._setReconsOptsVisible(False)
        self._qpbRunReconstruction.toggled.connect(self._setReconsOptsVisible)

    def __addLoadCfgOpt(self):
        txt = 'Load reconsparam setup from .cfg'
        self._qpbLoadCfgFile = qt.QPushButton(txt, parent=self)
        self._qpbLoadCfgFile.setAutoDefault(True)
        self.layout().addWidget(self._qpbLoadCfgFile)
        self._qpbLoadCfgFile.pressed.connect(self._loadCfgFile)

    def __addSubReconsOpt(self, mockNoFreeart):
        # build reconsparam option
        self._reconsGrp = []

        self._qpbSilxFBP = qt.QPushButton('Silx filtered back projection reconsparam',
                                          parent=self)
        self._qpbSilxFBP.setAutoDefault(True)
        self._reconsGrp.append(self._qpbSilxFBP)
        self.layout().addWidget(self._qpbSilxFBP, 2, 1)
        self._qpbSilxFBP.pressed.connect(self._launchSilxFBP)

        if freeart_missing is False and mockNoFreeart is False:
            self._qpbTxRecons = qt.QPushButton('freeart transmission reconsparam',
                                               parent=self)
            self._qpbTxRecons.setAutoDefault(True)
            self._reconsGrp.append(self._qpbTxRecons)
            self.layout().addWidget(self._qpbTxRecons, 1, 1)
            self._qpbTxRecons.pressed.connect(self._launchFreeARTTx)

            self._qpbFluorescence = qt.QPushButton('freeart Fluorescence reconsparam',
                                                   parent=self)
            self._qpbFluorescence.setAutoDefault(True)
            self._qpbFluorescence.setCheckable(True)
            self._reconsGrp.append(self._qpbFluorescence)
            self.layout().addWidget(self._qpbFluorescence, 3, 1)

            self.__addSubFluoReconsOpt()

            self._setFluoOptsVisible(False)
            self._qpbFluorescence.toggled.connect(self._setFluoOptsVisible)

    def __addSubFluoReconsOpt(self):
        self._fluoOptGrp = []
        # from ItI0 opt
        self._qpbFluoFromItI0 = qt.QPushButton(
            QDataSourceFluoWidget.GEN_ABS_SELF_ABS_OPT,
            parent=self)
        self._qpbFluoFromItI0.setAutoDefault(True)
        self._fluoOptGrp.append(self._qpbFluoFromItI0)
        self.layout().addWidget(self._qpbFluoFromItI0, 3, 2)
        self._qpbFluoFromItI0.pressed.connect(self._launchFreeARTFluoItI0)

        # from AbsMat only opt
        self._qpbFluoFrmAbsMatOnly = qt.QPushButton(
            QDataSourceFluoWidget.GIVE_ABS_MAT_AND_SELF_ABS_MAT_OPT,
            parent=self)
        self._qpbFluoFrmAbsMatOnly.setAutoDefault(True)
        self.layout().addWidget(self._qpbFluoFrmAbsMatOnly, 4, 2)
        self._fluoOptGrp.append(self._qpbFluoFrmAbsMatOnly)
        self._qpbFluoFrmAbsMatOnly.setToolTip("""This option mean that you have
            the absorption matrix already computed but not the self attenuation
            matrices""")
        self._qpbFluoFrmAbsMatOnly.pressed.connect(
            self._launchFreeARTFluoFrmAbsMatOnly)

        # give all absorption matrices opt
        self._qpbFluoGiveAllAbsMat = qt.QPushButton(
            QDataSourceFluoWidget.GIVE_ABS_MAT_AND_SELF_ABS_MAT_OPT,
        parent=self)
        self._qpbFluoGiveAllAbsMat.setAutoDefault(True)
        self._fluoOptGrp.append(self._qpbFluoGiveAllAbsMat)
        self.layout().addWidget(self._qpbFluoGiveAllAbsMat, 5, 2)
        self._qpbFluoGiveAllAbsMat.pressed.connect(
            self._launchFreeARTFluoGiveAll)

    def _setReconsOptsVisible(self, visibility):
        for button in self._reconsGrp:
            button.setVisible(visibility)
        # deal with the fluo opt recons options
        if visibility is True:
            if self._qpbFluorescence.isChecked():
                self._setFluoOptsVisible(True)
        else:
            self._setFluoOptsVisible(False)

    def _setFluoOptsVisible(self, visibility):
        # if freeart not here then the gui for fluorescence is not created
        if not hasattr(self, "_fluoOptGrp"):
            return
        for button in self._fluoOptGrp:
            button.setVisible(visibility)

    def launchAbsMatCreator(self):
        self._getAbsMatCreator().show()

    def launchTomoguiproject(self):
        # TODO : hide some according to the option
        pass

    def _loadCfgFile(self):
        fileSelected = self._getCFGFile()

        if fileSelected is None:
            return
        elif not os.path.isfile(fileSelected):
            err = 'Given path is not a file: %s' %fileSelected
            raise ValueError(err)
        else:
            self._launchTomoguiProject(fileSelected)

    def _getCFGFile(self):
        dialog = qt.QFileDialog(self)
        dialog.setFileMode(qt.QFileDialog.AnyFile)
        dialog.setNameFilters(["CFG (*.cfg)"])

        if not dialog.exec_():
            dialog.close()
            return None
        else:
            return dialog.selectedFiles()[0]

    def _launchFreeARTTx(self):
        projectWin = self._getProjectWindow()
        projectWin.filterOtherThan(freeartconfig._ReconsConfig.TX_ID)
        projectWin.show()

    def _launchSilxFBP(self):
        projectWin = self._getProjectWindow()
        projectWin.filterOtherThan(tomoguiconfig.FBPConfig.FBP_ID)
        projectWin.show()

    def _launchFreeARTFluoItI0(self):
        projectWin = self._getProjectWindow()
        projectWin.filterOtherThan(freeartconfig._ReconsConfig.FLUO_ID)
        projectWin.setReconsFluoMode(
            QDataSourceFluoWidget.GEN_ABS_SELF_ABS_OPT)
        projectWin.show()

    def _launchFreeARTFluoFrmAbsMatOnly(self):
        projectWin = self._getProjectWindow()
        projectWin.filterOtherThan(freeartconfig._ReconsConfig.FLUO_ID)
        projectWin.setReconsFluoMode(
            QDataSourceFluoWidget.GIVE_ABS_MAT_GEN_SELF_ABS_OPT)
        projectWin.show()

    def _launchFreeARTFluoGiveAll(self):
        projectWin = self._getProjectWindow()
        projectWin.filterOtherThan(freeartconfig._ReconsConfig.FLUO_ID)
        projectWin.setReconsFluoMode(
            QDataSourceFluoWidget.GIVE_ABS_MAT_AND_SELF_ABS_MAT_OPT)
        projectWin.show()

    def _launchTomoguiProject(self, cfgFile):
        assert(os.path.isfile(cfgFile))
        projectWin = self._getProjectWindow()
        projectWin.loadConfigurationFromFile(cfgFile)
        projectWin.show()

    def _getProjectWindow(self):
        if self.mainWindow is None:
            splash = utils.getMainSplashScreen()
            self.mainWindow = ProjectWindow(parent=self, cfgFile=None)
            splash.finish(self.mainWindow)
        return self.mainWindow

    def _getAbsMatCreator(self):
        if self.creator is None:
            splash = utils.getMainSplashScreen()
            self.creator = AbsMatCreator(parent=self)
            splash.finish(self.creator)
        return self.creator


if __name__ == '__main__':
    app = qt.QApplication.instance() or qt.QApplication([])
    mainWindow = qt.QMainWindow()
    widget = TomoguiMainWindow()
    mainWindow.setCentralWidget(widget)
    mainWindow.show()

    app.exec_()
