# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import division, absolute_import


# These are the wavelength and flux units that are used internally for all calculations.
PANDEIA_WAVEUNITS = "micron"
PANDEIA_FLUXUNITS = "mjy"


# Absolute and relative tolerance values to use to check if values are close enough to be considered equal.
# See https://docs.scipy.org/doc/numpy/reference/generated/numpy.isclose.html for details on how they're applied
# in comparisons.
PANDEIA_ATOL = 1.0e-8
PANDEIA_RTOL = 1.0e-6

# Pandeia subsamples lines in order to accurately reproduce thin spectral lines in a spectrum. This subsampling must
# extend over a large enough range to contain most of the wings and accurately reproduce the line.
#
# spectral_line_window determines the size of the wavelength window over which lines are subsampled. Values above 15
#  (decided empirically, see Issue #3292) are necessary to contain the wings of the line.
# spectral_line_subsample determines how much the spectrum is subsampled within the window to reproduce the shape of
#  the profile.
SPECTRAL_LINE_WINDOW = 20
SPECTRAL_LINE_SUBSAMPLE = 3

# In practice, a value of 200 samples within an imaging configuration's wavelength range (i.e. filter bandpass) should
# be more than enough to produce an accurate image. Note that because we use pysynphot to resample, the flux of
# even narrow lines is conserved.
SPECTRAL_MAX_SAMPLES = 200

# Pandeia's spectrum processing can use a considerable amount of memory for large fields (like SOSS. To handle this,
# we divide the spectra into chunks of wavelength planes (if necessary) at the cost of a few seconds of run time. There
# may be a more elegant way to handle this...
SPECTRAL_MAX_CHUNK = 1000

# Pandeia's FOV size (for the spatial axes of the scene cubes) is the largest of either the scene size, the PSF size,
# or the configured instrument's default FOV size. We need to add a small buffer to the scene size to adequately contain
# the full scene after sources have been represented by PSFs
SCENE_FOV_PIXBUFFER = 20

# The ConvolvedSceneCube function uses astropy.convolve_fft to produce a convolved scene cube. This cube cannot be
# created if any of the pixels are too bright - even getting close to the maximum floating point number that can be
# stored in a numpy array. Empirical studies show that values greater than 1e33 still cause astropy.convolve_fft to fail
# We have set this to 1e32 to be safe.
SCENE_MAX_PIXELVAL = 1e32
