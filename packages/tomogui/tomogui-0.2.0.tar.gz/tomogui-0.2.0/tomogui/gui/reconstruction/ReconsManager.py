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
__date__ = "24/05/2016"

from silx.gui import qt
from tomogui.configuration import config as tomoguiconfig
import tomogui.utils as utils
import tempfile
import sys
import logging

_logger = logging.getLogger("QFreeARTReconstructionManager")

try:
    from tomogui.gui.reconstruction.silxRM import SilxReconsManager, SilxReconsDialog
    # In the case open cl not install for example
    has_silx_RM = True
except ImportError as e:
    error_silx_FBP_import = e
    _logger.warning('Fail to import the silx reconstruction manager')
    _logger.warning(e)
    has_silx_RM = False
try:
    from freeart.utils import testutils
    from freeart.configuration import config as freeartconfig
    from freeart.configuration import structs
    from freeart.configuration import read as readConfigFile
    from freeart.configuration import save as saveConfigFile
    from .freeartRM import FreeartReconsManager, FreeartReconsDialog
    hasfreeart = True
except ImportError:
    from tomogui.third_party.configuration import config as freeartconfig
    from tomogui.third_party.configuration import structs
    from tomogui.third_party.configuration import read as readConfigFile
    from tomogui.third_party.configuration import save as saveConfigFile
    hasfreeart = False

_qapp = None


def runReconstruction(config, platformId=None, deviceId=None):
    """Top level function which can handle with more than one reconstruction if
    needed. For example in the case of the a fluorescence reconstruction
     having knowledge of It and I0 instead of the absorption matrix this
     will run first the absorption matrix reconstruction then the
     reconstruction of the fluorescence sinograms.

     :param config: configuration of the reconstruction to run
     :param int platformId: openCL platform id if any selected
     :param int deviceId: openCL device id if any selected
    """

    def _deduceTxforFluoAbsMat(configFluo):
        """Deduce from a fluorescence configuration the TxConfig to be run
        in order to reconstruct the absorption matrix. In this case
        configFluo.absMat is a sinogram and not an absorption matrix yet
        """
        configTx = freeartconfig.TxConfig()
        configTx.minAngle = configFluo.minAngle
        configTx.maxAngle = configFluo.maxAngle
        configTx.center = configFluo.center
        configTx.includeLastProjection = configFluo.includeLastProjection
        configTx.useAFileForI0 = configFluo.useAFileForI0
        configTx.I0 = configFluo.I0
        configTx.solidAngleOff = configFluo.solidAngleOff
        configTx.beamCalcMethod = configFluo.beamCalcMethod
        configTx.voxelSize = configFluo.voxelSize
        configTx.projections = configFluo.projections
        configTx.definitionReduction = configFluo.definitionReduction
        configTx.projectionNumberReduction = configFluo.projectionNumberReduction
        configTx.acquiInverted = configFluo.acquiInverted
        configTx.dampingFactor = configFluo.dampingFactor
        configTx.sinograms = [
            structs.TxSinogram(name='It',
                               fileInfo=configFluo.absMat.fileInfo,
                               data=configFluo.absMat.data)
            ]
        return configTx

    if config.reconsType == tomoguiconfig.FBPConfig.FBP_ID:
        if has_silx_RM is True:
            return SilxReconsDialog(parent=None, cfgFile=None, config=config,
                                    platformId=platformId, deviceId=deviceId).exec_()
        else:
            msg = qt.QMessageBox()
            msg.setIcon(qt.QMessageBox.Warning)
            msg.setText('Can\'t launch FBP reconstruction(s)')
            text = 'Import fail with error: %s' % error_silx_FBP_import
            msg.setInformativeText('Can\'t run reconstruction until defined')
            msg.exec_()
            exit(0)

    if hasfreeart is True:
        if config.reconsType == freeartconfig._ReconsConfig.TX_ID:
            return FreeartReconsDialog(parent=None, config=config).exec_()
        elif config.reconsType in (freeartconfig._ReconsConfig.FLUO_ID,
                                   freeartconfig._ReconsConfig.COMPTON_ID):
            # In the case we have to reconstruct the self attenuation matrix first
            if config.isAbsMatASinogram is True:
                txConfig = _deduceTxforFluoAbsMat(config)
                dialog = FreeartReconsDialog(parent=None, config=txConfig)
                if not dialog.exec_():
                    _logger.warning('Reconstruction of the absorption matrix has '
                                    'been canceled. Fluorescence sinogram won\'t'
                                    'be reconstructed')
                    return False
                else:
                    reconsAlgos = dialog.mainWindow.freeartInterpreter.getReconstructionAlgorithms()
                    assert(len(reconsAlgos) is 1)
                    reconsPh = reconsAlgos[reconsAlgos.keys()[0]].getPhantom()
                    config.absMat.fileInfo = None
                    config.absMat.data = reconsPh
                    assert(reconsPh is not None)
                    config.isAbsMatASinogram = False
            return FreeartReconsDialog(parent=None,
                                       config=config).exec_()
        else:
            raise ValueError('reconstruction type not managed')


