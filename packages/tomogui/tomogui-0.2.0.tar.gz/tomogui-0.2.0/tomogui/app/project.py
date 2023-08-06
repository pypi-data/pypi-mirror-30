#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from tomogui.gui import ProjectWidget
from silx.gui import qt
from tomogui import utils
import argparse
import os

def getinputinfo():
    return "tomogui project [projectfile.cfg]"


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'project_file',
        help='File to store the reconstruction defintion',
        nargs='?',
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

    newCFGFile = options.project_file
    if newCFGFile:
        fn, file_extension = os.path.splitext(newCFGFile)
        if file_extension.lower() not in ('.cfg', '.ini', '.h5', '.hdf5'):
            raise RuntimeError("The given project file has the wrong extension (should be .cfg, .h5 or .cfg)")

    global app  # QApplication must be global to avoid seg fault on quit
    app = qt.QApplication([])
    splash = utils.getMainSplashScreen()

    mainWindow = ProjectWidget.ProjectWindow(cfgFile=newCFGFile)
    mainWindow.setAttribute(qt.Qt.WA_DeleteOnClose)
    splash.finish(mainWindow)
    mainWindow.show()
    app.exec_()


if __name__ == "__main__":
    main(sys.argv)