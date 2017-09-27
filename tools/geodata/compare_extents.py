from base.base_tool import BaseTool
import collections
import arcpy
import base.utils
from base.decorators import input_output_table, input_tableview, parameter

tool_settings = {"label": "Compare Extents",
                 "description": "Compare Extents...",
                 "can_run_background": "True",
                 "category": "Geodata"}


class CompareExtentsGeodataTool(BaseTool):
    """
    """

    def __init__(self):
        """

        Returns:

        """

        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.aoi_extent = None
        self.aoi_srs_name = None
        self.aoi_extent_string = None

        return

    @input_tableview()
    @parameter("aoi_dataset", "Dataset (Area of Interest) to compare with", ["DEFeatureClass", "DERasterDataset"], "Required", False, "Input", None, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        """

        Returns:

        """

        return BaseTool.getParameterInfo(self)

    def initialise(self):
        """

        Returns:

        """

        self.aoi_extent = arcpy.Describe(self.aoi_dataset).extent
        self.aoi_srs_name = self.aoi_extent.spatialReference.name
        self.aoi_extent_string = "{0} {1}".format(self.aoi_extent, self.aoi_srs_name)

        return

    def iterate(self):
        """

        Returns:

        """

        self.iterate_function_on_tableview(self.compare, "geodata_table", ["geodata"], return_to_results=True)

        return

    def compare(self, data):
        """

        Args:
            data:

        Returns:

        """

        ds_in = data["geodata"]
        base.utils.validate_geodata(ds_in, srs_known=True)

        try:
            ds_extent = arcpy.Describe(ds_in).extent
        except:
            raise ValueError("Could not obtain extent from {0}".format(ds_in))

        # default results
        con = dis = ovr = equ = wit = tch = "Unknown"
        ds_extent_trx = "Unknown"
        ds_extent_raw = "{0} {1}".format(ds_extent, ds_extent.spatialReference.name)

        if ds_extent.spatialReference.name != "Unknown":
            x = ds_extent.projectAs(self.aoi_extent.spatialReference)
            con = x.contains(self.aoi_extent)
            dis = x.disjoint(self.aoi_extent)
            ovr = x.overlaps(self.aoi_extent)
            equ = x.equals(self.aoi_extent)
            wit = x.within(self.aoi_extent)
            tch = x.touches(self.aoi_extent)
            ds_extent_trx = "{0} {1}".format(x, x.spatialReference.name)

        r = collections.OrderedDict([
            ("geodata", ds_in),
            ("extent_aoi", self.aoi_extent_string),
            ("extent_dataset_raw", ds_extent_raw),
            ("extent_dataset_trx", ds_extent_trx),
            ("contains_aoi", con), ("within_aoi", wit),
            ("disjoint_aoi", dis), ("overlaps_aoi", ovr),
            ("equals_aoi", equ), ("touches_aoi", tch)])

        # self.info(self.result.add_pass(r))

        return r
