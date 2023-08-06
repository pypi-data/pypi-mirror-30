#!/usr/bin/python
# coding: utf-8
#
#    Project: Azimuthal integration
#             https://github.com/pyFAI/pyFAI
#
#    Copyright (C) 2015 European Synchrotron Radiation Facility, Grenoble, France
#
#    Principal author:       Jérôme Kieffer (Jerome.Kieffer@ESRF.eu)
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


__doc__ = """test module for pyFAI."""
__authors__ = ["Jérôme Kieffer", "Valentin Valls", "Henri Payno"]
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "07/02/2017"

import os
import shutil
import fileinput
try:  # Python3
    from urllib.request import urlopen, ProxyHandler, build_opener
except ImportError:  # Python2
    from urllib2 import urlopen, ProxyHandler, build_opener
import logging

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


class UtilsTest(object):
    """
    Static class providing useful stuff for preparing tests.
    """
    timeout = 100  # timeout in seconds for downloading datasets.tar.bz2
    url_base = "http://www.edna-site.org/pub/tomwer/"
    folderPath = "".join((os.path.dirname(__file__), '/datasets/'))
    archivename = "datasets.tar.bz2"
    archivefile = os.path.join(folderPath, archivename)

    def __init__(self):
        self.installed = False

    @classmethod
    def dataDownloaded(cls):
        return cls.dataIsHere() or cls.dataIsDownloaded()

    @classmethod
    def dataIsHere(cls):
        return os.path.isdir(cls.folderPath)

    @classmethod
    def dataIsDownloaded(cls):
        return os.path.isfile(cls.archivefile)

    @classmethod
    def getDataset(cls, folderID):
        path = os.path.abspath(os.path.join(cls.getDatasets(), folderID))
        if os.path.isdir(path):
            return path
        else:
            raise RuntimeError('Coul\'d find folder containing dataset %s' % folderID)

    @classmethod
    def getDatasets(cls):
        """
        Downloads the requested image from Forge.EPN-campus.eu

        @param: name of the image.
        For the RedMine forge, the filename contains a directory name that is removed
        @return: full path of the locally saved file
        """
        # download if needed
        if not cls.dataDownloaded():
            # create if needed path dataset
            print("Trying to download dataset %s, timeout set to %ss" % (cls.archivename, cls.timeout))
            logger.info("Trying to download dataset %s, timeout set to %ss",
                        cls.archivename, cls.timeout)
            dictProxies = {}
            if "http_proxy" in os.environ:
                dictProxies['http'] = os.environ["http_proxy"]
                dictProxies['https'] = os.environ["http_proxy"]
            if "https_proxy" in os.environ:
                dictProxies['https'] = os.environ["https_proxy"]
            if dictProxies:
                proxy_handler = ProxyHandler(dictProxies)
                opener = build_opener(proxy_handler).open
            else:
                opener = urlopen
            url = "%s/%s" % (cls.url_base, cls.archivename)
            logger.info("wget %s %s" % (url, cls.folderPath))
            print(url)
            data = opener(url, data=None, timeout=cls.timeout).read()
            logger.info("Image %s successfully downloaded." % cls.archivename)

            if not os.path.isdir(cls.folderPath):
                os.mkdir(cls.folderPath)

            try:
                with open(cls.archivefile, "wb") as outfile:
                    outfile.write(data)
            except IOError:
                raise IOError("unable to write downloaded \
                    data to disk at %s" % cls.folderPath)

            if not os.path.isfile(cls.archivefile):
                raise RuntimeError("Could not automatically \
                download test images %s!\n \ If you are behind a firewall, \
                please set both environment variable http_proxy and https_proxy.\
                This even works under windows ! \n \
                Otherwise please try to download the images manually from \n%s/%s" % (cls.archivename, cls.url_base, cls.archivename))

        # decompress if needed
        if os.path.isfile(cls.archivefile):
            logger.info("decompressing %s." % cls.archivefile)
            outdir = "".join((os.path.dirname(__file__)))
            shutil.unpack_archive(cls.archivefile, extract_dir=outdir, format='bztar')
            os.remove(cls.archivefile)
        else:
            logger.info("not trying to decompress it")

        return cls.folderPath

    def script_path(self, script_name, module_name):
        """Returns the script path according to it's location"""
        if self.installed:
            script = self.get_installed_script_path(script_name)
        else:
            import importlib
            module = importlib.import_module(module_name)
            script = module.__file__
        return script

