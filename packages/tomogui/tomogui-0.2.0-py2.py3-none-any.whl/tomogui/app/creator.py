#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import argparse
from silx.gui import qt
from tomogui import utils
from tomogui.gui.creator.AbsMatCreator import AbsMatCreator

logging.basicConfig()
_logger = logging.getLogger(__file__)


def getinputinfo():
    return "tomogui creator []"


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--debug',
        dest="debug",
        action="store_true",
        default=False,
        help='Set logging system in debug mode')

    options = parser.parse_args(argv[1:])

    if options.debug:
        logging.root.setLevel(logging.DEBUG)

    global app  # QApplication must be global to avoid seg fault on quit
    app = qt.QApplication.instance() or qt.QApplication([])

    splash = utils.getMainSplashScreen()

    creator = AbsMatCreator()
    splash.finish(creator)
    creator.show()
    app.exec_()


if __name__ == '__main__':
    main(sys.argv)