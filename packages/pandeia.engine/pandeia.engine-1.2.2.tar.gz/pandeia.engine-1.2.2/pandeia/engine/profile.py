import numpy as np
import scipy.integrate as ig
import astropy.units as u

from .config import DefaultConfig
from .coords import Grid
from .utils import get_key_list, get_dict_from_keys, recursive_subclasses, merge_data
from .custom_exceptions import EngineInputError, WavesetMismatch, DataError, RangeError, DataConfigurationError

def ProfileFactory(config={}, **kwargs):

    """
    Function to take profile configuration data and build/return a configured instance of 
    the appropriate distribution generator.

    Parameters
    ----------
    webapp: bool
        Switch to toggle strict API checking
    config: dict
        Configuration data in engine API dict format
    **kwargs: keyword/value pairs
        Additional configuration data
    """
    #all_config = merge_data(config, dict(**kwargs))
    all_config = config
    if 'geometry' in all_config.shape:
        method = all_config.shape['geometry'].replace('_', '')
    else:
        msg = "Must specify type of profile to create."
        raise EngineInputError(value=msg)
        


    # we need to run the API checks here after merging in the normalization type-specific defaults
    #if webapp:
    #    self._api_checks(all_config)

    types = recursive_subclasses(Distribution)
    methods = [t.__name__.lower().replace('distribution', '') for t in types]
    type_map = dict(list(zip(methods, types)))

    if method not in methods:
        msg = "Unsupported or not yet implemented profile type: %s" % method
        raise EngineInputError(value=msg)
    else:
        cls = type_map[method](config,**kwargs)
        return cls
        
class Distribution(DefaultConfig):
    """
    Abstract class for source profiles. 
    
    Parameters
    ----------
    src: dict
        Details of the source geometry to generate, from the Source block of the input files.

    Attributes
    ----------
    xoff: float
        Offset in X direction
    yoff: float
        Offset in Y direction
    pa: float
        Position angle of major axis
    xrot: np.ndarray
        rotated and shifted indicies, X axis values
    yrot: np.ndarray
        rotated and shifted indicies, Y axis values
    pix_area_sqarcsec: float
        area of a detector pixel in square arcseconds
    prof: np.ndarray
        raw 2D profile in detector units
    norm_prof: np.ndarray
        normalized 2D profile in detector units
        
    Methods
    -------
    sampled()
        return the normalized 2D profile
    raw()
        return the raw 2D profile

    """
    def __init__(self,src):
        self.pa=src.position['orientation']
        self.xoff=src.position['x_offset']
        self.yoff=src.position['y_offset']
        yrot, xrot = src.grid.shift_rotate(self.yoff, self.xoff, self.pa)
        self.xrot = np.abs(xrot)
        self.yrot = np.abs(yrot)
        self.pix_area_sqarcsec = src.grid.xsamp * src.grid.ysamp

    def pixelscale(self):
        if self.surf_area_units in ['sr']:
            arcsec2 = u.arcsec * u.arcsec
            normfactor = self.pix_area_sqarcsec / u.sr.to(arcsec2)  # convert area in steradians to area in pixels
        elif self.surf_area_units in ['arcsec^2', None]: # 'None' should be an option because integrated 
                                                                                                         #  flux technically shouldn't have units (internally, the grid is arcsec)
            normfactor = self.pix_area_sqarcsec
        else:
            msg = "Unsupported surface area unit: %s" % self.surf_area_units
            raise EngineInputError(value=msg)
            
        return normfactor
        
    def normalize(self,src):
        if src.shape['norm_method'] == 'integ_infinity':
                self.integrate_infinity()
        elif src.shape['norm_method'] == 'surf_scale':
            if src.shape['geometry'] == 'flat': # really needs to be refactored into something more clever
                msg = "Normalization method {0:} not supported for profile type {1:}".format(src.shape['norm_method'],src.shape['geometry'])
                raise EngineInputError(value=msg)
            else:
                        self.surface_scale()
        elif src.shape['norm_method'] == 'surf_center':
                self.surface_center()
        else:
            msg = "Normalization method {0:} not supported for profile type {1:}".format(src.shape['norm_method'],src.shape['geometry'])
            raise EngineInputError(value=msg)
    
    def sampled(self):
        return self.norm_prof
        
    def raw(self):
        return self.prof
        
