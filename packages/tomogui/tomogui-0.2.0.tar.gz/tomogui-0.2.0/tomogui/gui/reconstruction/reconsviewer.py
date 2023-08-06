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
from silx.gui.plot import Plot2D
from silx.gui.plot.Colormap import Colormap
from tomogui.gui.utils.QPlotWidget import QImageStackPlot, QDoubleImageStackPlot
import os
import logging
import numpy
try:
    from freeart.configuration import structs, config
    from freeart.utils.reconstrutils import decreaseMatSize
    from freeart.interpreter.configinterpreter import FluoConfInterpreter
    hasfreeart = True
except ImportError:
    hasfreeart = False
    from tomogui.third_party.configuration import structs, config
    from tomogui.third_party.edfutils import decreaseMatSize

_logger = logging.getLogger(__name__)


class ReconstructionItViewer(qt.QWidget):
    """
    Widget to display the reconstructions through iteration
    """
    def __init__(self, parent, interpreter):
        qt.QWidget.__init__(self, parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setLayout(qt.QHBoxLayout())
        self.tabs = ReconstructionItTabs(parent=self, interpreter=interpreter)
        # This is a bad hack tp move out the control slider
        # as the number of reconstruction is constante we can do it this way
        self.slider = qt.QSlider(parent=self)
        self.slider.setTickPosition(2)
        self.slider.setContentsMargins(0, 0, 0, 0)
        self.slider.setRange(0, self.tabs.controlSlider.maximum())
        self.layout().addWidget(self.slider)
        self.layout().addWidget(self.tabs)
        self.slider.valueChanged.connect(self.tabs.controlSlider.setValue)

    def update(self):
        qt.QWidget.update(self)
        self.tabs.updateView()

    def resetPlotsZoom(self):
        self.tabs.resetPlotsZoom()


class ReconstructionItTabs(qt.QTabWidget):
    """
    Used to display the reconstruction using iterations

    :param parent: the Qt parent widget
    :param interpreter: the interpreter linking the gui with the
                               core of the reconsparam.
    """
    DEF_COLORMAP = Colormap(name='temperature', normalization='linear',
                            vmin=None, vmax=None)

    def __init__(self, parent, interpreter):
        qt.QTabWidget.__init__(self, parent)
        self.interpreter = interpreter
        self.setContentsMargins(0, 0, 0, 0)

        self.reconsSino = QDoubleImageStackPlot(parent=self)
        # hide the slider to use the 'main one'
        self.reconsSino.hideSlider()
        # the slider controlling all the other. bad hack
        self.controlSlider = self.reconsSino._qslider
        self.reconsSino.setContentsMargins(0, 0, 0, 0)
        assert self.interpreter.config.sinograms is not None
        assert len(self.interpreter.config.sinograms) > 0
        for sino in self.interpreter.config.sinograms:
            assert(sino.name is not None)
            assert(sino.data is not None)
            imgSino = decreaseMatSize(sino.data)
            assert sino.name is not None
            self.reconsSino.addImage(label=sino.name,
                                     imgSino=imgSino,
                                     imgRecons=numpy.zeros((imgSino.shape[1],
                                                            imgSino.shape[1])))

        # tab sinogram and reconstructed phantom
        self.addTab(self.reconsSino, "Sinograms and reconstructions")

        # tab 4 reconstructed phantom
        self.addTab(self._getReconstructionGUI(), "reconstructions")

        if isinstance(self.interpreter.config, config.FluoConfig):
            self.absMatWidget = Plot2D(self)
            self.absMatWidget.setDefaultColormap(self.DEF_COLORMAP)

            self.absMatWidget.setKeepDataAspectRatio(True)

            # tab absorption matrice
            self.addTab(self.absMatWidget, "absorption matrix")

            # tab self attenuation matrices
            self.addTab(self._getSelfAbsMatGUI(), "self attenuation matrices")

            # self.interMatWidget = QImageStackPlot(parent=self,
            #                                       xlabel='X',
            #                                       ylabel='Y')
            # self.interMatWidget.setKeepDataAspectRatio(True)

            # self.addTab(self.interMatWidget, "interaction matrice")

        if isinstance(self.interpreter.config, config.FluoConfig):
            self.updateAbsorptionMatrices()

    def _getReconstructionGUI(self):
        self.recons = QImageStackPlot(parent=self)
        self.recons.showTitle(True)
        for sinogram in self.interpreter.config.sinograms:
            imgSino = decreaseMatSize(sinogram.data)
            self.recons.addImage(label=sinogram.name,
                                 image=numpy.zeros((imgSino.shape[1],
                                                    imgSino.shape[1])))
        # connect the slider with the control slider
        self.controlSlider.valueChanged.connect(
            self.recons._qslider.setValue)
        # hide it to only keep the control slider
        self.recons._qslider.hide()
        return self.recons

    def _getSelfAbsMatGUI(self):
        self.selfAbsMatWidget = QImageStackPlot(parent=self)
        for sinogram in self.interpreter.config.sinograms:
            if self.interpreter.config.reconsType == config._ReconsConfig.COMPTON_ID:
                assert(self.interpreter.config.absMat is not None)
                assert(self.interpreter.config.absMat.data is not None)
                selfAbsMat = self.interpreter.config.absMat.data
            elif self.interpreter.config.reconsType == config._ReconsConfig.FLUO_ID:
                assert(sinogram.selfAbsMat is not None)
                assert(sinogram.selfAbsMat.data is not None)
                selfAbsMat = sinogram.selfAbsMat.data
            else:
                raise ValueError('Invalid reconstruction type, not compton or fluo')

            self.selfAbsMatWidget.addImage(label=sinogram.name,
                                           image=decreaseMatSize(selfAbsMat))
        # connect the slider with the control slider
        self.controlSlider.valueChanged.connect(
            self.selfAbsMatWidget._qslider.setValue)
        # hide it to only keep the control slider
        self.selfAbsMatWidget._qslider.hide()
        return self.selfAbsMatWidget

    def _checkWithSampleComposition(self):
        """
        Ask for the user to define the sample composition if none set yet
        """
        # if we can pick the sample composition file :
        matCompoFile = self.interpreter.config.getMaterialCompositionFile()
        if (matCompoFile is not None) and os.path.isfile(matCompoFile):
            return True

        # if the fluointerpreter doesn't have the sample composition
        # (needed to build the selfAbs matrices): then we ask the user
        # to build it
        if matCompoFile is None:
            msg = qt.QMessageBox(self)
            msg.setIcon(qt.QMessageBox.Information)
            txt = "No information about the sample composition have been found."
            txt = txt + " Please define the sample composition"
            msg.setText(txt)
            msg.addButton(qt.QMessageBox.Yes)
            msg.addButton(qt.QMessageBox.Close)
            if msg.exec_() == qt.QMessageBox.Close:
                return self.close()

        if not os.path.isfile(matCompoFile):
            msg = qt.QMessageBox(self)
            msg.setIcon(qt.QMessageBox.Information)
            txt = "The given sample composition file is uncorrect "
            txt = txt + matCompoFile
            txt = txt + " please define the sample composition or set the correct file and restart."
            msg.setText(txt)
            msg.addButton(qt.QMessageBox.Yes)
            msg.addButton(qt.QMessageBox.Close)
            if msg.exec_() == qt.QMessageBox.Close:
                return self.close()

        edfFile = self.interpreter.config.getFluoAbsorptionMatriceFile()
        assert(edfFile is not None)
        assert(os.path.isfile((edfFile)))

    def updateView(self):
        """
        Function called to update all the plot in the GUI
        """
        for sinogram in self.interpreter.config.sinograms:
            if hasfreeart and isinstance(self.interpreter, FluoConfInterpreter):
                phantoms = self.interpreter.getDensityPhantoms()
                phantom = phantoms[sinogram.name].copy()
            else:
                phantom = self.interpreter.getReconstructionAlgorithms()[sinogram.name].getPhantom().copy()
                phantom = decreaseMatSize(phantom)
            self.reconsSino.updateRecons(name=sinogram.name, data=phantom)
            self.recons.update(name=sinogram.name, data=phantom)

        self.reconsSino.setImage(self.reconsSino.value())
        self.recons.setImage(self.reconsSino.value())

    def updateAbsorptionMatrices(self):
        """
        Update tab of absorption matrice
        """
        assert isinstance(self.interpreter.config.absMat, structs.AbsMatrix)
        if self.interpreter.config.absMat.data is None:
            self.interpreter.config.absMat.loadData(refFile=None)
        assert self.interpreter.config.absMat.data is not None
        data = self.interpreter.config.absMat.data.copy()
        data.shape = (data.shape[0], data.shape[1])
        self.absMatWidget.addImage(data, xlabel='X', ylabel='Y')

    def resetPlotsZoom(self):
        self.reconsSino.resetZoom()
        self.recons.resetZoom()
        if isinstance(self.interpreter.config, config.FluoConfig):
            self.absMatWidget.resetZoom()
            self.selfAbsMatWidget.resetZoom()
