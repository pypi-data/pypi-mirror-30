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
__date__ = "24/05/2016"

from silx.gui import qt
from tomogui.gui.utils.ConfigurationActor import ConfigurationActor
import tomogui.utils as utils
from .QDataSourceTxWidget import QDataSourceTxWidget
from tomogui.configuration.config import FBPConfig
from tomogui.configuration import config as tomoguiconfig
import logging
try:
    from freeart.configuration import config as freeartconfig
    from .QDataSourceFluoWidget import QDataSourceFluoWidget
    found_freeart = True
except ImportError:
    from tomogui.third_party.configuration import config as freeartconfig
    found_freeart = False
try:
    import pyopencl
    from silx.opencl.backprojection import Backprojection
    found_fbp = True
except ImportError:
    found_fbp = False

_logger = logging.getLogger(__file__)


class QDataSourceWidget(qt.QWidget, ConfigurationActor):
    """
    Widget used for all type of reconstructions to register all information
    about the input files needed
    """

    SILX_FBP_DEF = "Filtered back projection (silx)"
    """The silx filtered back projection ID for the reconsutrction"""

    FREEART_TX_DEF = "Transmission (freeart)"
    """The freeart transmission ID for the reconsutrction"""

    FREEART_COMPTON_DEF = "Compton (freeart)"
    """The freeart compton ID for the reconsutrction"""

    FREEART_FLUO_DEF = "Fluorescence (freeart)"
    """The freeart fluorescence ID for the reconsutrction"""

    DICT_IDS = {
        SILX_FBP_DEF: tomoguiconfig.FBPConfig.FBP_ID,
        FREEART_TX_DEF: freeartconfig._ReconsConfig.TX_ID,
        FREEART_COMPTON_DEF: freeartconfig._ReconsConfig.COMPTON_ID,
        FREEART_FLUO_DEF: freeartconfig._ReconsConfig.FLUO_ID,
    }

    sigReconstructionTypeChanged = qt.Signal(object)

    @staticmethod
    def _getTransmissionReconsInfo():
        return "A simple transmission reconsparam from freeart"

    @staticmethod
    def _getComptonReconsInfo():
        return "A compton reconsparam from freeart. Basically absorption == self attenuation"

    @staticmethod
    def _getFluoReconsInfo():
        return "A fluorescence reconsparam from freeart. You will have to give the absorption amtrice and the self attenuation matrice"

    @staticmethod
    def _getSilxFBPReconsInfo():
        return "Filtered back projection implementation from silx (opencl implementation)"

    def __init__(self, parent=None):
        """
        Constructor
        """
        def getToolTip():
            res = "<html> Potential reconstructions are : <ul>" + utils.addHTMLLine(self._getTransmissionReconsInfo())
            res = res + utils.addHTMLLine(self._getSilxFBPReconsInfo())
            if found_freeart is True:
                res = res + utils.addHTMLLine(self._getTransmissionReconsInfo())
                res = res + utils.addHTMLLine(self._getComptonReconsInfo())
                res = res + utils.addHTMLLine(self._getFluoReconsInfo())
            res = res + "</ul> </html>"
            return res

        qt.QWidget.__init__(self, parent)
        ConfigurationActor.__init__(self)

        # define the type of reconsparam we want to run
        _layout = qt.QVBoxLayout()

        # beamCalculationMethod
        self.qcbReconstructionType = self.getReconsTypeCombobox(parent=self)

        _layout.addWidget(self.qcbReconstructionType)
        self.qcbReconstructionType.currentIndexChanged.connect(
            self._reconsTypeChanged)

        self.qcbReconstructionType.setToolTip(getToolTip())

        # create data sources and link them to the signal
        # "_fileNormalizationChanged"
        self.qdsTx = QDataSourceTxWidget(self)
        _layout.addWidget(self.qdsTx)

        if found_freeart is True:
            self.qdsFluo = QDataSourceFluoWidget(self)
            _layout.addWidget(self.qdsFluo)
        else:
            self.qdsFluo = None

        self._showSelectedDataSource(tomoguiconfig.FBPConfig.FBP_ID)

        # add the vertical spacer
        spacer = qt.QWidget()
        spacer.setSizePolicy(qt.QSizePolicy.Expanding,
                             qt.QSizePolicy.Expanding)
        _layout.addWidget(spacer)
        _layout.setSpacing(4)

        self.setLayout(_layout)

    def clean(self):
        self.qdsFluo.clean()
        self.qdsTx.clean()

    @staticmethod
    def getReconsTypeCombobox(parent):
        """Return the combobox for the reconstruction types"""
        cb = qt.QComboBox(parent)
        # Warning : should always be stored in this order, otherwise may fail
        # Would be better to link it from the FreeARTReconsParam...
        iItem = 0
        if found_fbp is True:
            cb.addItem(QDataSourceWidget.SILX_FBP_DEF)
            cb.setItemData(iItem,
                           QDataSourceWidget._getSilxFBPReconsInfo(),
                           qt.Qt.ToolTipRole)
            iItem += 1
        if found_freeart is True:
            cb.addItem(QDataSourceWidget.FREEART_TX_DEF)
            cb.setItemData(iItem,
                           QDataSourceWidget._getTransmissionReconsInfo(),
                           qt.Qt.ToolTipRole)
            iItem += 1

            cb.addItem(QDataSourceWidget.FREEART_COMPTON_DEF)
            cb.setItemData(iItem,
                           QDataSourceWidget._getComptonReconsInfo(),
                           qt.Qt.ToolTipRole)
            iItem += 1

            cb.addItem(QDataSourceWidget.FREEART_FLUO_DEF)
            cb.setItemData(iItem,
                           QDataSourceWidget._getFluoReconsInfo(),
                           qt.Qt.ToolTipRole)
            iItem += 1

        return cb

    def getShortToolTip(self):
        return "Register all inputs files to run the reconsparam"

    def _reconsTypeChanged(self):
        """
        callback called when the item from the combobox qcbReconstructionType
        is called
        """
        ddict = {}
        ddict['event'] = "reconstructionTypeChanged"
        rtype = self.qcbReconstructionType.currentText()
        if rtype not in self.DICT_IDS:
            raise ValueError('Reconstruction type not recognized')
        reconsType = self.DICT_IDS[self.qcbReconstructionType.currentText()]
        ddict['reconstructionType'] = reconsType
        self.sigReconstructionTypeChanged.emit(ddict)
        self._showSelectedDataSource(reconsType)
        if reconsType in (freeartconfig._ReconsConfig.COMPTON_ID, freeartconfig._ReconsConfig.FLUO_ID):
            self.qdsFluo.setReconstructionType(reconsType)

    def _showSelectedDataSource(self, reconstructionType):
        """

        :param str econstructionType: the reconsparam for wich we want to
                                      get the user input.
        """
        assert reconstructionType in (tomoguiconfig.FBPConfig.FBP_ID,
                                      freeartconfig._ReconsConfig.TX_ID,
                                      freeartconfig._ReconsConfig.COMPTON_ID,
                                      freeartconfig._ReconsConfig.FLUO_ID)
        self.qdsTx.setVisible(reconstructionType in (tomoguiconfig.FBPConfig.FBP_ID, freeartconfig._ReconsConfig.TX_ID))
        if found_freeart is True:
            self.qdsTx.setVisible(
                reconstructionType in (freeartconfig._ReconsConfig.TX_ID,
                                       tomoguiconfig.FBPConfig.FBP_ID))
            self.qdsFluo.setVisible(reconstructionType in (freeartconfig._ReconsConfig.COMPTON_ID,
                                                           freeartconfig._ReconsConfig.FLUO_ID))

    def saveConfiguration(self, config, refFile):
        """
        dump information in a configuration file

        :param config: the configuration to save information
        """
        if found_freeart is True:
            if self.selectedReconstructionIsFluo() or self.selectedReconstructionIsComtpon():
                self.qdsFluo.saveConfiguration(config, refFile)
            if self.selectedReconstructionIsTx():
                self.qdsTx.saveConfiguration(config, refFile)

        if self.selectedReconstructionIsSilxFBP():
            self.qdsTx.saveConfiguration(config, refFile)

    def loadConfiguration(self, config):
        """
        load input file information fron a cfg file

        :param config: the configuration to load information
        """
        if type(config) is FBPConfig:
            self.qdsTx.loadConfiguration(config)
        else:
            if config.reconsType == freeartconfig._ReconsConfig.TX_ID:
                self.qdsTx.loadConfiguration(config)
            else:
                self.qdsFluo.loadConfiguration(config)

    def selectedReconstructionIsSilxFBP(self):
        """

        :return: True if the used asked for a silx FBP
        """
        reconsType = self.DICT_IDS[self.qcbReconstructionType.currentText()]
        return reconsType == tomoguiconfig.FBPConfig.FBP_ID

    def selectedReconstructionIsFluo(self):
        """

        :return: True if the used asked for a fluorescence reconsparam
        """
        reconsType = self.DICT_IDS[self.qcbReconstructionType.currentText()]
        return reconsType == freeartconfig._ReconsConfig.FLUO_ID

    def selectedReconstructionIsTx(self):
        """

        :return: True if the used asked for a transmission reconsparam
        """
        reconsType = self.DICT_IDS[self.qcbReconstructionType.currentText()]
        return reconsType == freeartconfig._ReconsConfig.TX_ID

    def selectedReconstructionIsComtpon(self):
        """

        :return bool: True if the used asked for a compton reconsparam
        """
        reconsType = self.DICT_IDS[self.qcbReconstructionType.currentText()]
        return reconsType == freeartconfig._ReconsConfig.COMPTON_ID

    def getReconstructionType(self):
        """

        :return: the Type of reconsparam the user want to process.
                 Values can be freeartconfig.FLUO_ID,
                 freeartconfig.COMPTON_ID, freeartconfig.TX_ID
        """
        return str(self.DICT_IDS[self.qcbReconstructionType.currentText()])

    def setReconstructionType(self, val):
        """
        Set the type of reconsparam to run

        :param val: the new type of reconsparam.
                    Value can be freeartconfig.FLUO_ID,
                    freeartconfig.COMPTON_ID or freeartconfig.TX_ID
        """
        if val == tomoguiconfig.FBPConfig.FBP_ID:
            self.qcbReconstructionType.setCurrentIndex(0)
        elif val == freeartconfig._ReconsConfig.TX_ID:
            self.qcbReconstructionType.setCurrentIndex(1)
        elif val == freeartconfig._ReconsConfig.COMPTON_ID:
            self.qcbReconstructionType.setCurrentIndex(2)
        elif val == freeartconfig._ReconsConfig.FLUO_ID:
            self.qcbReconstructionType.setCurrentIndex(3)
        else:
            err = "Given reconsparam type (%s) is not recognize" % val
            raise ValueError(err)
        self._reconsTypeChanged()


if __name__ == "__main__":
    global app  # QApplication must be global to avoid seg fault on quit
    app = qt.QApplication([])

    mainWindow = QDataSourceWidget()

    mainWindow.setAttribute(qt.Qt.WA_DeleteOnClose)
    mainWindow.show()

    app.exec_()
