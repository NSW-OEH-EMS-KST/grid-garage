from base.base_tool import BaseTool
from base.decorators import input_tableview, input_output_table_with_output_affixes, parameter
# from netCDF4 import Dataset
import arcpy
from base.utils import validate_geodata, make_raster_name, raster_formats
from os.path import join

tool_settings = {"label": "Extract Timeslices",
                 "description": "Extracts timeslices from CDF files",
                 "can_run_background": "True",
                 "category": "NetCDF"}


class ExtractTimeslicesCdfTool(BaseTool):

    def __init__(self):

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]

        return

    @input_tableview(data_type="cdf")
    @parameter("raster_format", "Format for output rasters", "GPString", "Required", False, "Input", raster_formats, None, None, raster_formats[0])
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.calc, return_to_results=False)

        return

    def calc(self, data):

        cdf = data["cdf"]

        nc_fprops = arcpy.NetCDFFileProperties(cdf)

        gvars = nc_fprops.getVariables()

        rp = "Rotated_pole"

        if rp in gvars:
            raise ValueError("Could not create layer from {}, variable {} was found".format(cdf, rp))
            # self.warn(e)
            # data.update({"error": e})
            # self.result.add_fail(data)
            # return

        tll = ["time", "lat", "lon"]
        exc = ["time_bands", "time_bnds"]

        if not all(v in gvars for v in tll):
            raise ValueError("Variable set {} was not found".format(cdf, tll))
            # self.warn(e)
            # data.update({"error": e})
            # self.result.add_fail(data)
            # return

        ovars = [v for v in gvars if v not in (tll + exc)]
        ov = ovars[-1]

        self.info("Creating layer from {} on {} ...".format(cdf, ov))

        lyr_tmp = r"in_memory\tmp_lyr"

        arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(4326)  # TO DO for now hard-wire wgs84

        # try:
        # arcpy.MakeNetCDFRasterLayer_md(cdf, ov, "lon", "lat", lyr_tmp, "time", None, "BY_VALUE")  #, {band_dimension}, {dimension_values}, {value_selection_method})
        arcpy.MakeNetCDFRasterLayer_md(cdf, ov, "x", "y", lyr_tmp, "time", None, "BY_VALUE")  #, {band_dimension}, {dimension_values}, {value_selection_method})

        # except Exception as e:
        #     self.warn(e)
        #     data.update({"error": e})
        #     self.result.add_fail(data)
        #     return

        self.info("... creating temporary dataset ...")

        ras_tmp = r"in_memory\tmp_ras"
        # try:
        arcpy.CopyRaster_management(lyr_tmp, ras_tmp)

        # except Exception as e:
        #     self.warn(e)
        #     data.update({"error": e})
        #     self.result.add_fail(data)
        #     return

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


def make_name(cdf, dimval, ws, fmt, pfx, sfx):

    likename = "{}_{}".format(cdf.replace(".", "_"), dimval)

    return make_raster_name(likename, ws, fmt, pfx, sfx)


def sanitise_dimension(d):

    d = d.replace("/", "-")

    d = d.replace("\\", "-")

    return d
