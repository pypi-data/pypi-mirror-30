# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016 European Synchrotron Radiation Facility
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
# ###########################################################################*/
"""Make sure all function called by pymca are still compatible."""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "17/10/2017"

import unittest
import numpy.random
from silx.gui import qt
from tomogui.gui.MainWidget import TomoguiMainWindow
from silx.image.phantomgenerator import PhantomGenerator
from tomogui.configuration import config as tomoguiconfig
from tomogui.gui.ProjectWidget import ProjectWindow
try:
    from freeart.configuration import config as freeartconfig
    freeart_missing = False
except ImportError:
    freeart_missing = True
try:
    from silx.opencl.backprojection import Backprojection
    has_silx_FBP = True
except ImportError:
    has_silx_FBP = False


class TestPyMcaInteraction(unittest.TestCase):
    def setUp(self):
        self.mainWindow = ProjectWindow()
        self.mainWindow.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.sinoData = PhantomGenerator.get2DPhantomSheppLogan(n=32).reshape(32, 32)

    def tearDown(self):
        self.mainWindow.close()

    @unittest.skipIf(has_silx_FBP is False, "freeart missing")
    def testSetFBP(self):
        self.mainWindow.setSinoToRecons(reconsType=tomoguiconfig.FBPConfig.FBP_ID,
                                        sinograms=[self.sinoData,
                                                   self.sinoData],
                                        names=('sino1', 'sino2'))
        self.assertTrue(self.mainWindow.mainWidget.getReconstructionType() == tomoguiconfig.FBPConfig.FBP_ID)
        currentConf = self.mainWindow.mainWidget.getConfiguration(None)
        self.assertTrue(numpy.array_equal(currentConf.sinograms[0].data, self.sinoData))
        info = self.mainWindow.mainWidget._tabWidget.dataSourceWidget.qdsTx.txSinogramSelector.sinoInfo
        dImage = info.sinoPreview.image()
        self.assertTrue(numpy.array_equal(dImage, self.sinoData))

        self.mainWindow.clean()
        currentConf = self.mainWindow.mainWidget.getConfiguration(None)
        self.assertTrue(len(currentConf.sinograms) is 0)

    @unittest.skipIf(freeart_missing,"freeart missing")
    def testSetTx(self):
        self.mainWindow.setSinoToRecons(reconsType=freeartconfig._ReconsConfig.TX_ID,
                                        sinograms=[self.sinoData,
                                                   self.sinoData],
                                        names=('sino1', 'sino2'))
        self.mainWindow.setLogRecons(False)
        self.assertTrue(self.mainWindow.mainWidget.getReconstructionType() == freeartconfig._ReconsConfig.TX_ID)
        currentConf = self.mainWindow.mainWidget.getConfiguration(None)
        self.assertTrue(numpy.array_equal(currentConf.sinograms[0].data, self.sinoData))
        info = self.mainWindow.mainWidget._tabWidget.dataSourceWidget.qdsTx.txSinogramSelector.sinoInfo
        dImage = info.sinoPreview.image()
        self.assertTrue(numpy.array_equal(dImage, self.sinoData))

        self.mainWindow.clean()
        currentConf = self.mainWindow.mainWidget.getConfiguration(None)
        self.assertTrue(len(currentConf.sinograms) is 0)

    @unittest.skipIf(freeart_missing, "freeart missing")
    def testSetFluo(self):
        self.mainWindow.setSinoToRecons(reconsType=freeartconfig._ReconsConfig.FLUO_ID,
                                        sinograms=[self.sinoData,
                                                   self.sinoData,
                                                   self.sinoData],
                                        names=('sino1', 'sino2', 'sino3'))
        self.assertTrue(self.mainWindow.mainWidget.getReconstructionType() == freeartconfig._ReconsConfig.FLUO_ID)
        sinograms = self.mainWindow.mainWidget._tabWidget.dataSourceWidget.qdsFluo.getSinograms()
        self.assertTrue(len(sinograms) == 3)
        self.assertTrue(numpy.array_equal(sinograms[0].data, self.sinoData))

        self.mainWindow.clean()
        sinograms = self.mainWindow.mainWidget._tabWidget.dataSourceWidget.qdsFluo.getSinograms()
        self.assertTrue(len(sinograms) is 0)

    @unittest.skipIf(freeart_missing, "freeart missing")
    def testSetCompton(self):
        self.mainWindow.setSinoToRecons(reconsType=freeartconfig._ReconsConfig.COMPTON_ID,
                                        sinograms=[self.sinoData,
                                                   self.sinoData,
                                                   self.sinoData],
                                        names=('sino1', 'sino2', 'sino3'))
        self.assertTrue(self.mainWindow.mainWidget.getReconstructionType() == freeartconfig._ReconsConfig.COMPTON_ID)
        sinograms = self.mainWindow.mainWidget._tabWidget.dataSourceWidget.qdsFluo.getSinograms()
        self.assertTrue(len(sinograms) == 3)
        self.assertTrue(numpy.array_equal(sinograms[0].data, self.sinoData))

        self.mainWindow.clean()
        sinograms = self.mainWindow.mainWidget._tabWidget.dataSourceWidget.qdsFluo.getSinograms()
        self.assertTrue(len(sinograms) is 0)


def suite():
    test_suite = unittest.TestSuite()
    for testClass in (TestPyMcaInteraction,):
        test_suite.addTest(
            unittest.defaultTestLoader.loadTestsFromTestCase(testClass))
    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
