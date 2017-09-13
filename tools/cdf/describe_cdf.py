from base.base_tool import BaseTool
from base.decorators import input_tableview, input_output_table
from netCDF4 import Dataset
import arcpy
from base.utils import validate_geodata


tool_settings = {"label": "Describe CDF",
                 "description": "Describe a CDF file",
                 "can_run_background": "True",
                 "category": "NetCDF"}


class DescribeCdfTool(BaseTool):

    def __init__(self):

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]
        self.polygon_srs = None

        return

    @input_tableview(data_type="cdf")
    @input_output_table
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.calc, return_to_results=True)

        return

    def calc(self, data):
        self.info(data)
        # cdf = data["cdf"]
        # validate_geodata(cdf, NetCdf=True)

        # print "Making layer for {}".format(cdf)
        # arcpy.MakeNetCDFRasterLayer_md(cdf, var_field, x_dimension, y_dimension, out_raster_layer, {band_dimension}, {dimension_values}, {value_selection_method})

        # ras_out = make_raster_name(cdf, self.output_file_workspace, None, self.output_file_workspace, self. output_filename_suffix)

        # self.info("Saving {0} -->> {1} ...".format(cdf, ras_out))

        # try:
        #     pass
        # except Exception as e:
        #     if "ERROR 00276" in e.message:
        #         self.info("Caught the 00276")




        # MakeNetCDFRasterLayer_md (in_netCDF_file, variable, x_dimension, y_dimension, out_raster_layer, {band_dimension}, {dimension_values}, {value_selection_method})
        # arcpy.MakeNetCDFRasterLayer_md(cdf, var_field, x_dimension, y_dimension, out_raster_layer, {band_dimension}, {dimension_values}, {value_selection_method})


        # DefineProjection_management(in_dataset, coor_system)

        return {"geodata": "dummy", "source_geodata": "dummy"}

