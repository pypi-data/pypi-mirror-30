###########################################################################
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
#############################################################################

__author__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "23/11/2017"

from silx.gui import qt
from tomogui import utils
from tomogui.gui.utils.QFileManagement import Q2DDataSelection
from tomogui.utils import formula
from .QDataSourceBaseWidget import QDataSourceBaseWidget
try:
    from tomogui.gui.datasource.sinofileselector.QSinoFileFluoSelector import _QSinoFluoSelector
    from freeart.configuration import structs, config as freeartconfig
    found_freeart = True
except ImportError:
    found_freeart = False


if found_freeart is True:
    class QDataSourceFluoWidget(QDataSourceBaseWidget):
        """
        QDataSourceFluoWidget is the widget dedicated to get the input from the
        user to get file paths for a Fluorescence reconsparam.
        This include :
            - absorption matrice : the path to the absorption matrice
            - interaction matrice : the path to the interaction matrice
            - self attenuation matrice (material help): In order to estimate the
              self attenuation matrice we ask the user to define the potential
              composition of the sample.
              If the absorption matrice is given from a matrice then we can create
              on the run the selfAbsMat.
              If she's given from a sinogram then we will ask the user later to get
              the self attenuation matrice.
            - sinogram files : paths to fluo sinograms to treat. For each file we
                will load al dataset and let the user select the one he want to
                treat
    
        Note : Because compton and Fluorescence are Very close we will this widget
               for both.
        """
        _GRP_BOX_IT_SINO_TITLE = "It sinogram"
        _BUTTON_IT_SINO_TITLE = "Select sinogram file"

        _GRP_BOX_ABS_MAT_TITLE = "Absorption matrix"
        _BUTTON_ABS_MAT_TITLE = "Select matrix file"

        GEN_ABS_SELF_ABS_OPT = "Generate absorption matrix and self attenuations " \
                               "matrices from It and I0 sinogram"

        GIVE_ABS_MAT_GEN_SELF_ABS_OPT = "Give absorption matrix and generate self " \
                                        "absorption matrices from the material sample definition"

        GIVE_ABS_MAT_AND_SELF_ABS_MAT_OPT = "Give absorption matrix and self " \
                                            "absorptions matrices for each matrial"

        RECONS_MODE = (
            GEN_ABS_SELF_ABS_OPT,
            GIVE_ABS_MAT_GEN_SELF_ABS_OPT,
            GIVE_ABS_MAT_AND_SELF_ABS_MAT_OPT
        )

        DEFAULT_RECONS_MODE = GEN_ABS_SELF_ABS_OPT

        sigReconsModeChanged = qt.Signal()
        """Signal emitted when the reconstruction mode change (how to get abs
        matrix and self abs matrices)"""

        def __init__(self, parent=None,
                     reconstructionType=freeartconfig._ReconsConfig.FLUO_ID):
            """Constructor"""
            QDataSourceBaseWidget.__init__(self, parent)
            _layout = qt.QVBoxLayout()
            _layout.addWidget(self._buildAbsMatricesOpt())
            # absorption matrice interface
            _layout.addWidget(self._buildAbsorptionMatrixGroup())

            self.fluoSinogramsSelector = _QSinoFluoSelector(self)
            self.fluoSinogramsSelector.fileSelector.sigSinogramHasBeenAdded.connect(
                self._sinogramRefHasChanged)
            self.fluoSinogramsSelector.fileSelector.sigSinogramHasBeenAdded.connect(
                self.notifyInfoForMaterialsChanged
            )

            _layout.addWidget(self.fluoSinogramsSelector)

            self.setLayout(_layout)
            self.layout().setSpacing(4)
            self.layout().setContentsMargins(0, 0, 0, 0)

            self.setToolTip(self.getFluorescenceInputsHelp())

            self.setReconstructionType(reconstructionType)
            self.setFluoReconsMode(self.GEN_ABS_SELF_ABS_OPT)

        def clean(self):
            self.fluoSinogramsSelector.clean()

        def _buildAbsMatricesOpt(self):

            group = qt.QGroupBox("Absorption matrix option", parent=self)
            group.setLayout(qt.QVBoxLayout())
            group.layout().setSpacing(4)
            group.layout().setContentsMargins(0, 0, 0, 0)

            group.setToolTip(
                """
                In order to run fluorescence reconstruction the algorithm need to know about
                  - the absorption matrix (1).
                  - the self attenuation matrices for each element which has a sinogram (2).
    
                (1) can be obtained by giving directly this absorption matrix or by giving It and I0 matrices.
                    So if It and I0 is given we will have to pass by an extra step for this reconstruction.
                (2) can be given directly or deduced knowing EF and having a description of the materials in the sample.
                """)

            self._qrbGenerateFrmItI0 = qt.QRadioButton(self.GEN_ABS_SELF_ABS_OPT)
            self._qrbGiveAbsBuildSampMat = qt.QRadioButton(
                self.GIVE_ABS_MAT_GEN_SELF_ABS_OPT)
            self._qrbGiveAllAbsMat = qt.QRadioButton(
                self.GIVE_ABS_MAT_AND_SELF_ABS_MAT_OPT)

            group.layout().addWidget(self._qrbGenerateFrmItI0)
            group.layout().addWidget(self._qrbGiveAbsBuildSampMat)
            group.layout().addWidget(self._qrbGiveAllAbsMat)

            self._qrbGenerateFrmItI0.toggled.connect(self._updateFluoReconsType)
            self._qrbGiveAbsBuildSampMat.toggled.connect(
                self._updateFluoReconsType)
            self._qrbGiveAllAbsMat.toggled.connect(self._updateFluoReconsType)

            return group

        def getFluorescenceInputsHelp(self):
            """
            :return: the help for the inpus
            """

            def addImageAndInfo(imageID, info):
                return "<img src=" + formula.getFormula(imageID) + "/> " + info

            res = "<html> The fluorescence and compton reconsparam folow the formula <br> <img src=" + formula.getFormula(
                'fluorescence') + "/> "
            res = res + "with : <ul>"
            res = res + utils.addHTMLLine(
                addImageAndInfo("incomingAbsorption",
                                "The absorption of the incoming rays"))
            res = res + utils.addHTMLLine(
                addImageAndInfo("outgoingAbsorption",
                                "The absorption of the outgoing rays"))
            res = res + utils.addHTMLLine(
                addImageAndInfo("interactionProbability",
                                "The probability of interaction of the incoming rays with the sample"))
            res = res + utils.addHTMLLine(
                addImageAndInfo("productionProbability",
                                "The probability of production of the outgoing beam if there is an interaction"))
            res = res + utils.addHTMLLine(
                addImageAndInfo("solidAngle",
                                "The solid angle relative to the detector and his position"))
            res = res + "</ul> </html> "
            return res

        def _sinogramRefHasChanged(self, sinogram):
            """
            Callback when the file for the normlalization of the center of rotation
            might have changed
            """
            if sinogram is not None:
                QDataSourceBaseWidget._sinogramRefHasChanged(self, sinogram)
                self._checkI0()

        def _checkI0(self):
            """check reconstruction and mode and look if a `sigI0MightChanged`
            should be emitted."""
            # if we can try to get I0 from It
            if self.getFluoReconsMode() == self.GEN_ABS_SELF_ABS_OPT:
                absMat = self.getAbsMat()
                if absMat is not None and absMat.fileInfo is not None:
                    absMat.loadData(None)
                    self.sigI0MightChanged.emit(absMat.data.max())
            # otherwise use the first fluorescence sinogram
            else:
                sinograms = self.getSinograms()
                if len(sinograms) > 0:
                    sino = sinograms[0]
                    self.sigI0MightChanged.emit(sino.data.max())

        def notifyInfoForMaterialsChanged(self):
            self.sigInfoForMaterialsChanged.emit()

        def _buildAbsorptionMatrixGroup(self):
            """
            create the gui relative to the absorption matrix
            """
            def getToolTip():
                return "<html> this is the &mu; &rho; in the formula <img src=" + \
                       formula.getFormula("incomingAbsorption") + "/></html>"

            self._qgbAbsMat = qt.QGroupBox(self)
            self._qgbAbsMat.setTitle("Absorption matrix")
            self._qgbAbsMat.setToolTip(getToolTip())
            self._qgbAbsMat.setLayout(qt.QVBoxLayout())

            self._qgbAbsMat.layout().setSpacing(4)
            self._qgbAbsMat.layout().setContentsMargins(0, 0, 0, 0)

            self.qfsAbsorptionMatrix = Q2DDataSelection(parent=self,
                                                        text=self._GRP_BOX_IT_SINO_TITLE)
            self.qfsAbsorptionMatrix.sigDataStoredChanged.connect(
                self.notifyInfoForMaterialsChanged)
            self.qfsAbsorptionMatrix.sigDataStoredChanged.connect(
                self._checkI0)

            self._qgbAbsMat.layout().addWidget(self.qfsAbsorptionMatrix)

            return self._qgbAbsMat

        def _sampleCompositionValidated(self, event):
            """
            Callback when the user validate the composition of the sample,
            from the QSampleComposition
            """
            if 'event' not in event or event['event'] != 'sampleCompositionValidation':
                raise RuntimeError("event is not recognized")

            # composition = event['composition']
            # materials = event['materials']
            outputFileComposition = event['outputFileSampleComposition']
            outputFileMaterials = event['outputFileMaterials']

            self.qfsSampCompositionFile.setFileSelected(outputFileComposition)
            self.qfsMaterial.setFileSelected(outputFileMaterials)

        def _updateFluoReconsType(self):
            """
            change some widget visibility according to the fluorescence
            reconsparam mode
            """
            mode = self.getFluoReconsMode()

            if mode == self.GEN_ABS_SELF_ABS_OPT:
                title = self._GRP_BOX_IT_SINO_TITLE
                buttonName = self._BUTTON_IT_SINO_TITLE
            else:
                title = self._GRP_BOX_ABS_MAT_TITLE
                buttonName = self._BUTTON_ABS_MAT_TITLE
            self._qgbAbsMat.setTitle(title)
            self.qfsAbsorptionMatrix.setText(buttonName)

            cptRecons = self.reconstructionType == freeartconfig._ReconsConfig.COMPTON_ID
            isUserProvidingSelfAbsMat = mode == self.GIVE_ABS_MAT_AND_SELF_ABS_MAT_OPT

            self.fluoSinogramsSelector.sinoInfo.showEF(
                not (cptRecons or isUserProvidingSelfAbsMat))
            self.fluoSinogramsSelector.sinoInfo.setSelfAbsMatVisible(
                isUserProvidingSelfAbsMat)

            reqMat = self.reconstructionType == freeartconfig._ReconsConfig.FLUO_ID and not isUserProvidingSelfAbsMat
            self.sigReconsModeChanged.emit()
            self.sigRequireMaterials.emit(reqMat)
            self._checkI0()

        def setFluoReconsMode(self, reconsType):
            """
    
            :param reconsType: should be in RECONS_MODE
            """
            self._qrbGenerateFrmItI0.setChecked(
                reconsType == self.GEN_ABS_SELF_ABS_OPT
            )
            self._qrbGiveAbsBuildSampMat.setChecked(
                reconsType == self.GIVE_ABS_MAT_GEN_SELF_ABS_OPT
            )
            self._qrbGiveAllAbsMat.setChecked(
                reconsType == self.GIVE_ABS_MAT_AND_SELF_ABS_MAT_OPT
            )

            self._updateFluoReconsType()
            self.sigReconsModeChanged.emit()

        def getFluoReconsMode(self):
            if self._qrbGenerateFrmItI0.isChecked():
                return self.GEN_ABS_SELF_ABS_OPT
            elif self._qrbGiveAbsBuildSampMat.isChecked():
                return self.GIVE_ABS_MAT_GEN_SELF_ABS_OPT
            elif self._qrbGiveAllAbsMat.isChecked():
                return self.GIVE_ABS_MAT_AND_SELF_ABS_MAT_OPT

        def saveConfiguration(self, config, refFile):
            """
            dump information in a configuration file
    
            :param config: the configuration to save information
            """
            if found_freeart is True:
                config.isAbsMatASinogram = self.isAbsMatASino()
                config.absMat = self.getAbsMat()
                self.fluoSinogramsSelector.saveConfiguration(config, refFile)
                if self.getFluoReconsMode() == self.GIVE_ABS_MAT_GEN_SELF_ABS_OPT:
                    """Remove all data information about selfAbsMat for sinogram
                    in the configuration"""
                    self.fluoSinogramsSelector.cleanSelfAbsMat(config)
            else:
                raise RuntimeWarning(
                    "'can't found freeART, no normalization possible")

        def setAbsMat(self, absMat):
            assert(isinstance(absMat, structs.AbsMatrix))
            if self.getFluoReconsMode() == self.GEN_ABS_SELF_ABS_OPT:
                self.setFluoReconsMode(self.GIVE_ABS_MAT_GEN_SELF_ABS_OPT)
            self.qfsAbsorptionMatrix.setDataStored(absMat)

        def setIt(self, absMat):
            assert(isinstance(absMat, structs.Sinogram))
            self.setFluoReconsMode(self.GEN_ABS_SELF_ABS_OPT)
            self.qfsAbsorptionMatrix.setDataStored(absMat)

        def getAbsMat(self):
            data = self.qfsAbsorptionMatrix.getDataStored()
            return structs.AbsMatrix(fileInfo=data.fileInfo,
                                     data=data.data)

        def loadConfiguration(self, config):
            """
            load input file information fron a cfg file
    
            :param config: the configuration to load information
            """
            if not found_freeart:
                raise RuntimeWarning(
                    "can't found freeart, no normalization possible")

            # abs info
            if config.absMat is not None:
                self.setAbsMat(config.absMat)
            if config.isAbsMatASinogram:
                type = self.GEN_ABS_SELF_ABS_OPT
            else:
                hasSelfAbs = False
                hasSelfAbsMissing = False
                for sinogram in config.sinograms:
                    if sinogram.selfAbsMat is None:
                        hasSelfAbsMissing = True
                    else:
                        hasSelfAbs = True
                if hasSelfAbs and not hasSelfAbsMissing:
                    type = self.GIVE_ABS_MAT_AND_SELF_ABS_MAT_OPT
                else:
                    type = self.GIVE_ABS_MAT_GEN_SELF_ABS_OPT
            self.setFluoReconsMode(type)

            # using a sinogram info
            val = config.isAbsMatASinogram
            if val is not None:
                if val is True:
                    self.setFluoReconsMode(self.GEN_ABS_SELF_ABS_OPT)

            self.fluoSinogramsSelector.loadConfiguration(config)

        def setAbsMatFile(self, file, uri):
            """
            Set the path to the absorptionMatrice
            :param file: path to the absorption matrice
            """
            self.qfsAbsorptionMatrix.setFileSelected(file, uri)

        def getAbsMatFile(self):
            """
            :return: the path to the absorptionMatrice
            """
            return self.qfsAbsorptionMatrix.getFileSelected()

        def setReconstructionType(self, reconstructionType):
            self.reconstructionType = reconstructionType
            if self.reconstructionType in (freeartconfig._ReconsConfig.FLUO_ID,
                                           freeartconfig._ReconsConfig.COMPTON_ID):
                self._updateFluoReconsType()

        def getSinograms(self):
            return self.fluoSinogramsSelector.getSinograms()

        def isAbsMatASino(self):
            return self.getFluoReconsMode() == self.GEN_ABS_SELF_ABS_OPT
