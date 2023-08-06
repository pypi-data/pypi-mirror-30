  #!/usr/bin/env python
# coding: utf-8
# /*##########################################################################
# Copyright (C) 2016 European Synchrotron Radiation Facility
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
# ############################################################################*/
"""
Simple application doing data.max() - data
"""

__authors__ = ["H> Payno"]
__license__ = "MIT"
__date__ = "08/08/2017"


from freeart.utils import reconstrutils
import argparse
import sys


def getinputinfo():
    return "tomogui invert [] []"


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('edf_input', help='edf file to invert')
    parser.add_argument('edf_output', help='output edf file')
    parser.add_argument(
        '--debug',
        dest="debug",
        action="store_true",
        default=False,
        help='Set logging system in debug mode')

    options = parser.parse_args(argv[1:])

    if options.debug:
        logging.root.setLevel(logging.DEBUG)

    _input = options.edf_input
    _output = options.edf_output

    data = reconstrutils.LoadEdf_2D(_input)
    data = data.max() - data
    reconstrutils.saveMatrix(data, _output, overwrite=True)


if __name__ == "__main__":
    """
    """
    main(sys.argv)

