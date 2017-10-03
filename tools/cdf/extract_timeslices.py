from base.base_tool import BaseTool
from base.decorators import input_tableview, input_output_table, parameter
from netCDF4 import Dataset
import numpy as np
import pandas as pd
import arcpy
from base.utils import validate_geodata, make_raster_name, raster_formats
from os.path import join
from math import cos, sin, atan2, asin, radians, degrees


tool_settings = {"label": "Extract Timeslices",
                 "description": "Extracts timeslices from CDF files",
                 "can_run_background": "True",
                 "category": "NetCDF"}


class ExtractTimeslicesCdfTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview(data_type="cdf")
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, raster_formats[0])
    @input_output_table(affixing=True)
    def getParameterInfo(self):
        """

        Returns:

        """

        return BaseTool.getParameterInfo(self)

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_tableview(self.calc, return_to_results=False)

        return

    def calc(self, data):
        """

        Args:
            data:

        Returns:

        """

        cdf = data["cdf"]

        nc_fprops = arcpy.NetCDFFileProperties(cdf)

        gvars = nc_fprops.getVariables()

        tll = ["time", "lat", "lon"]
        exc = ["time_bands", "time_bnds"]

        if not all(v in gvars for v in tll):
            raise ValueError("Georeferenced variable set {} was not found in {}".format(tll, cdf))

        rp = "Rotated_pole" if "Rotated_pole" in gvars else None  # flag for Rotated_pole projection

        if rp:
            self.info("'{}' is on a Rotated_pole projection".format(cdf))

        ovars = [v for v in gvars if v not in (tll + exc)]
        ov = ovars[-1]

        self.info("Exports will be based on variable {} ...".format(ov))

        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(4326)  # TO DO for now hard-wire wgs84

        if rp:
            self.info("Reading rotated pole array")
            ds = Dataset(cdf)
            ovz = ds.variables[ov]

        else:
            lyr_tmp = r"in_memory\tmp_lyr"
            arcpy.MakeNetCDFRasterLayer_md(cdf, ov, "lon", "lat", lyr_tmp, "time", None, "BY_VALUE")

            self.info("... creating temporary dataset ...")

            ras_tmp = r"in_memory\tmp_ras"
            arcpy.CopyRaster_management(lyr_tmp, ras_tmp)

            bandcount = int(arcpy.GetRasterProperties_management(ras_tmp, "BANDCOUNT").getOutput(0))

            self.info("Exporting {} individual bands from {}".format(bandcount, ras_tmp))

            for i in range(1, bandcount + 1):
                band = "Band_{}".format(i)
                i_ras = join(ras_tmp, band)
                dimension_value = sanitise_dimension(nc_fprops.getDimensionValue("time", i))
                o_ras = make_name(cdf, dimension_value, self.output_file_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)
                try:
                    arcpy.CopyRaster_management(i_ras, o_ras)
                    self.info("{} exported successfully".format(o_ras))

                    # at this point, if Rotated_pole, apply tx
                    df = arcpy.RasterToNumPyArray(o_ras)
                    # self.rotated_grid_transform(df)
                    self.info(df)

                    self.result.add_pass({"geodata}": o_ras, "source_geodata": cdf, "global_vars": gvars})

                except Exception as e:
                    self.warn("Failed to export {} : {}".format(o_ras, str(e)))
                    data.update({"error": e})
                    self.result.add_fail(data)

        try:
            arcpy.Delete_management(ras_tmp)
        except:
            pass

        try:
            arcpy.Delete_management(lyr_tmp)
        except:
            pass

        return

    def rotated_grid_transform(self, df, np_lon, np_lat, reverse=True):

        """
        Transformation script: Regular lon/lat <-> Rotated pole lon/lat

        This function transforms a coordinate tuple(lon,lat) in regular lon/lat
        degrees to a coordinate in rotated lon/lat degrees, and vice versa.

        Adapted from: http://ch.mathworks.com/matlabcentral/fileexchange/43435-rotated-grid-transform

        INSER SA, David Reksten, dr@inser.ch
        2017-05-03
        """

        """
        position:   tuple(lon, lat) = input coordinate
        reverse:  0 = Regular -> Rotated, 1 = Rotated -> Regular
        south_pole: tuple(lon, lat) = position of rotated south pole
        returns:    tuple(lon, lat) = output coordinate
        """

        self.info("Transforming raw coordinates...")

        # Convert degrees to radians
        df['rlat'] = df['lat'].apply(radians)
        df['rlon'] = df['lon'].apply(radians)

        self.info("Dataframe " * 10)
        self.info(df)

        # Rotations in radians
        theta = radians(90 + np_lat)  # Rotation around y-axis
        phi = radians(np_lon)  # Rotation around z-axis

        # Convert from spherical to cartesian coordinates
        df["x"] = df.apply(lambda x: cos(x["rlat"]) * cos(x["rlon"]))
        # x = cos(lon) * cos(lat)
        df["y"] = df.apply(lambda x: sin(x["rlon"]) * cos(x["rlat"]))
        # y = sin(lon) * cos(lat)
        df["z"] = sin(df["rlat"])
        # z = sin(lat)

        self.info("Dataframe " * 10)
        self.info(df)

        if not reverse:  # Regular -> Rotated

            df["x_new"] = df.apply(lambda x: cos(theta) * cos(phi) * x["x"] + cos(theta) * sin(phi) * x["y"] + sin(theta) * x["z"])
            df["y_new"] = df.apply(lambda x: -sin(phi) * x["x"] + cos(phi) * x["y"])
            df["z_new"] = df.apply(lambda x: -sin(theta) * cos(phi) * x["x"] - sin(theta) * sin(phi) * x["y"] + cos(theta) * x["z"])

        else:  # Rotated -> Regular
            self.info("reverse")
            phi = -phi
            theta = -theta

            df["x_new"] = df.apply(lambda x: cos(theta) * cos(phi) * x["x"] + sin(phi) * x["y"] + sin(theta) * cos(phi) * x["z"])
            df["y_new"] = df.apply(lambda x: -cos(theta) * sin(phi) * x["x"] + cos(phi) * x["y"] - sin(theta) * sin(phi) * x["z"])
            df["z_new"] = df.apply(lambda x: -sin(theta) * x["x"] + cos(theta) * x["z"])

        # Convert cartesian back to spherical coordinates (degrees)
        df["lon_new"] = df.apply(lambda x: degrees(atan2(x["y_new"], x["x_new"])))
        df["lat_new"] = degrees(asin(df["z_new"])) #asin(z_new)

        self.info("Dataframe " * 10)
        self.info(df)

        return df[["time", "lat_new", "lon_new"]]


