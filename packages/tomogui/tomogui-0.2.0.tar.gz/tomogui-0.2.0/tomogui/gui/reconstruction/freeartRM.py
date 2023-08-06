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
__date__ = "14/11/2017"


from silx.gui import qt
from silx.gui import icons as silxIcons
from tomogui.gui.utils import icons, QFileManagement
from .ReconsManagerBase import ReconsManagerBase
from freeart.interpreter import GlobalConfigInterpreter as freeartinterpreter
from .reconsviewer import ReconstructionItViewer
from freeart.configuration import read as readConfigFile
from freeart.configuration import config as freeartconfig
from freeart.configuration import save
from freeart.utils import reconstrutils
from tomogui.gui.materials.QSampleComposition import SampleCompDialog
from tomogui.gui.reconsparam.ReconsParamWidget import ReconsParamWidget
from tomogui.gui.materials.QSampleComposition import SampleCompDialog
from freeart.utils.reconstrutils import decreaseMatSize
import h5py
import numpy
import os
import time
import logging

_logger = logging.getLogger(__name__)


class FreeartReconsManager(ReconsManagerBase):
    """
    This is the widget used to manage the freeart reconsparam

    :param parent: The parent QObject
    :param config: the configuration to be runned
    """
    threadInterpreterIterator = None
    """the thread used to run the reconsparam iteration throught the freeart
    interpreter"""

    def __init__(self, parent, config=None, interpreter=None):
        ReconsManagerBase.__init__(self, parent)
        # if this is a fluorescence reconstruction and information is missing
        # about the materials ask first to define the self abs.
        if config is None:
            assert interpreter is not None

        if interpreter is None:
            assert config is not None

        # check if the materials is needed
        _conf = interpreter.config if config is None else config
        if self._makeSureAbsMatIsOk(_conf) is False:
            return

        if self._makeSureSelfAbsMatAreOk(_conf) is False:
            return

        if interpreter is not None:
            self.freeartInterpreter = interpreter
        else:
            self.freeartInterpreter = freeartinterpreter(filePath=None, config=config)
            if config is None:
                err = """Not enought information to build the
                    QFreeARTReconstructionManager."""
                raise RuntimeError(err)
        self._dealWithSinogramsNames()
        self._buildGUI()

    def _buildGUI(self):

        self._mainWidget = qt.QWidget(parent=self)
        self._mainWidget.setLayout(qt.QVBoxLayout())
        self._mainWidget.layout().addWidget(
            self._getViewer(self.freeartInterpreter.config)
        )
        # add the progress bar at the bottom
        self.progressBar = qt.QProgressBar(self)
        self._mainWidget.layout().addWidget(self.progressBar)
        self.setCentralWidget(self._mainWidget)

        self._reconsMenu = ReconsControl(self, self.freeartInterpreter.config)
        self._reconsMenu.setContentsMargins(0, 0, 0, 0)
        self._reconsMenu._qpbSaveReconstruction.clicked.connect(
            self._saveReconstructions)
        self._reconsMenu._qpbQuit.clicked.connect(self._quit)

        self._connectReconsParametersWithTheGUI(self._reconsMenu.reconsParam)

        self._dockWidgetMenu = qt.QDockWidget(parent=self)
        self._dockWidgetMenu.layout().setContentsMargins(0, 0, 0, 0)
        self._dockWidgetMenu.setFeatures(qt.QDockWidget.DockWidgetMovable |
                                qt.QDockWidget.DockWidgetFloatable)
        self._dockWidgetMenu.setWidget(self._reconsMenu)
        self.addDockWidget(qt.Qt.RightDockWidgetArea, self._dockWidgetMenu)
        self._dockWidgetMenu.setAllowedAreas(qt.Qt.RightDockWidgetArea |
                                             qt.Qt.LeftDockWidgetArea)

        # connect quit button
        self._reconsMenu._qpbQuit.clicked.connect(self._quit)
        # connect iterate button
        self._reconsMenu._qpbIterate.clicked.connect(self._runIteratation)

        # in the case that the transmission reconsparam is only the first
        # step of the full reconsparam
        interpreter = self.freeartInterpreter
        buildFluoGB = interpreter.isAFluoOrComptonReconstruction() and \
                      interpreter.config.isAbsMatASinogram
        self._buildFluoReconstructionGB(buildFluoGB)

    def resetPlotsZoom(self):
        self.viewer.resetPlotsZoom()

    def _dealWithSinogramsNames(self):
        iUnknowSino = 0
        for sinogram in self.freeartInterpreter.config.sinograms:
            if sinogram.name in (None, ''):
                sinogram.name = 'sinogram_' + str(iUnknowSino)
                iUnknowSino += 1
            assert sinogram.data is not None

    def _makeSureSelfAbsMatAreOk(self, config):
        # check if we have enought information ot get the self abs matrix for
        # each fluorescence sinogram, otherwise ask for sample composition
        # to the user
        assert config is not None
        if config.reconsType == freeartconfig._ReconsConfig.FLUO_ID:
            allSinoHasSelfAbs = True
            for sinogram in config.sinograms:
                if sinogram.selfAbsMat is None:
                    allSinoHasSelfAbs = False
                    break

            materialsUnDefined = config.materials is None or \
                                 len(config.materials.materials) is 0
            if materialsUnDefined is True and not allSinoHasSelfAbs:
                diag = SampleCompDialog(config=config)
                if not diag.exec_():
                    return False
                else:
                    config.materials = diag.getMaterials(None)

        return True

    def _makeSureAbsMatIsOk(self, config):
        assert config is not None
        if config.reconsType == freeartconfig._ReconsConfig.FLUO_ID:
            if config.absMat.data is None or 0 in config.absMat.data.shape:
                msg = qt.QMessageBox(parent=self)
                msg.setIcon(qt.QMessageBox.Warning)
                msg.setText("Can't run reconstruction. No absorption matrix "
                            "defined.")
                msg.setInformativeText('Please generate the absorption matrix '
                                       'first')
                msg.exec_()
                exit(0)
        return True

    def getReconsMenu(self):
        return self._reconsMenu

    def _getViewer(self, config):
        """
        Return the appropriate viewer depending ont the type of
        reconstruction we want to run
        """
        if len(config.sinograms) > 0:
            self.viewer = ReconstructionItViewer(self,
                                                 self.freeartInterpreter)
        else:
            raise RuntimeError("Reconstruction type unrecognized")

        return self.viewer

    def _quit(self):
        """
        quit the application
        """
        if self.parent():
            self.parent().close()
        else:
            self.close()

    def _runIteratation(self):
        """
        Call the freeart interpreter to run some extra iteration
        """
        self.userRequestStopIteration = False
        assert(self.freeartInterpreter is not None)
        nbIteration = self._reconsMenu.getNbIterations()
        self._reconsMenu.lockIterationAction()

        if nbIteration > 0 and self.threadInterpreterIterator is None:
            self.progressBar.setRange(0, nbIteration)
            self.progressBar.setValue(0)

            self.threadInterpreterIterator = FreeARTReconstructionIteratorThread(
                self.freeartInterpreter, nbIteration)
            self._reconsMenu._qpbStopIterate.clicked.connect(
                self.threadInterpreterIterator.interupt)
            self.threadInterpreterIterator.sigAllIterationsEnded.connect(
                self._runIterationEnded)
            self.threadInterpreterIterator.sigOneIterationEnded.connect(
                self._oneIterationEnded)

            self.threadInterpreterIterator.start()

    def _runIterationEnded(self):
        """
        Callback when all iterations requested by the user are ended
        """
        # update history if needed
        if not self.threadInterpreterIterator.listenForInteruption:
            hist = "runned " + str(self.threadInterpreterIterator.nbIteration)\
                   + " iterations "
            self._reconsMenu.addToHistory(hist)
        self.viewer.update()
        self._reconsMenu.releaseIterationAction()
        self.threadInterpreterIterator = None
        self.sigReconstructionEnded.emit()

    def _oneIterationEnded(self):
        """
        Callback when one iteration of the freeartinterpreter is ended
        """
        self.progressBar.setValue(self.progressBar.value()+1)
        self._reconsMenu.addToHistory("runned one iteration ")
        self._reconsMenu.increaseTotalIteration(1)

    def _connectReconsParametersWithTheGUI(self, reconsParamGUI):
        """
        Connect all widget fron reconsParamGUI that the user can change during
        the reconsparam
        """
        assert(type(reconsParamGUI) == ReconsParamWidget)
        # the only parameters the user can change are
        # oversampling
        reconsParamGUI.qleOversampling.textChanged.connect(
            self._oversamplingValueChanged)
        # dumping factor
        reconsParamGUI.qleDampingFactor.textChanged.connect(
            self._dampingFactorChanged)
        # rayPointsCalculationMethod
        reconsParamGUI.qcbWithInterpolation.toggled.connect(
            self._rayPointsCalculationMethodChanged)
        reconsParamGUI.qcbWithoutInterpolation.toggled.connect(
            self._rayPointsCalculationMethodChanged)
        # outgoingRayAlgorithm
        reconsParamGUI.qcbOutgoingBeamCalculation.currentIndexChanged.connect(
            self._outgoingRayAlgorithmChanged)

    def _oversamplingValueChanged(self, newVal):
        """
        callback function when the oversampling changed
        """
        newVal = int(newVal)
        assert(type(newVal) == int)
        assert(type(newVal) > 0)
        if self.freeartInterpreter:
            self.freeartInterpreter.setOversampling(newVal)
            hist = "change oversampling for " + str(newVal)
            self._reconsMenu.addToHistory(hist)

    def _dampingFactorChanged(self, newVal):
        """
        callback function when the damping factor changed
        """
        newVal = float(newVal)
        assert(type(newVal) == float)
        if self.freeartInterpreter and (newVal > 0 and newVal <= 1.0):
            self.freeartInterpreter.setDampingFactor(newVal)
            hist = "change dampingFactor for " + str(newVal)
            self._reconsMenu.addToHistory(hist)

    def _rayPointsCalculationMethodChanged(self, newVal):
        """
        Callback when the 'Calculation method combobox' changed
        """
        assert(type(newVal) == int)
        if self.freeartInterpreter:
            self.freeartInterpreter.setRayPointCalculationMethod(newVal)
            hist = "change rayPointsCalculationMethods for " + str(newVal)
            self._reconsMenu.addToHistory(hist)

    def _outgoingRayAlgorithmChanged(self, newVal):
        """
        Callback when the 'Outgoing ray algorithm combobox' changed
        """
        assert(type(newVal) == int)
        if self.freeartInterpreter:
            self.freeartInterpreter.setOutgoingRayAlgorithm(newVal)
            hist = "change outgoingRayAlgorithm for " + str(newVal)
            self._reconsMenu.addToHistory(hist)

    def _buildFluoReconstructionGB(self, prepare):
        """
        If the transmission reconsparam is only the first step of the full
        reconsparam get ready to move to the fluorescence reconsparam

        :param prepare: True if this transmission reconsparam is a first
                        step to get the absorption matrix
        """
        self.isAFirstStepBeforeFluo = prepare
        if prepare:
            group = qt.QWidget(self)
            _btLayout = qt.QHBoxLayout()
            spacer = qt.QWidget(self)
            spacer.setSizePolicy(qt.QSizePolicy.Expanding,
                                 qt.QSizePolicy.Minimum)
            _btLayout.addWidget(spacer)

            pbText = "validate absorption matrix and go to "\
                     + self.freeartInterpreter.getReconstructionType()\
                     + " reconsparam"
            self._qpbGoToFluoRecons = qt.QPushButton(pbText)
            self._qpbGoToFluoRecons.setToolTip(
                "Store this reconsparam and start the fluorescence reconsparam")
            self._qpbGoToFluoRecons.setIcon(silxIcons.getQIcon('selected'))
            self._qpbGoToFluoRecons.setAutoDefault(True)
            self._qpbGoToFluoRecons.clicked.connect(
                self._prepareFluoReconstruction)
            _btLayout.addWidget(self._qpbGoToFluoRecons)
            _btLayout.addWidget(spacer)
            group.setLayout(_btLayout)
            self.layout().addWidget(group)

    def _prepareFluoReconstruction(self):
        """
        Function to move from the transmission reconsparam
        (to build an absorption matrix) to the fluorescence reconsparam.
        Callback of the _qpbGoToFluoRecons button
        """
        # check that the absorption matrice is ok
        data = self.freeartInterpreter.getReconstructionAlgorithms()[
            "TxReconstruction"].getPhantom()

        if len(data) == 0:
            msgBox = qt.QMessageBox()
            msgBox.setIcon(qt.QMessageBox.Warning)
            msgBox.setText(
                "You need to reconstruct the absorption matrix first.")
            msgBox.exec_()
            return

        if self.freeartInterpreter.config.isAFluoReconstruction():
            # ask for the sampleComposition if needed
            # In this case the sample composition can't have been created yet
            self.physElemtPainterWindow = SampleCompDialog(parent=self,
                                                           data=data)
            maskTool = self.physElemtPainterWindow.physElmtPainter.maskToolWidget
            maskTool.sigSelfAbsValidated.connect(
                self._goToFluoReconstructionSampleCompositionValidate)
            self.physElemtPainterWindow.setAttribute(qt.Qt.WA_DeleteOnClose)
            self.physElemtPainterWindow.show()
        else:
            self._moveToFluoReconstruction()

    def _moveToFluoReconstruction(self, selfAbsMat=None, matFile=None):
        """
        """
        def saveAbsMatRequest():
            # for now we are forcing the user to store the absMatrix in a edf file
            # ask user if he want to save the absMat and update the cfg file
            dialog = qt.QFileDialog(self)
            dialog.setFileMode(qt.QFileDialog.AnyFile)
            dialog.setNameFilters(["EDf (*.edf)"])
            if not dialog.exec_():
                dialog.close()
                return

            outputFile = dialog.selectedFiles()[0]
            if not outputFile.lower().endswith(".edf"):
                outputFile = outputFile + '.edf'

            # saving the sinogram
            reconstrutils.savePhantom(
                self.freeartInterpreter.getReconstructionAlgorithms()["TxReconstruction"].getPhantom(),
                outputFile)

            return outputFile

        def overwriteCFGFileOption():
            # for now we are forcing the user to overwrite the cfg file
            configuration = self.freeartInterpreter.config
            configuration.setFluoAbsMatFileIsASinogram(False)
            configuration.setFluoAbsorptionMatriceFile(str(outputFile))
            if selfAbsMat is not None:
                configuration.setFluoSelfAbsMatFile(selfAbsMat)
            else:
                # get ready for compton reconsparam
                configuration.setFluoSelfAbsMatFile(str(outputFile))
            if matFile is not None:
                configuration.setMaterialsFile(matFile)

            configuration.write()

            return configuration.getFile()

        outputFile = saveAbsMatRequest()
        confFile = overwriteCFGFileOption()
        assert(type(self.parent().centralWidget()) == FreeartReconsManager)

        # launch the waiting dialog
        progressDialog = qt.QProgressDialog("preparing GUI for freeart reconsparam",
                                            "Ok",
                                            0,
                                            0,
                                            self.parent())
        progressDialog.setRange(0, 1)
        progressDialog.setValue(0)
        progressDialog.show()

        try:
            # launch the thread to get the freeartconfig
            threadBuildInterpreter = FreeARTInterpreterThreadBuilder(confFile)
            progressDialog.update()

            threadBuildInterpreter.start()

            while (threadBuildInterpreter.isRunning()):
                progressDialog.repaint()
                app = qt.QApplication.instance() or qt.QApplication([])
                # dummy 'infinite' advancement.
                progressDialog.setMaximum(progressDialog.maximum()+1)
                progressDialog.setValue(progressDialog.value()+1)
                app.processEvents()
                time.sleep(1.0)

            progressDialog.close()
            assert(threadBuildInterpreter.interpreter is not None)
            self.parent().setCentralWidget(
                FreeartReconsManager(parent=self.parent(),
                                     interpreter=threadBuildInterpreter.interpreter))
        except ValueError:
            raise RuntimeError("Bad matrices dimension")

        self.deleteLater()

    def _goToFluoReconstructionSampleCompositionValidate(self, event):
        """
        Follow the _prepareFluoReconstruction once the user has validated
        the sample composition
        """
        del self.physElemtPainterWindow
        assert('outputFileSampleComposition' in event)
        assert('outputFileMaterials' in event)
        self._moveToFluoReconstruction(
            str(event['outputFileSampleComposition']),
            str(event['outputFileMaterials']))

    def _saveReconstructions(self):
        """
        Callback of the save reconsparam button
        """
        assert(self.freeartInterpreter is not None)

        dialog = QFileManagement.QProjectFileDialog(
            parent=self, showMergeOpt=False, defaultMerge=True,
            nameFilters=(QFileManagement.H5_FILTER,))

        if not dialog.exec_():
            dialog.close()
            return

        _file = dialog.selectedFiles()[0]
        fn, file_extension = os.path.splitext(_file)
        if file_extension.lower() not in ('.h5', '.hdf5'):
            _file = _file + '.h5'

        # save freeart configuration
        save(configuration=self.freeartInterpreter.config,
             filePath=_file,
             overwrite=True,
             merge=True)

        # save reconstructions
        _h5pyfile = h5py.File(name=_file, mode='a')
        node = _h5pyfile.require_group(name='reconstruction/phantom')

        reconsAlgos = self.freeartInterpreter.getReconstructionAlgorithms()
        for algo in reconsAlgos:
            if algo in node:
                del node[algo]

            phantom = decreaseMatSize(reconsAlgos[algo].getPhantom())
            node.create_dataset(name=algo, data=phantom)


