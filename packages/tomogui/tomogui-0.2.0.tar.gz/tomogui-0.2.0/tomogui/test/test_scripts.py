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
from __future__ import absolute_import, division, print_function

"""Test suite to scripts"""

__authors__ = ["V.Valls", "H.Payno"]
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "26/02/2018"


import sys
import unittest
import logging
import subprocess
from tomogui.test.utils.utilstest import UtilsTest

_logger = logging.getLogger(__name__)

from silx.gui import qt
import silx


class TestScriptsHelp(unittest.TestCase):

    def executeCommandLine(self, command_line, env):
        """Execute a command line.

        Log output as debug in case of bad return code.
        """
        _logger.info("Execute: %s", " ".join(command_line))
        p = subprocess.Popen(command_line,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=env)
        out, err = p.communicate()
        _logger.info("Return code: %d", p.returncode)
        try:
            out = out.decode('utf-8')
        except UnicodeError:
            pass
        try:
            err = err.decode('utf-8')
        except UnicodeError:
            pass

        if p.returncode != 0:
            _logger.info("stdout:")
            _logger.info("%s", out)
            _logger.info("stderr:")
            _logger.info("%s", err)
        else:
            _logger.debug("stdout:")
            _logger.debug("%s", out)
            _logger.debug("stderr:")
            _logger.debug("%s", err)
        self.assertEqual(p.returncode, 0)

    def executeAppHelp(self, script_name, module_name):
        script = UtilsTest.script_path(script_name, module_name)
        env = UtilsTest.get_test_env()
        if script.endswith(".exe"):
            command_line = [script]
        else:
            command_line = [sys.executable, script]
        command_line.append("--help")
        self.executeCommandLine(command_line, env)

    def testRecons(self):
        self.executeAppHelp("recons", "tomogui.app.recons")

    def testProject(self):
        self.executeAppHelp("project", "tomogui.app.project")

    def testInvert(self):
        self.executeAppHelp("invert", "tomogui.app.invert")

    def testCreator(self):
        self.executeAppHelp("creator", "tomogui.app.creator")

    def testMaterials(self):
        self.executeAppHelp("materials", "tomogui.app.materials")

    def testNorm(self):
        self.executeAppHelp("norm", "tomogui.app.norm")


def suite():
    loader = unittest.defaultTestLoader.loadTestsFromTestCase
    testsuite = unittest.TestSuite()
    testsuite.addTest(loader(TestScriptsHelp))
    return testsuite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
