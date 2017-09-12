from base.base_tool import BaseTool
from base.results import result
from base.method_decorators import input_tableview, input_output_table_with_output_affixes, parameter
from netCDF4 import Dataset
import arcpy
from base.utils import validate_geodata, make_raster_name, stats_type


tool_settings = {"label": "Export CDF",
                 "description": "Exports a CDF file to another format",
                 "can_run_background": "True",
                 "category": "NetCDF"}


@result
class ExportCdfTool(BaseTool):

    def __init__(self):

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]
        self.polygon_srs = None

        return

    @input_tableview("cdf_table", "Table for CDF Files", False, ["CDF:geodata:"])
    @parameter("var_field", "Variable Field", "Field", "Required", False, "Input", None, None, ["cdf_table"], None, None)
    @parameter("xdim", "X dimension", "Field", "Required", False, "Input", None, None, ["cdf_table"], None, None)
    @parameter("ydim", "Y dimension", "Field", "Required", False, "Input", None, None, ["cdf_table"], None, None)
    @parameter("bdim", "Band dimension", "Field", "Required", False, "Input", None, None, ["cdf_table"], None, None)
    @parameter("dvals", "Band dimension values", "Field", "Required", False, "Input", None, None, ["cdf_table"], None, None)
    @parameter("selec", "Value Selection Method", "Field", "Required", False, "Input", None, None, ["cdf_table"], None, None)
    @input_output_table_with_output_affixes
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.calc, "cdf_table", ["geodata"], return_to_results=True)

        return

    def calc(self, data):

        cdf = data["geodata"]
        validate_geodata(cdf, NetCdf=True)

        print "Making layer for {}".format(cdf)
        # arcpy.MakeNetCDFRasterLayer_md(cdf, var_field, x_dimension, y_dimension, out_raster_layer, {band_dimension}, {dimension_values}, {value_selection_method})

        ras_out = make_raster_name(cdf, self.output_file_workspace, None, self.output_file_workspace, self. output_filename_suffix)

        self.info("Saving {0} -->> {1} ...".format(cdf, ras_out))

        try:
            pass
        except Exception as e:
            if "ERROR 00276" in e.message:
                self.info("Caught the 00276")




        # MakeNetCDFRasterLayer_md (in_netCDF_file, variable, x_dimension, y_dimension, out_raster_layer, {band_dimension}, {dimension_values}, {value_selection_method})
        # arcpy.MakeNetCDFRasterLayer_md(cdf, var_field, x_dimension, y_dimension, out_raster_layer, {band_dimension}, {dimension_values}, {value_selection_method})


        # DefineProjection_management(in_dataset, coor_system)

        return {"geodata": ras_out, "source_geodata": cdf}

