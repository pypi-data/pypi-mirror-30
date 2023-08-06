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

import unittest
from silx.gui import qt
from tomogui.gui.reconstruction.ReconsManager import ReconsManagerWindow
import time
try:
    import freeart
    from freeart.utils import testutils
except ImportError:
    freeart = None


@unittest.skipIf(freeart is None, "freeart missing")
class testIterateButton(unittest.TestCase):
    """
    Test that the QDataSourceTxWidget is well saving and loading parameters
    from a configuration file
    """

    materialName = "Steel"
    material = {
        'Comment': "No comment",
        'CompoundList': ['Cr', 'H', 'He'],
        'CompoundFraction': [18.37, 69.28, 12.35],
        'Density': 0.01,
        'Thickness': 1.0
    }

    materials = {materialName: material}
    sheppLoganPartID = {materialName: 2}
    interactionProba = {materialName: 0.01}
    elements=['K']

    def setUp(self):
        self.expExample = testutils.ComptonExperimentationExample(self.elements,
                                                                  self.materials,
                                                                  self.sheppLoganPartID,
                                                                  self.interactionProba,
                                                                  buildFromSinogram=False,
                                                                  oversampling=20,
                                                                  dampingFactor=0.02,
                                                                  nbAngles=360,
                                                                  E0=2e13)
        self.expExample.setUp()

        # Makes sure a QApplication exists and do it once for all
        self._qapp = qt.QApplication.instance() or qt.QApplication([])
        import shutil
        shutil.copy(self.expExample.cfg_fluo_file, 'testCFG.cfg')

        self.mainWindow = ReconsManagerWindow(self.expExample.cfg_fluo_file)
        self.mainWindow.setAttribute(qt.Qt.WA_DeleteOnClose)

    def tearDown(self):
        self.mainWindow.close()
        self.expExample.tearDown()

    def testIteration(self):
        """Test that the widget is well writing the configurataion file"""
        self.mainWindow.show()

        self.mainWindow.centralWidget()._runIteratation()
        maxWaitTime = 10.0
        sleepTime = 0.0
        self.mainWindow.centralWidget().threadInterpreterIterator.wait()


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(testIterateButton))

    return test_suite
