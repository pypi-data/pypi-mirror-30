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

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "23/09/2016"


try:
    from silx.gui import qt
except ImportError:
    raise ImportError("Can't found silx modules")
import tomogui
from tomogui.gui.utils import splashscreens, icons as tomoguiIcons


def getMainSplashScreen():
    pixmap = splashscreens.getQPixmap('tomogui')
    splash = qt.QSplashScreen(pixmap)
    splash.show()
    splash.raise_()
    # TODO : deal with version in the close future
    text = 'version ' + 'xxx'  # str(tomogui.version)
    splash.showMessage(text, qt.Qt.AlignLeft | qt.Qt.AlignBottom, qt.Qt.white)
    return splash


def addHTMLLine(txt):
    return "<li>" + txt + "</li>"