class FreeARTReconstructionIteratorThread(qt.QThread):
    """
    The thread to run the iteration on the freeart interpreter

    :param freeartInterpreter : the freeartinterpreter to be runned
    :param nbIteration: The number of iteration we want to run
    :param listenForInteruption: if True then we will run each iteration one
                                 after the other and between each check if the
                                 user has request a stop of the iteration.
                                 But will be slower. If False then we call the
                                 freeart core for nbIteration.
                                 No stop is possible


    """
    interupted = False
    sigAllIterationsEnded = qt.Signal()
    """signal emitted when the thread ends"""
    sigOneIterationEnded = qt.Signal()
    """signal emitted when an iteration is done (not emitted when
    listenForInteruption is False)"""

    def __init__(self, freeartInterpreter, nbIteration,
                 listenForInteruption=True):
        qt.QObject.__init__(self)
        self.freeartInterpreter = freeartInterpreter
        self.nbIteration = nbIteration
        self.listenForInteruption = listenForInteruption

    def run(self):
        """
        run of the thread. Basically call the iterate function of the
        interpreter
        """
        try:
            if self.listenForInteruption:
                # we run each time one iteration to display the progress bar.
                # The behavior should be improve to update each time the
                # iteration of one algorithm is ended (at least).
                for iIteration in numpy.arange(0, self.nbIteration):
                    self.freeartInterpreter.iterate(1)
                    self.sigOneIterationEnded.emit()
                    if self.interupt is True:
                        break
            else:
                self.freeartInterpreter.iterate(self.nbIteration)

        except RuntimeError:
            _logger.Error("iteration failed")
            raise RuntimeError("iteration failed")

        self.sigAllIterationsEnded.emit()

    def interupt(self):
        """
        Function to call the thread interuption.
        If listenForInteruption is False then this will be with no effect
        """
        self.interupt = True


