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

__author__ = ["H. Payno", "A. Sole"]
__license__ = "MIT"
__date__ = "04/03/2018"


from silx.gui import qt
from silx.opencl import ocl


class OpenCLPlatformSelector(qt.QWidget):
    """Widget used to select an openCL device."""
    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        self.setLayout(qt.QHBoxLayout())

        label = qt.QLabel("OpenCL Device:", self)
        self.layout().addWidget(label)
        self.deviceSelector = qt.QComboBox(self)
        self.deviceSelector.addItem("(-1, -1) No OpenCL device found")
        self.layout().addWidget(self.deviceSelector)

        devices = self.getOpenCLDevices()
        if len(devices):
            self.deviceSelector.clear()
            for device in devices:
                self.deviceSelector.addItem(
                    "(%d, %d) %s" % (device[0], device[1], device[2]))

    def getOpenCLDevices(self):
        devices = []
        if ocl is not None:
            for platformid, platform in enumerate(ocl.platforms):
                for deviceid, dev in enumerate(platform.devices):
                    devices.append((platformid, deviceid, dev.name))
        return devices

    def getSelectedDevice(self):
        """Return platform id and device id"""
        txt = str(self.deviceSelector.currentText()).split(")")[0]
        txt = txt[1:].split(",")
        return int(txt[0]), int(txt[1])
