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
"""
Contains the python representation of the reconstruction parameters
"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "18/10/2017"


from ..unitsystem import metricsystem
from silx.io import configdict
import numpy
import time
try:
    from freeart import version
except:
    version = ''
from . import structs, fileInfo
import os


class _ReconsConfig(object):

    TX_ID = "Transmission"
    COMPTON_ID = "Compton"
    FLUO_ID = "Fluorescence"

    RECONS_TYPES = [TX_ID, COMPTON_ID, FLUO_ID]

    PRECISION_TO_TYPE = {
        'simple': numpy.float32,
        'double': numpy.float64
    }

    reconsParams = None
    """
    The reconstruction parameters (oversampling...) to launch once configured
    """

    def __init__(self, reconsType=None, minAngle=None, maxAngle=None,
                 projections=None, defReduction=1, projNumReduction=1,
                 oversampling=1, solidAngleOff=False,
                 includeLastProjection=True, I0=None, beamCalcMethod=0,
                 centerOfRotation=-1, acquiInverted=False, precision='double'):
        """

        :param reconsType:
        :param centerOfRotation: if -1 then will take the middle
        :param precision: calcul precision, can be simple or double.
        """
        if reconsType not in _ReconsConfig.RECONS_TYPES:
            raise ValueError('reconsType not recognized')
        if minAngle is not None and not (0 <= minAngle <= 2.*numpy.pi):
            raise ValueError('min angle not in [0, 2pi]')
        if minAngle is not None and not (0 <= maxAngle <= 2.*numpy.pi):
            raise ValueError('max angle not in [0, 2pi]')
        if (minAngle is not None or maxAngle is not None) and not minAngle <= maxAngle:
            raise ValueError('False condition: minAngle <= maxAngle')

        self.precision = precision
        assert self.precision in self.PRECISION_TO_TYPE
        self.reconsType = reconsType
        self.center = centerOfRotation
        self.projections = projections
        """The projections to be consider for the reconstruction"""
        self.definitionReduction = defReduction
        """
        Should we take a pixel each definition_reduction for the reconstruction
        """
        self.projectionNumberReduction = projNumReduction
        """
        Should we take one projection each projection_number_reduction for the
         reconstruction.
        """
        self.voxelSize = metricsystem.cm
        """voxel size"""
        self.oversampling = oversampling
        """Oversampling value"""
        self.solidAngleOff = solidAngleOff
        """Should we always set the the value of the solid angle to 1"""
        self.minAngle = minAngle
        self.maxAngle = maxAngle
        self.includeLastProjection = includeLastProjection
        self.setI0(I0)
        self.beamCalcMethod = beamCalcMethod
        self.acquiInverted = acquiInverted

    def setI0(self, I0, i0_index=None):
        if type(I0) is str or (hasattr(I0, 'dtype') and numpy.issubdtype(I0.dtype,
                                                                   numpy.character)):
            self._I0 = structs.I0Sinogram()
            fn, file_extension = os.path.splitext(str(I0).split('::')[0])
            if file_extension.lower() == '.edf':
                self._I0.fileInfo = fileInfo.EDFMatrixFileInfo(filePath=str(I0),
                                                               index=int(i0_index or 0))
            else:
                self._I0.fileInfo = fileInfo.H5MatrixFileInfo(
                    filePath=str(I0) + '::'+ str(i0_index or ''))
            self.useAFileForI0 = True
        elif isinstance(I0, structs.I0Sinogram):
            self._I0 = I0
            self.useAFileForI0 = True
        else:
            self._I0 = 1.0 if I0 is None else I0
            self.useAFileForI0 = False

    def getI0(self):
        return self._I0

    I0 = property(getI0, setI0)

    def toDict(self):
        """Convert the configuration to a silx ConfigDict"""
        dic = configdict.ConfigDict()
        dic['general_settings'] = self._getGeneralSettings()
        dic['normalization'] = self._getNormalization()
        dic['reconstruction_properties'] = self._getReconsProp()
        dic['reduction_data'] = self._getReductionDataInfo()
        dic['projection_information'] = self._getProjInfo()
        return dic

    def _getGeneralSettings(self):
        return {
            'reconstruction_type': self.reconsType,
            'date ': str(time.strftime("%d/%m/%Y")),
            'freeart_version': version,
            'precision': self.precision
        }

    def _getNormalization(self):
        if isinstance(self.I0, structs.DataStored):
            if self.I0.fileInfo is None:
                i0_out = ''
                i0_index = ''
            else:
                i0_out = self.I0.fileInfo.filePath
                i0_index = self.I0.fileInfo.location
        else:
            i0_out = self.I0
            i0_index = ''
        return {
            'rotation_center': self.center,
            'normalizationi0fromafile': self.useAFileForI0,
            'i0': i0_out,
            'i0_index': i0_index
        }

    def _getReconsProp(self):
        return {
            'voxel_size': self.voxelSize,
            'oversampling': self.oversampling,
            'bean_calculation_method': self.beamCalcMethod,
            'solid_angle_is_off': self.solidAngleOff,
            'include_last_angle': self.includeLastProjection
        }

    def _getReductionDataInfo(self):
        return {
            'definition_reducted_by': self.definitionReduction,
            'projection_number_reducted_by': self.projectionNumberReduction,
        }

    def _getProjInfo(self):
        return {
            'min_angle': self.minAngle,
            'max_angle': self.maxAngle,
            'projections_sel': self.projections or ':',
            'acqui_inv': self.acquiInverted
        }

    def _fromDict(self, dict):
        """set the configuration fron a silx ConfigDict"""
        self._setGenSettingFrmDict(dict)
        self._setNormalizationFrmDict(dict)
        self._setReconsPropFrmDict(dict)
        self._setReducDataFrmDict(dict)
        self._setProjInfoFrmDict(dict)
        return self

    def _setGenSettingFrmDict(self, dict):
        assert('general_settings' in dict)
        assert('reconstruction_type' in dict['general_settings'])
        self.reconsType = dict['general_settings']['reconstruction_type']
        if type(self.reconsType) is not str:
            self.reconsType = str(self.reconsType.tostring().decode())
        assert('precision' in dict['general_settings'])
        self.precision = dict['general_settings']['precision']
        if type(self.precision) is not str:
            self.precision = str(self.precision.tostring().decode())

    def _setNormalizationFrmDict(self, dict):
        assert('normalization' in dict)
        info = dict['normalization']
        assert('rotation_center' in info)
        assert('i0' in info)
        self.center = info['rotation_center']
        i0 = info['i0']
        if hasattr(i0, 'dtype') and not numpy.issubdtype(i0.dtype, numpy.number):
            i0 = str(i0.tostring().decode())
        i0_index = info['i0_index'] if 'i0_index' in info else None
        if hasattr(i0_index, 'dtype') and not numpy.issubdtype(i0_index.dtype, numpy.number):
            i0_index = str(i0_index.tostring().decode())

        self.setI0(i0, i0_index)

    def _setReconsPropFrmDict(self, dict):
        assert('reconstruction_properties' in dict)
        info = dict['reconstruction_properties']
        assert('voxel_size' in info)
        assert('oversampling' in info)
        assert('bean_calculation_method' in info)
        assert('solid_angle_is_off' in info)
        assert('include_last_angle' in info)
        self.voxelSize = float(info['voxel_size'])
        self.oversampling = int(info['oversampling'])
        self.beamCalcMethod = int(info['bean_calculation_method'])
        self.solidAngleOff = bool(info['solid_angle_is_off'])
        self.includeLastProjection = bool(info['include_last_angle'])

    def _setReducDataFrmDict(self, dict):
        assert('reduction_data' in dict)
        info = dict['reduction_data']
        assert('definition_reducted_by' in info)
        assert('projection_number_reducted_by' in info)
        self.definitionReduction = info['definition_reducted_by']
        self.projectionNumberReduction = info['projection_number_reducted_by']

    def _setProjInfoFrmDict(self, dict):
        assert('projection_information' in dict)
        info = dict['projection_information']
        assert('min_angle' in info)
        assert('max_angle' in info)
        assert('projections_sel' in info)
        assert('acqui_inv' in info)
        self.minAngle = info['min_angle']
        self.maxAngle = info['max_angle']
        self.projections = info['projections_sel']
        if not type(self.projections) is str:
            self.projections = str(self.projections.tostring().decode())
        self.acquiInverted = bool(info['acqui_inv'])

    def __eq__(self, other):
        projectionsAreEqual = self.projections == other.projections or \
            self.projections is None and other.projections == ':' or \
            self.projections == ':' and other.projections is None

        return self.reconsType == other.reconsType and \
               self.maxAngle == other.maxAngle and \
               self.minAngle == other.minAngle and \
               self.I0 == other.I0 and \
               self.center == other.center and \
               self.includeLastProjection == other.includeLastProjection and \
               self.useAFileForI0 == other.useAFileForI0 and \
               self.solidAngleOff == other.solidAngleOff and \
               self.beamCalcMethod == other.beamCalcMethod and \
               self.voxelSize == other.voxelSize and \
               self.definitionReduction == other.definitionReduction and \
               projectionsAreEqual and \
               self.projectionNumberReduction == other.projectionNumberReduction and \
               self.acquiInverted == other.acquiInverted and \
               self.precision == other.precision


    def __str__(self):
        res = 'reconsType is %s \n' % self.reconsType
        res = res + 'oversampling is %s \n' % self.oversampling
        res = res + 'minAngle is %s \n' % self.minAngle
        res = res + 'maxAngle is %s \n' % self.maxAngle
        res = res + 'I0 is %s \n' % self.I0
        res = res + 'center is %s \n' % self.center
        res = res + 'includeLastProjection is %s \n' % self.includeLastProjection
        res = res + 'useAFileForI0 is %s \n' % self.useAFileForI0
        res = res + 'solidAngleOff is %s \n' % self.solidAngleOff
        res = res + 'beamCalcMethod is %s \n' % self.beamCalcMethod
        res = res + 'voxelSize is %s \n' % self.voxelSize
        res = res + 'definitionReduction is %s \n' % self.definitionReduction
        res = res + 'projections is %s \n' % self.projections
        res = res + 'acquiInverted is %s \n' % self.acquiInverted
        res = res + 'projectionNumberReduction is %s \n' % self.projectionNumberReduction
        return res

    def setFileInfoToH5File(self, refFile, save=False):
        """
        Change all the fileInfo to point ot the given h5 file

        :param refFile: the h5 file to store information
        :param save: if true once the file info updated, save the dataset
        """
        assert fileInfo
        fn, file_extension = os.path.splitext(refFile)
        assert file_extension in ('.hdf5', '.hdf', '.h5')
        if self.I0 is not None and self.useAFileForI0 is True:
            self.I0.fileInfo = fileInfo.H5MatrixFileInfo(refFile + structs.I0Sinogram.I0_DATASET)
            if save is True:
                self.I0.save()


class _ItReconsConfig(_ReconsConfig):
    """Define parameters needed for an iterative reconstruction

    :param dampingFactor: if the dampingFactor is None then will be deduced
                          automatically
    """
    def __init__(self, dampingFactor=None, *var, **kw):
        _ReconsConfig.__init__(self, *var, **kw)
        self.dampingFactor = dampingFactor

    def _getReconsProp(self):
        dict = _ReconsConfig._getReconsProp(self)
        dict['relaxation_factor'] = self.dampingFactor
        return dict

    def _setReconsPropFrmDict(self, dict):
        _ReconsConfig._setReconsPropFrmDict(self, dict)
        assert('relaxation_factor' in dict['reconstruction_properties'])
        self.dampingFactor = dict['reconstruction_properties']['relaxation_factor']

    def __eq__(self, other):
        return _ReconsConfig.__eq__(self, other) and self.dampingFactor == other.dampingFactor


class _SimpleSinoConfig(_ItReconsConfig):
    def __init__(self, reconsType, sinograms=None, computeLog=True, *var, **kw):
        _ItReconsConfig.__init__(self, *var, reconsType=reconsType, **kw)
        self.sinograms = []
        if sinograms:
            for sinogram in sinograms:
                self.addSinogram(sinogram)

    def addSinogram(self, sinogram):
        if sinogram is None:
            return
        elif isinstance(sinogram, self._defaultSinoType()):
            _sinogram = sinogram
        # case of h5 file
        elif type(sinogram) is str or (hasattr(sinogram, 'dtype') and
                                           numpy.issubdtype(sinogram.dtype, numpy.character)):
            _sinogram = self._defaultSinoType()()
            # Raw check for hdf5 file
            if '::' in str(sinogram):
                _sinogram.fileInfo = fileInfo.H5MatrixFileInfo(
                    filePath=str(sinogram))
            else:
                _sinogram.fileInfo = fileInfo.EDFMatrixFileInfo(
                    filePath=str(sinogram))
        else:
            _sinogram = self._defaultSinoType()()
            _sinogram.data = sinogram

        self.sinograms.append(_sinogram)

    def _defaultSinoType(self):
        return structs.Sinogram

    def setFileInfoToH5File(self, refFile, save=False):
        """
        Change all the fileInfo to point ot the given h5 file

        :param refFile: the h5 file to store information
        :param save: if true once the file info updated, save the dataset
        """
        _ItReconsConfig.setFileInfoToH5File(self, refFile, save)
        if self._sinogram:
            self._sinogram.fileInfo = fileInfo.H5MatrixFileInfo(refFile + self._sinogram.h5defaultPath)
        if save is True:
            self._sinogram.save()

    def toDict(self):
        dic = _ItReconsConfig.toDict(self)
        dic[self._getDataSourceHeader()] = self._getDataSourceInfo()
        self._sinogramsToDict(dic)
        return dic

    def _sinogramsToDict(self, dic):
        sinogramsDict = self.getSinogramsFileDict()
        iSinoFile = 0
        for iSinoFile, sinoFile in enumerate(sinogramsDict):
            index = 0
            section = 'sino_file_' + str(iSinoFile)
            dic[section] = {}
            dic[section]['file_path'] = sinoFile
            for sinogram in sinogramsDict[sinoFile]:
                assert(isinstance(sinogram, self._defaultSinoType()))
                fi = ''
                fp = ''
                if sinogram.fileInfo is not None:
                    fp = sinogram.fileInfo.filePath
                    fi = sinogram.fileInfo.location
                    dic[section]['sino_file_' + str(index)] = fp
                    dic[section]['sino_file_index_' + str(index)] = fi
                    dataNameID = 'data_name_' + str(index)
                    dic[section][dataNameID] = sinogram.name
                    index += 1
        return dic

    def _getDataSourceHeader(self):
        return 'data_source_tx'

    def _getDataSourceInfo(self):
        return {}

    def _fromDict(self, dict):
        _ItReconsConfig._fromDict(self, dict)
        self._sinogramsFromDict(dict)
        return self

    def _sinogramsFromDict(self, dict):
        iFile = 0
        section = 'sino_file_' + str(iFile)
        while section in dict:
            info = dict[section]
            filePath = info['file_path']
            if hasattr(filePath, 'tostring'):
                filePath = str(info['file_path'].tostring().decode())

            index = 0
            info = dict[section]
            while ('sino_file_' + str(index) in info):
                file = info['sino_file_' + str(index)]
                location = info['sino_file_index_' + str(index)]

                if not type(file) is str:
                    file = str(file.tostring().decode())

                if hasattr(location, 'dtype') and \
                        not numpy.issubdtype(location.dtype, numpy.number):
                    location = str(location.tostring().decode())
                fi = retrieveInfoFile(file=file, index=location)

                dataNameID = 'data_name_' + str(index)
                name = info[dataNameID]
                if hasattr(name, 'astype'):
                    name = str(name.astype('U13'))

                self.addSinogram(sinogram=structs.TxSinogram(fileInfo=fi,
                                                             name=name))
                index += 1
            iFile += 1
            section = 'sino_file_' + str(iFile)

    def __eq__(self, other):
        return _ItReconsConfig.__eq__(self, other) and \
               self.getSinogramsFileDict() == other.getSinogramsFileDict()

    def checkSinoType(self, sino):
        assert(isinstance(sino, structs.Sinogram))

    def getSinogramsFileDict(self):
        """
        return the sinograms as a dictionnary with key the file containing the
        sinograms and values the list of sinograms in this file

        :return: dict
        """
        dd = {}
        for sinogram in self.sinograms:
            filePath = 'unknow'
            if sinogram.fileInfo and sinogram.fileInfo.getFile():
                filePath = sinogram.fileInfo.getFile()
            if filePath not in dd:
                dd[filePath] = []
            dd[filePath].append(sinogram)
        import collections
        sortedDict = collections.OrderedDict(sorted(dd.items()))
        return sortedDict

    def fillSinogramNames(self):
        # if no name define, define one for each sinogram
        if self.sinograms is not None:
            index = 0
            for sinogram in self.sinograms:
                if sinogram.name is None:
                    sinogram.name = 'sinogram_' + str(index)
                    index += 1


class TxConfig(_SimpleSinoConfig):
    """

    .. note:: Need to get a differentiation between TxConfig and this class
              because tomogui has also to deal with the FBP... and won't have the log
              option and maybe others
    """
    def __init__(self, sinograms=None, computeLog=True, *var, **kw):
        _SimpleSinoConfig.__init__(self, reconsType=self.TX_ID,
                                   sinograms=sinograms, *var, **kw)
        self.computeLog = computeLog

    def _setNormalizationFrmDict(self, dict):
        _SimpleSinoConfig._setNormalizationFrmDict(self, dict)
        assert('normalization' in dict)
        info = dict['normalization']
        assert('computeminuslog' in info)
        self.computeLog = info['computeminuslog']

    def _getNormalization(self):
        dic = _SimpleSinoConfig._getNormalization(self)
        dic['computeminuslog'] = self.computeLog
        return dic

    def __eq__(self, other):
        return _SimpleSinoConfig.__eq__(self, other) and \
               self.computeLog == other.computeLog


class FluoConfig(_SimpleSinoConfig):
    """
    configuration to build fluorescence or compton reconstruction algorithm
    """
    def __init__(self, outBeamCalMethod=0, sinoI0=None, absMat=None,
                 isAbsMatASinogram=False, detector=None, materials=None,
                 sinograms=None, e0=1, *var, **kw):
        _SimpleSinoConfig.__init__(self, reconsType=self.FLUO_ID, *var, **kw)
        assert(absMat is None or isinstance(absMat, structs.AbsMatrix))
        self.absMat = absMat
        if self.absMat is None:
            self.absMat = structs.AbsMatrix()

        self.sinoI0 = sinoI0
        self.isAbsMatASinogram = isAbsMatASinogram

        assert(materials is None or isinstance(materials, structs.Materials))
        self.materials = materials
        if self.materials is None:
            self.materials = structs.Materials()
        self.detector = detector
        self.outBeamCalMethod = outBeamCalMethod
        self.E0 = e0

    def _defaultSinoType(self):
        return structs.FluoSino

    def _getDataSourceHeader(self):
        return 'data_source_fluo'

    def toDict(self):
        dic = _SimpleSinoConfig.toDict(self)
        dic['detector_setup'] = self._getDetector()
        return dic

    def _sinogramsToDict(self, dic):
        # deal with all fluorescence sinogram
        sinogramsDict = self.getSinogramsFileDict()
        for iSinoFile, sinoFile in enumerate(sinogramsDict):
            section = 'fluo_sino_file_' + str(iSinoFile)
            dic[section] = {}
            dic[section]['file_path'] = sinoFile

            indexSino = 0
            for sino in sinogramsDict[sinoFile]:
                indexID = 'data_set_index_' + str(indexSino)
                loc = ''
                if sino.fileInfo:
                    loc = sino.fileInfo.location
                dic[section][indexID] = loc

                dataNameID = 'data_name_' + str(indexSino)
                dic[section][dataNameID] = sino.name

                dataPhysElmtID = 'data_physical_element_' + str(indexSino)
                dic[section][dataPhysElmtID] = sino.physElmt

                EFID = 'ef_' + str(indexSino)
                dic[section][EFID] = sino.EF

                selfAbsMatID = 'self_absorption_file_' + str(indexSino)
                selfAbsMatIndexID = 'self_absorption_index_file_' + str(indexSino)

                if sino.selfAbsMat is None:
                    dic[section][selfAbsMatID] = ''
                else:
                    assert(isinstance(sino.selfAbsMat, structs.AbsMatrix))
                    assert(sino.selfAbsMat.fileInfo is not None)
                    dic[section][selfAbsMatID] = sino.selfAbsMat.fileInfo.getFile()
                    dic[section][selfAbsMatIndexID] = sino.selfAbsMat.fileInfo.location

                indexSino += 1

        return dic

    def _fromDict(self, dict):
        _SimpleSinoConfig._fromDict(self, dict)
        assert('detector_setup' in dict)
        info = dict['detector_setup']
        assert('det_width' in info)
        assert('det_pos_x' in info)
        assert('det_pos_y' in info)
        assert('det_pos_z' in info)

        self.detector = structs.Detector(x=info['det_pos_x'],
                                         y=info['det_pos_y'],
                                         z=info['det_pos_z'],
                                         width=info['det_width'])

        # deal with data_source_fluo
        assert('data_source_fluo' in dict)
        info = dict['data_source_fluo']
        self.isAbsMatASinogram = bool(info['absorption_file_is_a_sinogram'])
        absMat = info['absorption_file']
        if not type(absMat) is str:
            absMat = str(absMat.tostring().decode())
        absMat_index = info['absorption_file_index']
        if hasattr(absMat_index, 'dtype') and not numpy.issubdtype(absMat_index.dtype, numpy.number):
            absMat_index = str(absMat_index.tostring().decode())

        info_file_abs_mat = retrieveInfoFile(file=absMat,
                                             index=absMat_index)
        self.absMat = structs.AbsMatrix(fileInfo=info_file_abs_mat)

        materialCompoFile = info['samp_composition_file']
        if not type(materialCompoFile) is str:
            materialCompoFile = str(info['samp_composition_file'].tostring().decode())
        materialCompoIndex = info['samp_composition_file_index']
        if hasattr(materialCompoIndex, 'dtype') and not numpy.issubdtype(materialCompoIndex.dtype, numpy.number):
            materialCompoIndex = str(materialCompoIndex.tostring().decode())
        info_file_comp = retrieveInfoFile(file=materialCompoFile,
                                          index=materialCompoIndex)

        materialsFile = info['materials_file']
        if not type(materialsFile) is str:
            materialsFile = str(info['materials_file'].tostring().decode())
        materialsIndex = info['materials_file_index']
        if hasattr(materialsIndex, 'dtype') and not numpy.issubdtype(materialsIndex.dtype, numpy.number):
            materialsIndex = str(materialsIndex.tostring().decode())
        info_file_mat_dic = retrieveInfoFile(file=materialsFile,
                                             index=materialsIndex)

        self.materials = structs.Materials(
            materials=structs.MaterialsDic(fileInfo=info_file_mat_dic),
            matComposition=structs.MatComposition(fileInfo=info_file_comp))

        return self

    def _sinogramsFromDict(self, dict):
        # deal with all fluorescence sinogram
        iFile = 0
        section = 'fluo_sino_file_' + str(iFile)
        while section in dict:
            info = dict[section]
            filePath = info['file_path']
            if hasattr(filePath, 'tostring'):
                filePath = str(info['file_path'].tostring().decode())

            indexSino = 0
            indexID = 'data_set_index_' + str(indexSino)
            sinogramsToAdd = []
            while indexID in info:
                dataNameID = 'data_name_' + str(indexSino)
                dataPhysElmtID = 'data_physical_element_' + str(indexSino)
                EFID = 'ef_' + str(indexSino)
                selfAbsMatID = 'self_absorption_file_' + str(indexSino)
                selfAbsMatIndexID = 'self_absorption_index_file_' + str(indexSino)
                index = info[indexID]
                if hasattr(index, 'dtype') and not numpy.issubdtype(
                        index.dtype, numpy.number):
                    index = str(index.tostring().decode())
                # deal with sinogram
                file_info = retrieveInfoFile(filePath, index)
                selfAbsMat = structs.SelfAbsMatrix(fileInfo=file_info)

                # deal with selfAbsMat
                selfAbsMatFile = info[selfAbsMatID] if selfAbsMatID in info else None
                if hasattr(selfAbsMatFile, 'tostring'):
                    selfAbsMatFile = str(selfAbsMatFile.tostring().decode())

                selfAbsMatIndex = info[selfAbsMatIndexID] if selfAbsMatIndexID in info else None
                if hasattr(selfAbsMatIndex, 'dtype') and not numpy.issubdtype(
                        selfAbsMatIndex.dtype, numpy.number):
                    selfAbsMatIndex = str(selfAbsMatIndex.tostring().decode())

                selfAbsMatFileInfo = None
                if selfAbsMatFile is None or selfAbsMatFile == '' or ord(selfAbsMatFile[0]) == 0:
                    selfAbsMat = None
                else:
                    selfAbsMat = structs.SelfAbsMatrix(
                        fileInfo=retrieveInfoFile(file=selfAbsMatFile,
                                                  index=selfAbsMatIndex))

                name = info[dataNameID]
                if hasattr(name, 'astype'):
                    name = str(name.astype('U13'))
                physElmt = info[dataPhysElmtID]
                if hasattr(physElmt, 'astype'):
                    physElmt = str(physElmt.astype('U13'))
                # create the fluorescence sinogram
                self.addSinogram(structs.FluoSino(name=name,
                                                  fileInfo=file_info,
                                                  physElmt=physElmt,
                                                  ef=info[EFID],
                                                  selfAbsMat=selfAbsMat))
                indexSino += 1
                indexID = 'data_set_index_' + str(indexSino)
            iFile += 1
            section = 'fluo_sino_file_' + str(iFile)

    def _getDataSourceInfo(self):
        assert(type(self.isAbsMatASinogram) is bool)
        compoFile = compoFileIndex = matFile = matFileIndex = None
        if self.materials is not None:
            if self.materials.matComposition is not None:
                if self.materials.matComposition.fileInfo is not None:
                    compoFile = self.materials.matComposition.fileInfo.getFile()
                    assert (isinstance(self.materials.matComposition, structs.MatComposition))
                    if isinstance(self.materials.matComposition.fileInfo, fileInfo.EDFMatrixFileInfo):
                        compoFileIndex = self.materials.matComposition.fileInfo.getIndex()
                    elif isinstance(self.materials.matComposition.fileInfo, fileInfo.H5MatrixFileInfo):
                        compoFileIndex = self.materials.matComposition.fileInfo.getH5Location()
                elif self.materials.matComposition.data is not None:
                    compoFile = ''
                    compoFileIndex = self.materials.matComposition.h5defaultPath

            if self.materials.materials is not None:
                if self.materials.materials.fileInfo is not None:
                    assert(isinstance(self.materials.materials, structs.MaterialsDic))
                    assert(isinstance(self.materials.materials.fileInfo, fileInfo.MatrixFileInfo))
                    matFile = self.materials.materials.fileInfo.getFile()
                    if isinstance(self.materials.materials.fileInfo, fileInfo.EDFMatrixFileInfo):
                        matFileIndex = self.materials.materials.fileInfo.getIndex()
                    elif isinstance(self.materials.materials.fileInfo, fileInfo.H5MatrixFileInfo):
                        matFileIndex = self.materials.materials.fileInfo.getH5Location()
                elif self.materials.materials.data is not None:
                    matFile = ''
                    matFileIndex = self.materials.materials.h5defaultPath

        absMatIndex = ''
        absMatFile = ''
        if self.absMat is not None and self.absMat.fileInfo is not None and \
            self.absMat.fileInfo.filePath is not None:
            absMatFile = self.absMat.fileInfo.getFile()
            if isinstance(self.absMat.fileInfo, fileInfo.EDFMatrixFileInfo):
                absMatIndex = self.absMat.fileInfo.getIndex()
            elif isinstance(self.absMat.fileInfo, fileInfo.H5MatrixFileInfo):
                absMatIndex = self.absMat.fileInfo.getH5Location()

        return {
            'absorption_file_is_a_sinogram': self.isAbsMatASinogram,
            'absorption_file': absMatFile,
            'absorption_file_index': absMatIndex,
            'samp_composition_file': compoFile or '',
            'samp_composition_file_index': compoFileIndex or '',
            'materials_file': matFile or '',
            'materials_file_index': matFileIndex or ''
        }

    def _getReconsProp(self):
        dic = _ItReconsConfig._getReconsProp(self)
        dic['outgoing_bean_calculation_method'] = self.outBeamCalMethod or 0
        dic['e0'] = self.E0
        return dic

    def _setReconsPropFrmDict(self, dict):
        _ItReconsConfig._setReconsPropFrmDict(self, dict)
        assert('outgoing_bean_calculation_method' in dict['reconstruction_properties'])
        self.outBeamCalMethod = dict['reconstruction_properties']['outgoing_bean_calculation_method']
        assert('e0' in dict['reconstruction_properties'])
        self.E0 = dict['reconstruction_properties']['e0']

    def _getDetector(self):
        if self.detector is None:
            return structs.Detector(x=None,
                                    y=None,
                                    z=None,
                                    width=None).toDict()
        else:
            return self.detector.toDict()

    def setFileInfoToH5File(self, refFile, save=False):
        """
        Change all the fileInfo to point ot the given h5 file

        :param refFile: the h5 file to store information
        :param save: if true once the file info updated, save the dataset
        """
        def dealWithSinograms():
            if self.sinograms:
                sinograms = []
                for sino in self.sinograms:
                    sino.fileInfo = fileInfo.H5MatrixFileInfo(
                        refFile + sino.h5defaultPath)
                    if save is True:
                        sino.save()
                    if sino.selfAbsMat:
                        sino.selfAbsMat.fileInfo = fileInfo.H5MatrixFileInfo(
                            refFile + sino.selfAbsMat.h5defaultPath)
                        if save is True:
                            sino.selfAbsMat.save()
                sinograms.append(sino)
                self.sinograms = sinograms

        def dealWithMaterials():
            if self.materials:
                if self.materials.materials:
                    self.materials.materials.fileInfo = fileInfo.H5MatrixFileInfo(
                        refFile + self.materials.materials.h5defaultPath)
                    if save is True:
                        self.materials.materials.save()
                if self.materials.matComposition:
                    self.materials.matComposition.fileInfo = fileInfo.H5MatrixFileInfo(
                        refFile + self.materials.matComposition.h5defaultPath)
                    if save is True:
                        self.materials.matComposition.save()

        def dealWithAbsMat():
            if self.absMat:
                self.absMat.fileInfo = fileInfo.H5MatrixFileInfo(
                    refFile + self.absMat.h5defaultPath)
                if save is True:
                    self.absMat.save()

        _ItReconsConfig.setFileInfoToH5File(self, refFile, save)
        dealWithSinograms()
        dealWithMaterials()
        dealWithAbsMat()

    def __eq__(self, other):
        return _SimpleSinoConfig.__eq__(self, other) and \
               self.materials == other.materials and \
               self.detector == other.detector and \
               self.absMat == other.absMat and \
               self.sinoI0 == other.sinoI0 and \
               self.isAbsMatASinogram == other.isAbsMatASinogram

    def __str__(self):
        l = _ItReconsConfig.__str__(self)
        l += 'outgoing beam calculation meth = %s\n' % self.outBeamCalMethod
        l += str(self.materials)
        return l

    def checkSinoType(self, sino):
        assert(isinstance(sino, structs.FluoSino))


def retrieveInfoFile(file, index):
    """Simple function to get the adapted infoFile from a file and
    an index

    :param file: the file storing the data
    :param index: int or str location of the data in the file
    """
    assert type(file) is str
    if file == '' or file is None or ord(file[0]) == 0:
        return None
    assert(type(file) is str)
    info_file = None
    if file.lower().endswith('.h5') or file.lower().endswith('.hdf5'):
        fp = str(file) + '::' + str(index)
        info_file = fileInfo.H5MatrixFileInfo(filePath=fp)
    elif file.lower().endswith('.npy') or file.lower().endswith('.dict') or file.lower().endswith('.ini'):
        info_file = fileInfo.MatrixFileInfo(filePath=file)
    elif file.lower().endswith('.edf'):
        if index == '' or index is None:
            _index = 0
        else:
            _index = int(index)
        info_file = fileInfo.EDFMatrixFileInfo(
            filePath=str(file),
            index=int(_index))
    else:
        raise ValueError('extension not managed (%s)' % os.path.basename(file))
    return info_file