def make_name(cdf, dimval, ws, fmt, pfx, sfx):
    """

    Args:
        cdf:
        dimval:
        ws:
        fmt:
        pfx:
        sfx:

    Returns:

    """

    likename = "{}_{}".format(cdf.replace(".", "_"), dimval)

    return make_raster_name(likename, ws, fmt, pfx, sfx)


def sanitise_dimension(d):
    """

    Args:
        d:

    Returns:

    """

    d = d.replace("/", "-")

    d = d.replace("\\", "-")

    return d

    # from netCDF4 import Dataset
    # import numpy

    # # lons, lats, weather_elements and time_values are numpy arrays
    # # print the longitude, latitude, time and temperature (T_SFC) at the first data point at the initial time
    # print lons[0], lats[0], time_values[0], weather_elements[0, 0, 0]
    # ncdf.close()


#
#     if __name__ == '__main__':
#         south_pole_relocated = (10, -40)  # COSMO-EU shift
#
#         cosmo_origo = rotated_grid_transform((0, 0), 2, south_pole_relocated)
#         print "Cosmo origo", cosmo_origo
#
#         print "Cosmo-EU lower left", rotated_grid_transform((-18.0, -20.0), 2, south_pole_relocated)
#         print "Cosmo-EU lower right", rotated_grid_transform((23.5, -20.0), 2, south_pole_relocated)
#         print "Cosmo-EU upper right", rotated_grid_transform((23.5, 21.0), 2, south_pole_relocated)
#         print "Cosmo-EU upper left", rotated_grid_transform((-18.0, 21.0), 2, south_pole_relocated)
#
#         print ""
#         print "Cosmo-7 lower left", rotated_grid_transform((-9.8, 35.16), 1, south_pole_relocated)
#         print "Cosmo-7 upper right", rotated_grid_transform((23.02, 56.84), 1, south_pole_relocated)
#
#         print ""
#         print "Cosmo-2 lower left", rotated_grid_transform((2.25, 42.72), 1, south_pole_relocated)
#         print "Cosmo-2 upper right", rotated_grid_transform((17.25, 49.76), 1, south_pole_relocated)


# def rotated_grid_transform(grid_in, option, SP_coor):
# function [grid_out] = rotated_grid_transform(grid_in, option, SP_coor)
#     lon = grid_in(:,1);
#     lat = grid_in(:,2);
#     lon = (lon*pi)/180; % Convert degrees to radians
#     lat = (lat*pi)/180;
#     SP_lon = SP_coor(1);
#     SP_lat = SP_coor(2);
#     theta = 90+SP_lat; % Rotation around y-axis
#     phi = SP_lon; % Rotation around z-axis
#     phi = (phi*pi)/180; % Convert degrees to radians
#     theta = (theta*pi)/180;
#     x = cos(lon).*cos(lat); % Convert from spherical to cartesian coordinates
#     y = sin(lon).*cos(lat);
#     z = sin(lat);
#     if option == 1 % Regular -> Rotated
#         x_new = cos(theta).*cos(phi).*x + cos(theta).*sin(phi).*y + sin(theta).*z;
#         y_new = -sin(phi).*x + cos(phi).*y;
#         z_new = -sin(theta).*cos(phi).*x - sin(theta).*sin(phi).*y + cos(theta).*z;
#     elseif option == 2 % Rotated -> Regular
#         phi = -phi;
#         theta = -theta;
#         x_new = cos(theta).*cos(phi).*x + sin(phi).*y + sin(theta).*cos(phi).*z;
#         y_new = -cos(theta).*sin(phi).*x + cos(phi).*y - sin(theta).*sin(phi).*z;
#         z_new = -sin(theta).*x + cos(theta).*z;
