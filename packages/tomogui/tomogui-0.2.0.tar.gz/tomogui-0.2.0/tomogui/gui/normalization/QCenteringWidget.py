from __future__ import division
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


import numpy as np
from silx.gui import qt, icons
from silx.gui.plot import PlotWidget
from silx.gui.plot.actions.control import YAxisInvertedAction, ResetZoomAction
from silx.gui.plot.CurvesROIWidget import CurvesROIWidget
from fabio.edfimage import edfimage
from silx.gui.plot import PlotTools
from silx.gui.plot.Colormap import Colormap
from tomogui.core.utils import rescale_intensity
from tomogui.gui.normalization import QRotationCenterWidget
from tomogui.gui.utils.QFileManagement import QFileSelection
try:
    from silx.gui.plot.utils.axis import SyncAxes
except importError:
    SyncAxes = None

class QCenteringWindow(qt.QMainWindow):
    """
    A window which basically include a QCenteringWidget and a personnalized
    toolbar"""
    def __init__(self, parent=None, keepAspectRatio=False, backend=None):
        qt.QMainWindow.__init__(self, parent)

        self.centeringWidget = QCenteringWidget(self)
        self.setCentralWidget(self.centeringWidget)

        self._addToolBar()

    def _addToolBar(self):
        self.profileToolBar = PlotTools.ProfileToolBar(self.centeringWidget)
        # add the profile tool
        self.addToolBar(self.profileToolBar)
        self.profileToolBar.removeAction(self.profileToolBar.lineAction)

        # Add Separator
        self._separator1 = qt.QAction('separator', self)
        self._separator1.setSeparator(True)
        self.profileToolBar.addAction(self._separator1)

        # Flip Y axis
        self.flipYButton = YAxisInvertedAction(self.centeringWidget)
        self.profileToolBar.addAction(self.flipYButton)

        # Reset zoom action
        self.resetZoomButton = ResetZoomAction(self.centeringWidget)
        self.profileToolBar.addAction(self.resetZoomButton)

        # Separator
        self._separator2 = qt.QAction('separator', self.centeringWidget)
        self._separator2.setSeparator(True)
        self.profileToolBar.addAction(self._separator2)

        # Add "select ROI" button
        self.selectROIButton = qt.QAction(
            icons.getQIcon('image-select-box'),
            'Vertical Profile Mode', None)
        self.selectROIButton.setToolTip(
            'Enables vertical profile selection mode')
        self.selectROIButton.setCheckable(True)
        self.selectROIButton.toggled[bool].connect(self.centeringWidget._selectROIButtonToggled)
        self.profileToolBar.addAction(self.selectROIButton)

        # Add "enhance contrast" button
        self.contrastButton = qt.QAction('C', None)
        self.contrastButton.setToolTip('Enhance contrast')
        self.contrastButton.setCheckable(False)
        self.contrastButton.triggered[bool].connect(self.centeringWidget._enhanceContrast)
        self.profileToolBar.addAction(self.contrastButton)

    def _updateYAxisInverted(self, inverted=None):
        """Sync image, vertical histogram and radar view axis orientation."""
        if inverted is None:
            # Do not perform this when called from plot signal
            inverted = self.isYAxisInverted()

        self._histoVPlot.setYAxisInverted(inverted)

        # Use scale to invert radarView
        # RadarView default Y direction is from top to bottom
        # As opposed to Plot. So invert RadarView when Plot is NOT inverted.
        self._radarView.resetTransform()
        if not inverted:
            self._radarView.scale(1., -1.)
        self._updateRadarView()

        self._radarView.update()


