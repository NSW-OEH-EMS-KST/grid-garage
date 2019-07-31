from base.base_tool import BaseTool
from base.decorators import input_tableview, input_output_table, parameter
# from netCDF4 import Dataset
import arcpy
from base.utils import validate_geodata, make_table_name, raster_formats2
import numpy as np


tool_settings = {"label": "To Standard Grid",
                 "description": "Exports CDF files with a standard grid",
                 "can_run_background": "True",
                 "category": "NetCDF"}


class ToStandardGridCdfTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview(data_type="geodata")
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

        geodata = data["geodata"]

        # function[grid_out] = rotated_grid_transform(grid_in, option, SP_coor)
#     def rotated_grid_transform(self, grid_in, option, SP_coor)
#
#         lon = grid_in(:, 1);
#         lat = grid_in(:, 2);
#
#         lon = (lon * pi) / 180; % Convert degrees to radians
#         lat = (lat * pi) / 180;
#
#         SP_lon = SP_coor(1);
#         SP_lat = SP_coor(2);
#
#         theta = 90 + SP_lat; % Rotation around y - axis
#         phi = SP_lon; % Rotation around z - axis
#
#         phi = (phi * pi) / 180; % Convert degrees to radians
#         theta = (theta * pi) / 180;
#
#         x = cos(lon). * cos(lat); % Convert from spherical to cartesian coordinates
#         y = sin(lon). * cos(lat);
#         z = sin(lat);
#
#         if option == 1 % Regular -> Rotated
#
#         x_new = cos(theta). * cos(phi). * x + cos(theta). * sin(phi). * y + sin(theta). * z;
#         y_new = -sin(phi). * x + cos(phi). * y;
#         z_new = -sin(theta). * cos(phi). * x - sin(theta). * sin(phi). * y + cos(theta). * z;
#
#     elseif
#     option == 2 % Rotated -> Regular
#
#     phi = -phi;
#     theta = -theta;
#
#     x_new = cos(theta). * cos(phi). * x + sin(phi). * y + sin(theta). * cos(phi). * z;
#     y_new = -cos(theta). * sin(phi). * x + cos(phi). * y - sin(theta). * sin(phi). * z;
#     z_new = -sin(theta). * x + cos(theta). * z;
#
#
# end
#
# lon_new = atan2(y_new, x_new); % Convert  cartesian back to spherical coordinates
# lat_new = asin(z_new);
#
# lon_new = (lon_new * 180) / pi; % Convert radians back to degrees
# lat_new = (lat_new * 180) / pi;
#
# grid_out = [lon_new lat_new];

# scratch = arcpy.env.scratchFolder
        #
        # validate_geodata(cdf, NetCdf=True)
        #
        # nc_fprops = arcpy.NetCDFFileProperties(cdf)
        #
        # ncDim = nc_fprops.getDimensions()
        #
        # for dim in ncDim:
        #     print "%s (%s)" % (dim, nc_fprops.getFieldType(dim))
        #     top = nc_fprops.getDimensionSize(dim)
        #     for i in range(0, top):
        #         print nc_fprops.getDimensionValue(dim, i)
        #
        # return
        # # gvars = nc_fprops.getVariables()
        #
        # # for v in gvars:
        # #     self.info("Creating layer from {} on {} ...".format(cdf, v))
        #
        # ras_tmp = make_raster_name(cdf, scratch, "tif", self.output_filename_prefix, self.output_filename_suffix)
        #
        # ras_out = make_raster_name(cdf, self.output_file_workspace, self.raster_format, self.output_filename_prefix, self.output_filename_suffix)
        #
        # try:
        #         # The following will delete the TIF file that was created by CopyRaster tool.
        #         # arcpy.Delete_management(Output_Raster, "#")
        #
        #         if all(["lat", "lon", "time"] in gvars for v in gvars):
        #             arcpy.MakeNetCDFRasterLayer_md(cdf, v, "lon", "lat", ras_out, "", "time", "BY_VALUE")  #, {band_dimension}, {dimension_values}, {value_selection_method})
        #         elif all(["lat", "lon"] in gvars for v in gvars):
        #             arcpy.MakeNetCDFRasterLayer_md(cdf, v, "lon", "lat", ras_out, "", "", "BY_VALUE")  #, {band_dimension}, {dimension_values}, {value_selection_method})
        #         else:
        #             out = "{}_layer".format(v)
        #         # arcpy.MakeNetCDFRasterLayer_md(cdf, v, "x", "y", ras_out)  #, {band_dimension}, {dimension_values}, {value_selection_method})
        #         arcpy.MakeNetCDFRasterLayer_md(in_netCDF_file=cdf, variable=v, x_dimension="x", y_dimension="y",
        #                                        out_raster_layer=out, band_dimension="", dimension_values="", value_selection_method="BY_VALUE")
        #
        #         self.info("... attempting export -->> {} ...".format(ras_out))
        #                     # arcpy.MakeNetCDFRasterLayer_md(inNetCDF, variable, x_dimension, y_dimension, nowFile, band_dimension, dimension_values, valueSelectionMethod)
        #
        #         arcpy.CopyRaster_management(out, ras_out, "", "", "", "NONE", "NONE", "")
        #     arcpy.mapping.Layer(out).save(ras_out)
        #
        #     self.result.add_pass({"geodata": ras_out, "source_geodata": cdf})
        #
        # except Exception as e:
        #     self.error("FAILED exporting {}: {}".format(cdf, str(e)))
        #     self.result.add_fail(data)

        return


