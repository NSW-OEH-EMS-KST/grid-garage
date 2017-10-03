from base.base_tool import BaseTool
from base.decorators import input_tableview, input_output_table
# from netCDF4 import Dataset
import arcpy
from base.utils import validate_geodata

tool_settings = {"label": "Describe",
                 "description": "Describe a CDF file",
                 "can_run_background": "True",
                 "category": "NetCDF"}


class DescribeCdfTool(BaseTool):
    """
    """
    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.iterate]
        self.polygon_srs = None

        return

    @input_tableview(data_type="cdf")
    @input_output_table()
    def getParameterInfo(self):
        """

        Returns:

        """

        return BaseTool.getParameterInfo(self)

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_tableview(self.cdf_describe, return_to_results=True)

        return

    def cdf_describe(self, data):
        """

        Args:
            data:

        Returns:

        """

        cdf = data["cdf"]

        validate_geodata(cdf, NetCdf=True)  # not implemented in function TODO

        nc_fprops = arcpy.NetCDFFileProperties(cdf)

        # get global attributes
        datts = [{att: nc_fprops.getAttributeValue("", att)} for att in nc_fprops.getAttributeNames("")]

        # get variables
        gvars = []
        vars = nc_fprops.getVariables()
        for nc_var in vars:

            vatts = [{att: nc_fprops.getAttributeValue(nc_var, att)} for att in nc_fprops.getAttributeNames(nc_var)]

            vdims = {}
            for nc_dim in nc_fprops.getDimensionsByVariable(nc_var):
                vdims[nc_dim] = {"size": nc_fprops.getDimensionSize(nc_dim), "type": nc_fprops.getFieldType(nc_dim)}

            var_d = {nc_var: {"type": nc_fprops.getFieldType(nc_var), "dimensions": vdims, "attributes": vatts}}

            gvars.append(var_d)

        # get dimensions
        ddims = []
        dims = nc_fprops.getDimensions()
        for nc_dim in dims:

            dvars = {nc_dim: nc_fprops.getFieldType(dvar) for dvar in nc_fprops.getVariablesByDimension(nc_dim)}

            ddim = {nc_dim: {"size": nc_fprops.getDimensionSize(nc_dim), "type": nc_fprops.getFieldType(nc_dim), "variables": dvars}}

            ddims.append(ddim)

        return {"geodata": cdf, "variables": vars, "dimensions": dims, "global_attributes_x": datts, "variables_x": gvars, "dimensions_x": ddims}