class PointDistribution(Distribution):
    """
    Use pandeia.engine.coords.Grid.point_source() to generate a point source with 
    subpixel positioning.
    
    Parameters
    ----------
    src: dict
        Details of the source geometry to generate, from the Source block of the input files.

    Attributes
    ----------
    xoff: float
        Offset in X direction
    yoff: float
        Offset in Y direction
    prof: np.ndarray
        raw 2D profile in detector units
    norm_prof: np.ndarray
        normalized 2D profile in detector units

    """
    def __init__(self,src):

        self.xoff=src.position['x_offset']
        self.yoff=src.position['y_offset']

        # This function both creates and fills the point source profile. It should
        # eventually be refactored to work the same way as other sources
        self.prof = src.grid.point_source(xoff=self.xoff, yoff=self.yoff)
        
        self.norm_prof = self.prof


class SersicDistribution(Distribution):
    """
    Create a 2-dimensional elliptical source on the current grid. The intensity 
    profile is described by a Sersic profile, I(r) = I(0) * exp(-(r/r_scale)**(1/n)), 
    where r_scale is the scale length where I(r) = I(0)/e and n is the Sersic index. 
    The ellipticity is governed by specifying major and minor axis scale lengths 
    separately.
    
    
    Parameters
    ----------
    src: dict
        Details of the source geometry to generate, from the Source block of the input files.

    Attributes
    ----------
    minor: float
        Minor axis scale length
    major: float
        Major axis scale length
    pa: float
        Position angle in degrees of major axis measured positive in +X direction
    xoff: float
        Offset in X direction
    yoff: float
        Offset in Y direction
    sersic_index: float
        Sersic profile shape parameter. 0.5 => gaussian, 1.0 => exponential, 4.0 => de Vaucouleurs
    prof: np.ndarray
        raw 2D profile in detector units
    norm_prof: np.ndarray
        normalized 2D profile in detector units

    Methods
    -------
        integrate_infinity():
            Normalization is performed using scipy.integrate.dblquad to integrate the profile 
        in 2D from -Inf to +Inf in both axes.  This will account for flux that falls 
        outside of the FOV. This works well for sersic_index <= 2.0 or so, but slow 
        convergence for larger values can impact performance noticeably.  For example, it 
        takes 10 times longer to normalize a de Vaucouleurs profile with sersic_index=4.0 
        than an exponential disc with sersic_index=1.  Truncating the integration range 
        can help, but also significantly impacts accuracy as sersic_index increases.  
        Ultimate solution may be to implement the integration in C somehow.
    surface_center():
        Normalization is to the surface brightness of the center of the profile. This 
        formulation is already normalized at that point.
    surface_scale():
        Normalization is to the surface brightness of a point at the e-folding radius of
        this profile, where intensity is 1/e of the central intensity.
    """
    def __init__(self,src):
        Distribution.__init__(self,src)
        self.major=src.shape['major']
        self.minor=src.shape['minor']
        self.sersic_index=src.shape['sersic_index']
        self.surf_area_units = src.shape['surf_area_units']


        self.prof = self._sersic_func(self.yrot, self.xrot, self.major, self.minor, self.sersic_index)
        
        self.normalize(src)

    def integrate_infinity(self):
        # integrate the Sersic profile to get the total flux for normalization, including flux outside the FOV
        integral = ig.dblquad(
                self._sersic_func,
                -np.inf,
                np.inf,
                lambda y: -np.inf,
                lambda y: np.inf,
                args=(self.major, self.minor, self.sersic_index)
        )
        self.norm_prof = self.prof/integral[0] * self.pixelscale()
        
    def surface_scale(self):
        self.norm_prof = self.prof * np.e * self.pixelscale()

    def surface_center(self):
        self.norm_prof = self.prof * self.pixelscale()

    def _sersic_func(self, y, x, major, minor, index):
        """
        Implement Sersic intensity profile in a way that scipy.integrate.dblquad can use 
        since it is passed there as a callable. We need to integrate this function to 
        normalize it properly for flux outside the calculation FOV.

        Parameters
        ----------
        y: float or numpy.ndarray
            Y values for evaluating function
        x: float or numpy.ndarray
            X values for evaluating function
        major: float
            Major axis scale length
        minor: float
            Minor axis scale length
        index: float
            Sersic index

        Returns
        -------
        profile: float or numpy.ndarray
            Float or array containing evaluated Sersic profile
        """
        dist = np.sqrt((x / major)**2.0 + (y / minor)**2.0)
        profile = np.exp(-dist**(1.0 / index))
        return profile

