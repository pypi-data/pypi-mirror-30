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
__date__ = "31/10/2017"


from silx.gui import qt
from tomogui.gui.utils.ConfigurationActor import ConfigurationActor
from tomogui.configuration.config import FBPConfig
from tomogui.gui.utils.guiutils import QLineEditMetric
from tomogui.gui.utils import icons
try:
    from freeart.resources import resource_filename
    from freeart.configuration import structs
    hasfreeart = True
except:
    hasfreeart = False


class DetSetupGrp(qt.QGroupBox, ConfigurationActor):
    """The group box for the detector geometry

    :param title: the title of the groupbox
    :param parent: the parent of the group box
    """

    FLUO_SETUP_IMG = "fluorescenceSetup"

    FLUO_SETUP_I_IMG = "fluorescenceSetup_i"

    DETEC_WIDTH = "detector width    "

    DETEC_X = "detector x position"
    DETEC_Y = "detector y position"
    DETEC_Z = "detector z position"

    INVERT_ACQUI_ROT = 'Invert acquisition rotation'

    def __init__(self, title, parent=None):
        qt.QGroupBox.__init__(self, parent)

        self.setTitle(title)

        layout = qt.QHBoxLayout()
        layout.addWidget(self._buildUserInterface())
        layout.addWidget(self._buildSetupDisplayer())
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        self.setLayout(layout)

    def _buildUserInterface(self):
        widget = qt.QWidget(parent=self)
        layout = qt.QVBoxLayout()
        widget.setLayout(layout)

        widget.setSizePolicy(qt.QSizePolicy.Minimum,
                             qt.QSizePolicy.Expanding)

        # det distance
        self.qlemDetWidth = QLineEditMetric(widget, self.DETEC_WIDTH)
        layout.addWidget(self.qlemDetWidth)

        # det position
        self.qlemDetPosX = QLineEditMetric(parent=widget,
                                           label=self.DETEC_X,
                                           canBeNegative=True)
        self.qlemDetPosX.setValue(1000.0)
        self.qlemDetPosY = QLineEditMetric(parent=widget,
                                           label=self.DETEC_Y,
                                           canBeNegative=True)
        self.qlemDetPosY.setValue(0.0)
        self.qlemDetPosZ = QLineEditMetric(parent=widget,
                                           label=self.DETEC_Z,
                                           canBeNegative=True)
        self.qlemDetPosZ.setValue(0.0)

        self._qcbInvertRotation = qt.QCheckBox(parent=widget,
                                               text=self.INVERT_ACQUI_ROT)
        self._qcbInvertRotation.toggled.connect(self._changeAcquiDirImg)

        layout.addWidget(self.qlemDetPosX)
        layout.addWidget(self.qlemDetPosY)
        layout.addWidget(self.qlemDetPosZ)
        layout.addWidget(self._qcbInvertRotation)

        self.qlemDetPosZ.lockValueAt(0.0)
        return widget

    def _buildSetupDisplayer(self):
        try:
            self._fluoSetupImg = qt.QSvgWidget(parent=self)
        except:
            self._fluoSetupImg = qt.QLabel(parent=self)

        self._setFluoSetupImg()
        self._fluoSetupImg.setSizePolicy(qt.QSizePolicy.Expanding,
                                         qt.QSizePolicy.Expanding)

        return self._fluoSetupImg

    def _setFluoSetupImg(self, inverted=False):
        if inverted:
            img = self.FLUO_SETUP_I_IMG
        else:
            img = self.FLUO_SETUP_IMG
        if hasfreeart:
            if type(self._fluoSetupImg) is qt.QLabel:
                pixmap = qt.QPixmap()
                pixmap.load(resource_filename(img + '.png'))
                self._fluoSetupImg.setPixmap(pixmap)
            else:
                self._fluoSetupImg.load(resource_filename(img + '.svg'))

    def isAcquiRotationInverted(self):
        """

        :return: if the sinogram angles are in trigonometric direction or not
        """
        return self._qcbInvertRotation.isChecked()

    def _changeAcquiDirImg(self):
        self._setFluoSetupImg(self.isAcquiRotationInverted())

    def saveConfiguration(self, config):
        """
        save widget setup to the configuration file
        """
        if isinstance(config, FBPConfig):
            return
        else:
            assert hasfreeart
            detector = structs.Detector(x=self.qlemDetPosX.getValue(),
                                        y=self.qlemDetPosY.getValue(),
                                        z=self.qlemDetPosZ.getValue(),
                                        width=self.qlemDetWidth.getValue())
            config.detector = detector
            config.acquiInverted = self._qcbInvertRotation.isChecked()

    def loadConfiguration(self, config):
        """
        load the widget setup from a configuration file
        """
        if isinstance(config, FBPConfig) or config.detector is None:
            return

        # det distance
        val = config.detector.width
        if val is not None:
            self.qlemDetWidth.setValue(float(val))

        # det pos X
        val = config.detector.x
        if val is not None:
            self.qlemDetPosX.setValue(float(val))

        # det pos Y
        val = config.detector.y
        if val is not None:
            self.qlemDetPosY.setValue(float(val))

        # det pos Z
        val = config.detector.z
        if val is not None:
            self.qlemDetPosZ.setValue(float(val))

        # angle inversion
        val = config.acquiInverted
        if val is not None:
            self._qcbInvertRotation.setChecked(bool(val))
