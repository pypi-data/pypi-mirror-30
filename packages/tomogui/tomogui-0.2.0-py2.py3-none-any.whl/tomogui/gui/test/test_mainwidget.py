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
from silx.gui import qt
try:
    import freeart
except:
    freeart = None
from tomogui.gui.MainWidget import TomoguiMainWindow


class TestQmainWindow(unittest.TestCase):
    """
    pass
    """

    def testMainWindowOption(self):
        """
        Make sure the option adapt to the available python module such as
        freeart.
        """
        _qapp = qt.QApplication.instance() or qt.QApplication([])
        widget = TomoguiMainWindow(mockNoFreeart=True)
        widget.show()
        widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.assertTrue(hasattr(widget, "_qpbSilxFBP"))
        if freeart is not None:
            self.assertFalse(hasattr(widget, "_qpbTxRecons"))
            self.assertFalse(hasattr(widget, "_qpbFluorescence"))
        widget.close()

        widget = TomoguiMainWindow(mockNoFreeart=False)
        widget.show()
        widget.setAttribute(qt.Qt.WA_DeleteOnClose)
        self.assertTrue(hasattr(widget, "_qpbSilxFBP"))
        if freeart is not None:
            self.assertTrue(hasattr(widget, "_qpbTxRecons"))
            self.assertTrue(hasattr(widget, "_qpbFluorescence"))
        widget.close()


def suite():
    test_suite = unittest.TestSuite()
    for testClass in (TestQmainWindow,):
        test_suite.addTest(
            unittest.defaultTestLoader.loadTestsFromTestCase(testClass))
    return test_suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