class Gaussian2dDistribution(SersicDistribution):
    """
    The Gaussian 2D profile is a special case of the Sersic profile, where sersic index = 0.5.

    Parameters
    ----------
    src: dict
        Details of the source geometry to generate, from the Source block of the input files.

    Attributes
    ----------
    minor: float
        Minor axis scale length
    major: float
        Major axis scale length
    pa: float
        Position angle in degrees of major axis measured positive in +X direction
    xoff: float
        Offset in X direction
    yoff: float
        Offset in Y direction
    prof: np.ndarray
        raw 2D profile in detector units
    norm_prof: np.ndarray
        normalized 2D profile in detector units

    """
    def __init__(self,src):
        Distribution.__init__(self,src)
        self.major=src.shape['major']*np.sqrt(2.0) # to match the usual definition of a gaussian
        self.minor=src.shape['minor']*np.sqrt(2.0)
        self.sersic_index=0.5
        self.surf_area_units = src.shape['surf_area_units']

        
        self.prof = self._sersic_func(self.yrot, self.xrot, self.major, self.minor, self.sersic_index)
        
        self.normalize(src)

class FlatDistribution(Distribution):
    """
    Implement a source with a constant surface brightness as an ellipse, i.e. a tilted disc.
    
    Parameters
    ----------
    src: dict
        Details of the source geometry to generate, from the Source block of the input files.

    Attributes
    ----------
    minor: float
        Minor axis scale length
    major: float
        Major axis scale length
    pa: float
        Position angle in degrees of major axis measured positive in +X direction
    xoff: float
        Offset in X direction
    yoff: float
        Offset in Y direction
    prof: np.ndarray
        raw 2D profile in detector units
    norm_prof: np.ndarray
        normalized 2D profile in detector units

    Methods
    -------
        integrate_infinity():
            Normalization to flux at infinity means total flux, and that if all pixels in the 
            profile are summed up, they should sum to 1.
    surface_center():
        Normalization to the center is, in this case, a no-op, because the initial 
        definition of the disk sets the center (and everywhere else) to 1
    bright_effective():
        Normalization to average brightness within the effective radius (or here, radius)
        means that the intensity per square arcsecond should sum to 1. Thus, all we need 
        to take care of is the pixel scale in arcseconds^2
    """
    def __init__(self,src):
        Distribution.__init__(self,src)
        self.major=src.shape['major']
        self.minor=src.shape['minor']
        self.surf_area_units = src.shape['surf_area_units']


        self.prof = src.grid.elliptical_mask(self.major, self.minor, pa=self.pa, xoff=self.xoff, yoff=self.yoff)
        
        self.normalize(src)

    def integrate_infinity(self):
        self.norm_prof = self.prof / (np.pi * self.major * self.minor) * self.pixelscale()
        
    def surface_center(self):
        self.norm_prof = self.prof * self.pixelscale()

