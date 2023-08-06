#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Launch the material dialog / editor from a configuration file"""

import sys
import logging
import argparse
from silx.gui import qt
try:
    from freeart.configuration import read, fileInfo, structs
    from freeart.configuration import config as freeartconfig
except:
    from tomogui.third_party.configuration import read, fileInfo, structs
    from tomogui.third_party.configuration import config as freeartconfig
from tomogui.gui.materials.QSampleComposition import SampleCompDialog

logging.basicConfig()
_logger = logging.getLogger(__file__)


def getinputinfo():
    return "tomogui materials [configFile]"


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'mat_file',
        help='file containing the material definition')
    parser.add_argument(
        '--debug',
        dest="debug",
        action="store_true",
        default=False,
        help='Set logging system in debug mode')

    options = parser.parse_args(argv[1:])

    if options.debug:
        logging.root.setLevel(logging.DEBUG)

    filePath = options.mat_file
    file_info_dict = fileInfo.H5MatrixFileInfo(filePath + structs.MaterialsDic.MATERIALS_DICT)
    file_info_comp = fileInfo.H5MatrixFileInfo(filePath + structs.MatComposition.MAT_COMP_DATASET)

    global app  # QApplication must be global to avoid seg fault on quit
    app = qt.QApplication.instance() or qt.QApplication([])

    dialog = None
    # if this is a fluoConfig file
    try:
        config = read(filePath)
        assert(isinstance(config, freeartconfig.FluoConfig))
        dialog = SampleCompDialog(config=config)
    except:
        _logger.info('fail to open the file as a fluoconfiguration file.'
                     'Try to open it as a simple materials file')
        dialog = None

    if dialog is None:
        materials = structs.Materials(
            materials=structs.MaterialsDic(fileInfo=file_info_dict),
            matComposition=structs.MatComposition(fileInfo=file_info_comp))
        try:
            materials.loadData(filePath=filePath)
        except IOError:
            raise ValueError('Fail to open data, are you sure file exists')
        except KeyError:
            raise ValueError('Materials definition and the sample composition '
                             'can\'t be loaded seems like they are not existing '
                             'or set at uncommun location')
        dialog = SampleCompDialog(materials=materials)
    dialog.exec_()
    return 0


if __name__ == '__main__':
    main(sys.argv)
    exit(0)