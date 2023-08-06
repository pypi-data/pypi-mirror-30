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

import shutil
import tempfile
import unittest
from silx.gui import qt
from tomogui.gui.reconsparam.ReconsParamWidget import ReconsParamWidget
try:
    from freeart.unitsystem import metricsystem
    from freeart.utils import outgoingrayalgorithm, raypointsmethod
    from freeart.configuration import config as freeartconfig
    from freeart.utils import testutils as freeart_testutils
    freeart_missing = False
except ImportError:
    freeart_missing = True


@unittest.skipIf(freeart_missing, "freeart missing")
class TestQFreeARTReconsParamConfiguration(unittest.TestCase):
    """
    Unit test for the FreeartReconsParam
    """

    def setUp(self):
        self.voxelSizeToTest = 2.63 * metricsystem.mm
        self.oversamplingToTest = 4
        self.beamCalculationToTest = raypointsmethod.withoutInterpolation
        self.outgoingBeamCalculationMethodToTest = outgoingrayalgorithm.createOneRayPerSamplePoint
        self.solidAngleIsOffToTest = True
        self.lastAngleEqualFirstToTest = True
        self.nbProjectionReductionToTest = 2
        self.definitionReductionToTest = 3
        self.dampingFactorToTest = 0.2
        self.precisionToTest = 'simple'

        self.tempdir = tempfile.mkdtemp()
        self.ori_config = freeart_testutils.createConfigFluo(tempdir=self.tempdir,
                                                             addSelfAbsMat=False,
                                                             selfAbsMat=None,
                                                             withMaterials=False,
                                                             fileExtension='.edf')

        self.ori_config.voxelSize = self.voxelSizeToTest
        self.ori_config.oversampling = self.oversamplingToTest
        self.ori_config.dampingFactor = self.dampingFactorToTest
        self.ori_config.beamCalcMethod = self.beamCalculationToTest
        self.ori_config.outBeamCalMethod = self.outgoingBeamCalculationMethodToTest
        self.ori_config.solidAngleOff = self.solidAngleIsOffToTest
        self.ori_config.projectionNumberReduction = self.nbProjectionReductionToTest
        self.ori_config.definitionReduction = self.definitionReductionToTest
        self.ori_config.precision = self.precisionToTest

        self._qapp = qt.QApplication.instance() or qt.QApplication([])
        self.widget = ReconsParamWidget()
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)

    def tearDown(self):
        self.widget.close()
        shutil.rmtree(self.tempdir)

    def testWriting(self):
        """
        Test that setup  a widget with the requested values and save this
        configuration.
        The configuration file must fit with the widget configuration
        """
        # set the widget
        self.widget.setVoxelSize(self.voxelSizeToTest)
        self.widget.setOversampling(self.oversamplingToTest)
        self.widget.setDampingFactor(self.dampingFactorToTest)
        self.widget.setRayPointsMethod(self.beamCalculationToTest)
        self.widget.setOutgoingRayAlgorithm(self.outgoingBeamCalculationMethodToTest)
        self.widget.setSolidAngleOff(self.solidAngleIsOffToTest)
        self.widget.setLastAngleIsIncluded(self.lastAngleEqualFirstToTest)
        self.widget.setProjectionReductionFactor(self.nbProjectionReductionToTest)
        self.widget.setDefinitionReduction(self.definitionReductionToTest)
        self.widget.setPrecision(self.precisionToTest)
        # do the writing
        conf = freeartconfig.FluoConfig()
        self.widget.saveConfiguration(conf)

        self.assertTrue(conf.voxelSize == self.voxelSizeToTest)
        self.assertTrue(conf.oversampling == self.oversamplingToTest)
        self.assertTrue(conf.dampingFactor == self.dampingFactorToTest)
        self.assertTrue(conf.outBeamCalMethod == self.outgoingBeamCalculationMethodToTest)
        self.assertTrue(conf.solidAngleOff == self.solidAngleIsOffToTest)
        self.assertTrue(conf.includeLastProjection == self.lastAngleEqualFirstToTest)
        self.assertTrue(conf.projectionNumberReduction == self.nbProjectionReductionToTest)
        self.assertTrue(conf.definitionReduction == self.definitionReductionToTest)
        self.assertTrue(conf.precision == self.precisionToTest)

    def testReading(self):
        """
        Test that if the widget load configuration fron a valid file the setup
        of the widget will be correct
        """
        self.widget.loadConfiguration(self.ori_config)
        self.assertTrue(
            self.widget.getVoxelSize() == self.voxelSizeToTest)
        self.assertTrue(
            self.widget.getOversampling() == self.oversamplingToTest)
        self.assertTrue(
            self.widget.getDampingFactor() == self.dampingFactorToTest)
        self.assertTrue(
            self.widget.getRayPointsMethod() == self.beamCalculationToTest)
        self.assertTrue(
            self.widget.getOutgoingRayAlgorithm() == self.outgoingBeamCalculationMethodToTest)
        self.assertTrue(
            self.widget.isSolidAngleOff() == self.solidAngleIsOffToTest)
        self.assertTrue(
            self.widget.isLastAngleIncluded() == self.lastAngleEqualFirstToTest)
        self.assertTrue(
            self.widget.getDefinitionReduction() == self.definitionReductionToTest)
        self.assertTrue(
            self.widget.getProjectionReductionFactor() == self.nbProjectionReductionToTest)
        self.assertTrue(
            self.widget.getPrecision() == self.precisionToTest)

def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(TestQFreeARTReconsParamConfiguration))

    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
