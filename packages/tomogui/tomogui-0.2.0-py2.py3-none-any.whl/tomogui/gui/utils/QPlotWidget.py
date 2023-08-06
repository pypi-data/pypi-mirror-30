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

from silx.gui import qt
from silx.gui.plot import Plot2D
from silx.gui.plot.Colormap import Colormap
import numpy as np

class QImageStackPlot(qt.QWidget):
    """
    Widget to display a stack of image
    """
    def __init__(self, parent, withQSlider=True, xlabel='X', ylabel='Y'):
        """
        Constructor
        :param parent: the Qt parent widget
        """
        qt.QWidget.__init__(self, parent)
        self._showTitle = False

        self.images = {}
        self.xlabel=xlabel
        self.ylabel=ylabel

        layout = qt.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self._plot = Plot2D(self)
        self._plot.layout().setContentsMargins(0, 0, 0, 0)
        self._plot.setKeepDataAspectRatio(False)
        self._plot.setDefaultColormap(Colormap(name='viridis',
                                               normalization='linear',
                                               vmin=None,
                                               vmax=None))
        layout.addWidget(self._plot)

        if withQSlider : 
            self._qslider = qt.QSlider(qt.Qt.Vertical)
            self._qslider.setRange(0, 0)
            self._qslider.setTickPosition(1)
            self._qslider.valueChanged.connect(self.setImage)
            self._qslider.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self._qslider)
        else:
            self._qslider = None

        self.setLayout(layout)

    def setImages(self, images):
        """
        Set the images to display
        """
        if not images is None :
            self.images = images
            if len(self.images) > 0 :
                self.setImage(0)
                
        if self._qslider :
            self._qslider.setRange(0, len(self.images) - 1)

    def showTitle(self, b):
        self._showTitle = b

    def setImage(self, index):
        """
        Set the image of index \'index\' as the current image displayed
        """
        if (not self.images is None) and (index < len(self.images)) and (index >= 0):
            legend = list(self.images.keys())[index]
            self._plot.addImage(self.images[legend],
                                legend=legend,
                                xlabel=self.xlabel,
                                ylabel=self.ylabel,
                                resetzoom=True)
            self._plot.setGraphTitle(legend if self._showTitle else '')
            return legend
        else:
            return None

    def update(self, name, data):
        if name not in self.images:
            raise ValueError('name of the image is not recognized')
        self.images[name] = data

    def isEmpty(self):
        """
        Return True if no reconsparam has been set yet
        """
        return (self.images is None or len(self.images) == 0)

    def setKeepDataAspectRatio(self, b):
        """Set the keepAspectRatio parameteter to the plot widget
        :param b: do we want to keep the aspect ratio for the plot
        """
        self._plot.setKeepDataAspectRatio(b)

    def addImage(self, label, image):
        assert image is not None
        assert label is not None
        if self._qslider:
            self._qslider.setMaximum(self._qslider.maximum() + 1)
        self.images[label] = image
        self.setImage(len(self.images) - 1)

    def clear(self):
        if self._qslider:
            self._qslider.setMaximum(0)
        self._plot.clear()
        self.images = {}

    def resetZoom(self):
        self._plot.resetZoom()


class QDoubleImageStackPlot(qt.QWidget):
    """
    Simple widget to display two images in parallel. The sinogram and the
     reconstruction of the sinogram.
    """
    def __init__(self, parent=None):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QHBoxLayout())
        self.setContentsMargins(0, 0, 0, 0)

        widgetPlots = qt.QWidget(parent=self)
        widgetPlots.setLayout(qt.QVBoxLayout())
        widgetPlots.setContentsMargins(0, 0, 0, 0)

        self.layout().addWidget(widgetPlots)
        widgetName = qt.QWidget(parent=widgetPlots)
        widgetName.setContentsMargins(0, 0, 0, 0)
        widgetName.setLayout(qt.QHBoxLayout())
        self._currentImgName = qt.QLabel('', parent=widgetName)
        self._currentImgName.setContentsMargins(0, 0, 0, 0)
        spacer = qt.QWidget(parent=widgetName)
        spacer.setSizePolicy(qt.QSizePolicy.Expanding,
                             qt.QSizePolicy.Minimum)
        spacer.setContentsMargins(0, 0, 0, 0)
        widgetName.layout().addWidget(spacer)
        widgetName.layout().addWidget(self._currentImgName)
        widgetPlots.layout().addWidget(widgetName)

        self._sinoStack = QImageStackPlot(parent=widgetPlots,
                                          withQSlider=False)
        self._sinoStack.setContentsMargins(0, 0, 0, 0)
        widgetPlots.layout().addWidget(self._sinoStack)
        self._reconsStack = QImageStackPlot(parent=widgetPlots,
                                            withQSlider=False)
        self._reconsStack.setContentsMargins(0, 0, 0, 0)
        widgetPlots.layout().addWidget(self._reconsStack)

        self._qslider = qt.QSlider(qt.Qt.Vertical)
        self._qslider.setContentsMargins(0, 0, 0, 0)
        self._qslider.setRange(0, 0)
        self._qslider.setTickPosition(1)
        self._qslider.valueChanged.connect(self.setImage)
        self.layout().addWidget(self._qslider)

    def setImage(self, index):
        name = self._sinoStack.setImage(index)
        self._reconsStack.setImage(index)
        self._currentImgName.setText(name or '')

    def addImage(self, label, imgSino, imgRecons):
        self._sinoStack.addImage(label=label, image=imgSino)
        self._reconsStack.addImage(label=label, image=imgRecons)
        nImage = len(self._sinoStack.images)
        self._qslider.setMaximum(nImage - 1)
        self.setImage(self._qslider.value())

    def clear(self):
        self._sinoStack.clear()
        self._reconsStack.clear()
        self._qslider.setMaximum(0)

    def updateRecons(self, name, data):
        self._reconsStack.update(name, data)

    def value(self):
        """Return slider position"""
        return self._qslider.value()

    def hideSlider(self):
        self._qslider.hide()

    def resetZoom(self):
        self._reconsStack.resetZoom()
        self._sinoStack.resetZoom()
