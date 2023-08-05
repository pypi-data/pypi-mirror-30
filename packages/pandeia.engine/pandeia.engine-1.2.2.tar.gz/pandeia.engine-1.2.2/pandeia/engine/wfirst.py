# Licensed under a 3-clause BSD style license - see LICENSE.rst
from __future__ import division, absolute_import
import os

from .telescope import Telescope
from .instrument import Instrument

class WFIRST(Telescope):

    """
    Currently a dummy class for directory/file discovery, but could eventually contain WFIRST-specific methods
    """
    pass


class WFIRSTInstrument(Instrument):

    """
    Generic WFIRST Instrument class
    """

    def __init__(self, mode=None, config={}, **kwargs):
        telescope = WFIRST()
        # these are the required sections and need to be passed via API in webapp mode
        self.instrument_pars = {}
        self.instrument_pars['detector'] = ["nexp", "ngroup", "nint", "readmode", "subarray"]
        self.instrument_pars['instrument'] = ["aperture", "disperser", "filter", "instrument", "mode"]
        self.api_parameters = list(self.instrument_pars.keys())

        # these are required for calculation, but ok to live with config file defaults
        self.api_ignore = ['dynamic_scene', 'max_scene_size', 'scene_size']

        Instrument.__init__(self, telescope=telescope, mode=mode, config=config, **kwargs)


class WFIRSTImager(WFIRSTInstrument):

    """
    Currently the WFIRSTImager requires only one methods beyond those provided by the generic Instrument class
    """
    def _loadpsfs(self):
        """
        Short-wavelength filters need PSFs that don't have the cold pupil mask (0.48-1.6 microns)
        Long-wavelength filters need PSFs that DO have the cold pupil mask (0.8-2.2 microns)
        Because the ranges overlap, we need to switch between PSF libraries.
        The mask is specifically baked into the filters, so selecting by filter seems appropriate
        """
        if self.instrument['filter'] in self.cold_pupil:
            psf_key = "%s%s" % (self.instrument['aperture'], 'lw')
        else:
            psf_key = "%s%s" % (self.instrument['aperture'], 'sw')

        self.psf_library = self._load_psf_library(psf_key)


class WFIRSTIFU(WFIRSTInstrument):

    """
    Currently the WFIRSTIFU requires no extra methods beyond those provided by the generic Instrument class
    """
    pass
