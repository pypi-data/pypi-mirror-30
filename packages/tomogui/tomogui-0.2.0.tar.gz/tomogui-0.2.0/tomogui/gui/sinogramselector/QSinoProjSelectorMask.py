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
__date__ = "15/09/2017"

import logging
import numpy
from silx.gui import qt
from silx.gui.plot import PlotWidget
from silx.gui.plot.MaskToolsWidget import MaskToolsWidget
from silx.gui.plot.actions.mode import PanModeAction

from tomogui.gui.utils import icons

logger = logging.getLogger(__name__)


class QSinoProjSelectorMask(qt.QWidget):
    """"""
    def __init__(self, parent=None):
        qt.QWidget.__init__(self)
        self._plot = PlotWidget()
        self._mask = _QMaskLineSelector(self._plot)
        self.setLayout(qt.QVBoxLayout())
        self.layout().addWidget(self._plot)
        self.layout().addWidget(self._mask)

    def setImage(self, image):
        self._plot.addImage(image)

        mask = numpy.zeros(image.shape, dtype=numpy.uint8)
        self._mask.setSelectionMask(mask)

    def getSelection(self):
        return self._mask.getSelection()

    def setSelection(self, val):
        self._mask.setSelection(val)


class _QMaskLineSelector(MaskToolsWidget):
    """mask tool to select the accessible"""

    sigSelectionChanged = qt.Signal(str)

    def __init__(self, plot):
        MaskToolsWidget.__init__(self, parent=None, plot=plot)
        assert plot is not None
        # remove unused widgets
        self.transparencyWidget.hide()
        self.levelWidget.hide()
        self.thresholdGroup.hide()

        self._startHLineSel = None

    def _initDrawGroupBox(self):
        """Init drawing tools widgets"""
        layout = qt.QVBoxLayout()

        self.browseAction = PanModeAction(self.plot, self.plot)
        self.addAction(self.browseAction)

        # Draw tools
        self.lineSelectionAction = qt.QAction(
                icons.getQIcon('lineselection'), 'Line selection tool', None)
        self.lineSelectionAction.setCheckable(True)
        self.lineSelectionAction.triggered.connect(self._activeHLineMode)
        self.addAction(self.lineSelectionAction)

        self.drawActionGroup = qt.QActionGroup(self)
        self.drawActionGroup.setExclusive(True)
        self.drawActionGroup.addAction(self.lineSelectionAction)

        actions = (self.browseAction, self.lineSelectionAction)
        drawButtons = []
        for action in actions:
            btn = qt.QToolButton()
            btn.setDefaultAction(action)
            drawButtons.append(btn)
        container = self._hboxWidget(*drawButtons)
        layout.addWidget(container)

        # Mask/Unmask radio buttons
        maskRadioBtn = qt.QRadioButton('Mask')
        maskRadioBtn.setToolTip(
                'Drawing masks with current level. Press <b>Ctrl</b> to unmask')
        maskRadioBtn.setChecked(True)

        unmaskRadioBtn = qt.QRadioButton('Unmask')
        unmaskRadioBtn.setToolTip(
                'Drawing unmasks with current level. Press <b>Ctrl</b> to mask')

        self.maskStateGroup = qt.QButtonGroup()
        self.maskStateGroup.addButton(maskRadioBtn, 1)
        self.maskStateGroup.addButton(unmaskRadioBtn, 0)

        self.maskStateWidget = self._hboxWidget(maskRadioBtn, unmaskRadioBtn)
        layout.addWidget(self.maskStateWidget)

        self.maskStateWidget.setHidden(True)

        # Pencil settings
        self.pencilSetting = self._createPencilSettings(None)
        self.pencilSetting.setVisible(False)
        layout.addWidget(self.pencilSetting)

        layout.addStretch(1)

        drawGroup = qt.QGroupBox('Draw tools')
        drawGroup.setLayout(layout)
        return drawGroup

    def _activeHLineMode(self):
        self._releaseDrawingMode()
        self._drawingMode = 'hline'
        self.plot.sigPlotSignal.connect(self._plotDrawEvent)
        color = self.getCurrentMaskColor()
        self.plot.setInteractiveMode(
            'draw', shape='hline', source=self, color=color)
        self._updateDrawingModeWidgets()

    def _interactiveModeChanged(self, source):
        """Handle plot interactive mode changed:

        If changed from elsewhereprojection in, disable drawing tool
        """
        if source is not self:
            self.lineSelectionAction.setCheckable(False)
            self._releaseDrawingMode()
            self._updateDrawingModeWidgets()

    def _updateInteractiveMode(self):
        if self._drawingMode == 'hline':
            self._activeHLineMode()

    def _plotDrawEvent(self, event):
        """Handle draw events from the plot"""
        if (self._drawingMode is None or
                event['event'] not in ('drawingProgress', 'drawingFinished')):
            return

        level = self.levelSpinBox.value()

        if (self._drawingMode == 'hline' and
                event['event'] == 'drawingFinished'):
            doMask = self._isMasking()
            assert self._startHLineSel is not None
            start_y = min(self._startHLineSel, event['ydata'][0])
            end_y = max(self._startHLineSel, event['ydata'][0])

            for yline in numpy.arange(start_y, end_y+1):
                self._mask.updateLine(level,
                                      yline,
                                      event['xdata'][0],
                                      yline,
                                      event['xdata'][1],
                                      1,
                                      mask=doMask)
            self._startHLineSel = None

            self.sigSelectionChanged.emit(self.getSelection())

        if (self._drawingMode == 'hline' and
                    event['event'] == 'drawingProgress'):
            if self._startHLineSel is None:
                self._startHLineSel = event['ydata'][0]

    def getSelection(self):
        """Return the selection made"""
        def concate(res, start, end):
            if start == end:
                return res + str(start) + ";"
            else:
                return res + str(start) + ":" + str(end + 1) + ";"

        s = (self._mask._mask.sum(axis=1))
        start = None
        res = ""
        for index, elmt in enumerate(s):
            # print(elmt)
            if elmt > 0:
                if start is None:
                    start = index
            elif start is not None:
                res = concate(res, start=start, end=index-1)
                start = None

        if start is not None:
            res = concate(res, start=start, end=index-1 if elmt == 0 else index)

        return res[:-1]  # -1: remove last ';'

    def setSelection(self, selection):
        if self.plot.getActiveImage() is None:
            logger.info("No active image, can't set any mask")
            return

        _selection = selection
        if _selection is None or _selection == 'None':
            _selection = ':'

        level = self.levelSpinBox.value()
        self._mask.clear(level)

        _selection = _selection.replace(" ", "")
        selections = _selection.split(";")
        for sel in selections:
            vals = sel.split(":")
            if len(vals) == 1:
                if vals[0] == "":
                    start = 0
                    end = self.plot.getActiveImage().getData().shape[0]
                else:
                    start = int(sel)
                    end = int(sel)
            else:
                assert len(vals) is 2
                start, end = vals
                if start == "":
                    start = 0
                if end == "":
                    end = self.plot.getActiveImage().getData().shape[0]

                start = int(start)
                end = int(end)

            if start == end:
                end = end + 1

            width = self.plot.getActiveImage().getData().shape[1]
            self._mask._mask[start:end, :] = level


if __name__ == "__main__":
    app = qt.QApplication([])

    import numpy.random
    data = numpy.random.random((50, 50))
    widget = QSinoProjSelectorMask()
    app.exec_()
