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

import time
import unittest

try:
    import freeart
    from freeart.utils import genph, reconstrutils, testutils
    from freeart.configuration import config, read, structs, fileInfo
    from freeart.configuration.h5ConfigIO import H5ConfigWriter
    from freeart.configuration.iniConfigIO import IniConfigWriter
    freeart_missing = False
except ImportError:
    from tomogui.third_party.configuration import read, structs, fileInfo
    from tomogui.third_party.configuration.h5ConfigIO import H5ConfigWriter
    from tomogui.third_party.configuration.iniConfigIO import IniConfigWriter
    freeart_missing = True
import tomogui.gui.ProjectWidget as QFreeARTWidget
from tomogui.gui.reconstruction.ReconsManager import ReconsManagerWindow
from tomogui.configuration import config as tomoguiconfig
from silx.gui import qt
from silx.gui.test.utils import TestCaseQt
import numpy
import tempfile
import os
import shutil
try:
    from silx.opencl.backprojection import Backprojection
    has_silx_FBP = True
except ImportError:
    has_silx_FBP = False

# Makes sure a QApplication exists and do it once for all
_qapp = qt.QApplication.instance() or qt.QApplication([])


@unittest.skipIf(freeart_missing, "freeart missing")
class TestProjectCreationAndReconstructionTx(unittest.TestCase):
    """
    Simple check that a project created from the QFreeARTWidget can be run by
    the QFreeARTRecosntructionWidget
    """

    def setUp(self):
        unittest.TestCase.setUp(self)
        "create a reconsparam tx project from the QFreeARTWidget"
        self.phGenerator = genph.PhantomGenerator()

        # build sinogram
        self.sheppLogan_phantom_tx = self.phGenerator.get2DPhantomSheppLogan(56)

        # decentralize the sinogram
        self._originalCenter = int(self.sheppLogan_phantom_tx.shape[0] / 2)
        self.sheppLogan_phantom_tx.resize(self.sheppLogan_phantom_tx.shape[0],
                                          self.sheppLogan_phantom_tx.shape[1])

        # build the sinogram
        self.sheppLogan_phantom_tx.shape = (self.sheppLogan_phantom_tx.shape[0],
                                            self.sheppLogan_phantom_tx.shape[1],
                                            1)

        al = freeart.TxFwdProjection(self.sheppLogan_phantom_tx,
                                     minAngle=0,
                                     maxAngle=2.0*numpy.pi,
                                     anglesNb=360)
        al.setRandSeedToZero(True)

        self.tempdir = tempfile.mkdtemp()
        self.sino_file = os.path.join(self.tempdir, "sinoTx.edf")
        sinogram = structs.TxSinogram(
            data=al.makeSinogram()[0],
            fileInfo=fileInfo.EDFMatrixFileInfo(self.sino_file)
        )
        sinogram.save()

        self.configfile_path_write = os.path.join(self.tempdir,
                                                  "tmp_config_write.cfg")

        # set reconsparam parameters
        self.widget = QFreeARTWidget.MainWidget()
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)

        self.widget.getDataSourceWidget().setReconstructionType(config._ReconsConfig.TX_ID)
        self.widget.getDataSourceWidget().qdsTx.addSinogram(sinogram)
        cWidget = self.widget.getNormalizationWidget().centeringWidget
        cWidget.groupRotationWidget.qleRotationCenter.setText(str(self._originalCenter))
        self.widget.getReconsParamWidget().qleOversampling.setText(str(5))
        self.widget.getReconsParamWidget().qleDampingFactor.setText(str(0.02))

        # save
        self.widget.saveConfiguration(self.configfile_path_write, merge=False)
        assert os.path.isfile(self.configfile_path_write)

    def tearDown(self):
        if os.path.isfile(self.sino_file):
            os.unlink(self.sino_file)

        if os.path.isfile(self.configfile_path_write):
            os.unlink(self.configfile_path_write)
        self.widget.close()
        unittest.TestCase.tearDown(self)

    def testRunReconstruction(self):
        """
        Build the reconsparam fron the QFreeARTReconstructionManager from
        the configuration file writed by the QFreeARTWidget
        """
        self.reconsWidget = ReconsManagerWindow(cfgFile=self.configfile_path_write)
        self.reconsWidget.show()
        self.reconsWidget.centralWidget()._runIteratation()
        self.reconsWidget.centralWidget().threadInterpreterIterator.wait()