class QCenteringWidget(qt.QWidget):
    """
    A widget to center a sinogram
    """
    SINOGRAM_HEIGHT = 200
    """Height in pixels of the side histograms."""

    SINOGRAM_WIDTH = 200
    """Minimum width in pixels of the image area."""

    CHECK_BOXES_WIDTH = 100
    CHECK_BOXES_HEIGHT = SINOGRAM_HEIGHT

    SUM_SINOGRAM_WIDTH = CHECK_BOXES_WIDTH
    SUM_SINOGRAM_HEIGHT = 100

    HISTOGRAMS_COLOR = 'green'

    # are we passing a pointer ??? otherwise will be heavy
    imageChanged = qt.Signal(object)

    sigSetYAxisInverted = qt.Signal(bool)
    sigPlotSignal = qt.Signal(bool)

    def __init__(self, parent=None, keepAspectRatio=False, withGraphSum=True,
                 withFileSelection=True):
        """Constructor"""
        def sizeMainWidget():
            return qt.QSize(self.SINOGRAM_WIDTH, self.SINOGRAM_HEIGHT)

        def sizeCheckBoxesWidget():
            return qt.QSize(self.CHECK_BOXES_WIDTH, self.CHECK_BOXES_HEIGHT)

        def sizeSumSinogram():
            return qt.QSize(self.SUM_SINOGRAM_WIDTH, self.SUM_SINOGRAM_HEIGHT)

        qt.QWidget.__init__(self, parent)

        self._cache = None
        self._roiInfo = None
        self._defaultMode = 'zoom'
        self.keepAspectRatio = keepAspectRatio
        self.roiData = None

        _layout = qt.QGridLayout()
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.setSpacing(4)

        if withGraphSum:
            # Define the SUM sinogram widget
            self._sumSinogramwidget = PlotWidget(parent=self)
            self._sumSinogramwidget.setKeepDataAspectRatio(False)
            _layout.addWidget(self._sumSinogramwidget, 2, 0)

        if withFileSelection:
            self.fileSelection = QFileSelection(self)
            _layout.addWidget(self.fileSelection, 0, 0)
            self.fileSelection.sigFileSelected.connect(self._forwardFileSelection)

        self.groupRotationWidget = QRotationCenterWidget.QRotationCenterWidget(self)

        self.centralWidget = PlotWidget(parent=self)
        self.centralWidget.setDefaultColormap(Colormap(name='viridis',
                                                       normalization='linear',
                                                       vmin=None,
                                                       vmax=None))

        self.centralWidget.setKeepDataAspectRatio(self.keepAspectRatio)

        if withGraphSum and SyncAxes:
            self._syncAxes = SyncAxes([self.centralWidget.getXAxis(), self._sumSinogramwidget.getXAxis()])

        # Redefinition of the layout
        if withFileSelection is True:
            _layout.addWidget(self.groupRotationWidget, 1, 1)
        else:
            _layout.addWidget(self.groupRotationWidget, 0, 0)

        _layout.addWidget(self.centralWidget, 1, 0)
        self.setLayout(_layout)

    def _histoVPlotCB(self, eventDict):
        pass

    def _checkBoxesWidgetCB(self, eventDict):
        pass

    def clean(self):
        self.centralWidget.clear()

    def setImage(self, data, legend=None):
        self.data = data
        self.centralWidget.addImage(data,
                                    legend=legend,
                                    xlabel='translation',
                                    ylabel='angle')
        self.updateHistogram()
        # update if needed the value of the center of rotation
        image = self.centralWidget.getImage("sino")
        data = image.getData() if hasattr(image, 'getData') else image[0]
        self.imageChanged.emit(data)
        self.groupRotationWidget.dataChanged(data)

    def _enhanceContrast(self):
        imageInfos = self.getImage("sino")
        imageData = imageInfos[0]
        imageData2 = rescale_intensity(imageData, from_subimg=self.roiData)
        self.setImage(imageData2, "sino")

    def updateDataFromFile(self, fileName):
        # get the data to display
        edfReader = edfimage()
        edfReader.read(fileName)
        if edfReader.nframes == 1:
            dataToDisplay = edfReader.getData()
        elif edfReader.nframes > 1:
            dataToDisplay = edfReader.getframe(0).getData()

        return self.updateData(dataToDisplay)

    def updateData(self, data):
        self.setImage(data, "sino")
        self.groupRotationWidget.dataChanged(data)

    def _forwardFileSelection(self, event):
        assert(event['event'] == "fileSelected")
        self.updateDataFromFile(event['filePath'])

    def saveConfiguration(self, config):
        """Save configuration to use those in FreeART app"""
        self.groupRotationWidget.saveConfiguration(config)

    def loadConfiguration(self, config):
        """Save configuration to use those in FreeART app"""
        self.groupRotationWidget.loadConfiguration(config)

    # TODO: put computation in a separate file
    def updateHistogram(self):
        # Rebuild histograms for visible area
        activeImage = self.centralWidget.getActiveImage()

        if activeImage is not None:
            data = activeImage.getData() if hasattr(activeImage, 'getData') else activeImage[0]
            if hasattr(activeImage, 'getScale') and hasattr(activeImage, 'getOrigin'):
                origin = activeImage.getOrigin()
                scale = activeImage.getScale()
            else:
                params = activeImage[4]
                origin, scale = params['origin'], params['scale']

            height, width = data.shape

            xMin, xMax = self.centralWidget.getGraphXLimits()
            yMin, yMax = self.centralWidget.getGraphYLimits()

            # Convert plot area limits to image coordinates
            # and work in image coordinates (i.e., in pixels)
            xMin = int((xMin - origin[0]) / scale[0])
            xMax = int((xMax - origin[0]) / scale[1])
            yMin = int((yMin - origin[1]) / scale[1])
            yMax = int((yMax - origin[1]) / scale[1])

            if (xMin < width and xMax >= 0 and
                    yMin < height and yMax >= 0):
                # The image is at least partly in the plot area
                # Get the visible bounds in image coords (i.e., in pixels)
                subsetXMin = 0 if xMin < 0 else xMin
                subsetXMax = (width if xMax >= width else xMax) + 1
                subsetYMin = 0 if yMin < 0 else yMin
                subsetYMax = (height if yMax >= height else yMax) + 1

                visibleData = data[subsetYMin:subsetYMax,
                                   subsetXMin:subsetXMax]
                histoHVisibleData = np.sum(visibleData, axis=0)
                histoVVisibleData = np.sum(visibleData, axis=1)

                self._cache = {
                    'dataXMin': subsetXMin,
                    'dataXMax': subsetXMax,
                    'dataYMin': subsetYMin,
                    'dataYMax': subsetYMax,

                    'histoH': histoHVisibleData,
                    'histoHMin': np.min(histoHVisibleData),
                    'histoHMax': np.max(histoHVisibleData),

                    'histoV': histoVVisibleData,
                    'histoVMin': np.min(histoVVisibleData),
                    'histoVMax': np.max(histoVVisibleData)
                }

                lsum = np.sum(data, axis=0)
                self._sumSinogramwidget.addCurve(x=np.arange(0, len(lsum)),
                                                 y=lsum,
                                                 legend="sum",
                                                 resetzoom=True)

    def _plotWindowSlot(self, event):
        """Listen to Plot to handle drawing events to refresh ROI and profile.
        """
        #if event['event'] not in ('drawingProgress', 'drawingFinished'): return
        if event['event'] == 'drawingFinished':
            roiStart, roiEnd = event['points'][0], event['points'][1]
            self._roiInfo = roiStart, roiEnd
            self.processROI()

    def _selectROIButtonToggled(self, checked):
        """Handle horizontal line profile action toggle"""
        if checked:
            self.setInteractiveMode('draw', shape='rectangle', color='red')
            self.sigPlotSignal.connect(self._plotWindowSlot)
        else:
            self.sigPlotSignal.disconnect(self._plotWindowSlot)
            self.setInteractiveMode(self._defaultMode)
            self.roiData = None

    def processROI(self):
        if self._roiInfo is None:
            return
        imageData = self.centralWidget.getActiveImage()
        if imageData is None:
            return
        roiStart, roiEnd = self._roiInfo

        data, params = imageData[0], imageData[4]
        origin, scale = params['origin'], params['scale']
        startPt = (
            (roiStart[1] - origin[1]) / scale[1],
            (roiStart[0] - origin[0]) / scale[0]
        )
        endPt = (
            (roiEnd[1] - origin[1]) / scale[1],
            (roiEnd[0] - origin[0]) / scale[0]
        )

        Nr, Nc = data.shape
        startR = np.clip(int(round(startPt[0])), 0, Nr-1)
        startC = np.clip(int(round(startPt[1])), 0, Nc-1)
        endR = np.clip(int(round(endPt[0])), 0, Nr-1)
        endC = np.clip(int(round(endPt[1])), 0, Nc-1)
        #~ print("%d %d %d %d" % (startR, startC, endR, endC))
        if not(self.isYAxisInverted()): startR, endR = endR, startR
        dataRoi = data[startR:endR, startC:endC]
        self.roiData = np.copy(dataRoi)


if __name__ == "__main__":
    dataToDisplay = np.random.randn(800, 512)

    global app  # QApplication must be global to avoid seg fault on quit
    app = qt.QApplication([])

    mainWindow = QCenteringWindow()

    mainWindow.setAttribute(qt.Qt.WA_DeleteOnClose)
    dataToDisplay = np.random.randn(800, 512)
    mainWindow.centeringWidget.setImage(dataToDisplay, "sino")
    mainWindow.show()

    app.exec_()
