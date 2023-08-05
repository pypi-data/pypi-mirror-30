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

__all__ = []

import json
from scipy import optimize
from pywicta.optimization.objectivefunc.wavelets_mrfilter_delta_psi import ObjectiveFunction as WaveletObjectiveFunction
from pywicta.optimization.objectivefunc.tailcut_delta_psi import ObjectiveFunction as TailcutObjectiveFunction

# For wavelets
import pywicta.denoising.cdf
from pywicta.denoising.inverse_transform_sampling import EmpiricalDistribution

def main():

    algo = "wavelet_mrfilter"
    #algo = "tailcut"

    instrument = "astri"
    #instrument = "astri_konrad"
    #instrument = "digicam"
    #instrument = "flashcam"
    #instrument = "nectarcam"
    #instrument = "lstcam"

    print("algo:", algo)
    print("instrument:", instrument)

    if instrument == "astri":

        input_files = ["/dev/shm/.jd/astri/gamma/"]
        noise_distribution = EmpiricalDistribution(pywicta.denoising.cdf.ASTRI_CDF_FILE)

    elif instrument == "astri_konrad":

        input_files = ["/dev/shm/.jd/astri_konrad/gamma/"]
        noise_distribution = EmpiricalDistribution(pywicta.denoising.cdf.ASTRI_CDF_FILE)

    elif instrument == "digicam":

        input_files = ["/dev/shm/.jd/digicam/gamma/"]
        noise_distribution = EmpiricalDistribution(pywicta.denoising.cdf.DIGICAM_CDF_FILE)

    elif instrument == "flashcam":

        input_files = ["/dev/shm/.jd/flashcam/gamma/"]
        noise_distribution = EmpiricalDistribution(pywicta.denoising.cdf.FLASHCAM_CDF_FILE)

    elif instrument == "nectarcam":

        input_files = ["/dev/shm/.jd/nectarcam/gamma/"]
        noise_distribution = EmpiricalDistribution(pywicta.denoising.cdf.NECTARCAM_CDF_FILE)

    elif instrument == "lstcam":

        input_files = ["/dev/shm/.jd/lstcam/gamma/"]
        noise_distribution = EmpiricalDistribution(pywicta.denoising.cdf.LSTCAM_CDF_FILE)

    else:

        raise Exception("Unknown instrument", instrument)

    if algo == "wavelet_mrfilter":

        func = WaveletObjectiveFunction(input_files=input_files,
                                        noise_distribution=noise_distribution,
                                        max_num_img=None,
                                        aggregation_method="mean")  # "mean" or "median"

        s1_slice = slice(1, 5, 1)
        s2_slice = slice(1, 5, 1)
        s3_slice = slice(1, 5, 1)
        s4_slice = slice(1, 5, 1)

        search_ranges = (s1_slice,
                         s2_slice,
                         s3_slice,
                         s4_slice)

    elif algo == "tailcut":

        func = TailcutObjectiveFunction(input_files=input_files,
                                        max_num_img=None,
                                        aggregation_method="mean")  # "mean" or "median"

        s1_slice = slice(-2., 10., 0.5)
        s2_slice = slice(-2., 10., 0.5)

        search_ranges = (s1_slice,
                         s2_slice)

    else:

        raise ValueError("Unknown algorithm", algo)

    res = optimize.brute(func,
                         search_ranges,
                         full_output=True,
                         finish=None)     #optimize.fmin)

    print("x* =", res[0])
    print("f(x*) =", res[1])

    # SAVE RESULTS ############################################################

    res_dict = {
                "best_solution": res[0].tolist(),
                "best_score": float(res[1]),
                "solutions": res[2].tolist(),
                "scores": res[3].tolist()
               }

    with open("optimize_sigma.json", "w") as fd:
        json.dump(res_dict, fd, sort_keys=True, indent=4)  # pretty print format


if __name__ == "__main__":
    main()