@unittest.skipIf(has_silx_FBP is False, "silx fbp missing")
class TestLoadAndSaveFBPConfig(unittest.TestCase):
    """
    Simple test writing a reference cfg file for transmission and display it
    """

    def setUp(self):
        unittest.TestCase.setUp(self)
        # create the sino file
        self.tempdir = tempfile.mkdtemp()
        self.tempdir = tempfile.mkdtemp()
        self.conf = tomoguiconfig.FBPConfig()
        sinoFile = os.path.join(self.tempdir, 'sinogram.edf')
        self.conf.sinogram = structs.Sinogram(
            fileInfo=fileInfo.EDFMatrixFileInfo(filePath=sinoFile),
            data=numpy.arange(100).reshape(10, 10)
        )
        self.conf.sinogram.save()
        self.conf.minAngle = 0.0
        self.conf.maxAngle = 1.2

        self.mainWindow = QFreeARTWidget.ProjectWindow()
        self.mainWindow.setAttribute(qt.Qt.WA_DeleteOnClose)

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        self.mainWindow.close()
        unittest.TestCase.tearDown(self)

    def testFBPH5(self):
        output_cfg_file = os.path.join(self.tempdir, 'config.h5')
        input_cfg_file = os.path.join(self.tempdir, 'inputConf.h5')

        H5ConfigWriter().write(filePath=input_cfg_file,
                               reconsConfiguration=self.conf)
        self.mainWindow.setConfFile(input_cfg_file)
        self.assertTrue(os.path.isfile(input_cfg_file))
        self.mainWindow.mainWidget.saveConfiguration(output_cfg_file,
                                                     merge=False)

        savedConfig = read(output_cfg_file)
        savedConfig.sinograms[0].loadData(refFile=None)
        # some conversion issue can appear for angles
        self.assertTrue(numpy.isclose(savedConfig.minAngle, self.conf.minAngle))
        self.assertTrue(numpy.isclose(savedConfig.maxAngle, self.conf.maxAngle))
        savedConfig.minAngle = self.conf.minAngle
        savedConfig.maxAngle = self.conf.maxAngle
        savedConfig.projections = self.conf.projections
        savedConfig.dampingFactor = self.conf.dampingFactor
        self.assertTrue(savedConfig == self.conf)

    def testFBPCFG(self):
        output_cfg_file = os.path.join(self.tempdir, 'config.cfg')
        input_cfg_file = os.path.join(self.tempdir, 'inputConf.cfg')

        IniConfigWriter().write(filePath=input_cfg_file,
                                reconsConfiguration=self.conf)
        self.mainWindow.setConfFile(input_cfg_file)
        self.assertTrue(os.path.isfile(input_cfg_file))

        self.mainWindow.mainWidget.saveConfiguration(output_cfg_file,
                                                     merge=False)
        savedConfig = read(output_cfg_file)
        savedConfig.sinograms[0].loadData(refFile=None)
        savedConfig.dampingFactor = self.conf.dampingFactor
        self.assertTrue(savedConfig == self.conf)


@unittest.skipIf(freeart_missing, "freeart missing")
class TestLoadAndSaveTxConfig(unittest.TestCase):
    """
    Simple test writing a reference cfg file for transmission and display it
    """

    def setUp(self):
        unittest.TestCase.setUp(self)
        # create the sino file
        self.tempdir = tempfile.mkdtemp()
        self.conf = testutils.createConfigTx(self.tempdir)
        self.mainWindow = QFreeARTWidget.ProjectWindow()
        self.mainWindow.setAttribute(qt.Qt.WA_DeleteOnClose)

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        self.mainWindow.close()
        unittest.TestCase.tearDown(self)

    def testTxH5(self):
        output_cfg_file = os.path.join(self.tempdir, 'config.h5')
        input_cfg_file = os.path.join(self.tempdir, 'inputConf.h5')

        H5ConfigWriter().write(filePath=input_cfg_file,
                               reconsConfiguration=self.conf)
        self.mainWindow.setConfFile(input_cfg_file)
        self.mainWindow.mainWidget.saveConfiguration(output_cfg_file,
                                                     merge=False)

        savedConfig = read(output_cfg_file)
        savedConfig.sinograms[0].loadData(refFile=None)
        # some conversion issue can appear for angles
        self.assertTrue(numpy.isclose(savedConfig.minAngle, self.conf.minAngle))
        self.assertTrue(numpy.isclose(savedConfig.maxAngle, self.conf.maxAngle))
        savedConfig.minAngle = self.conf.minAngle
        savedConfig.maxAngle = self.conf.maxAngle
        self.assertTrue(savedConfig == self.conf)

    def testTxCFG(self):
        output_cfg_file = os.path.join(self.tempdir, 'config.cfg')
        input_cfg_file = os.path.join(self.tempdir, 'inputConf.cfg')

        IniConfigWriter().write(filePath=input_cfg_file,
                                reconsConfiguration=self.conf)
        self.mainWindow.setConfFile(input_cfg_file)
        self.mainWindow.mainWidget.saveConfiguration(output_cfg_file,
                                                     merge=False)

        savedConfig = read(output_cfg_file)
        savedConfig.sinograms[0].loadData(refFile=None)
        self.assertTrue(savedConfig == self.conf)


