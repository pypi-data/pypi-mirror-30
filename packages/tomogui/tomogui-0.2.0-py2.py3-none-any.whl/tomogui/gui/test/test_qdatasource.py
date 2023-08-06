#/*##########################################################################
# Copyright (C) 2004-2016 European Synchrotron Radiation Facility
#
# This file is part of the PyMca X-ray Fluorescence Toolkit developed at
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

import numpy
import os
import shutil
import sys
import tempfile
import unittest
from silx.gui import qt
from tomogui.configuration import config as tomoguiconfig
from tomogui.gui.datasource.QDataSourceWidget import QDataSourceTxWidget
from tomogui.gui.datasource.sinofileselector.QSinoFileFluoSelector import _QSinoFluoSelector
try:
    import freeart
    from freeart.configuration import config as freeartconfig
    from freeart.utils import h5utils, genph, reconstrutils, testutils as freeart_testutils
    from freeart.unitsystem import metricsystem
    from freeart.configuration import structs, fileInfo
    from freeart.utils import testutils
    from tomogui.gui.datasource.QDataSourceWidget import QDataSourceFluoWidget
    freeart_missing = False
except ImportError:
    from tomogui.third_party.configuration import structs, fileInfo
    freeart_missing = True


class TestConfigurationFileDataSourceFBP(unittest.TestCase):
    """
    Test that the QDataSourceTxWidget is well saving and loading parameters
    from a FBP configuration file
    """

    def setUp(self):
        # deal with files
        self.tempdir = tempfile.mkdtemp()
        self.conf = tomoguiconfig.FBPConfig()
        sinoFile = os.path.join(self.tempdir, 'sinogram.edf')
        self.conf.addSinogram(
            structs.Sinogram(
                fileInfo=fileInfo.EDFMatrixFileInfo(filePath=sinoFile),
                data=numpy.arange(100).reshape(10, 10)
            )
        )
        self.conf.sinograms[0].save()

        self.widget = QDataSourceTxWidget()
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)

        # skip unmanaged parameters
        self.conf.minAngle = None
        self.conf.maxAngle = None
        self.conf.center = -1
        self.conf.projections = None

    def tearDown(self):
        self.widget.close()
        shutil.rmtree(self.tempdir)

    def testReadWrite(self):
        """Test that the widget is well writing the configuration file"""
        self.widget.loadConfiguration(self.conf)

        # check input is output
        confSaveCFG = tomoguiconfig.FBPConfig()
        self.widget.saveConfiguration(confSaveCFG, refFile=None)
        confSaveCFG.sinograms[0].loadData(refFile=None)
        self.assertTrue(confSaveCFG == self.conf)


@unittest.skipIf(freeart_missing, "freeart missing")
class TestConfigurationFileDataSourceTx(unittest.TestCase):
    """
    Test that the QDataSourceTxWidget is well saving and loading parameters
    from a configuration file
    """
    SINO_TEST = structs.TxSinogram(name='toto')

    def setUp(self):
        # deal with files
        self.tempdir = tempfile.mkdtemp()
        self.conf = testutils.createConfigTx(self.tempdir)
        self.widget = QDataSourceTxWidget()
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)

        # skip unmanaged parameters
        self.conf.minAngle = None
        self.conf.maxAngle = None
        self.conf.center = -1
        self.conf.acquiInverted = False
        self.conf.outBeamCalMethod = 0
        self.conf.dampingFactor = None
        self.conf.projections = None
        assert(len(self.conf.sinograms) is 1)

    def tearDown(self):
        self.widget.close()
        shutil.rmtree(self.tempdir)

    def testReadWrite(self):
        """Test that the widget is well writing the configuration file"""
        self.widget.loadConfiguration(self.conf)

        # check input is output
        confSaveCFG = freeartconfig.TxConfig()
        self.widget.saveConfiguration(confSaveCFG, refFile=None)
        confSaveCFG.sinograms[0].loadData(refFile=None)
        self.assertTrue(confSaveCFG == self.conf)