def extractAllNetCDF(cdf, variable, dimension, x_dimension, y_dimension, band_dimension, value_selection_method="BY_VALUE"):
    """

    Args:
        cdf:
        variable:
        dimension:
        x_dimension:
        y_dimension:
        band_dimension:
        value_selection_method:
    """

    # variable = "RRt_10m"
    # x_dimension = "lon"
    # y_dimension = "lat"
    # band_dimension = ""
    # dimension = "time"
    # value_selection_method = "BY_VALUE"

    outLoc = "E:/New Folder/"
    inNetCDF = "E:/netCDFFiles/RRt.nc"

    nc_FP = arcpy.NetCDFFileProperties(cdf)
    nc_Dim = nc_FP.getDimensions()

    for dimension in nc_Dim:

        top = nc_FP.getDimensionSize(dimension)

        for i in range(0, top):

            if dimension == "time":
                dimension_value = nc_FP.getDimensionValue(dimension, i)
                nowFile = str(dimension_value)

                # THIS IS THE NEW CODE HERE
                dv1 = ["time", dimension_value]
                dimension_values = [dv1]
                # END NEW CODE

                arcpy.MakeNetCDFRasterLayer_md(inNetCDF, variable, x_dimension, y_dimension, nowFile, band_dimension, dimension_values,
                                               value_selection_method)
                arcpy.CopyRaster_management(nowFile, outLoc + nowFile + ".img", "", "", "", "NONE", "NONE", "")
                print dimension_values, i


                    # # Copy the NetCDF layer as a TIF file.
    # arcpy.CopyRaster_management(Input_Name, Output_Raster)
    # arcpy.AddMessage(Output_Raster + " " + "created from NetCDF layer")
    #
    # # Reading number of band information from saved TIF
    # bandcount = arcpy.GetRasterProperties_management(Output_Raster, "BANDCOUNT")
    # resultValue = bandcount.getOutput(0)
    #
    # count = 1
    # arcpy.AddMessage("Exporting individual bands from" + Output_Raster)
    #
    # # Loop through the bands and copy bands as a seperate TIF file.
    # while count <= int(resultValue):
    #     Input_Raster_Name = Output_Raster + os.sep + "Band_" + str(count)
    #     Output_Band = Output_Folder + os.sep + "Band_" + str(count) + ".tif"
    #     arcpy.CopyRaster_management(Input_Raster_Name, Output_Band)
    #     arcpy.AddMessage("Band_" + str(count) + ".tif" + " " "exported" + " " + "successfully")
    #     count += 1
    #
    # # The following will delete the TIF file that was created by CopyRaster tool.
    # arcpy.Delete_management(Output_Raster, "#")
    #
    # arcpy.AddMessage("Tool Executed Successfully")
# def extractAllNetCDF():
#
#     variable = "RRt_10m"
#     x_dimension = "lon"
#     y_dimension = "lat"
#     band_dimension = ""
#     dimension = "time"
#     valueSelectionMethod = "BY_VALUE"
#
#     outLoc = "E:/New Folder/"
#     inNetCDF = "E:/netCDFFiles/RRt.nc"
#
#     nc_FP = arcpy.NetCDFFileProperties(inNetCDF)
#     nc_Dim = nc_FP.getDimensions()
#
#     for dimension in nc_Dim:
#
#         top = nc_FP.getDimensionSize(dimension)
#
#         for i in range(0, top):
#
#             if dimension == "time":
#
#                 dimension_values = nc_FP.getDimensionValue(dimension, i)
#                 nowFile = str(dimension_values)
#
#                 #THIS IS THE NEW CODE HERE
#                 dv1 = ["time", dimension_value]
#                 dimension_values = [dv1]
#                 #END NEW CODE
#
#                 arcpy.MakeNetCDFRasterLayer_md(inNetCDF, variable, x_dimension, y_dimension, nowFile, band_dimension, dimension_values, valueSelectionMethod)
#                 arcpy.CopyRaster_management(nowFile, outLoc + nowFile + ".img", "", "", "", "NONE", "NONE", "")
#                 print dimension_values, i