@unittest.skipIf(freeart_missing, "freeart missing")
class TestLoadAndSaveFluoConfig(unittest.TestCase):
    """
    Simple test wich right a reference cfg file for fluorescence and display it
    """

    def setUp(self):
        unittest.TestCase.setUp(self)
        # create the sino file
        self.tempdir = tempfile.mkdtemp()
        self.mainWindow = QFreeARTWidget.ProjectWindow()
        self.mainWindow.setAttribute(qt.Qt.WA_DeleteOnClose)

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        self.mainWindow.close()
        unittest.TestCase.tearDown(self)

    def testFluoH5EDF(self):
        """Test that the configuration from h5 files using .edf to store
        fluorescence sinogram are correctly load and save"""
        conf = testutils.createConfigFluo(self.tempdir,
                                          fileExtension='.edf',
                                          withMaterials=True)
        output_cfg_file = os.path.join(self.tempdir, 'config.h5')
        input_cfg_file = os.path.join(self.tempdir, 'inputConf.h5')

        H5ConfigWriter().write(filePath=input_cfg_file,
                               reconsConfiguration=conf)
        self.mainWindow.setConfFile(input_cfg_file)
        self.mainWindow.mainWidget.saveConfiguration(output_cfg_file,
                                                     merge=False)

        savedConfig = read(output_cfg_file)
        self.assertTrue(numpy.isclose(savedConfig.minAngle, conf.minAngle))
        self.assertTrue(numpy.isclose(savedConfig.maxAngle, conf.maxAngle))
        savedConfig.minAngle = conf.minAngle
        savedConfig.maxAngle = conf.maxAngle

        # ..warning:: As dictdump is not retrieving the correct types we have to update the
        # materials dict but the loaded one will keep the API of the dict
        mat = {}
        for key in savedConfig.materials.materials.data:
            mat[key] = savedConfig.materials.materials.data[key]
            assert("CompoundFraction" in mat[key])
            assert("CompoundList" in mat[key])
            mat[key]["CompoundFraction"] = list(mat[key]["CompoundFraction"])
            mat[key]["CompoundList"] = list(mat[key]["CompoundList"])
        savedConfig.materials.materials.data = mat

        self.assertTrue(savedConfig == conf)

    def testFluoEDFCFG(self):
        """Test that the configuration from cfg/ini files using .edf to store
        fluorescence sinogram are correctly load and save"""
        conf = testutils.createConfigFluo(self.tempdir,
                                          fileExtension='.edf',
                                          withMaterials=True)

        output_cfg_file = os.path.join(self.tempdir, 'config.cfg')
        input_cfg_file = os.path.join(self.tempdir, 'inputConf.cfg')

        IniConfigWriter().write(filePath=input_cfg_file,
                                reconsConfiguration=conf)
        self.mainWindow.setConfFile(input_cfg_file)
        self.mainWindow.mainWidget.saveConfiguration(output_cfg_file,
                                                     merge=False)
        savedConfig = read(output_cfg_file)
        # ..warning:: As dictdump is not retrieving the correct types we have to update the
        # materials dict but the loaded one will keep the API of the dict
        mat = {}
        for key in savedConfig.materials.materials.data:
            mat[key] = savedConfig.materials.materials.data[key]
            assert("CompoundFraction" in mat[key])
            assert("CompoundList" in mat[key])
            mat[key]["CompoundFraction"] = list(mat[key]["CompoundFraction"])
            mat[key]["CompoundList"] = list(mat[key]["CompoundList"])
        savedConfig.materials.materials.data = mat

        self.assertTrue(savedConfig == conf)

    def testFluoH5CFG(self):
        """Test that the configuration from cfg/ini files using .h5 to store
        fluorescence sinogram are correctly load and save"""
        pass

    def testFluoH5H5(self):
        """Test that the configuration from H5 files using .h5 to store
        fluorescence sinogram are correctly load and save"""
        pass


def suite():
    test_suite = unittest.TestSuite()
    for ui in (TestProjectCreationAndReconstructionTx, TestLoadAndSaveTxConfig,
               TestLoadAndSaveFluoConfig):
        test_suite.addTest(
            unittest.defaultTestLoader.loadTestsFromTestCase(ui))

    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
