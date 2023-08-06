# coding: utf-8
from __future__ import division
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

__author__ = ["P. Paleo", "H. Payno"]
__license__ = "MIT"
__date__ = "12/05/2016"


import numpy as np
from math import pi
from silx.math.fit import leastsq, CPOSITIVE


def rescale_intensity(img, from_subimg=None, percentiles=None):
    if percentiles is None: percentiles = [2, 98]
    data = from_subimg if from_subimg is not None else img
    imin, imax = np.percentile(data, percentiles)
    res = np.clip(img, imin, imax)
    return res


def enhance_contrast(img, bins=256, levels=None, fromregion=None,
                     from_cdf=None, return_cdf=False):
    """
    Enhance the contrast of an image by equalizing the histogram.
    Code from scikit image:
    github.com/scikit-image/scikit-image/blob/master/skimage/exposure/exposure.py

    :param numpy.ndarray img: Input image
    :param int bins:
    :param int levels:
    :param np.ndarray fromregion: optional. if provided, the contrast is
                                  enhanced based on an image sub-region.
    """
    normalization = img.max() if levels is None else levels-1
    img = img.astype(np.float64)
    # Normalize temp. image to 0-1
    img = (img-img.min())/(img.max()-img.min())
    if fromregion is not None:
        from_img = fromregion
    else: from_img = img
    if from_cdf is None:
        hist, bin_edges = np.histogram(from_img, bins)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.
        img_cdf = hist.cumsum()
        img_cdf = img_cdf / float(img_cdf[-1])
    else: # use a provided cdf
        img_cdf, bin_centers = from_cdf
    """
    The interpolating function is the cdf.
    Considering the plot of cdf (0... levels-1) against the bins "Bins"
    (vmin=Bins[0], ..., vmax=Bins[-1]),
    given an input image value "v", find the new value
    1) find index "i" in "Bins" such that Bins[i] == v
      Bins = vmin+delta/2 + k*delta   where delta=(vmax-vmin)/nbins
      i = (v - vmin)*nbins/(vmax-vmin)
    2) v_new = cdf[i]
    delta = (vmax-vmin*1.0)/bins
    i = (img - vmin)/delta-0.5


    res = cdf[np.int64(i)] # ceil to 0, floor to 255
    However, this is not accurate since values do not fall exactly in a bin
    center.
    Instead, an interpolation is used :
    """
    out = np.interp(img.flat, bin_centers, img_cdf)
    out = out.reshape(img.shape)*normalization
    if return_cdf:
        return out, img_cdf, bin_centers
    else:
        return out


#
# These functions might be moved to silx.math, or something like silx.tomography
#


# TODO: apodization to dampen the sinogram borders
def calc_center_corr(sino, fullrot=False, props=1):
    """
    Compute a guess of the Center of Rotation (CoR) of a given sinogram.
    The computation is based on the correlation between the line projections at
    angle (theta = 0) and at angle (theta = 180).

    Note that for most scans, the (theta=180) angle is not included,
    so the CoR might be underestimated.
    In a [0, 360[ scan, the projection angle at (theta=180) is exactly in the
    middle for odd number of projections.

    :param sino: numpy.ndarray Sinogram
    :param boolean fullrot: optional. If False (default), the scan is assumed
                           to be [0, 180). If True, the scan is assumed to be
                           [0, 380].
    :param int props: optional. Number of propositions for the CoR
    """

    n_a, n_d = sino.shape
    first = 0
    last = -1 if not(fullrot) else n_a//2
    proj1 = sino[first, :]
    proj2 = sino[last, :][::-1]

    # Compute the correlation in the Fourier domain
    proj1_f = np.fft.fft(proj1, 2*n_d)
    proj2_f = np.fft.fft(proj2, 2*n_d)
    corr = np.abs(np.fft.ifft(proj1_f * proj2_f.conj()))

    if props == 1:
        pos = np.argmax(corr)
        if pos > n_d//2:
            pos -= n_d
        return (n_d + pos)/2.
    else:
        corr_argsorted = np.argsort(corr)[:props]
        corr_argsorted[corr_argsorted > n_d//2] -= n_d
        return (n_d + corr_argsorted)/2.


def _sine_function(t, offset, amplitude, phase):
    """
    Helper function for calc_center_centroid
    """
    #~ t = np.linspace(0, n_angles, n_angles, False)
    n_angles = t.shape[0]
    return offset + amplitude * np.sin(2*pi*(1./(2*n_angles))*t + phase)


def _sine_function_derivative(t, params, eval_idx):
    """
    Helper function for calc_center_centroid
    """
    offset, amplitude, phase = params
    n_angles = t.shape[0]
    w = 2*pi*(1./(2*n_angles))*t + phase
    grad = (1.0, np.sin(w), amplitude*np.cos(w))
    return grad[eval_idx]


def calc_center_centroid(sino, debug=False):
    """
    Compute a guess of the Center of Rotation (CoR) of a given sinogram.
    The computation is based on the computation of the centroid of each
    projection line, which should be a sine function according to the
    Helgason-Ludwig condition.
    This method is unlikely to work in local tomography.

    Parameters
    ----------
    sino: numpy.ndarray
        Sinogram
    debug: bool, optional
        If True, plots the fit of the centroids with a sine function
    """

    n_a, n_d = sino.shape
    # Compute the vector of centroids of the sinogram
    i = np.arange(n_d)
    centroids = np.sum(sino*i, axis=1)/np.sum(sino, axis=1)

    # Fit with a sine function : phase, amplitude, offset
    # Using non-linear Levenberg–Marquardt  algorithm
    angles = np.linspace(0, n_a, n_a, True)
    # Initial parameter vector
    cmax, cmin = centroids.max(), centroids.min()
    offs = (cmax + cmin)/2.
    amp = (cmax - cmin)/2.
    phi = 1.1
    p0 = (offs, amp, phi)

    if debug:
        import matplotlib.pyplot as plt
        plt.figure()
        plt.plot(angles, centroids)
        plt.show()

    constraints = np.zeros((3, 3))
    #~ constraints[0][0] = CPOSITIVE # offset should be positive

    popt, _ = leastsq(_sine_function,
                      angles,
                      centroids,
                      p0,
                      sigma=None,
                      constraints=constraints,
                      model_deriv=None,
                      epsfcn=None,
                      deltachi=None,
                      full_output=0,
                      check_finite=True,
                      left_derivative=False,
                      max_iter=100)
    return popt[0]
