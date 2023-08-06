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

__author__ = ["P. Paleo, H. Payno"]
__license__ = "MIT"
__date__ = "24/05/2016"

import silx.gui
from silx.gui import qt, icons
from silx.gui.plot import PlotWindow, PlotWidget, ImageView

import tomogui.core.utils as utils
from tomogui.configuration.config import FBPConfig
from tomogui.gui.utils.ConfigurationActor import ConfigurationActor
try:
    from freeart.configuration import config
except ImportError:
    from tomogui.third_party.configuration import config


class QRotationCenterWidget(qt.QWidget, ConfigurationActor):
    """
    Widget able to compute the rotation center of a given sinogram or recording
    the one given by the user"""

    sigCenterchanged = qt.Signal(int)
    """Emitted when some information that might help the SampleCompTab like the
    AbsMat or the fluoSinograms"""

    def __init__(self, parent):
        """
        Constructor
        :param parent: the parent of the widget in the Qt hierarchy
        """         
        super(QRotationCenterWidget, self).__init__(parent)

        layoutV = qt.QVBoxLayout(self)

        # Center of rotation widget
        layoutV.setContentsMargins(0, 0, 0, 0)
        layoutV.setSpacing(0)

        spacerBegin = qt.QWidget()
        spacerBegin.setSizePolicy(qt.QSizePolicy.Expanding,
                             qt.QSizePolicy.Expanding)

        layoutV.addWidget(spacerBegin)

        self.rbGiveCenter = qt.QRadioButton("give center manually")
        self.rbTakeMediumPoint = qt.QRadioButton("take the middle value from the sinogram definition ")
        self.rbComputeCenterAbsorption = qt.QRadioButton("compute the center of rotation for absorption sinogram (transmission)")
        self.rbComputeCenterEmission = qt.QRadioButton("compute the center of rotation for emission sinogram (fluorescence, compton ...)")

        layoutV.addWidget(self.rbComputeCenterEmission)
        layoutV.addWidget(self.rbComputeCenterAbsorption)
        layoutV.addWidget(self.rbGiveCenter)
        layoutV.addWidget(self.rbTakeMediumPoint)

        self.rbGiveCenter.toggled.connect(self.updateCenterOfRotationInfo)
        self.rbGiveCenter.setToolTip("Give manually the center of rotation")
        self.rbTakeMediumPoint.toggled.connect(self.updateCenterOfRotationInfo)
        self.rbTakeMediumPoint.setToolTip("Pich the middle x value as the center of rotation (equal no normalization)")
        self.rbComputeCenterAbsorption.toggled.connect(self.updateCenterOfRotationInfo)
        self.rbComputeCenterAbsorption.setToolTip("Compute the center of rotation using the center of mass for absorption sinogram")
        self.rbComputeCenterEmission.toggled.connect(self.updateCenterOfRotationInfo)
        self.rbComputeCenterEmission.setToolTip("Compute the center of rotation using the center of mass for emission sinogram")

        self.groupRotationWidgetValue = qt.QGroupBox(self)
        layoutH2 = qt.QHBoxLayout()
        self.qlRotationCenter = qt.QLabel("center of rotation will be : ")
        self.qleRotationCenter = qt.QLineEdit("0", parent=self.groupRotationWidgetValue)
        self.qleRotationCenter.textChanged.connect(self.notifyCenterChanged)
        self.qleRotationCenter.setValidator(qt.QIntValidator(-1, 0))
        layoutH2.addWidget(self.qlRotationCenter)
        layoutH2.addWidget(self.qleRotationCenter)
        layoutH2.setContentsMargins(0, 0, 0, 0)
        layoutH2.setSpacing(4)
        self.groupRotationWidgetValue.setLayout(layoutH2)
        layoutV.addWidget(self.groupRotationWidgetValue)

        # add the vertical spacer
        spacerEnd = qt.QWidget()
        spacerEnd.setSizePolicy(qt.QSizePolicy.Expanding,
                             qt.QSizePolicy.Expanding)

        layoutV.addWidget(spacerEnd)
        layoutV.setContentsMargins(0, 0, 0, 0)
        layoutV.setSpacing(4)

        self.data = None
        self.setLayout(layoutV)
        
        # by default the active option is 'take the middle point'
        self.rbTakeMediumPoint.setChecked(True)

    def notifyCenterChanged(self):
        self.sigCenterchanged.emit(self.getCenter())

    def updateCenterOfRotationInfo(self):
        """
        callback when the radio button to select the method to get the center of rotation is changed
        """
        if self.rbGiveCenter.isChecked():
            self.qleRotationCenter.setEnabled(True)
        elif self.rbComputeCenterAbsorption.isChecked():
            self.qleRotationCenter.setEnabled(False)
            if self.data is not None:
                self.setCenter(int(round(utils.calc_center_corr(self.data))))
        elif self.rbComputeCenterEmission.isChecked():
            self.qleRotationCenter.setEnabled(False)
            if self.data is not None:
                data = self.data.copy()
                data = data.max() - data
                self.setCenter(int(round(utils.calc_center_corr(data))))
        elif self.rbTakeMediumPoint.isChecked():
            self.qleRotationCenter.setEnabled(False)
            if self.data is not None:
                self.setCenter(self.data.shape[1] // 2)

        if self.data is not None:
            self.qleRotationCenter.setValidator(qt.QIntValidator(-1, self.data.shape[1]-1))

    def dataChanged(self, data):
        """
        Function called when the data to treat have been changed
        """
        self.data = data
        self.updateCenterOfRotationInfo()

    def saveConfiguration(self, config):
        """
        save the configuration in the given configParser
        """
        config.center = self.getCenter()

    def loadConfiguration(self, config):
        """
        Update the widget fron a configuraton file
        :param filePath: The path of the configuration file. Warning: This must be a \'.cfg\' file
        """
        val = int(config.center)
        if val:
            self.setCenter(val)
        # for loading we considerer that the user gave himself the value
        self.rbGiveCenter.setChecked(True)

    def getCenter(self):
        return int(self.qleRotationCenter.displayText())

    def setCenter(self, val):
        """
        Set the center of rotation
        :param val: the new center of rotation
        """
        assert(type(val) == int)
        self.qleRotationCenter.setText(str(val))