class ReconsManagerWindow(qt.QMainWindow):
    """
    The main window to run a reconsparam

    :param cfgFile: the configuration file containing all information
                    concerning the reconsparam to be run.
    """
    def __init__(self, cfgFile):
        qt.QMainWindow.__init__(self)
        self.setAttribute(qt.Qt.WA_DeleteOnClose)
        # Both the __SilxTomoConfig and the freeart config manager car read the
        # reconsparam type of each other.
        config = readConfigFile(cfgFile)

        reconsType = config.reconsType
        if reconsType == tomoguiconfig.FBPConfig.FBP_ID:
            if has_silx_RM is True:
                self.manager = SilxReconsManager(self, config)
                title = 'silx - FBP'
            else:
                raise ImportError(error_silx_FBP_import)
        elif hasfreeart and reconsType in (freeartconfig._ReconsConfig.FLUO_ID,
                                           freeartconfig._ReconsConfig.TX_ID,
                                           freeartconfig._ReconsConfig.COMPTON_ID):
            self.manager = FreeartReconsManager(self, config)
            title = self.manager.freeartInterpreter.getReconstructionType()\
                    + " reconsparam"
            hasAbsMatrix = self.manager.freeartInterpreter.isAFluoOrComptonReconstruction()
            hasAbsMatrix = hasAbsMatrix and self.manager.freeartInterpreter.config.isAbsMatASinogram
            if hasAbsMatrix:
                title = title + " - absorption matrix definition"
        else:
            err = "reconsparam type %s is not recognized" % reconsType
            raise ValueError(err)

        self.setCentralWidget(self.manager)
        self.setWindowTitle(title)


if __name__ == "__main__":
    if not hasfreeart:
        exit(0)
    global app
    app = qt.QApplication([])

    splash = utils.getMainSplashScreen()
    app.processEvents()

    if len(sys.argv) == 2 and sys.argv[1].lower().endswith(".cfg"):
        cfgFile = sys.argv[1]
        expExample = None
    else:

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
        interactionProba = {materialName: 0.0001}

        expExample = testutils.ComptonExperimentationExample(materials,
                                                             sheppLoganPartID,
                                                             interactionProba,
                                                             buildFromSinogram=True,
                                                             oversampling=20,
                                                             dampingFactor=0.02,
                                                             nbAngles=360,
                                                             E0=2e13)
        expExample.setUp()
        cfgFile = expExample.cfg_fluo_file

    mainWindow = ReconsManagerWindow(cfgFile)

    mainWindow.setAttribute(qt.Qt.WA_DeleteOnClose)
    mainWindow.show()
    splash.finish(mainWindow)

    app.exec_()

    if expExample:
        expExample.tearDown()
