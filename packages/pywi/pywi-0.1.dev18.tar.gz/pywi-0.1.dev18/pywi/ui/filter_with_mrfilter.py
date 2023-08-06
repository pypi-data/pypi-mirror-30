#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Jérémie DECOCK (http://www.jdhp.org)

# This script is provided under the terms and conditions of the MIT license:
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
Denoise FITS images with Wavelet Transform.

This script use mr_filter -- a program written CEA/CosmoStat
(www.cosmostat.org) -- to make Wavelet Transform.

Usage
-----

::

    filter_with_mrfilter.py [-h] [--type-of-filtering INTEGER]
                                 [--coef-detection-method INTEGER]
                                 [--type-of-multiresolution-transform INTEGER]
                                 [--type-of-filters INTEGER]
                                 [--type-of-non-orthog-filters INTEGER]
                                 [--noise-model INTEGER]
                                 [--number-of-scales integer]
                                 [--k-sigma-noise-threshold FLOAT]
                                 [--number-of-iterations integer] [--epsilon FLOAT]
                                 [--support-file-name FILE]
                                 [--suppress-isolated-pixels]
                                 [--kill-isolated-pixels] [--suppress-last-scale]
                                 [--detect-only-positive-structure]
                                 [--precision FLOAT]
                                 [--first-detection-scale INTEGER]
                                 [--suppress-positivity-constraint]
                                 [--maximum-level-constraint]
                                 [--mask-file-path MASK_FILE_NAME]
                                 [--offset-after-calibration FLOAT]
                                 [--correction-offset]
                                 [--input-image-scale INPUT_IMAGE_SCALE]
                                 [--noise-cdf-file FILE] [--tmp-dir DIRECTORY]
                                 [--verbose] [--debug] [--max-images INTEGER]
                                 [--telid INTEGER] [--eventid INTEGER]
                                 [--camid STRING] [--benchmark STRING]
                                 [--label STRING] [--plot] [--saveplot FILE]
                                 [--output FILE]
                                 FILE [FILE ...]
    
    Denoise images with Wavelet Transform.
    
    positional arguments:
      FILE                  The files image to process. If fileargs is a
                            directory, all files it contains are processed.
    
    optional arguments:
      -h, --help            show this help message and exit
      --type-of-filtering INTEGER, -f INTEGER
                            Type of filtering: 1: Multiresolution Hard K-Sigma
                            Thresholding 2: Multiresolution Soft K-Sigma
                            Thresholding 3: Iterative Multiresolution Thresholding
                            4: Adjoint operator applied to the multiresolution
                            support 5: Bivariate Shrinkage 6: Multiresolution
                            Wiener Filtering 7: Total Variation + Wavelet
                            Constraint 8: Wavelet Constraint Iterative Methods 9:
                            Median Absolute Deviation (MAD) Hard Thesholding 10:
                            Median Absolute Deviation (MAD) Soft Thesholding.
                            Default=1.
      --coef-detection-method INTEGER, -C INTEGER
                            Coef_Detection_Method: 1: K-SigmaNoise Threshold 2:
                            False Discovery Rate (FDR) Theshold 3: Universal
                            Threshold 4: SURE Threshold 5: Multiscale SURE
                            Threshold. Default=1.
      --type-of-multiresolution-transform INTEGER, -t INTEGER
                            Type of multiresolution transform: 1: linear wavelet
                            transform: a trous algorithm 2: bspline wavelet
                            transform: a trous algorithm 3: wavelet transform in
                            Fourier space 4: morphological median transform 5:
                            morphological minmax transform 6: pyramidal linear
                            wavelet transform 7: pyramidal bspline wavelet
                            transform 8: pyramidal wavelet transform in Fourier
                            space: algo 1 (diff. between two resolutions) 9:
                            Meyer's wavelets (compact support in Fourier space)
                            10: pyramidal median transform (PMT) 11: pyramidal
                            laplacian 12: morphological pyramidal minmax transform
                            13: decomposition on scaling function 14: Mallat's
                            wavelet transform (7/9 filters) 15: Feauveau's wavelet
                            transform 16: Feauveau's wavelet transform without
                            undersampling 17: Line Column Wavelet Transform
                            (1D+1D) 18: Haar's wavelet transform 19: half-
                            pyramidal transform 20: mixed Half-pyramidal WT and
                            Median method (WT-HPMT) 21: undecimated diadic wavelet
                            transform (two bands per scale) 22: mixed WT and PMT
                            method (WT-PMT) 23: undecimated Haar transform: a
                            trous algorithm (one band per scale) 24: undecimated
                            (bi-) orthogonal transform (three bands per scale) 25:
                            non orthogonal undecimated transform (three bands per
                            scale) 26: Isotropic and compact support wavelet in
                            Fourier space 27: pyramidal wavelet transform in
                            Fourier space: algo 2 (diff. between the square of two
                            resolutions) 28: Fast Curvelet Transform. Default=2.
      --type-of-filters INTEGER, -T INTEGER
                            Type of filters: 1: Biorthogonal 7/9 filters 2:
                            Daubechies filter 4 3: Biorthogonal 2/6 Haar filters
                            4: Biorthogonal 2/10 Haar filters 5: Odegard 9/7
                            filters 6: 5/3 filter 7: Battle-Lemarie filters (2
                            vanishing moments) 8: Battle-Lemarie filters (4
                            vanishing moments) 9: Battle-Lemarie filters (6
                            vanishing moments) 10: User's filters 11: Haar filter
                            12: 3/5 filter 13: 4/4 Linar spline filters 14:
                            Undefined sub-band filters. Default=1.
      --type-of-non-orthog-filters INTEGER, -U INTEGER
                            Type of non-orthogonal filters: 1: SplineB3-Id+H:
                            H=[1,4,6,4,1]/16, Ht=H, G=Id-H, Gt=Id+H 2:
                            SplineB3-Id: H=[1,4,6,4,1]/16, Ht=H, G=Id-H*H, Gt=Id
                            3: SplineB2-Id: H=4[1,2,1]/4, Ht=H, G=Id-H*H, Gt=Id 4:
                            Harr/Spline POS:
                            H=Haar,G=[-1/4,1/2,-1/4],Ht=[1,3,3,1]/8,Gt=[1,6,1]/4.
                            Default=2.
      --noise-model INTEGER, -m INTEGER
                            Noise model: 1: Gaussian noise 2: Poisson noise 3:
                            Poisson noise + Gaussian noise 4: Multiplicative noise
                            5: Non-stationary additive noise 6: Non-stationary
                            multiplicative noise 7: Undefined stationary noise 8:
                            Undefined noise 9: Stationary correlated noise 10:
                            Poisson noise with few events. Default=1.
      --number-of-scales integer, -n integer
                            Number of scales used in the multiresolution
                            transform. Default=4.
      --k-sigma-noise-threshold FLOAT, -s FLOAT
                            Thresholding at nsigma * SigmaNoise. Default=3.
      --number-of-iterations integer, -i integer
                            Maximum number of iterations. Default=10.
      --epsilon FLOAT, -e FLOAT
                            Convergence parameter. Default=0.001000 or 0.000010 in
                            case of poisson noise with few events.
      --support-file-name FILE, -w FILE
                            Creates an image from the multiresolution support and
                            save to disk.
      --suppress-isolated-pixels, -k
                            Suppress isolated pixels in the support
      --kill-isolated-pixels
                            Suppress isolated pixels in the support (scipy
                            implementation)
      --suppress-last-scale, -K
                            Suppress the last scale (to have background pixels =
                            0)
      --detect-only-positive-structure, -p
                            Detect only positive structure
      --precision FLOAT, -E FLOAT
                            Epsilon = precision for computing thresholds (only
                            used in case of poisson noise with few events).
                            Default=1.00e-03.
      --first-detection-scale INTEGER, -F INTEGER
                            First scale used for the detection. Default=1.
      --suppress-positivity-constraint, -P
                            Suppress positivity constraint
      --maximum-level-constraint
                            Add the maximum level constraint. Max value is 255.
      --mask-file-path MASK_FILE_NAME
                            Filename of the mask containing the bad data
                            (Mask[i,j]=1 for good pixels and 0 otherwise. Default
                            is none.
      --offset-after-calibration FLOAT
                            Value added to all pixels of the input image after
                            calibration. Default=0.
      --correction-offset   Apply a correction offset to the output image.
      --input-image-scale INPUT_IMAGE_SCALE
                            Use a different scale for the input image ('linear',
                            'log' or 'sqrt'). Default='linear'.
      --noise-cdf-file FILE
                            The JSON file containing the Cumulated Distribution
                            Function of the noise model used to inject artificial
                            noise in blank pixels (those with a NaN value).
                            Default=None.
      --tmp-dir DIRECTORY   The directory where temporary files are written.
      --verbose, -v         Verbose mode
      --debug               Debug mode
      --max-images INTEGER  The maximum number of images to process
      --telid INTEGER       Only process images from the specified telescope
      --eventid INTEGER     Only process images from the specified event
      --camid STRING        Only process images from the specified camera
      --benchmark STRING, -b STRING
                            The benchmark method to use to assess the algorithm
                            for thegiven images
      --label STRING, -l STRING
                            The label attached to the produced results
      --plot                Plot images
      --saveplot FILE       The output file where to save plotted images
      --output FILE, -o FILE
                            The output file path (JSON)

Examples
--------
  ./filter_with_mrfilter.py -h
  ./filter_with_mrfilter.py ./test.fits
  ipython3 -- ./filter_with_mrfilter.py -n4 ./test.fits

Notes
-----
This script requires the mr_filter program
(http://www.cosmostat.org/software/isap/).
"""

__all__ = ['WaveletTransform',
           'add_arguments']

import argparse
import numpy as np
import os
import time

from pywi.image.pixel_clusters import kill_isolated_pixels as scipy_kill_isolated_pixels
from pywi.image.pixel_clusters import kill_isolated_pixels_stats
from pywi.image.pixel_clusters import number_of_islands

from pywi.io import images

from pywi.ui.argparse_commons import add_common_arguments
#from pywi.ui.commons import AbstractCleaningAlgorithm

# CONSTANTS ##################################################################

DEBUG = False

# EXCEPTIONS #################################################################

class MrFilterError(Exception):
    pass

class WrongDimensionError(MrFilterError):
    """Exception raised when trying to save a FITS with more than 3 dimensions
    or less than 2 dimensions.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self):
        super(WrongDimensionError, self).__init__("Unexpected error: the output FITS file should contain a 2D array.")


##############################################################################

#class WaveletTransform(AbstractCleaningAlgorithm):
class WaveletTransform:

    def __init__(self):
        super(WaveletTransform, self).__init__()
        self.label = "WT (mr_filter)"  # Name to show in plots

    def clean_image(self,
                    input_img,
                    type_of_multiresolution_transform=None,
                    type_of_filters=None,
                    type_of_non_orthog_filters=None,
                    number_of_scales=None,
                    suppress_last_scale=False,
                    suppress_isolated_pixels=False,
                    kill_isolated_pixels=False,
                    coef_detection_method=None,
                    k_sigma_noise_threshold=None,
                    noise_model=None,
                    detect_only_positive_structure=False,
                    suppress_positivity_constraint=False,
                    type_of_filtering=None,
                    first_detection_scale=None,
                    number_of_iterations=None,
                    epsilon=None,
                    support_file_name=None,
                    precision=None,
                    mask_file_path=None,
                    offset_after_calibration=None,
                    correction_offset=False,
                    input_image_scale='linear',
                    noise_distribution=None,
                    verbose=False,
                    raw_option_string=None,
                    tmp_files_directory=".",       # "/Volumes/ramdisk"
                    mrfilter_directory=None,       # "/Volumes/ramdisk"
                    output_data_dict=None,
                    **kwargs):
        """Clean the `input_img` image.

        Apply the wavelet transform, filter planes and return the reverse
        transformed image.

        Parameters
        ----------
        input_img : array_like
            The input image to transform.
        number_of_scales : int
            The number of scales used to transform `input_image` or in other words
            the number of wavelet planes returned.
        tmp_files_directory : str
            The path of the directory used to store mr_transform temporary data.
            The default is the current directory, but it may be more appropriate to
            specify here the path of a directory mounted in a ramdisk to speedup
            I/Os ("/Volumes/ramdisk" on MacOSX or "/dev/shm" on Linux).
        noise_distribution : EmpiricalDistribution
            The noise distribution used to fill 'empty' NaN pixels with the
            appropriate random noise distribution. If none, NaN pixels are fill
            with zeros (which may add unwanted harmonics in wavelet planes).

        Returns
        -------
        array_like
            Return the cleaned image.

        Raises
        ------
        WrongDimensionError
            If `cleaned_img` is not a 2D array.
        """

        input_img = input_img.copy()

        if input_img.ndim != 2:
            raise WrongDimensionError()

        input_file_path = os.path.join(tmp_files_directory, ".tmp_{}_{}_in.fits".format(os.getpid(), time.time()))
        mr_output_file_path = os.path.join(tmp_files_directory, ".tmp_{}_{}_out.fits".format(os.getpid(), time.time()))

        if output_data_dict is not None:
            output_data_dict["mr_input_tmp_file_path"] = input_file_path
            output_data_dict["mr_output_tmp_file_path"] = mr_output_file_path

        if (output_data_dict is not None) and (mask_file_path is not None):
            output_data_dict["mr_mask_file_path"] = mask_file_path

        # INJECT NOISE IN NAN ##################################

        # See https://stackoverflow.com/questions/29365194/replacing-missing-values-with-random-in-a-numpy-array

        nan_mask = images.fill_nan_pixels(input_img, noise_distribution)

        # APPLY AN OFFSET ######################################

        if offset_after_calibration is not None:
            if verbose:
                print("Apply an offset after calibration:", offset_after_calibration)
            input_img = input_img + offset_after_calibration

        # CHANGE THE SCALE #####################################

        if input_image_scale == 'log':
            if verbose:
                print("Apply log scale")
            #images.plot(input_img)
            input_img = np.log10(input_img)  # TODO: it creates NaN values where pixels <= 0
            #images.plot(input_img)
        elif input_image_scale == 'sqrt':
            if verbose:
                print("Apply sqrt scale")
            #images.plot(input_img)
            input_img = np.sqrt(input_img)   # TODO: it creates NaN values where pixels < 0
            #images.plot(input_img)

        # WRITE THE INPUT FILE (FITS) ##########################

        try:
            initial_time = time.perf_counter()
            images.save_fits(input_img, input_file_path)
            exec_time_sec = time.perf_counter() - initial_time
            if output_data_dict is not None:
                output_data_dict["save_tmp_file_time_sec"] = exec_time_sec
        except:
            print("Error on input FITS file:", input_file_path)
            raise

        # EXECUTE MR_FILTER ####################################

        # TODO: improve the following lines
        if mrfilter_directory is None:
            cmd = 'mr_filter'
        else:
            cmd = os.path.join(mrfilter_directory, 'mr_filter')

        if raw_option_string is None:
            cmd += ' -t{}'.format(type_of_multiresolution_transform) if type_of_multiresolution_transform is not None else ''
            cmd += ' -T{}'.format(type_of_filters) if type_of_filters is not None else ''
            cmd += ' -U{}'.format(type_of_non_orthog_filters) if type_of_non_orthog_filters is not None else ''
            cmd += ' -n{}'.format(number_of_scales) if number_of_scales is not None else ''
            cmd += ' -K' if suppress_last_scale else ''
            cmd += ' -k' if suppress_isolated_pixels else ''      # You should use scipy implementation instead (pywi/denoising/kill_isolated_pixels.py); it's much more efficient
            cmd += ' -C{}'.format(coef_detection_method) if coef_detection_method is not None else ''
            cmd += ' -s{}'.format(k_sigma_noise_threshold) if k_sigma_noise_threshold is not None else ''
            cmd += ' -m{}'.format(noise_model) if noise_model is not None else ''
            cmd += ' -p' if detect_only_positive_structure else ''
            cmd += ' -P' if suppress_positivity_constraint else ''
            cmd += ' -f{}'.format(type_of_filtering) if type_of_filtering is not None else ''
            cmd += ' -F{}'.format(first_detection_scale) if first_detection_scale is not None else ''
            cmd += ' -i{}'.format(number_of_iterations) if number_of_iterations is not None else ''
            cmd += ' -e{}'.format(epsilon) if epsilon is not None else ''
            cmd += ' -w{}'.format(support_file_name) if support_file_name is not None else ''
            cmd += ' -E{}'.format(precision) if precision is not None else ''
            cmd += ' -I {}'.format(mask_file_path) if mask_file_path is not None else ''

            cmd += ' -v' if verbose else ''
        else:
            cmd += ' ' + raw_option_string

        #self.label = "WT ({})".format(cmd)  # Name to show in plots
        cmd += ' "{}" "{}"'.format(input_file_path, mr_output_file_path)

        #cmd = 'mr_filter -K -k -C1 -s3 -m3 -n{} "{}" {}'.format(number_of_scales, input_file_path, mr_output_file_path)
        #cmd = 'mr_filter -K -k -C1 -s3 -m2 -p -P -n{} "{}" {}'.format(number_of_scales, input_file_path, mr_output_file_path)

        if verbose:
            print()
            print(cmd)
        else:
            cmd += ' > /dev/null'

        try:
            initial_time = time.perf_counter()
            os.system(cmd)
            exec_time_sec = time.perf_counter() - initial_time
            if output_data_dict is not None:
                output_data_dict["mrfilter_cmd_exec_time_sec"] = exec_time_sec
        except:
            print("Error on command:", cmd)
            raise

        # READ THE MR_FILTER OUTPUT FILE #######################

        try:
            initial_time = time.perf_counter()
            cleaned_img = images.load_fits(mr_output_file_path, 0)
            exec_time_sec = time.perf_counter() - initial_time
            if output_data_dict is not None:
                output_data_dict["load_tmp_file_time_sec"] = exec_time_sec
        except:
            print("Error on output FITS file:", mr_output_file_path)
            raise

        # REMOVE FITS FILES ####################################

        os.remove(input_file_path)
        os.remove(mr_output_file_path)

        # CHECK RESULT #########################################

        if cleaned_img.ndim != 2:
            raise WrongDimensionError()

        # INJECT NOISE IN NAN: PUT BACK NAN VALUES #############

        cleaned_img[nan_mask] = np.nan

        # CHANGE THE SCALE #####################################

        if input_image_scale == 'log':
            if verbose:
                print("Invert log scale")
            cleaned_img = np.power(10., cleaned_img)
        elif input_image_scale == 'sqrt':
            if verbose:
                print("Invert sqrt scale")
            cleaned_img = np.power(2., cleaned_img)

        # INVERT THE OFFSET ####################################

        if (offset_after_calibration is not None) and (not suppress_last_scale):
            cleaned_img = cleaned_img - offset_after_calibration

        # CORRECTION OFFSET ####################################

        if correction_offset:
            if verbose:
                print("Apply a correction offset after cleaning")
            cleaned_img = cleaned_img - np.nanmin(cleaned_img)
            cleaned_img[ np.isfinite(cleaned_img) & (cleaned_img < 1.0) ] = 0.   # May genereate warnings on NaN values

        # KILL ISOLATED PIXELS #################################

        img_cleaned_islands_delta_pe, img_cleaned_islands_delta_abs_pe, img_cleaned_islands_delta_num_pixels = kill_isolated_pixels_stats(cleaned_img)
        img_cleaned_num_islands = number_of_islands(cleaned_img)

        if output_data_dict is not None:
            output_data_dict["img_cleaned_islands_delta_pe"] = img_cleaned_islands_delta_pe
            output_data_dict["img_cleaned_islands_delta_abs_pe"] = img_cleaned_islands_delta_abs_pe
            output_data_dict["img_cleaned_islands_delta_num_pixels"] = img_cleaned_islands_delta_num_pixels
            output_data_dict["img_cleaned_num_islands"] = img_cleaned_num_islands

        if kill_isolated_pixels:
            if verbose:
                print("Kill isolated pixels")
            initial_time = time.perf_counter()
            cleaned_img = scipy_kill_isolated_pixels(cleaned_img)
            exec_time_sec = time.perf_counter() - initial_time
            if output_data_dict is not None:
                output_data_dict["scipy_kill_isolated_pixels_time_sec"] = exec_time_sec

        #print(cleaned_img)
        #images.plot_hist(cleaned_img)
        #images.plot_hist(cleaned_img, num_bins=500, x_max=5)

        return cleaned_img


def add_arguments(parser):
    """Populate the given argparse.ArgumentParser with arguments.

    This function can be used to make the definition these argparse arguments
    reusable in other modules and avoid the duplication of these definitions
    among the executable scripts.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The parser to populate.

    Returns
    -------
    argparse.ArgumentParser
        Return the populated ArgumentParser object.
    """

    parser.add_argument("--type-of-filtering", "-f", type=int, metavar="INTEGER",
                        help="""Type of filtering:
                            1: Multiresolution Hard K-Sigma Thresholding
                            2: Multiresolution Soft K-Sigma Thresholding
                            3: Iterative Multiresolution Thresholding
                            4: Adjoint operator applied to the multiresolution support
                            5: Bivariate Shrinkage
                            6: Multiresolution Wiener Filtering
                            7: Total Variation + Wavelet Constraint
                            8: Wavelet Constraint Iterative Methods
                            9: Median Absolute Deviation (MAD) Hard Thesholding
                            10: Median Absolute Deviation (MAD) Soft Thesholding.
                            Default=1.""")

    parser.add_argument("--coef-detection-method", "-C", type=int, metavar="INTEGER",
                        help="""Coef_Detection_Method:
                            1: K-SigmaNoise Threshold
                            2: False Discovery Rate (FDR) Theshold
                            3: Universal Threshold
                            4: SURE Threshold
                            5: Multiscale SURE Threshold.
                            Default=1.""")

    parser.add_argument("--type-of-multiresolution-transform", "-t", type=int, metavar="INTEGER",
                        help="""Type of multiresolution transform:
                            1: linear wavelet transform: a trous algorithm
                            2: bspline wavelet transform: a trous algorithm
                            3: wavelet transform in Fourier space
                            4: morphological median transform
                            5: morphological minmax transform
                            6: pyramidal linear wavelet transform
                            7: pyramidal bspline wavelet transform
                            8: pyramidal wavelet transform in Fourier space: algo 1 (diff. between two resolutions)
                            9: Meyer's wavelets (compact support in Fourier space)
                            10: pyramidal median transform (PMT)
                            11: pyramidal laplacian
                            12: morphological pyramidal minmax transform
                            13: decomposition on scaling function
                            14: Mallat's wavelet transform (7/9 filters)
                            15: Feauveau's wavelet transform
                            16: Feauveau's wavelet transform without undersampling
                            17: Line Column Wavelet Transform (1D+1D)
                            18: Haar's wavelet transform
                            19: half-pyramidal transform
                            20: mixed Half-pyramidal WT and Median method (WT-HPMT)
                            21: undecimated diadic wavelet transform (two bands per scale)
                            22: mixed WT and PMT method (WT-PMT)
                            23: undecimated Haar transform: a trous algorithm (one band per scale)
                            24: undecimated (bi-) orthogonal transform (three bands per scale)
                            25: non orthogonal undecimated transform (three bands per scale)
                            26: Isotropic and compact support wavelet in Fourier space
                            27: pyramidal wavelet transform in Fourier space: algo 2 (diff. between the square of two resolutions)
                            28: Fast Curvelet Transform.
                            Default=2.""")

    parser.add_argument("--type-of-filters", "-T", type=int, metavar="INTEGER",
                        help="""Type of filters:
                            1: Biorthogonal 7/9 filters
                            2: Daubechies filter 4
                            3: Biorthogonal 2/6 Haar filters
                            4: Biorthogonal 2/10 Haar filters
                            5: Odegard 9/7 filters
                            6: 5/3 filter
                            7: Battle-Lemarie filters (2 vanishing moments)
                            8: Battle-Lemarie filters (4 vanishing moments)
                            9: Battle-Lemarie filters (6 vanishing moments)
                            10: User's filters
                            11: Haar filter
                            12: 3/5 filter
                            13: 4/4 Linar spline filters
                            14: Undefined sub-band filters.
                            Default=1.""")

    parser.add_argument("--type-of-non-orthog-filters", "-U", type=int, metavar="INTEGER",
                        help="""Type of non-orthogonal filters:
                            1: SplineB3-Id+H:  H=[1,4,6,4,1]/16, Ht=H, G=Id-H, Gt=Id+H
                            2: SplineB3-Id:  H=[1,4,6,4,1]/16, Ht=H, G=Id-H*H, Gt=Id
                            3: SplineB2-Id: H=4[1,2,1]/4, Ht=H, G=Id-H*H, Gt=Id
                            4: Harr/Spline POS: H=Haar,G=[-1/4,1/2,-1/4],Ht=[1,3,3,1]/8,Gt=[1,6,1]/4.
                            Default=2.""")

#         [-u number_of_undecimated_scales]
#             Number of undecimated scales used in the Undecimated Wavelet Transform
#             Default is all scale.
#
#         [-g sigma]
#             sigma = noise standard deviation
#             default is automatically estimated.
#
#         [-c gain,sigma,mean]
#             Poisson + readout noise, with:
#                 gain = gain of the CCD
#                 sigma = read-out noise standard deviation
#                 mean = read-out noise mean
#             default is no (Gaussian).

    parser.add_argument("--noise-model", "-m", type=int, metavar="INTEGER",
                        help="""Noise model:
                            1: Gaussian noise
                            2: Poisson noise
                            3: Poisson noise + Gaussian noise
                            4: Multiplicative noise
                            5: Non-stationary additive noise
                            6: Non-stationary multiplicative noise
                            7: Undefined stationary noise
                            8: Undefined noise
                            9: Stationary correlated noise
                            10: Poisson noise with few events. Default=1.""")

    parser.add_argument("--number-of-scales", "-n", type=int, metavar="integer",
                        help="Number of scales used in the multiresolution transform. Default=4.")

    parser.add_argument("--k-sigma-noise-threshold", "-s", metavar="FLOAT",
                        help="Thresholding at nsigma * SigmaNoise. Default=3.")

    parser.add_argument("--number-of-iterations", "-i", type=int, metavar="integer",
                        help="Maximum number of iterations. Default=10.")

    parser.add_argument("--epsilon", "-e", type=float, metavar="FLOAT",
                        help="Convergence parameter. Default=0.001000 or 0.000010 in case of poisson noise with few events.")

    parser.add_argument("--support-file-name", "-w", metavar="FILE",
                        help="Creates an image from the multiresolution support and save to disk.")

    parser.add_argument("--suppress-isolated-pixels", "-k", action="store_true",
                        help="Suppress isolated pixels in the support")

    parser.add_argument("--kill-isolated-pixels", action="store_true",
                        help="Suppress isolated pixels in the support (scipy implementation)")

    parser.add_argument("--suppress-last-scale", "-K", action="store_true",
                        help="Suppress the last scale (to have background pixels = 0)")

    parser.add_argument("--detect-only-positive-structure", "-p", action="store_true",
                        help="Detect only positive structure")

    parser.add_argument("--precision", "-E", type=float, metavar="FLOAT",
                        help="Epsilon = precision for computing thresholds (only used in case of poisson noise with few events). Default=1.00e-03.")

#         [-S SizeBlock]
#             Size of the  blocks used for local variance estimation.
#             default is 7.
#
#         [-N NiterSigmaClip]
#             Iteration number used for local variance estimation.
#             default is 1.

    parser.add_argument("--first-detection-scale", "-F", type=int, metavar="INTEGER",
                        help="First scale used for the detection. Default=1.")

#         [-R RMS_Map_File_Name]
#              RMS Map (only used with -m 5 and -m 9 options).

    parser.add_argument("--suppress-positivity-constraint", "-P", action="store_true",
                        help="Suppress positivity constraint")

    parser.add_argument("--maximum-level-constraint", action="store_true",
                        help="Add the maximum level constraint. Max value is 255.")

#         [-B BackgroundModelImage]
#             Background Model Image: the background image is
#             subtracted during the filtering.
#             Default is no.
#
#         [-M Flat_Image]
#             Flat Image: The solution is corrected from the flat (i.e. Sol = Input / Flat)
#             Default is no.
#
#         [-h]
#             write info used for computing the probability map.
#             Default is no.
#
#         [-G RegulParam]
#              Regularization parameter for the TV method.
#              default is 0.100000
#
#         [-z]
#             Use virtual memory.
#                default limit size: 4
#                default directory: .
#
#         [-Z VMSize:VMDIR]
#             Use virtual memory.
#                VMSize = limit size (megabytes)
#                VMDIR = directory name
#

    parser.add_argument("--mask-file-path", metavar="MASK_FILE_NAME",
                        help="Filename of the mask containing the bad data (Mask[i,j]=1 for good pixels and 0 otherwise. Default is none.")

    parser.add_argument("--offset-after-calibration", type=float, metavar="FLOAT",
                        help="Value added to all pixels of the input image after calibration. Default=0.")

    parser.add_argument("--correction-offset", action="store_true",
                        help="Apply a correction offset to the output image.")

    parser.add_argument("--input-image-scale", default="linear",
                        help="Use a different scale for the input image ('linear', 'log' or 'sqrt'). Default='linear'.")

    parser.add_argument("--noise-cdf-file", metavar="FILE",
                        help="The JSON file containing the Cumulated Distribution Function of the noise model used to inject artificial noise in blank pixels (those with a NaN value). Default=None.")

    parser.add_argument("--tmp-dir", default=".", metavar="DIRECTORY",
                        help="The directory where temporary files are written.")

    return parser


def main():
    """The main module execution function.

    Contains the instructions executed when the module is not imported but
    directly called from the system command line.
    """

    # PARSE OPTIONS ###########################################################

    parser = argparse.ArgumentParser(description="Denoise images with Wavelet Transform.")

    parser = add_arguments(parser)
    parser = add_common_arguments(parser)

    args = parser.parse_args()

    type_of_multiresolution_transform = args.type_of_multiresolution_transform
    type_of_filters = args.type_of_filters
    type_of_non_orthog_filters = args.type_of_non_orthog_filters
    number_of_scales = args.number_of_scales
    suppress_last_scale = args.suppress_last_scale
    suppress_isolated_pixels = args.suppress_isolated_pixels
    kill_isolated_pixels = args.kill_isolated_pixels
    coef_detection_method = args.coef_detection_method
    k_sigma_noise_threshold = args.k_sigma_noise_threshold
    noise_model = args.noise_model
    detect_only_positive_structure = args.detect_only_positive_structure
    suppress_positivity_constraint = args.suppress_positivity_constraint
    type_of_filtering = args.type_of_filtering
    first_detection_scale = args.first_detection_scale
    number_of_iterations = args.number_of_iterations
    epsilon = args.epsilon
    support_file_name = args.support_file_name
    precision = args.precision
    mask_file_path = args.mask_file_path
    offset_after_calibration = args.offset_after_calibration
    correction_offset = args.correction_offset
    input_image_scale = args.input_image_scale
    noise_cdf_file = args.noise_cdf_file
    tmp_dir = args.tmp_dir

    verbose = args.verbose
    debug = args.debug
#    max_images = args.max_images
#    benchmark_method = args.benchmark
#    label = args.label
    plot = args.plot
    saveplot = args.saveplot

#    input_file_or_dir_path_list = args.fileargs
    input_file = args.fileargs[0]

    #############################################

    #if args.output is None:
    #    output_file_path = "score_wavelets_benchmark_{}.json".format(benchmark_method)
    #else:
    #    output_file_path = args.output

    ##if noise_cdf_file is not None:
    ##    noise_distribution = EmpiricalDistribution(noise_cdf_file)
    ##else:
    ##    noise_distribution = None
    noise_distribution = None

    # CLEAN THE INPUT IMAGE ###################################

    img_filter = WaveletTransform()
    input_img = images.load_image(input_file)

    # Copy the image (otherwise some cleaning functions may change it)
    input_img_copy = input_img.astype('float64', copy=True)

    cleaned_img = img_filter.clean_image(input_img_copy,
                                         type_of_multiresolution_transform=type_of_multiresolution_transform,
                                         type_of_filters=type_of_filters,
                                         type_of_non_orthog_filters=type_of_non_orthog_filters,
                                         number_of_scales=number_of_scales,
                                         suppress_last_scale=suppress_last_scale,
                                         suppress_isolated_pixels=suppress_isolated_pixels,
                                         kill_isolated_pixels=kill_isolated_pixels,
                                         coef_detection_method=coef_detection_method,
                                         k_sigma_noise_threshold=k_sigma_noise_threshold,
                                         noise_model=noise_model,
                                         detect_only_positive_structure=detect_only_positive_structure,
                                         suppress_positivity_constraint=suppress_positivity_constraint,
                                         type_of_filtering=type_of_filtering,
                                         first_detection_scale=first_detection_scale,
                                         number_of_iterations=number_of_iterations,
                                         epsilon=epsilon,
                                         support_file_name=support_file_name,
                                         precision=precision,
                                         mask_file_path=mask_file_path,
                                         offset_after_calibration=offset_after_calibration,
                                         correction_offset=correction_offset,
                                         input_image_scale=input_image_scale,
                                         noise_distribution=noise_distribution,
                                         verbose=verbose,
                                         tmp_files_directory=tmp_dir)

    # PLOT IMAGES #########################################################

    if plot or (saveplot is not None):
        image_list = [input_img, cleaned_img] 
        title_list = ["Input image", "Filtered image"] 

        if plot:
            images.plot_list(image_list, title_list=title_list)

        if saveplot is not None:
            plot_file_path = saveplot
            print("Saving {}".format(plot_file_path))
            images.mpl_save_list(image_list,
                                 output_file_path=plot_file_path,
                                 title_list=title_list)

    # SAVE IMAGE ##########################################################

    basename, extension = os.path.splitext(input_file)
    output_file_path = "{}-out{}".format(basename, extension)
    images.save_image(cleaned_img, output_file_path)

if __name__ == "__main__":
    main()

