"""Useful constants.

"""
from rasterio.crs import CRS

WGS84_SRID = 4326
WGS84_CRS = CRS({'init': 'epsg:{:4d}'.format(WGS84_SRID)})

WEB_MERCATOR_SRID = 3857
WEB_MERCATOR_CRS = CRS({'init': 'epsg:{:4d}'.format(WEB_MERCATOR_SRID)})

# Best widely used, equal area projection according to
# http://icaci.org/documents/ICC_proceedings/ICC2001/icc2001/file/f24014.doc
# (found on https://en.wikipedia.org/wiki/Winkel_tripel_projection#Comparison_with_other_projections)
EQUAL_AREA_CRS = CRS({'proj': 'eck4'})

DEFAULT_SRID = WGS84_SRID
DEFAULT_CRS = WGS84_CRS
