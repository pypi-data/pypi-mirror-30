# -*- coding: utf-8 -*-

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
import sys
try:
    import freeart
    from freeart.unitsystem import metricsystem
    from freeart.configuration import config as freeartconfig
    found_freeart = True
except ImportError:
    from tomogui.third_party.configuration import config as freeartconfig
    from tomogui.third_party.unitsystem import metricsystem
    found_freeart = False
from tomogui.configuration import config as tomoguiconfig


class QLineEditMetric(qt.QWidget):
    """
    A simple wodget with a QLine edit and a tool box to enter metric
    information (link with freeart library)
    """
    defaultVoxelSize = 1.0
    unitIndexes = {}

    MICROMETER_STR = u'\u00B5\u006D'

    def __init__(self, parent, label, canBeNegative=False):
        """
        :param parent: the parent widget
        :param label: the label to set to the Line
        :param canBeNegative: if True then the QLineEdit can accept negative values (for position for example)
        """
        qt.QWidget.__init__(self, parent)
        layout = qt.QHBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)

        # label
        self.qlabel = qt.QLabel(label)
        layout.addWidget(self.qlabel)
        self.qLineEdit = qt.QLineEdit()
        if canBeNegative:
            self.qLineEdit.setValidator(qt.QDoubleValidator(-float("inf"), float("inf"), 100))
        else:
            self.qLineEdit.setValidator(qt.QDoubleValidator(0.0, float("inf"), 100))
        self.qLineEdit.setText(str(self.defaultVoxelSize))
        layout.addWidget(self.qLineEdit)
        
        # metric combobox
        self.qcbMetric = qt.QComboBox(self)
        self.qcbMetric.addItem("cm")
        self.unitIndexes["cm"] = 0
        self.qcbMetric.addItem("mm")
        self.unitIndexes["mm"] = 1
        self.qcbMetric.addItem("nm")
        self.unitIndexes[self.MICROMETER_STR] = 2
        self.qcbMetric.addItem(self.MICROMETER_STR)
        self.unitIndexes["nm"] = 3
        self.qcbMetric.addItem("m")
        self.unitIndexes["m"] = 4
        layout.addWidget(self.qcbMetric)

        # spacer
        spacer = qt.QWidget()
        spacer.setSizePolicy(qt.QSizePolicy.Expanding,
                             qt.QSizePolicy.Minimum)
        layout.addWidget(spacer)   

        self.setLayout(layout) 

    def getValue(self):
        """
        Return the value converted in the FreeART unit.
        This is the setted by the used taking into account the setted unit
        """
        val = float(self.qLineEdit.displayText())
        if self.qcbMetric.currentText() == "cm":
            return val * metricsystem.cm
        elif self.qcbMetric.currentText() == "mm":
            return val * metricsystem.mm
        elif self.qcbMetric.currentText() == "nm":
            return val * metricsystem.nm
        elif self.qcbMetric.currentText() == "m":
            return val * metricsystem.m
        elif self.qcbMetric.currentText() == self.MICROMETER_STR:
            return val * metricsystem.micrometer
        else:
            return val

    def setValue(self, val, unit="cm"):
        # By default unit is cm
        assert(type(val) == float)
        self.qLineEdit.setText(str(val))
        self.qcbMetric.setCurrentIndex(self.unitIndexes[unit])

    def lockValueAt(self, val, unit="cm"):
        self.setValue(val, unit)
        self.qLineEdit.setEnabled(False)


def checkCanReconstructDialog(configuration, extraInfo=None):
    """
    Serie of test to make sure all needed function to run the reconstructions
    are present in the configuration file. Otherwise present missing elements
    from a dialog.    
    
    :param configuration: 
    :param extraInfo: 
    :return: 
    """
    assert(isinstance(configuration, freeartconfig._ReconsConfig))
    if found_freeart is True:
        if isinstance(configuration, freeartconfig.TxConfig):
            return _checkCanReconstructTxDialog(configuration, extraInfo)
        elif isinstance(configuration, freeartconfig.FluoConfig):
            return _checkCanReconstructFluoDialog(configuration, extraInfo)
    if isinstance(configuration, tomoguiconfig.FBPConfig):
        return _checkCanReconstructFBPDialog(configuration, extraInfo)


def _checkCanReconstructFBPDialog(configuration, extraInfo=None):
    if not hasattr(configuration, 'sinograms') or configuration.sinograms is None \
            or len(configuration.sinograms) is 0:
        msg = qt.QMessageBox()
        msg.setIcon(qt.QMessageBox.Warning)
        msg.setText('Sinograms to reconstruct is missing')
        msg.setInformativeText('Can\'t run reconstruction until defined')
        msg.exec_()
        return False
    return True


def _checkCanReconstructTxDialog(configuration, extraInfo):
    return _checkCanReconstructFBPDialog(configuration, extraInfo)


def _checkCanReconstructFluoDialog(configuration, extraInfo):
    assert hasattr(configuration, 'absMat')
    if configuration.absMat is None or \
            (configuration.absMat.fileInfo is None and configuration.absMat.data is None):
        msg = qt.QMessageBox()
        msg.setIcon(qt.QMessageBox.Warning)
        msg.setText('Absorption matrix or It sinogram is missing')
        msg.setInformativeText('Can\'t run reconstruction until defined')
        msg.exec_()
        return False

    assert(hasattr(configuration, 'sinograms'))
    if len(configuration.sinograms) is 0:
        msg = qt.QMessageBox()
        msg.setIcon(qt.QMessageBox.Warning)
        msg.setText('No fluorescence sinogram have been found.')
        msg.setInformativeText('You must at least chooce one sinogram to be reconstructed')
        msg.exec_()
        return False

    # in the case we have to get selfAbsMat
    if configuration.reconsType == freeartconfig._ReconsConfig.FLUO_ID:
        allSinoHasSelfAbs = True
        for sinogram in configuration.sinograms:
            if sinogram.selfAbsMat is None:
                allSinoHasSelfAbs = False
                break
        if configuration.materials is None and allSinoHasSelfAbs is False:
            msg = SelfAbsMatMissingInfoMessage()
            if msg.exec_() == qt.QMessageBox.Cancel:
                return False

    return True


class SelfAbsMatMissingInfoMessage(qt.QMessageBox):
    def __init__(self):
        qt.QMessageBox.__init__(self)

        self.setIcon(qt.QMessageBox.Warning)
        self.setText('There is some information missing about self attenuation.'
                    'You can either set now the missing information (press stop)'
                    'Or the fluorescence reconstruction will ask you later'
                    'to define the sample composition.')
        self.setInformativeText(
            'Reminder: either the sample materials have to be defined or'
            'a self attenuation matrix has to be given for all fluorescence sinograms')

        self.yesButton = self.addButton(qt.QMessageBox.Ignore)
        self.noButton = self.addButton(qt.QMessageBox.Cancel)
