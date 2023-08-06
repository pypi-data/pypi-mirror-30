#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from silx.gui import qt
from tomogui import utils
from tomogui.gui.reconstruction import ReconsManager
try:
    from freeart.configuration import read as readConfigFile
except ImportError:
    from tomogui.third_party.configuration import read as readConfigFile

def getinputinfo():
    return "tomogui recons [projectfile.*]"


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'project_file',
        help='File to load the project configuration',
        default=None
    )
    parser.add_argument(
        '--debug',
        dest="debug",
        action="store_true",
        default=False,
        help='Set logging system in debug mode')

    options = parser.parse_args(argv[1:])

    if options.debug:
        logging.root.setLevel(logging.DEBUG)

    cfgFile = options.project_file
    fn, file_extension = os.path.splitext(cfgFile)
    if file_extension.lower() not in ('.cfg', 'ini', '.h5', '.hdf5'):
        raise RuntimeError("The given project file has the wrong extension (should be .cfg, .h5 or .hdf5)")

    global app  # QApplication must be global to avoid seg fault on quit
    app = qt.QApplication([])
    ReconsManager.runReconstruction(readConfigFile(cfgFile))


if __name__ == "__main__":
    main(sys.argv)
