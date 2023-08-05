from os.path import abspath
from os.path import dirname
from os.path import join

from osgeo.osr import SpatialReference
from pyproj import Proj
from six import string_types

__author__ = 'Gregory Halverson'

with open(join(abspath(dirname(__file__)), 'version.txt')) as f:
    __version__ = f.read()


def proj4_to_mapping(proj4):
    mapping = {}
    parameters = proj4.strip().split()

    for parameter in parameters:
        print(parameter)

        if '=' in parameter:
            key, value = parameter.split('=')
            key = key.lstrip('+')
        else:
            key = parameter.lstrip('+')
            value = True

        mapping[key] = value

    return mapping


def mapping_to_proj4(mapping):
    raise NotImplementedError("conversion from mapping to PROJ4 not yet implemented")


class CRS(object):
    def __init__(
            self,
            init=None,
            epsg=None,
            proj4=None,
            gdal=None,
            pyproj=None,
            wkt=None,
            esri=None,
            mapping=None,
            **kwargs):

        self._proj4 = None
        self._gdal = None

        if epsg is not None:
            self._gdal = SpatialReference()
            error = self._gdal.ImportFromEPSG(int(epsg))

            if error != 0:
                raise ValueError("unable to interpret EPSG code '{}'".format(epsg))

        elif isinstance(init, CRS):
            self._proj4 = init._proj4
            self._gdal = init._gdal

        elif isinstance(init, Proj):
            self._proj4 = init.srs

        elif isinstance(pyproj, Proj):
            self._proj4 = pyproj.srs

        elif isinstance(init, SpatialReference):
            self._gdal = init

        elif isinstance(gdal, SpatialReference):
            self._gdal = gdal

        elif isinstance(init, dict):
            self._proj4 = mapping_to_proj4(init)

        elif isinstance(mapping, dict):
            self._proj4 = mapping_to_proj4(mapping)

        elif isinstance(init, string_types):
            projection_string = str(init)

            self._gdal = SpatialReference()

            error = -1

            if error != 0:
                try:
                    error = self._gdal.ImportFromProj4(projection_string)
                except:
                    error = -1

            if error != 0:
                try:
                    error = self._gdal.ImportFromWkt(projection_string)
                except:
                    error = -1

            if error != 0:
                try:
                    error = self._gdal.ImportFromESRI(projection_string)
                except:
                    error = -1

            if error != 0:
                try:
                    error = self._gdal.ImportFromUrl(projection_string)
                except:
                    error = -1

            if error != 0:
                try:
                    error = self._gdal.ImportFromXML(projection_string)
                except:
                    error = -1

            if error != 0:
                try:
                    error = self._gdal.ImportFromEPSG(projection_string)
                except:
                    error = -1

            if error != 0:
                try:
                    error = self._gdal.ImportFromEPSGA(projection_string)
                except:
                    error = -1

            if error != 0:
                try:
                    error = self._gdal.ImportFromERM(projection_string)
                except:
                    error = -1

            if error != 0:
                try:
                    error = self._gdal.ImportFromMICoordSys(projection_string)
                except:
                    error = -1

            if error != 0:
                try:
                    error = self._gdal.ImportFromOzi(projection_string)
                except:
                    error = -1

            if error != 0:
                try:
                    error = self._gdal.ImportFromPCI(projection_string)
                except:
                    error = -1

            if error != 0:
                try:
                    error = self._gdal.ImportFromUSGS(projection_string)
                except:
                    error = -1

            if error != 0:
                pyproj = Proj(projection_string)
                self._proj4 = pyproj.srs

        elif proj4 is not None:
            self._proj4 = proj4
            self._gdal = SpatialReference()
            error = self._gdal.ImportFromProj4(proj4)

            if error != 0:
                raise ValueError("unable to interpret PROJ4 string '{}'".format(proj4))

        elif wkt is not None:
            self._gdal = SpatialReference()
            error = self._gdal.ImportFromWkt(wkt)

            if error != 0:
                raise ValueError("unable to interpret WKT string '{}'".format(wkt))

        elif esri is not None:
            self._gdal = SpatialReference()
            error = self._gdal.ImportFromESRI(esri)

            if error != 0:
                raise ValueError("unable to interpret ESRI string '{}'".format(esri))

    @staticmethod
    def from_epsg(epsg):
        return CRS(epsg=epsg)

    @staticmethod
    def from_proj4(proj4):
        return CRS(proj4=proj4)

    @staticmethod
    def from_wkt(wkt):
        return CRS(wkt=wkt)

    @staticmethod
    def from_esri(esri):
        return CRS(esri=esri)

    @staticmethod
    def from_pyproj(pyproj):
        return CRS(pyproj=pyproj)

    @staticmethod
    def from_gdal(gdal):
        return CRS(gdal=gdal)

    @property
    def proj4(self):
        if self._proj4 is not None:
            pass
        elif self._gdal is not None:
            self._proj4 = self._gdal.ExportToProj4()
        else:
            raise ValueError("unable to produce PROJ4 string")

        return self._proj4

    @property
    def pyproj(self):
        return Proj(self.proj4)

    @property
    def mapping(self):
        return proj4_to_mapping(self.proj4)

    @property
    def gdal(self):
        if self._gdal is not None:
            pass
        elif self._proj4 is not None:
            self._gdal = SpatialReference()
            self._gdal.ImportFromProj4(self._proj4)

        return self._gdal

    @property
    def wkt(self):
        return self.gdal.ExportToWkt()

    @property
    def pretty_wkt(self):
        return self.gdal.ExportToPrettyWkt()

    @property
    def usgs(self):
        return self.gdal.ExportToUSGS()

    @property
    def xml(self):
        return self.gdal.ExportToXML()

    @property
    def pci(self):
        return self.gdal.ExportToPCI()

    @property
    def mi(self):
        return self.gdal.ExportToMICoordSys()

    @property
    def is_latlon(self):
        return self.pyproj.is_latlong()

    @property
    def is_geocentric(self):
        return self.pyproj.is_geocent()

    @property
    def _cstype(self):
        return 'GEOGCS' if self.is_latlon else 'PROJCS'

    @property
    def authority(self):
        return self.gdal.GetAuthorityName(self._cstype)

    @property
    def code(self):
        return self.gdal.GetAuthorityCode(self._cstype)

    def __repr__(self):
        return "CRS('{}')".format(self.proj4)
