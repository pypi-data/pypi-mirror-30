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


import tempfile
import unittest
import copy
import shutil
import numpy
from silx.gui import qt
try:
    from freeart.utils import testutils
    from freeart.configuration import structs, fileInfo, config as freeartconfig
    from tomogui.gui.materials.QSampleComposition import QSampleComposition
    freeart_missing = False
except ImportError:
    freeart_missing = True


@unittest.skipIf(freeart_missing, "freeart missing")
class TestLoadAndSave(unittest.TestCase):
    """
    Test that sample composition widgets are correctly loading and saving
    materials.
    """
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.fluoConfig = testutils.createConfigFluo(self.tempdir,
                                                     fileExtension='.edf',
                                                     withMaterials=True)
        assert('mat1' in self.fluoConfig.materials.materials)
        assert('mat2' in self.fluoConfig.materials.materials)

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def testSimpleInteraction(self):
        def createMask():
            colorAir = qt.QColor(255, 0, 0)
            widget.maskToolWidget._addMask('mat1',
                                           self.fluoConfig.materials.materials[
                                               'mat1'], colorAir)
            colorWater = qt.QColor(255, 0, 0)
            widget.maskToolWidget._addMask('mat2',
                                           self.fluoConfig.materials.materials[
                                               'mat2'], colorWater)
        confToLoad = copy.copy(self.fluoConfig)
        confToLoad.materials = None
        widget = QSampleComposition(config=confToLoad)
        createMask()

        outFile = self.tempdir + 'materials.h5'
        widget.saveTo(outFile)

        refMaterials = structs.Materials(
            materials=structs.MaterialsDic(
                fileInfo=fileInfo.H5MatrixFileInfo(outFile + structs.MaterialsDic.MATERIALS_DICT)),
            matComposition=structs.MatComposition(
                fileInfo=fileInfo.H5MatrixFileInfo(outFile + structs.MatComposition.MAT_COMP_DATASET))
        )
        refMaterials.loadData(outFile)

        # check materials
        for key in refMaterials.materials:
            self.assertTrue(str(key) in self.fluoConfig.materials.materials)

    def testLoad(self):
        widget = QSampleComposition(config=self.fluoConfig)
        self.assertTrue("mat1" in widget.maskToolWidget.materials)
        self.assertTrue("mat2" in widget.maskToolWidget.materials)
        self.assertTrue(self.fluoConfig.materials.materials.keys() == widget.maskToolWidget.materials.keys())


@unittest.skipIf(freeart_missing, "freeart missing")
class TestConfigurationFileDataSourceFluo(unittest.TestCase):
    """
    Test that the QsampleComposition is correctly loading and saving
    from/to configuration file

    .. note:: this test is not including the QSinoFluoSelector test for reading
              and writing configuration. A special test has been created for
              this purpose.
    """

    def setUp(self):
        # deal with files
        self.tempdir = tempfile.mkdtemp()
        self.fluoConfig = testutils.createConfigFluo(self.tempdir,
                                                     fileExtension='.h5',
                                                     withMaterials=True,
                                                     fileExtensionMat='.h5')

        self.widget = QSampleComposition(config=self.fluoConfig)
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)

    def tearDown(self):
        self.widget.close()
        shutil.rmtree(self.tempdir)

    def testH5(self):
        """Test that the widget is well writing the configuration file"""
        self.widget.loadConfiguration(self.fluoConfig)
        outConf = freeartconfig.FluoConfig()
        self.widget.saveConfiguration(outConf, refFile=None)
        for sinoFile in outConf.sinograms:
            for sino in outConf.sinograms[sinoFile]:
                sino.loadData(refFile=None)
        outConf.materials.loadData(filePath=None)

        mat = {}
        self.assertTrue(outConf.materials is not None)
        self.assertTrue(outConf.materials.materials is not None)
        self.assertTrue(outConf.materials.materials.data is not None)

        for key in outConf.materials.materials.data:
            mat[key] = outConf.materials.materials.data[key]
            assert ("CompoundFraction" in mat[key])
            assert ("CompoundList" in mat[key])
            mat[key]["CompoundFraction"] = list(mat[key]["CompoundFraction"])
            mat[key]["CompoundList"] = list(mat[key]["CompoundList"])
            # deal with float
            for icf, v in enumerate(mat[key]["CompoundFraction"]):
                ref = self.fluoConfig.materials.materials.data[key]["CompoundFraction"][icf]
                self.assertTrue(numpy.isclose(mat[key]["CompoundFraction"][icf],
                                              ref))
                mat[key]["CompoundFraction"][icf] = ref

        outConf.materials.materials.data = mat

        self.assertTrue(outConf.materials == self.fluoConfig.materials)


def suite():
    test_suite = unittest.TestSuite()
    for testClass in (TestLoadAndSave, TestConfigurationFileDataSourceFluo):
        test_suite.addTest(
            unittest.defaultTestLoader.loadTestsFromTestCase(testClass))

    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
