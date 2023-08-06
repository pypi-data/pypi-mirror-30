###########################################################################
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
#############################################################################

__author__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "23/11/2017"

from silx.gui import qt
from tomogui.gui.utils.ConfigurationActor import ConfigurationActor
import numpy


class QDataSourceBaseWidget(qt.QWidget, ConfigurationActor):
    """
    Abstract class of QDataSourceTxWidget and QDataSourceFluoWidget
    """
    sigSinoRefChanged = qt.Signal(numpy.ndarray)
    """
    We have the concept of reference sinogram. He will be used to get the
    center of rotation of all other sinogram. He will also serve to define
    the projection we want to use for reconstructions
    """

    sigSinoRefDimChanged = qt.Signal(tuple)
    """
    Signal emitted when the dimension of the reference sinogram are changing
    """

    sigRequireMaterials = qt.Signal(bool)
    """
    Signal emitted when the reconstruction will need to get the sample
    composition
    """

    sigInfoForMaterialsChanged = qt.Signal()
    """Emitted when some information that might help the SampleCompTab like the
    AbsMat or the fluoSinograms"""

    sigI0MightChanged = qt.Signal(float)
    """Emitted when I0 value (based from a setted sinogram) have changed. This
    modification might be taken into account if we are using a unique value for
    I0 and not a sinogram"""

    def __init__(self, parent):
        qt.QWidget.__init__(self, parent)
        ConfigurationActor.__init__(self)

    def _sinogramRefHasChanged(self, sinogram):
        """
        Callback when the file for the normlalization of the center of rotation
        might have changed
        """
        if sinogram is not None:
            if sinogram.data is not None:
                data = sinogram.data
            elif sinogram.fileInfo is not None:
                sinogram.loadData(refFile=None)
                data = sinogram.data
            else:
                return
            self.sigSinoRefChanged.emit(data)
            self.sigSinoRefDimChanged.emit(data.shape)
