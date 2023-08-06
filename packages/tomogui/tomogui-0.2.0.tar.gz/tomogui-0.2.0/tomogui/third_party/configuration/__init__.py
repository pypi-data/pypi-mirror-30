# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2015-2016 European Synchrotron Radiation Facility
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
configuration used to run freeart reconstruction.
The interpreter will have an instance of :class:`_ReconsConfig` which can either
be a :class:`TxConfig` or a :class:`FluoConfig`

Those classes can saved and read to configuration files.
freeart is using a `silx.io.dictdump.DictDump` object. So those configuration
can be saved into (.ini, .cfg, .h5) files.
To save them you simply have to call :meth:`save` and :meth:`read` to load them.

Transmission configuration
--------------------------

This is an example of a configuration file (.cfg) and what are the main
parameters.

.. code-block:: txt

    [general_settings]
    date  = 14/11/2017
    reconstruction_type = Transmission
    freeart_version = 3.0.0
    precision = simple

    [normalization]
    i0 = 1.0
    i0_index = 
    rotation_center = 327
    computeminuslog = True
    normalizationi0fromafile = False

    [reconstruction_properties]
    include_last_angle = False
    solid_angle_is_off = False
    voxel_size = 1.0
    oversampling = 2
    relaxation_factor = 0.00311526479751
    bean_calculation_method = 0

    [reduction_data]
    definition_reducted_by = 1
    projection_number_reducted_by = 1

    [projection_information]
    projections_sel = 0:321
    acqui_inv = False
    min_angle = 0.0
    max_angle = 6.28318530718

    [data_source_tx]
    sino_file = /users/toto/sinogram.edf
    sino_file_index = 0


Fluorescence configuration
--------------------------

This is an example of a configuration file (.cfg) and what are the main
parameters.


.. code-block:: txt

    [general_settings]
    date  = 14/11/2017
    reconstruction_type = Fluorescence
    freeart_version = 3.0.0
    precision = double

    [normalization]
    i0 = 1.0
    i0_index =
    rotation_center =
    normalizationi0fromafile = False

    [reconstruction_properties]
    include_last_angle = False
    solid_angle_is_off = False
    voxel_size = 1.0
    oversampling = 2
    relaxation_factor = 0.00311526479751
    bean_calculation_method = 0
    e0 = 1.0
    outgoing_bean_calculation_method = 0

    [reduction_data]
    definition_reducted_by = 1
    projection_number_reducted_by = 1

    [projection_information]
    projections_sel = :
    acqui_inv = False
    min_angle = 0.0
    max_angle = 6.28318530718

    [detector_setup]
    det_pos_x = 1000.0
    det_pos_y = 1000.0
    det_pos_z = 0.0
    det_width = 1.0

    [data_source_fluo]
    materials_file =
    absorption_file = absorptionMatrix.edf
    samp_composition_file =
    absorption_file_is_a_sinogram = False
    samp_composition_file_index =
    absorption_file_index = 0
    materials_file_index =

    [fluo_sino_file_0]
    self_absorption_file_0 = absorptionFile.edf
    data_set_index_0 = 0
    data_name_0 = \0
    data_physical_element_0 = H
    ef_0 = 1.0
    file_path = fluoSinogram.edf


.. note:: In order to generate for configuration file you can use tomogui (http://gitlab.esrf.fr/tomoTools/tomogui)

"""

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "30/10/2017"

from .h5ConfigIO import H5ConfigReader, H5ConfigWriter
from .iniConfigIO import IniConfigReader, IniConfigWriter
import os


INI_FILE_EXT = '.cfg', '.ini'
"""Extension compatible with the dict dump"""

HDF5_FILE_EXT = '.h5', '.hdf5'
"""Valid file extension for hdf5"""


def read(filePath):
    """
    Read the configuration stored in the given file path

    :param filePath: file to read
    :return: the object containing the information for the reconstruction
    :rtype: _ReconsConfig instance
    """
    assert os.path.isfile(filePath)
    fn, file_extension = os.path.splitext(filePath)
    if file_extension in INI_FILE_EXT:
        reader = IniConfigReader()
    elif file_extension in HDF5_FILE_EXT:
        reader = H5ConfigReader()
    else:
        raise IOError('File extension not managed, can\'t read the file')

    return reader.read(filePath)


def save(configuration, filePath, overwrite=False, merge=False):
    """
    save the given configuration into the given filePath

    :param configuration: the configuration to write
    :param filePath: storage location
    """
    if filePath.lower().endswith(INI_FILE_EXT):
        writer = IniConfigWriter()
    elif filePath.lower().endswith(HDF5_FILE_EXT):
        writer = H5ConfigWriter()
    else:
        raise IOError('File extension not managed, can\'t write the file')
    writer.write(filePath=filePath, reconsConfiguration=configuration,
                 overwrite=overwrite, merge=merge)
