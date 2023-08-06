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

try:
    from freeart.configuration import config as freeartconfig
    from freeart.configuration import structs
    from freeart.utils import raypointsmethod as freeartRayPointMethod
    hasfreeart = True
except ImportError:
    from tomogui.third_party.configuration import config as freeartconfig
    hasfreeart = False
from tomogui.configuration import config as tomoguiconfig
from tomogui.gui.utils.ConfigurationActor import ConfigurationActor
from tomogui.gui.datasource.QDataSourceWidget import QDataSourceWidget
from tomogui.gui.utils.guiutils import QLineEditMetric
from tomogui.configuration.config import FBPConfig
from tomogui.gui.sinogramselector import QSinoProjSelector
from tomogui.gui.reconsparam.OpenCLPlatformSelector import OpenCLPlatformSelector
from tomogui.gui.utils import icons
from .DetectorSetup import DetSetupGrp
import sys
import numpy


class ReconsParamWidget(qt.QWidget, ConfigurationActor):
    """
    The widget for user inputs of all reconsparam parameters such as :
        - oversampling
        - damping factor
        - reconsparam mathods (with or without interpolation)
        - detector geometry (for compton and fluorescence)
        - ...
    """

    sigInfoForMaterialsChanged = qt.Signal()
    """Emitted when some information that might help the SampleCompTab like the
    AbsMat or the fluoSinograms"""

    def __init__(self, parent=None):
        """Constructor"""
        super(ReconsParamWidget, self).__init__(parent)
        ConfigurationActor.__init__(self)
        self.setContentsMargins(0, 0, 0, 0)

        self.dims = [0, 0]

        self.defaultOversampling = 2
        self.defaultDampingFactor = 1.0

        self.fluoAndComptonOnlyElements = []
        self.fluoOnlyElements = []

        self._reconstructionType = None

        self.dims = [0, 0]

        layout = qt.QVBoxLayout()

        # defined basic parameters GUI
        self.createGeneralParametersGUI(layout)

        # detector setUp
        self.detectorSetupWidget = DetSetupGrp(
            "Fluorescence detector setUp")
        self.fluoAndComptonOnlyElements.append(self.detectorSetupWidget)
        layout.addWidget(self.detectorSetupWidget)

        # add the option to display the advanced parameters
        self._qbAdvancedOptions = qt.QPushButton("Advanced options")
        self._qbAdvancedOptions.setIcon(icons.getQIcon('add'))
        self._qbAdvancedOptions.setAutoDefault(True)

        myFont = self._qbAdvancedOptions.font()
        myFont.setItalic(True)
        p = self._qbAdvancedOptions.palette()
        p.setColor(qt.QPalette.ButtonText, qt.Qt.blue)
        self._qbAdvancedOptions.setPalette(p)
        self._qbAdvancedOptions.setFont(myFont)

        self._qbAdvancedOptions.clicked.connect(
            self.reverseShowAdvancedParameters)
        self._qbAdvancedOptions.setAutoDefault(True)

        self._qbAdvancedOptions.setFlat(True)

        layout.addWidget(self._qbAdvancedOptions)

        # defined advanced parameters GUI
        self.createAdvancedParametersGUI(layout)

        # spacer
        spacer = qt.QWidget()
        spacer.setSizePolicy(qt.QSizePolicy.Expanding,
                             qt.QSizePolicy.Minimum)
        layout.addWidget(spacer)

        # by default not visible
        self.advancedParamsWidget.hide()

        # selfAbsMat
        self.setLayout(layout)
        self.setToolTip(self.getShortToolTip())

    def getShortToolTip(self):
            return "register all parameters of the ART algorithm"

    def createGeneralParametersGUI(self, layout):
        """
        Build all widgets for the \'general \' parameters
        :param layout: the layout which will register all the widgets created in this section
        """
        def toolTipNbPro():
            return "Take only one projection (eq. proj angle) each n projection (with n = reduction number )"

        def toolTipDefinition():
            return "Take only one voxel (eq. X data) each n voxel (with n = reduction number )"

        self.generalSettings = qt.QGroupBox()
        generalSettingsLayout = qt.QVBoxLayout()
        generalSettingsLayout.setSpacing(4)
        generalSettingsLayout.setContentsMargins(0, 0, 0, 0)

        # oversampling
        self.groupOversampling = qt.QWidget(self)
        layoutOversampling = qt.QHBoxLayout()
        layoutOversampling.setContentsMargins(0, 0, 0, 0)
        layoutOversampling.setSpacing(4)
        self.qlaOversampling = qt.QLabel("Oversampling ")
        self.qleOversampling = qt.QLineEdit()
        self.qlaOversampling.setToolTip(
            "How many points will be evaluated per voxel.")
        self.qleOversampling.setValidator(qt.QIntValidator(0, 99))
        self.qleOversampling.setText(str(self.defaultOversampling))

        layoutOversampling.addWidget(self.qlaOversampling)
        layoutOversampling.addWidget(self.qleOversampling)
        self.groupOversampling.setLayout(layoutOversampling)
        generalSettingsLayout.addWidget(self.groupOversampling)

        # voxel size
        self.qlemVoxelSize = QLineEditMetric(self, "Voxel size")
        self.qlemVoxelSize.setToolTip(
            "What is the width of a voxel in real world")
        generalSettingsLayout.addWidget(self.qlemVoxelSize)

        # damping factor
        self.groupDampingFactor = qt.QWidget(self)
        layoutDampingFactor = qt.QHBoxLayout()
        layoutDampingFactor.setContentsMargins(0, 0, 0, 0)
        layoutDampingFactor.setSpacing(4)
        self.qlaRelaxationFactor = qt.QLabel("Relaxation factor ")
        layoutDampingFactor.addWidget(self.qlaRelaxationFactor)
        self.qleDampingFactor = qt.QLineEdit(parent=self.groupDampingFactor)
        self.qleDampingFactor.setValidator(qt.QDoubleValidator(0, 1.0, 100))
        self.qleDampingFactor.setText(str(self.defaultDampingFactor))
        self.groupDampingFactor.setLayout(layoutDampingFactor)
        layoutDampingFactor.addWidget(self.qleDampingFactor)
        generalSettingsLayout.addWidget(self.groupDampingFactor)

        # projection selection
        self._projectionSelector = QSinoProjSelector(parent=self)
        self._projectionSelector.setToolTip(
            'The projection can be selected using the same synthax as '
            'python slicing: \n'
            '   - ":" will select all the projections\n'
            '   - ":-2" will select all the projection except the two last\n'
            '   - "1:3" will select the second and third projections'
            'otherwise you can select the projections from the interative mode')
        generalSettingsLayout.addWidget(self._projectionSelector)

        # data reduction
        self.groupDataReduction = qt.QGroupBox("data reduction", self)
        layoutDataReduction = qt.QGridLayout()

        lProj = qt.QLabel("reduce number of projection by : ")
        lProj.setToolTip(toolTipNbPro())
        layoutDataReduction.addWidget(lProj, 0, 0)
        self.qleProjectionReduction = qt.QLineEdit("1",
                                                   self.groupDataReduction)
        self.qleProjectionReduction.setToolTip(toolTipNbPro())
        self.qleProjectionReduction.setValidator(qt.QIntValidator(0, 1000000))
        layoutDataReduction.addWidget(self.qleProjectionReduction, 0, 1)

        lDef = qt.QLabel("reduce definition by : ")
        lDef.setToolTip(toolTipDefinition())
        layoutDataReduction.addWidget(lDef, 1, 0)
        self.qleDefinitionReduction = qt.QLineEdit("1",
                                                   self.groupDataReduction)
        self.qleProjectionReduction.setToolTip(toolTipDefinition())
        self.qleDefinitionReduction.setValidator(qt.QIntValidator(0, 1000000))
        layoutDataReduction.addWidget(self.qleDefinitionReduction, 1, 1)
        spacer = qt.QWidget()
        spacer.setSizePolicy(qt.QSizePolicy.Expanding,
                             qt.QSizePolicy.Minimum)

        layoutDataReduction.addWidget(spacer, 1, 2)
        layoutDataReduction.addWidget(spacer, 0, 2)

        self.groupDataReduction.setLayout(layoutDataReduction)
        generalSettingsLayout.addWidget(self.groupDataReduction)

        # angle information
        self.groupAngle = qt.QGroupBox("projection information", self)
        layoutAngle = qt.QGridLayout()

        layoutAngle.addWidget(qt.QLabel("min angle (deg)"), 0, 0)
        self.qleMinAngle = qt.QLineEdit("0.0", self.groupAngle)
        self.qleMinAngle.setValidator(qt.QDoubleValidator(0.0, 360.0, 5))
        layoutAngle.addWidget(self.qleMinAngle, 0, 1)

        layoutAngle.addWidget(qt.QLabel("max angle (deg)"), 1, 0)
        self.qleMaxAngle = qt.QLineEdit("360.0", self.groupAngle)
        self.qleMaxAngle.setValidator(qt.QDoubleValidator(0.0, 360.0, 5))
        layoutAngle.addWidget(self.qleMaxAngle, 1, 1)

        self._qpbIncludeMaxAngle = qt.QPushButton("]", self)
        self.setLastAngleIsIncluded(True)
        self._qpbIncludeMaxAngle.setAutoDefault(True)
        self._qpbIncludeMaxAngle.clicked.connect(self._updateInculdeButton)
        tooltip = """if include the max angle (']') we interpolate n values
            between min and max. If not ('[') we will interpolate n +1 value
            and remove the last value. """
        self._qpbIncludeMaxAngle.setToolTip(tooltip)
        layoutAngle.addWidget(self._qpbIncludeMaxAngle, 1, 2)

        self.groupAngle.setLayout(layoutAngle)
        generalSettingsLayout.addWidget(self.groupAngle)

        # E0 - EF information
        self.groupE0EF = qt.QGroupBox("E0 - EF information", self)
        layoutE0EF = qt.QGridLayout()

        layoutE0EF.addWidget(qt.QLabel("E0 (keV) : "), 0, 0)
        self.qleE0 = qt.QLineEdit("1.0", self.groupE0EF)
        self.qleE0.setValidator(qt.QDoubleValidator(0.0, float("inf"), 100))
        layoutE0EF.addWidget(self.qleE0, 0, 1)

        self.fluoOnlyElements.append(self.groupE0EF)

        self.groupE0EF.setLayout(layoutE0EF)
        generalSettingsLayout.addWidget(self.groupE0EF)

        self._openCLSelector = OpenCLPlatformSelector(parent=self)
        generalSettingsLayout.addWidget(self._openCLSelector)

        self.generalSettings.setLayout(generalSettingsLayout)
        layout.addWidget(self.generalSettings)

    def _updateInculdeButton(self):
        """Switch value of includeLastAngle"""
        self.setLastAngleIsIncluded(not self.__includeLastAngle)

    def getOpenCLDevice(self):
        return self._openCLSelector.getSelectedDevice()

    def _sinogramDim_haschanged(self, dims):
        """Callback when the sinogram dimensions change"""
        assert(len(dims) == 2)

        if self.dims != dims:
            self.dims = dims
            x = self.dims[0]
            assert(type(x) is int)
            # reset the dampingFactor proposed
            if self.getDampingFactor() >= 1.0:
                self.setDampingFactor(1.0/x)

            # reset the projection selection
            self._projectionSelector.setSelection(":")

    def createAdvancedParametersGUI(self, layout):
        """
        Build all widget for the \'Advanced'\ options part.

        :param layout: the layout which will register all the widgets created
                       in this section
        """
        def getToolTipBeamCalculation():
            return 'Freeart is using ray tracing algorithm. \n' \
                   'In order to compute effect of absorption ' \
                   'the point sample on the ray can only affect ' \
                   'the voxel the point is in or his neighbours also. \n' \
                   'This is respectively the without and the ' \
                   'with interpolation cases.'

        def getToolTipOutgoingRayCalculation():
            return """
                <html>
                Algorithm to compute the outgoing ray.
                <ul>
                    <li>raw approximation </li>
                    <li>create one ray per sammple point </li>
                    <li>matrice subdivision </li>
                </ul>
                </html>"""

        self.advancedParamsWidget = qt.QGroupBox()
        self.advancedParamsWidget.setTitle("Advanced options")
        self.advancedParamsWidget.setLayout(qt.QVBoxLayout())
        layout.addWidget(self.advancedParamsWidget)

        # precision
        gpPrecision = qt.QGroupBox('calculation precision',
                                   parent=self.advancedParamsWidget)
        gpPrecision.setLayout(qt.QHBoxLayout())
        gpPrecision.setToolTip('freeart has been mainly tested on double '
                               'precision so it is recommand it to use double '
                               'precision. But this will take more memory to run.')
        self.qcbSimplePrec = qt.QRadioButton("simple", parent=gpPrecision)
        gpPrecision.layout().addWidget(self.qcbSimplePrec)
        self.qcbDoublePrec = qt.QRadioButton("double", parent=gpPrecision)
        gpPrecision.layout().addWidget(self.qcbDoublePrec)

        self.qcbDoublePrec.setChecked(True)
        self.advancedParamsWidget.layout().addWidget(gpPrecision)

        # beamCalculationMethod
        gpInterpolation = qt.QGroupBox('interpolation',
                                       parent=self.advancedParamsWidget)
        gpInterpolation.setLayout(qt.QHBoxLayout())
        gpInterpolation.setToolTip(getToolTipBeamCalculation())

        self.qcbWithInterpolation = qt.QRadioButton("with", parent=gpInterpolation)
        gpInterpolation.layout().addWidget(self.qcbWithInterpolation)
        self.qcbWithoutInterpolation = qt.QRadioButton("without", parent=gpInterpolation)
        gpInterpolation.layout().addWidget(self.qcbWithoutInterpolation)

        self.qcbWithInterpolation.setChecked(True)
        self.advancedParamsWidget.layout().addWidget(gpInterpolation)

        # outgoingBeamCalculation
        outBCWid = qt.QWidget(parent=self.advancedParamsWidget)
        outBCWid.setLayout(qt.QHBoxLayout())
        outBCWid.setToolTip(getToolTipOutgoingRayCalculation())
        self.advancedParamsWidget.layout().addWidget(outBCWid)
        outBCWid.layout().addWidget(qt.QLabel('outgoing beam calculation method',
                                    parent=outBCWid))
        self.qcbOutgoingBeamCalculation = qt.QComboBox(outBCWid)
        self.fluoAndComptonOnlyElements.append(outBCWid)
        # Warning : should always be stored in this order, otherwise may fail
        # Would be better to link it from the FreeARTReconsParam...
        self.qcbOutgoingBeamCalculation.addItem("rawApproximation")
        self.qcbOutgoingBeamCalculation.addItem("createOneRayPerSamplePoint")
        self.qcbOutgoingBeamCalculation.addItem("matriceSubdivision")
        self.advancedParamsWidget.layout().addWidget(self.qcbOutgoingBeamCalculation)

        # turn off solid angle
        self.qcbTurnOff = qt.QCheckBox("turn off solid angle",
                                       self.advancedParamsWidget)
        self.advancedParamsWidget.layout().addWidget(self.qcbTurnOff)

    def reverseShowAdvancedParameters(self):
        """
        If the advanced widgets are visible, hide them.
        If the advanced widgets are hidden, show them.
        """
        self.advancedParamsWidget.setVisible(
            not self.advancedParamsWidget.isVisible())

    def saveConfiguration(self, config):
        """
        Store input data into the configuration file

        :param config : the configuration file to save the current
                        configuration
        """
        assert isinstance(config, freeartconfig._ReconsConfig)
        config.minAngle = self.getMinAngle()
        config.maxAngle = self.getMaxAngle()
        config.projections = self.getProjections()
        config.includeLastProjection = self.isLastAngleIncluded()
        config.definitionReduction = self.getDefinitionReduction()
        config.projectionNumberReduction = self.getProjectionReductionFactor()

        if isinstance(config, freeartconfig.TxConfig) or isinstance(config, freeartconfig.FluoConfig):
            config.precision = self.getPrecision()
            config.voxelSize = self.getVoxelSize()
            config.oversampling = self.getOversampling()
            config.dampingFactor = self.getDampingFactor()
            config.beamCalcMethod = self.getRayPointsMethod()
            config.solidAngleOff = self.isSolidAngleOff()

        if isinstance(config, freeartconfig.FluoConfig):
            config.E0 = self.getE0()
            config.outBeamCalMethod = self.getOutgoingRayAlgorithm()
            self.detectorSetupWidget.saveConfiguration(config)

    def loadConfiguration(self, conf):
        """
        Load configuration from a configuration file

        :param conf : the configuration file to load the current
                        configuration
        """
        assert isinstance(conf, freeartconfig._ReconsConfig)
        self.setMinAngle(float(conf.minAngle or 0.0))
        self.setMaxAngle(float(conf.maxAngle or numpy.pi * 2.0))
        self.setProjections(str(conf.projections))
        self.setLastAngleIsIncluded(bool(conf.includeLastProjection))
        self.setDefinitionReduction(int(conf.definitionReduction))
        self.setProjectionReductionFactor(int(conf.projectionNumberReduction))

        if isinstance(conf, freeartconfig.TxConfig) or isinstance(conf, freeartconfig.FluoConfig):
            self.setPrecision(str(conf.precision))
            self.setVoxelSize(float(conf.voxelSize), unit="cm")
            self.setOversampling(int(conf.oversampling))
            self.setDampingFactor(float(conf.dampingFactor or 0.1))
            self.setRayPointsMethod(int(conf.beamCalcMethod))
            self.setSolidAngleOff(bool(conf.solidAngleOff))

        if isinstance(conf, freeartconfig.FluoConfig):
            self.setE0(float(conf.E0 or 1.0))
            self.setOutgoingRayAlgorithm(int(conf.outBeamCalMethod))
            self.detectorSetupWidget.loadConfiguration(conf)

    def getOversampling(self):
        """

        :return: the oversampling
        """
        return int(self.qleOversampling.displayText())

    def setOversampling(self, val):
        """
        Set the oversampling

        :param val: the new value of the oversampling. Must be an int
        """
        assert(type(val) == int)
        self.qleOversampling.setText(str(val))

    def getDampingFactor(self):
        """

        :return: the damping factor recorded
        """
        return float(self.qleDampingFactor.displayText())

    def setDampingFactor(self, val):
        """
        Set the damping factor

        :param val: the new value of the damping factor. Must be a float
        """
        assert(type(val) == float)
        self.qleDampingFactor.setText(str(val))

    def getRayPointsMethod(self):
        """

        :return: the method used for beam calculation
        """
        if self.qcbWithInterpolation.isChecked():
            return freeartRayPointMethod.withInterpolation
        else:
            return freeartRayPointMethod.withoutInterpolation

    def setRayPointsMethod(self, val):
        """
        Set the method used for beam calculation

        :param val: the new method to compute beams. Value can be
                    BeamCalculationMethod.withInterpolation or
                    BeamCalculationMethod.withoutInterpolation
        """
        assert(type(val) == int)
        if val == freeartRayPointMethod.withInterpolation:
            self.qcbWithInterpolation.setChecked(True)
        else:
            self.qcbWithoutInterpolation.setChecked(True)

    def getOutgoingRayAlgorithm(self):
        """

        :return: the method used for outgoing beam calculation
        """
        return self.qcbOutgoingBeamCalculation.currentIndex()

    def setOutgoingRayAlgorithm(self, val):
        """
        Set the method used for outgoing beam calculation

        :param val: the new method to compute beams.
                    Value can be OutgoingBeamCalculationMethod.rawApproximation,
                    OutgoingBeamCalculationMethod.createOneRayPerSamplePoint or
                    OutgoingBeamCalculationMethod.matriceSubdivision
        """
        assert(type(val) == int)
        return self.qcbOutgoingBeamCalculation.setCurrentIndex(val)

    def getVoxelSize(self):
        """
        Return the size of the voxel in the experimentation
        """
        return self.qlemVoxelSize.getValue()

    def setVoxelSize(self, val, unit="cm"):
        """
        Set the size of the voxel in the experimentation

        :param val: The new size of the voxel
        :param unit: the unit in which the voxel size is given
        """
        self.qlemVoxelSize.setValue(val, unit)

    def isSolidAngleOff(self):
        """

        :return: True if we want to turn of the solid Angle
                 (Then solid angle will always be 1)
        """
        return bool(self.qcbTurnOff.isChecked())

    def setSolidAngleOff(self, b):
        """
        Set the solidAngleOff value
        :param b: True if we want to turn off the solid angle
        """
        assert(type(b) == bool)
        self.qcbTurnOff.setChecked(b)

    def setLastAngleIsIncluded(self, b):
        """
        Notice that the last projection of the sinogram is from the same angle
        as the first projection

        :param b: True if the last projection of the sinogram is from the same
                  angle as the first projection
        """
        assert(type(b) == bool)
        self.__includeLastAngle = b
        if b:
            self._qpbIncludeMaxAngle.setText(']')
        else:
            self._qpbIncludeMaxAngle.setText('[')

    def isLastAngleIncluded(self):
        """

        :return: True if the last projection of the sinogram is from the same
                 angle as the first projection
        """
        return self.__includeLastAngle

    def getProjections(self):
        return self._projectionSelector.getSelection()

    def setProjections(self, projections):
        return self._projectionSelector.setSelection(projections)

    def setProjectionReductionFactor(self, val):
        """
        Set the factor of witch we want to reduce the number of projection
        (for speeding up for example)

        :param val: the factor of reduction for the projections number.
                    Must be an int
        """
        assert(type(val) is int)
        self.qleProjectionReduction.setText(str(val))

    def getProjectionReductionFactor(self):
        """

        :return: the factor of witch we want to reduce the number of projection
                 (for speeding up for example)
        """
        return int(self.qleProjectionReduction.displayText())

    def setDefinitionReduction(self, val):
        """
        Set the factor of witch we want to reduce the number of voxels
        (for speeding up for example)

        :param val: the factor of reduction for the voxels number.
                    Must be an int
        """
        assert(type(val) == int)
        self.qleDefinitionReduction.setText(str(val))

    def getDefinitionReduction(self):
        """

        :return: the factor of witch we want to reduce the number of voxels
                 (for speeding up for example)
        """
        return int(self.qleDefinitionReduction.displayText())

    def setE0(self, val):
        """
        Set the new E0 value (in keV)

        :param val: The E0 value to set
        """
        assert(type(val) is float)
        self.qleE0.setText(str(val))

    def getE0(self):
        """

        :return: the E0 value set by the used (in keV)
        """
        return float(self.qleE0.displayText())

    def getMinAngle(self):
        """

        :return: the min angle of the acquisition
        """
        return float(self.qleMinAngle.displayText())/180.0*numpy.pi

    def setMinAngle(self, val):
        """
        Set the min Angle

        :param float val: the new value of the angle
        """
        assert(type(val) is float)
        # convert from radian to float
        self.qleMinAngle.setText(str(val * 180.0 / numpy.pi))

    def getMaxAngle(self):
        """

        :return: the max angle of the acquisition
        """
        return float(self.qleMaxAngle.displayText()) / 180.0 * numpy.pi

    def setMaxAngle(self, val):
        """
        Set the max Angle

        :param float val: the new value of the angle
        """
        assert(type(val) is float)
        self.qleMaxAngle.setText(str(val*180.0/numpy.pi))

    def setPrecision(self, precision):
        if precision == 'simple':
            self.qcbSimplePrec.setChecked(True)
        else:
            self.qcbDoublePrec.setChecked(True)

    def getPrecision(self):
        if self.qcbSimplePrec.isChecked():
            return 'simple'
        else:
            return 'double'

    def _setReconstructionType(self, event):
        """
        Set the widget to fit to the reconsparam type

        :param event: the event received. Must contained the key
                      'reconstructionType'
        """
        if event['event'] == "reconstructionTypeChanged":
            assert('reconstructionType' in event)
            self._reconstructionType = event['reconstructionType']
            # deal with elements used for compton and fluorescence only
            for elemt in self.fluoAndComptonOnlyElements:
                if self._reconstructionType in [freeartconfig._ReconsConfig.FLUO_ID,
                                                freeartconfig._ReconsConfig.COMPTON_ID]:
                    elemt.show()
                else:
                    elemt.hide()

            # deal with elements used for fluorescence only
            for elemt in self.fluoOnlyElements:
                if self._reconstructionType == freeartconfig._ReconsConfig.FLUO_ID:
                    elemt.show()
                else:
                    elemt.hide()

            iterOptVis = self._reconstructionType != tomoguiconfig.FBPConfig.FBP_ID
            self.groupOversampling.setVisible(iterOptVis)
            self.qlemVoxelSize.setVisible(iterOptVis)
            self.groupDampingFactor.setVisible(iterOptVis)
            self._qbAdvancedOptions.setVisible(iterOptVis)
            # to fit the default behavior of hidden we have to add an extra check
            if self.advancedParamsWidget.isVisible() is True:
                self.advancedParamsWidget.setVisible(iterOptVis)
            self.groupDataReduction.setVisible(iterOptVis)
            self._openCLSelector.setVisible(not iterOptVis)

    def lockReconstructionParameters(self):
        """
        Lock all reconsparam parameters the user can t interact with
        """
        self.detectorSetupWidget.setEnabled(False)
        self.qlemVoxelSize.setEnabled(False)
        self.groupDataReduction.setEnabled(False)
        self.qcbTurnOff.setEnabled(False)
        self._qpbIncludeMaxAngle.setEnabled(False)
        self.qleE0.setEnabled(False)


if __name__ == "__main__":
    global app
    app = qt.QApplication([])
    widget = ReconsParamWidget(parent=None)
    widget.show()
    app.exec_()
