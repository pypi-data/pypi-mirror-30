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
__date__ = "23/02/2018"

import unittest
import numpy
from silx.gui import qt
import tempfile
import os
from tomogui.gui.ProjectWidget import ProjectWindow
try:
    from freeart.configuration import structs, config as freeartconfig
    from freeart.configuration import read
except ImportError:
    from tomogui.third_party.configuration import structs, config as freeartconfig


app = qt.QApplication.instance() or qt.QApplication([])


class _ScenarioBase(unittest.TestCase):
    pass


class ScenarioProject(_ScenarioBase):
    DET_X = 20
    N_PROJECTION = 40

    def setUp(self):
        self.mainWindow = ProjectWindow()
        self.mainWindow.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.sinos = []
        self.iElement = 0
        self.tempdir = tempfile.mkdtemp()
        self._file = os.path.join(self.tempdir, 'storeConfig.h5')

    def tearDown(self):
        self.mainWindow.close()

    def setReconstructionType(self, _type):
        self.mainWindow.mainWidget.getDataSourceWidget().setReconstructionType(_type)

    def getReconstructionType(self):
        return self.mainWindow.mainWidget.getDataSourceWidget().getReconstructionType()

    def setI0(self):
        data = numpy.random.random((self.N_PROJECTION, self.DET_X))
        self.I0 = structs.I0Sinogram(data=data)
        self._getNormWidget().I0Normalization.setI0(self.I0)

    def addNewSinogram(self):
        rtype = self.getReconstructionType()
        if rtype in (freeartconfig._ReconsConfig.FLUO_ID, freeartconfig._ReconsConfig.COMPTON_ID):
            self._addNewFluoSino()
        else:
            self._addNewTxSino()

    def _addNewFluoSino(self):
        data = numpy.random.random((self.N_PROJECTION, self.DET_X))
        sino = structs.FluoSino(name='element'+str(self.iElement),
                                data=data,
                                fileInfo=None,
                                physElmt='Fe',
                                ef=1.0,
                                selfAbsMat=None)
        self._getQDSFluo().fluoSinogramsSelector.addSinogram(sino)
        self.iElement = self.iElement + 1

    def _addNewTxSino(self):
        data = numpy.random.random((self.N_PROJECTION, self.DET_X))
        sino = structs.TxSinogram(data=data)
        self._getQDSTx().txSinogramSelector.addSinogram(sino)

    def setFluoReconsMode(self, mode):
        assert(self.getReconstructionType() in (freeartconfig._ReconsConfig.FLUO_ID,
                                                freeartconfig._ReconsConfig.COMPTON_ID))
        self._getQDSFluo().setFluoReconsMode(mode)

    def _getQDSFluo(self):
        return self.mainWindow.mainWidget.getDataSourceWidget().qdsFluo

    def _getQDSTx(self):
        return self.mainWindow.mainWidget.getDataSourceWidget().qdsTx

    def _getNormWidget(self):
        return self.mainWindow.mainWidget.getNormalizationWidget()

    def save(self):
        self.mainWindow.mainWidget.saveConfiguration(self._file, merge=True)

    def loadFileConfig(self, _file):
        assert os.path.exists(_file)
        return read(_file)
