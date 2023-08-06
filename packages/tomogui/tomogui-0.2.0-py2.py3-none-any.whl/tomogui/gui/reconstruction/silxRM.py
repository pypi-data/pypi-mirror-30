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
from silx.gui.plot.Colormap import Colormap
from silx.opencl.backprojection import Backprojection
from .ReconsManagerBase import ReconsManagerBase
import os
from tomogui.configuration import config as tomoguiconfig
from tomogui.gui.utils.QPlotWidget import QImageStackPlot, QDoubleImageStackPlot
from silx.gui.plot import Plot2D
try:
    from freeart.configuration import read as readConfigFile
    from freeart.utils import sinogramselection
except ImportError:
    from tomogui.third_party.configuration import read as readConfigFile
    from tomogui.third_party import sinogramselection
import numpy
import logging

_logger = logging.getLogger(__name__)


class SilxReconsManager(ReconsManagerBase):
    """
    Class to manage the silx reconstuctions
    """

    def __init__(self, parent, cfgFile=None, config=None, platformId=None,
                 deviceId=None):
        ReconsManagerBase.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0)
        assert deviceId is None or type(deviceId) is int
        assert platformId is None or type(platformId) is int
        self._deviceId = deviceId
        self._platformId = platformId
        self.config = config
        self.__buildGUI()
        if self.config is None:
            self.loadConfig(cfgFile)

        assert(self.config.sinograms is not None)
        iUnknowSino = 0
        for sinogram in self.config.sinograms:
            sinogram.loadData(cfgFile)
            if sinogram.name is None:
                sinogram.name = 'sinogram_' + str(iUnknowSino)
                iUnknowSino += 1
            assert sinogram.data is not None

        self.runReconstruction()

    def loadConfig(self, cfgFile):
        """
        Run the reconsparam from a saved cfg file

        :param cfgFile: the file from witch we want to load the reconsparam
                        parameters
        """
        if cfgFile is None or not os.path.isfile(cfgFile):
            raise RuntimeError("Please give a valid cfgFile to be intrepreted")

        self.config = readConfigFile(cfgFile)
        for sinogram in self.config.sinograms:
            sinogram.loadData(cfgFile)

    def runReconstruction(self):
        """

        :param config: the FBP configuration to run the reconstruction
        """
        assert isinstance(self.config, tomoguiconfig.FBPConfig)
        assert self.config.sinograms is not None
        assert len(self.config.sinograms) > 0
        for sinogram in self.config.sinograms:
            assert sinogram.data is not None

        self.recons = {}

        for sinogram in self.config.sinograms:
            assert sinogram.data.ndim is 2
            nbAngles = sinogram.data.shape[0]
            angles = numpy.linspace(self.config.minAngle,
                                    self.config.maxAngle,
                                    nbAngles)

            sinoForRebuid = sinogramselection.getSelection(projections=sinogram.data,
                                                           selection=self.config.projections)

            angles = sinogramselection.getSelection(projections=angles,
                                                    selection=self.config.projections)

            info = 'Projection goes from %s to %s' % (angles[0], angles[-1])
            _logger.info(info)

            fbp = Backprojection(sino_shape=sinoForRebuid.shape,
                                 slice_shape=None,
                                 axis_position=self.config.center,
                                 angles=angles,
                                 filter_name=None,
                                 ctx=None,
                                 devicetype="all",
                                 platformid=self._platformId,
                                 deviceid=self._deviceId,
                                 profile=False)
            recons = fbp.filtered_backprojection(sinoForRebuid)
            self.recons[sinogram.name] = recons
            self.addReconsImage(sinogram, recons)

        self.controlSlider.setRange(0, max(len(self.config.sinograms)-1, 0))

    def resetPlotsZoom(self):
        self._plotSinoRecons.resetZoom()
        self._plotRecons.resetZoom()

    def __buildGUI(self):
        self._centralWidget = qt.QWidget(parent=self)
        self.setCentralWidget(self._centralWidget)

        self._centralWidget.setLayout(qt.QHBoxLayout())
        self._centralWidget.layout().setContentsMargins(0, 0, 0, 0)

        self._mainWidget = qt.QTabWidget(self._centralWidget)
        self._centralWidget.layout().addWidget(self._mainWidget)

        self.controlSlider = qt.QSlider(parent=self)
        self.controlSlider.setTickPosition(2)
        self.controlSlider.setContentsMargins(0, 0, 0, 0)
        self._centralWidget.layout().addWidget(self.controlSlider)

        # build sinogram / reconstruction plot
        self._plotSinoRecons = QDoubleImageStackPlot(parent=self)
        self._plotSinoRecons.setContentsMargins(0, 0, 0, 0)
        # connect the slider with the control slider
        self.controlSlider.valueChanged.connect(
            self._plotSinoRecons._qslider.setValue)
        # hide it to only keep the control slider
        self._plotSinoRecons._qslider.hide()

        self._mainWidget.addTab(self._plotSinoRecons,
                                'Sinograms and reconstruction')

        # build reconstruction plot
        self._plotRecons = QImageStackPlot(parent=self)
        self._plotRecons.showTitle(True)
        self._plotRecons.setContentsMargins(0, 0, 0, 0)
        self._plotRecons.showTitle(True)
        self._mainWidget.addTab(self._plotRecons, 'Reconstruction')

        # connect the slider with the control slider
        self.controlSlider.valueChanged.connect(
            self._plotRecons._qslider.setValue)
        # hide it to only keep the control slider
        self._plotRecons._qslider.hide()

    def addReconsImage(self, sino, reconsPh):
        """
        
        :param sino: the source sinogram 
        :param reconsPh: the reconstruction of the sinogram
        """
        assert sino is not None
        assert reconsPh is not None
        self._plotSinoRecons.addImage(label=sino.name,
                                      imgSino=sino.data,
                                      imgRecons=reconsPh)
        self._plotRecons.addImage(label=sino.name,
                                  image=reconsPh)


class SilxReconsDialog(qt.QDialog):
    def __init__(self, parent, cfgFile, config=None, platformId=None,
                 deviceId=None):
        qt.QDialog.__init__(self, parent)
        self.setWindowFlags(qt.Qt.Widget)
        self.setWindowTitle('reconstruction of the absorption matrix')
        self.setWindowFlags(qt.Qt.Widget)
        types = qt.QDialogButtonBox.Ok | qt.QDialogButtonBox.Cancel
        _buttons = qt.QDialogButtonBox(parent=self)
        _buttons.setStandardButtons(types)
        self._mainWindow = SilxReconsManager(parent=self,
                                             cfgFile=cfgFile,
                                             config=config,
                                             platformId=platformId,
                                             deviceId=deviceId)

        self.setLayout(qt.QVBoxLayout())
        self.layout().addWidget(self._mainWindow)
        self.layout().addWidget(_buttons)

        _buttons.accepted.connect(self.accept)
        _buttons.rejected.connect(self.reject)

    def exec_(self):
        # bad hack to make sure the images are correctly displayed
        # but as we are using the keep aspect ratio if the plot is not show
        # and the zoom reset matplotlib will not be able to deduce the correct
        # dimension of the plot area
        self.show()
        self._mainWindow.resetPlotsZoom()
        return qt.QDialog.exec_(self)
