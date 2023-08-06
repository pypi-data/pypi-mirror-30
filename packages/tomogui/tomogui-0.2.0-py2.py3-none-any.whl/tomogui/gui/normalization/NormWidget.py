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
__date__ = "10/11/2017"


from silx.gui import qt
from tomogui.configuration import config as configtomogui
from tomogui.gui.utils.ConfigurationActor import ConfigurationActor
from tomogui.gui.normalization.QCenteringWidget import QCenteringWidget
from tomogui.gui.datasource.QDataSourceWidget import QDataSourceWidget
from tomogui.gui.utils.QFileManagement import Q2DDataSelection
from tomogui.configuration.config import FBPConfig
try:
    from freeart.configuration import structs, config as freeartconfig
except ImportError:
    from tomogui.third_party.configuration import structs, config as freeartconfig


class NormWidget(qt.QWidget, ConfigurationActor):
    """
    Widget containing all widgets used for sinogram normalization

    :param parent: the parent of the widget in the Qt hierarchy
    """

    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)

        layout = qt.QVBoxLayout()

        self.centeringWidget = QCenteringWidget(parent=self,
                                                withGraphSum=True,
                                                withFileSelection=False)
        layout.addWidget(self.centeringWidget)
        self.I0Normalization = QI0NormalizationWidget(self)
        layout.addWidget(self.I0Normalization)
        self.setLayout(layout)

        self.setToolTip(self.getShortToolTip())

    def clean(self):
        self.centeringWidget.clean()
        self.I0Normalization.clean()

    def saveConfiguration(self, config):
        """
        dump informations in a configuration file

        :param config: the configuration to save information
        """
        self.centeringWidget.saveConfiguration(config)
        if type(config) is not FBPConfig:
            self.I0Normalization.saveConfiguration(config)

    def loadConfiguration(self, config):
        """
        load input file information fron a cfg file

        :param config: the configuration to load information
        """
        self.centeringWidget.loadConfiguration(config)
        if type(config) is not FBPConfig:
            self.I0Normalization.loadConfiguration(config)

    def getShortToolTip(self):
        return "Define normalization values for the sinograms used"

    def reconstructionTypeChanged(self, reconsType):
        """
        Callback when the reconsparam type is saved
        """
        assert type(reconsType) is dict
        self.I0Normalization.setVisible(
            reconsType['reconstructionType'] != configtomogui.FBPConfig.FBP_ID)


class QI0NormalizationWidget(qt.QWidget, ConfigurationActor):
    """
    Widget containg all needs for the I0 normalization
    """
    def __init__(self, parent=None):
        """
        Constructor

        :param parent: the parent of the widget in the Qt hierarchy
        """
        def getToolTip():
            return """
            <html>
                If normalization I0 from a sinogram is activated then enter the path to the I0 sinogram.
                Else give a numerical value to define I0.
                </html>"""

        qt.QWidget.__init__(self, parent)
        ConfigurationActor.__init__(self)
        layout = qt.QVBoxLayout()
        self.setLayout(layout)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(4)

        # checkbox
        self._qcbI0FromFile = qt.QCheckBox("Normalize I0 from a sinogram")
        layout.addWidget(self._qcbI0FromFile)

        # selection from a file
        self._qssI0Sinogram = Q2DDataSelection(parent=self,
                                               text="Select I0 file")
        layout.addWidget(self._qssI0Sinogram)

        # selection from a constant I0
        self._qwI0Const = qt.QWidget(self)
        I0ConstLayout = qt.QHBoxLayout()
        I0ConstLayout.addWidget(qt.QLabel("I0 = "))
        self._qleI0Const = qt.QLineEdit('1.0')
        self._qleI0Const.setValidator(qt.QDoubleValidator(0.000000000001,
                                                          float("inf"),
                                                          100))
        I0ConstLayout.addWidget(self._qleI0Const)
        self._qwI0Const.setLayout(I0ConstLayout)
        layout.addWidget(self._qwI0Const)
        self._qssI0Sinogram.hide()

        self._computeMinusLog = qt.QCheckBox("Compute -log()")
        tooltip = "If the given sinogram for absorption is 'I' then this should be activated."
        tooltip += "If the given sinogram is already -log(I/I0) then you can deactivate the option."
        # TODO : deal with show/hide of this option
        self._computeMinusLog.setToolTip(tooltip)
        self._computeMinusLog.setChecked(True)
        layout.addWidget(self._computeMinusLog)

        # connect the check box
        self._qcbI0FromFile.stateChanged.connect(self._switchSelectionMode)

        self.setToolTip(getToolTip())

    def clean(self):
        self._qcbI0FromFile.setCheckState(qt.Qt.Unchecked)

    def _switchSelectionMode(self):
        """
        switch from a file selection to a constante float selection to define
        I0 or the over way around
        """
        if self._qcbI0FromFile.isChecked():
            self._qwI0Const.hide()
            self._qssI0Sinogram.show()
        else:
            self._qssI0Sinogram.hide()
            self._qwI0Const.show()

    def saveConfiguration(self, config):
        """
        dump informations in a configuration file

        :param config: the configuration to save information
        """
        if self._qcbI0FromFile.isChecked():
            ds = self._qssI0Sinogram.getDataStored()
            config.I0 = structs.I0Sinogram(fileInfo=ds.fileInfo,
                                           data=ds.data)
        else:
            config.I0 = float(self._qleI0Const.displayText())
        if isinstance(config, freeartconfig.TxConfig):
            config.computeLog = self._computeMinusLog.isChecked()

    def loadConfiguration(self, config):
        """
        load input file information fron a cfg file

        :param config: the configuration to load information
        """
        if config.useAFileForI0 is True:
            self._qcbI0FromFile.setCheckState(qt.Qt.Checked)
            self._qssI0Sinogram.setDataStored(config.getI0())
        else:
            self._qcbI0FromFile.setCheckState(qt.Qt.Unchecked)
            I0 = config.getI0()
            if I0 is not None:
                self._qleI0Const.setText(str(I0))

        if hasattr(config, 'computeLog'):
            self._computeMinusLog.setChecked(config.computeLog)

    def setI0(self, i0):
        """Update the numerical value of I0"""
        assert(i0 is not None)
        if isinstance(i0, structs.I0Sinogram):
            self._qcbI0FromFile.setCheckState(qt.Qt.Checked)
            self._qssI0Sinogram.setDataStored(i0)
        else:
            self._qcbI0FromFile.setCheckState(qt.Qt.Unchecked)
            self._qleI0Const.setText(str(i0))
