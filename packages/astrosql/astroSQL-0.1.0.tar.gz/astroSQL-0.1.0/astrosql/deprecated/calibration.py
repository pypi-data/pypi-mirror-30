"""Calibrate aperature photometry

Example: 
    $ astrosql calibrate image.fits reference.txt --band clear

    # Experimental feature 'from' keyword
    $ astrosql calibrate image.fits --from "apass 5 5 1" --band clear

"""
import os
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.table import Table
from astropy.io import fits
from astropy.io import ascii
from astropy import units as u
from astropy import wcs

def gr2R(g, r):
    """Use the Lupton 2005 transformations listed at
    http://classic.sdss.org/dr7/algorithms/sdssUBVRITransform.html
    to transform g,r passbands into R.

    Returns array of R and float estimate of systematic RMS error of transformation.
    """
    R = r - 0.1837*(g - r) - 0.0971
    sigma = 0.0106
    return R, sigma

def ri2I(r, i):
    """Use the Lupton 2005 transformations listed at
    http://classic.sdss.org/dr7/algorithms/sdssUBVRITransform.html
    to transform r,i passbands into I.

    Returns array of I and float estimate of systematic RMS error of transformation.
    """
    I = r - 1.2444*(r - i) - 0.3820
    sigma = 0.0078
    return I, sigma

def xy2rd(image, x, y):
    """Returns the right ascension and declination coordinates (degrees) given x and y cartesian coordinates.

    Parameters:
    -----------
    image : fits
    x, y : float or array_like
        A single number or array containing the coordinates
    """
    # Parse the WCS keywords in the primary HDU and get ra & dec
    w = wcs.WCS(image[0].header)
    ra, dec = w.wcs_pix2world(x, y, 1) * u.deg

    # Check whether floating point error is > 1e-6
    x2, y2 = w.wcs_world2pix(ra, dec, 1)
    assert np.max(np.abs(x - x2)) < 1e-6
    assert np.max(np.abs(y - y2)) < 1e-6

    return {'RA': ra, 'DEC': dec}

def guess_band(filename):
    """ Guess the passband using the image's filename"""
    if '_B_' in filename:
        passband = 'B'
    elif '_V_' in filename:
        passband = 'V'
    elif '_R_' in filename:
        passband = 'R'
    elif '_I_' in filename:
        passband = 'I'
    else:
        passband = 'clear'
    return passband

def zeropoint_mean(image, reference, mag='3.5p', passband='clear'):
    """Returns the average zeropoint difference between image and reference.
    
    image : dict-like 
    reference : dict-like
    mag : str
        The magnitude to be used for zeropoint average
    passband : str
        The passband of the image. Accepts B, V, R, or I
    """
    if passband == 'clear' or passband == 'R':
        reference_mag = gr2R(reference['g'], reference['r'])[0]
    elif passband == 'I':
        reference_mag = ri2I(reference['r'], reference['i'])[0]
    elif passband == 'B' or passband == 'V':
        reference_mag = reference[passband]
    else:
        raise NotImplementedError("{} passband must be either of BVRI".format(passband))

    zeropoints = reference_mag - image[mag]
    zeropoints = zeropoints[np.isfinite(zeropoints)] # np.isfinite ignores non-finite values like NaN
    return np.mean(zeropoints)

def apply_zeropoint(image, zeropoint):
    """Takes a zeropoint and adds it to all magnitude's zeropoint

    Parameters:
    -----------
    image : dict-like
    zeropoint : float
    """
    mag_columns = [x for x in image.colnames if 'p' in x]
    for mag in mag_columns:
        image[mag] += zeropoint

def main(args):
    """ Main function operates the following steps:
    
    1. Get fits and aperature datafile
    2. Get or guess the passband from filename
    3. Get ra and dec from fits
    4. Match image and reference with SkyCoord using ra's and dec's
    5. Calculate zeropoint
    5. Apply zeropoint to aperature data.
    """
    image_name = os.path.splitext(args.image)[0][0:-2]

    names = "id   ximage   yimage    3.5p   3.5err    5.0p  5.0err    7.0p   7.0err    9.0p   9.0err   1.0fh   1.0err   1.5fh  1.5err   2.0fh   2.0err".split()
    print(names)
    
    try:
        image = Table.read('{}_apt.txt'.format(image_name),
                           format='ascii', names=names)
    except FileNotFoundError:
        image = Table.read('{}_apt.txt'.format(image_name))

    image_fits = fits.open(args.image)
    reference = Table.read(args.reference, format='ascii')

    passband = args.passband
    if not passband:
        passband = guess_band(args.image)

    print(image)
    print(reference)
    image_radec = xy2rd(image_fits, image['ximage'], image['yimage'])

    image_catalog = SkyCoord(ra=image_radec['RA'], dec=image_radec['DEC'])
    reference_catalog = SkyCoord(
        ra=(reference['RA'] * u.deg), dec=(reference['DEC']*u.deg))

    # Match image catalog to reference catalog and get zeropoint
    match_id, sep2d, dist3d = image_catalog.match_to_catalog_sky(
        reference_catalog)
    reference = reference[match_id]
    zeropoint = zeropoint_mean(image, reference, mag='3.5p', passband=passband)

    # Apply zeropoint
    apply_zeropoint(image, zeropoint)

    # Save calibrated aperature data
    if args.outfile:
        ascii.write(image, output=args.outfile, delimiter='\t',
                    overwrite=True)
        print('Write to {}: Success'.format(args.outfile))
    return image
