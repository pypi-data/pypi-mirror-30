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
__date__ = "18/09/2017"

import unittest
from tomogui.gui.sinogramselector import QSinoProjSelector
import silx
if silx._version.MINOR < 7:
    from silx.test.utils import ParametricTestCase
else:
    from silx.utils.testutils import ParametricTestCase
from silx.gui import qt
import numpy

_qapp = None

class TestQProjectionSelector(ParametricTestCase):
    """
    Test the QProjectionSelector functionalities
    """

    def setUp(self):
        global _qapp
        if _qapp is None:
            # Makes sure a QApplication exists and do it once for all
            _qapp = qt.QApplication.instance() or qt.QApplication([])

        self.widget = QSinoProjSelector(parent=None)
        self.widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.widget.setSinogram(numpy.random.rand(50, 50))

    def tearDown(self):
        self.widget.close()
        ParametricTestCase.tearDown(self)

    def testGetSetSelection(self):
        possibleSelection = ("0:2", "7", "5;8", "2:9;13:22")
        for selection in possibleSelection:
            with self.subTest(input=selection):
                self.widget.setSelection(selection)
                self.assertTrue(
                    self.widget.getSelection() == selection
                )
                self.assertTrue(
                    self.widget.getInteractiveSelWidget().getSelection() == selection
                )

        self.widget.setSelection("")
        self.assertTrue(
            self.widget.getInteractiveSelWidget().getSelection() == "0:50"
        )

        self.widget.setSelection(":10")
        self.assertTrue(
            self.widget.getInteractiveSelWidget().getSelection() == "0:10"
        )

        self.widget.setSelection("5:")
        self.assertTrue(
            self.widget.getInteractiveSelWidget().getSelection() == "5:50"
        )


def suite():
    test_suite = unittest.TestSuite()
    for test in (TestQProjectionSelector, ):
        test_suite.addTest(
            unittest.defaultTestLoader.loadTestsFromTestCase(test))

    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')