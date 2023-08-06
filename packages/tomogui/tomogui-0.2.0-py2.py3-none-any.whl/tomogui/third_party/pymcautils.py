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
__date__ = "31/10/2017"

import logging
import os

_logger = logging.getLogger(__name__)



def tryToFindPattern(filePath, groupType=None):
    """Basically try to fit with pymca output files

    :param filePath: the file we want to find pattern for.

    :return: the files we can group and the type of group we can process
    """

    # try to fit with pymca files
    if not groupType or groupType == 'pymca':
        pattern = 'ANALYSIS/det'
        if pattern in filePath:
            pymcaFiles = []
            if filePath.count(pattern) > 1:
                mess = """found more than one pattern in the folder path.
                    Can t determine any"""
                _logger.info(mess)
                return

            assert(len(pattern) < len(filePath)+2)
            indexPattern = filePath.find(pattern)
            # get detxx value
            detPatternStart = indexPattern+len(pattern)-3
            detPatternEnd = indexPattern+len(pattern)+2
            currentDet = filePath[detPatternStart: detPatternEnd]
            # try replacing det xx by all possible values
            for iDet in range(100):
                if iDet < 10:
                    detID = 'det0' + str(iDet)
                else:
                    detID = 'det' + str(iDet)

                potentialFileID = filePath.replace(currentDet, detID)
                if os.path.isfile(potentialFileID):
                    pymcaFiles.append(potentialFileID)

            if len(pymcaFiles) > 0:
                return pymcaFiles, 'pymca'

    return [], None