@unittest.skipIf(freeart_missing, "freeart missing")
class TestConfigurationFileDataSourceFluo(unittest.TestCase):
    """
    Test that the QDataSourceFluoWidget is well saving and loading parameters
    from a configuration file

    .. note:: this test is not including the QSinoFluoSelector test for reading
              and writing configuration. A special test has been created for
              this purpose.
    """

    def setUp(self):
        # deal with files
        self.tempdir = tempfile.mkdtemp()
        self.confH5 = testutils.createConfigFluo(self.tempdir,
                                                 fileExtension='.h5',
                                                 withMaterials=False,
                                                 addAbsMat=True,
                                                 fileExtensionMat='.h5')
        self.confEDF = testutils.createConfigFluo(self.tempdir,
                                                  fileExtension='.edf',
                                                  withMaterials=False,
                                                  addAbsMat=True,
                                                  fileExtensionMat='.npy')
        # The one not managed by the qdatasource
        self.confH5.minAngle = self.confEDF.minAngle = None
        self.confH5.maxAngle = self.confEDF.maxAngle = None
        self.confH5.center = self.confEDF.center = -1
        self.confH5.acquiInverted = self.confEDF.acquiInverted = False
        self.confH5.outBeamCalMethod = self.confEDF.outBeamCalMethod = 0
        self.confH5.dampingFactor = self.confEDF.dampingFactor = None
        self.confH5.detector = self.confEDF.detector = None

        self.widget = QDataSourceFluoWidget()
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)

    def tearDown(self):
        self.widget.close()
        shutil.rmtree(self.tempdir)

    def testH5(self):
        """Test that the widget is well writing the configuration file"""
        self.widget.loadConfiguration(self.confH5)
        outConf = freeartconfig.FluoConfig()
        self.widget.saveConfiguration(outConf, refFile=None)
        for sinogram in outConf.sinograms:
            sinogram.loadData(refFile=None)

        outConf.absMat.loadData(None)

        self.assertTrue(outConf == self.confH5)

    def testEDF(self):
        self.widget.loadConfiguration(self.confEDF)

        outConf = freeartconfig.FluoConfig()
        self.widget.saveConfiguration(outConf, refFile=None)
        for sinogram in outConf.sinograms:
            sinogram.loadData(refFile=None)

        outConf.absMat.loadData(None)
        self.assertTrue(outConf == self.confEDF)


@unittest.skipIf(freeart_missing, "freeart missing")
class TestConfigurationQSinoFluoSelector(unittest.TestCase):
    """
    Test that the QDataSourceFluoWidget is well saving and loading parameters
    from a configuration file

    ..note:: this test is not including the QSinoFluoSelector test for reading
             and writing configuration. A special test has been created for
             this purpose.
    """

    def setUp(self):
        # deal with files
        self.tempdir = tempfile.mkdtemp()
        self.confH5 = testutils.createConfigFluo(self.tempdir,
                                                 fileExtension='.h5')
        self.confEDF = testutils.createConfigFluo(self.tempdir,
                                                  fileExtension='.edf')
        self.widget = _QSinoFluoSelector()
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)

    def tearDown(self):
        self.widget.close()
        shutil.rmtree(self.tempdir)

    def testH5(self):
        """Make sure SinoFluoSelector is valid with .h5 file"""
        self.widget.loadConfiguration(self.confH5)

        outConf = freeartconfig.FluoConfig()
        self.widget.saveConfiguration(outConf, refFile=None)

        for sinogram in outConf.sinograms:
            sinogram.loadData(refFile=None)

        # this widget is only managing the sinograms
        self.assertTrue(self.confH5.getSinogramsFileDict() == outConf.getSinogramsFileDict())

    def testEDF(self):
        """Make sure SinoFluoSelector is valid with .edf file"""
        self.widget.loadConfiguration(self.confEDF)

        outConf = freeartconfig.FluoConfig()
        self.widget.saveConfiguration(outConf, refFile=None)

        for sinogram in outConf.sinograms:
            sinogram.loadData(refFile=None)

        # this widget is only managing the sinograms
        self.assertTrue(self.confEDF.getSinogramsFileDict() == outConf.getSinogramsFileDict())


@unittest.skipIf(freeart_missing, "freeart missing")
class TestQFluoSinoSelector(unittest.TestCase):
    def setUp(self):
        tempdir = tempfile.mkdtemp()
        self.config = freeart_testutils.createConfigFluo(tempdir)
        assert(len(self.config.sinograms) is 5)
        # add some sinogram in the same .h5 file
        fileName = 'multiSino' + '.h5'
        self.multiSinoFile = os.path.join(tempdir, fileName)

        for iSino in (1, 3, 6):
            path = "/data/sino___" + str(iSino)
            h5utils.createH5WithDataSet(filePath=self.multiSinoFile,
                                        h5path=path,
                                        data=numpy.arange(100).reshape(10, 10),
                                        mode='a')
            file_info = fileInfo.H5MatrixFileInfo(
                filePath=self.multiSinoFile + "::" + path)

            self.config.addSinogram(
                structs.FluoSino(fileInfo=file_info,
                                 data=None,
                                 name='Sinogram_' + str(iSino),
                                 physElmt='O',
                                 ef=12.0,
                                 selfAbsMat=None)
            )

        assert(len(self.config.sinograms) is 8)

    def test(self):
        widget = _QSinoFluoSelector()
        widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        widget.loadConfiguration(self.config)
        self.assertTrue(len(widget.fileSelector.dictFileToItem) is 6)
        self.assertTrue(len(widget.getSinograms()) is 8)
        self.assertTrue(len(widget.fileSelector.listFiles) is 6)
        widget.close()


def suite():
    test_suite = unittest.TestSuite()
    for ui in (TestConfigurationFileDataSourceTx,
               TestConfigurationFileDataSourceFluo,
               TestConfigurationQSinoFluoSelector,
               TestQFluoSinoSelector):
        test_suite.addTest(
            unittest.defaultTestLoader.loadTestsFromTestCase(ui))

    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
