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

__author__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "08/08/2017"


from silx.gui import qt


class QMessageGroupFiles(qt.QMessageBox):
    """
    Simple dialog to ask the user if he wants to group some files during
    freeart treatment
    """
    def __init__(self, group, groupType, parent=None):
        """
        Constructor

        :param plot : the plot widget to be linked with
        """
        qt.QMessageBox.__init__(self, parent)

        text = "Do you want to group those files ? "
        if groupType == 'pymca':
            text += " which seems to have been generated from pymca. "

        text += " We will create a 'mean sinogram' from all sinograms having" \
                " the same ID (Title). And we will rebuild those sinograms."

        label = qt.QLabel(text, self)
        label.setWordWrap(True)
        label.setMinimumWidth(500)

        self.layout().addWidget(label, 0, 0)

        # list of files
        self.list = qt.QListWidget(self)
        for iFile in group:
            self.list.addItem(iFile)

        self.layout().addWidget(self.list, 1, 0)

        # buttons
        self.yesButton = self.addButton(qt.QMessageBox.Yes)
        self.noButton = self.addButton(qt.QMessageBox.No)

        # rearange the QMesageBox button
        self.layout().removeWidget(self.yesButton)
        self.layout().removeWidget(self.noButton)
        layoutButton = qt.QHBoxLayout()
        spacer = qt.QWidget()
        spacer.setSizePolicy(qt.QSizePolicy.Expanding,
                             qt.QSizePolicy.Expanding)
        layoutButton.addWidget(spacer)
        layoutButton.addWidget(self.yesButton)
        layoutButton.addWidget(self.noButton)
        layoutButton.addWidget(spacer)
        widgetButton = qt.QWidget()
        widgetButton.setLayout(layoutButton)
        self.layout().addWidget(widgetButton, 2, 0)
