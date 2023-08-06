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

import sys
import unittest

if sys.version < '3.0':
    import ConfigParser as configparser
else:
    import configparser

from silx.gui import qt
from tomogui.gui.normalization.QCenteringWidget import QCenteringWidget
from tomogui.gui.normalization.QRotationCenterWidget import QRotationCenterWidget
import shutil
import os
import tempfile
try:
    import freeart
    from freeart.configuration import config as freeartconfig
    from freeart.utils import testutils
    freeart_missing = False
except ImportError:
    freeart_missing = True


@unittest.skipIf(freeart_missing, "freeart missing")
class testConfigurationQCenteringWidget(unittest.TestCase):
    """
    Test that the QCenteringWidget is able to read and write correctly
    configuration file
    """
    rotationCenterToTest = 10
    def setUp(self):
        self.tempdir = tempfile.mkdtemp()
        self.conf = testutils.createConfigFluo(self.tempdir)

        self.conf.center = self.rotationCenterToTest

        self.widget = QCenteringWidget()
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)

    def tearDown(self):
        self.widget.close()
        shutil.rmtree(self.tempdir)

    def testCenter(self):
        """Make sure the center parameter is correctly saved and load"""
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)

        self.widget.loadConfiguration(self.conf)
        confOut = freeartconfig.FluoConfig()
        self.widget.saveConfiguration(confOut)

        self.assertTrue(confOut.center == self.conf.center)
        self.assertTrue(confOut.center == self.rotationCenterToTest)


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(
        unittest.defaultTestLoader.loadTestsFromTestCase(testConfigurationQCenteringWidget))

    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