class FreeARTInterpreterThreadBuilder(qt.QThread):
    """
    Simple class heritating from a QThread to launch the construction of the
    freeart interpreter which can take some time

    :param config : the path to the configuration file
    """
    def __init__(self, config):
        qt.QObject.__init__(self)
        self.config = config
        self.interpreter = None

    def run(self):
        """
        run the thread. Basically build the freeart interpreter
        """
        try:
            self.interpreter = freeartinterpreter(self.config)
        except RuntimeError:
            raise RuntimeError("unable to initialize the freeartinterpreter")


class ReconsControl(qt.QWidget):
    """
    The widget containing all the interface to fully control the freeart
    reconsparam

    :param parent: The parent QObject
    :param config: the configuration containing all information
                    concerning the reconstruction to be run
    """
    total_iterations = 0

    def __init__(self, parent, config):
        qt.QWidget.__init__(self, parent)
        assert(config)
        self.config = config
        layout = qt.QVBoxLayout()

        # reconsparam parameters group
        layout.addWidget(self.getFreeARTReconstructionParams())

        # iterate button
        layout.addWidget(self.getGrpIterate())

        # save reconstruction button
        self._qpbSaveReconstruction = qt.QPushButton(
            "Save current status")
        self._qpbSaveReconstruction.setToolTip(
            "Save the reconstruction parameters and all the reconstructions "
            "of the sinograms")
        self._qpbSaveReconstruction.setAutoDefault(True)
        layout.addWidget(self._qpbSaveReconstruction)

        # spacer
        spacer = qt.QWidget(self)
        spacer.setSizePolicy(qt.QSizePolicy.Minimum, qt.QSizePolicy.Expanding)
        layout.addWidget(spacer)

        # history group
        layout.addWidget(self.getGrpHistory())

        # quit button
        self._qpbQuit = qt.QPushButton("Quit")
        self._qpbQuit.setToolTip("Exit the application")
        self._qpbQuit.setIcon(icons.getQIcon('exit'))
        myFont = self._qpbQuit.font()
        myFont.setBold(True)
        self._qpbQuit.setFont(myFont)
        layout.addWidget(self._qpbQuit)

        self.setLayout(layout)

        self._addFileToHistory()

    def _addFileToHistory(self):
        """
        will dump the cfg file in the history
        """
        self.addToHistory("#####################")
        self.addToHistory("loading reconstruction configuration")
        self.addToHistory("#####################")

    def getGrpIterate(self):
        """
        Build the widget for the iterate functionnality
        """
        grpWidgetsIterate = qt.QWidget(self)
        layoutGrpWidgetIterate = qt.QGridLayout()

        # iterate button
        self._qpbIterate = qt.QPushButton("Iterate")
        self._qpbIterate.setToolTip(
            "Run x iterations on all the ARTAlgorithm defined (equal for all sinogram)")
        self._qpbIterate.setIcon(icons.getQIcon('run'))
        self._qpbIterate.setAutoDefault(True)
        myFont = self._qpbIterate.font()
        myFont.setBold(True)
        self._qpbIterate.setFont(myFont)
        layoutGrpWidgetIterate.addWidget(self._qpbIterate, 0, 0)

        # stop iteration button
        self._qpbStopIterate = qt.QPushButton("Stop Iteration")
        self._qpbStopIterate.setToolTip(
            "Stop iterations reconsparam after the end of the current iteration")
        self._qpbStopIterate.setIcon(icons.getQIcon('stop'))
        self._qpbStopIterate.setAutoDefault(True)
        self._qpbStopIterate.setEnabled(False)
        layoutGrpWidgetIterate.addWidget(self._qpbStopIterate, 1, 0)

        # nb iteration spinbox
        self._qsbNbIteration = qt.QSpinBox()
        self._qsbNbIteration.setRange(1, 100)
        self._qsbNbIteration.setValue(1)
        self._qsbNbIteration.setToolTip(
            "number of iteration to run on the next 'iterate' action")
        layoutGrpWidgetIterate.addWidget(self._qsbNbIteration, 0, 1)

        grpWidgetsIterate.setLayout(layoutGrpWidgetIterate)

        # total numer of iteration label
        widgetTotalIteration = qt.QWidget(self)
        layoutTotalIteration = qt.QHBoxLayout()
        layoutTotalIteration.addWidget(qt.QLabel("total iteration "))
        tooltip = """Sum of all the iteration executed since the beginning of
            the reconsparam"""
        widgetTotalIteration.setToolTip(tooltip)
        self._iterationSum = qt.QLabel("0")
        layoutTotalIteration.addWidget(self._iterationSum)
        widgetTotalIteration.setLayout(layoutTotalIteration)
        layoutGrpWidgetIterate.addWidget(widgetTotalIteration, 2, 0)

        grpWidgetsIterate.setLayout(layoutGrpWidgetIterate)
        return grpWidgetsIterate

    def getGrpHistory(self):
        """
        Build the widgets for the history functionnality
        Basically we are storing every user modification in the reconsparam
        param and his call to iterate.
        Then the user can save this history to make sure he can run again the
        same reconsparam from the sinograms
        """
        def getHistoryToolTip():
            return """
                <html>
                The history register all the actions made by the user and all the ietration runned.
                From this history you can find back all the actions done which have bring to the current reconsparam.
                <html>
                """

        grpWidgetHistory = qt.QWidget(self)
        layoutHistory = qt.QVBoxLayout()
        self._qpbHistory = qt.QPushButton("History", self)
        self._qpbHistory.setToolTip(getHistoryToolTip())
        self._qpbHistory.setIcon(icons.getQIcon('history'))
        self._qpbHistory.setAutoDefault(True)
        self._qpbHistory.clicked.connect(self._hideShowHistory)
        layoutHistory.addWidget(self._qpbHistory)

        myFont = self._qpbHistory.font()
        myFont.setItalic(True)
        p = self._qpbHistory.palette()
        p.setColor(qt.QPalette.ButtonText, qt.Qt.blue)
        self._qpbHistory.setPalette(p)
        self._qpbHistory.setFont(myFont)
        self._qpbHistory.setFlat(True)

        self._qsaHistory = qt.QScrollArea(self)
        self._qteHistory = qt.QTextEdit("")
        self._qteHistory.setReadOnly(True)
        self._qsaHistory.setWidget(self._qteHistory)
        self._qsaHistory.setWidgetResizable(True)
        self._qsaHistory.hide()

        layoutHistory.addWidget(self._qsaHistory)

        self._qpbSaveHistory = qt.QPushButton("Save history", self)
        self._qpbSaveHistory.setToolTip("Dump all the history into a file")
        self._qpbSaveHistory.setIcon(icons.getQIcon('document-save'))
        self._qpbSaveHistory.setAutoDefault(True)
        self._qpbSaveHistory.clicked.connect(self._saveHistory)
        layoutHistory.addWidget(self._qpbSaveHistory)

        grpWidgetHistory.setLayout(layoutHistory)
        return grpWidgetHistory

    def getFreeARTReconstructionParams(self):
        """
        Build the reconsparam parameters section.
        Update the reconsparam parameters value from the given configuration
        file
        """
        group = qt.QWidget(self)
        group.setContentsMargins(0, 0, 0, 0)
        layoutGrp = qt.QVBoxLayout()
        layoutGrp.setContentsMargins(0, 0, 0, 0)
        # Reconstruction parameters button
        self._qpbReconsParams = qt.QPushButton("Reconstruction params")
        self._qpbReconsParams.setIcon(icons.getQIcon('parameters'))
        self._qpbReconsParams.setAutoDefault(True)
        self._qpbReconsParams.setFlat(True)
        self._qpbReconsParams.setToolTip(
            "Access to the reconsturctions parameters")

        myFont = self._qpbReconsParams.font()
        myFont.setItalic(True)
        p = self._qpbReconsParams.palette()
        p.setColor(qt.QPalette.ButtonText, qt.Qt.blue)
        self._qpbReconsParams.setPalette(p)
        self._qpbReconsParams.setFont(myFont)

        layoutGrp.addWidget(self._qpbReconsParams)

        self.reconsParam = ReconsParamWidget(group)
        self.reconsParam.setContentsMargins(0, 0, 0, 0)
        self.reconsParam.loadConfiguration(self.config)

        self.reconsParam.lockReconstructionParameters()

        # insert all in a scrollArea
        self._qsaReconsParams = qt.QWidget(parent=None)
        self._qsaReconsParams.setLayout(qt.QVBoxLayout())
        self._qsaReconsParams.layout().addWidget(self.reconsParam)

        group.setLayout(layoutGrp)

        # connect button
        self._qpbReconsParams.clicked.connect(self._hideShowReconsParam)

        return group

    def getNbIterations(self):
        """
        Return the maximal number of iteration the user want to run
        """
        return int(self._qsbNbIteration.value())

    def _hideShowHistory(self):
        """
        show the history QLineEdit if hidden, otherwise hide it
        """
        if self._qsaHistory.isHidden():
            self._qsaHistory.show()
        else:
            self._qsaHistory.hide()

    def _saveHistory(self):
        """
        Call back when the user request to save the history
        """
        dialog = qt.QFileDialog(self)
        dialog.setAcceptMode(qt.QFileDialog.AcceptSave)
        dialog.setWindowTitle("Save history")
        dialog.setModal(1)
        dialog.setNameFilters(["txt (*.txt)"])

        if not dialog.exec_():
            dialog.close()
            return

        newFile = dialog.selectedFiles()[0]
        if not newFile.lower().endswith('.txt'):
            newFile = newFile + '.txt'

        historyFile = open(newFile, "w")
        historyFile.write(self._qteHistory.toPlainText())
        historyFile.close()

    def _hideShowReconsParam(self):
        """
        show the history QLineEdit if hidden, otherwise hide it
        """
        if self._qsaReconsParams.isHidden():
            self._qsaReconsParams.show()
        else:
            self._qsaReconsParams.hide()

    def increaseTotalIteration(self, val):
        """
        Increase the count of the iteration done on the reconsparam
        """
        assert(val > 0)
        self.total_iterations = self.total_iterations + val
        self._iterationSum.setText(str(self.total_iterations))

    def lockIterationAction(self):
        """
        lock the widget to avoid any interaction during the reconsparam
        """
        self._qpbIterate.setEnabled(False)
        self._qsbNbIteration.setEnabled(False)
        self._qpbStopIterate.setEnabled(True)
        app = qt.QApplication.instance() or qt.QApplication([])
        app.setOverrideCursor(qt.Qt.BusyCursor)

    def releaseIterationAction(self):
        """
        lock the widget to avoid any interaction during the reconsparam
        """
        self._qpbIterate.setEnabled(True)
        self._qsbNbIteration.setEnabled(True)
        self._qpbStopIterate.setEnabled(False)
        app = qt.QApplication.instance() or qt.QApplication([])
        app.setOverrideCursor(qt.Qt.ArrowCursor)

    def addToHistory(self, sentence):
        """
        Add the given sentence to the history
        :param sentence: the sentence to add
        """
        assert(type(sentence) == str)
        self._qteHistory.append(sentence)


class FreeartReconsDialog(qt.QDialog):
    def __init__(self, parent, config):
        qt.QDialog.__init__(self, parent)
        self.setWindowTitle('Tomography reconstruction')
        self.setWindowFlags(qt.Qt.Widget)
        types = qt.QDialogButtonBox.Ok | qt.QDialogButtonBox.Cancel
        _buttons = qt.QDialogButtonBox(parent=self)
        _buttons.setStandardButtons(types)
        self.mainWindow = FreeartReconsManager(parent=self, config=config)
        self.mainWindow.setAttribute(qt.Qt.WA_DeleteOnClose)
        # hide the quit button
        self.mainWindow.getReconsMenu()._qpbQuit.hide()
        self.setLayout(qt.QVBoxLayout())
        self.layout().addWidget(self.mainWindow)
        self.layout().addWidget(_buttons)

        _buttons.accepted.connect(self.accept)
        _buttons.rejected.connect(self.reject)

    def exec_(self):
        # bad hack to make sure the images are correctly displayed
        # but as we are using the keep aspect ratio if the plot is not show
        # and the zoom reset matplotlib will not be able to deduce the correct
        # dimension of the plot area
        self.show()
        self.mainWindow.resetPlotsZoom()
        return qt.QDialog.exec_(self)
