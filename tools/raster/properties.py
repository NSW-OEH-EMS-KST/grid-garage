from base.base_tool import BaseTool
from base.results import result
from base.utils import validate_geodata
from base.method_decorators import input_output_table, input_tableview
from arcpy import Describe, GetRasterProperties_management
from os.path import join
from collections import OrderedDict

tool_settings = {"label": "Band Properties",
                 "description": "Reports raster band properties",
                 "can_run_background": "True",
                 "category": "Raster"}

describe_field_groups = dict(
    raster=["bandCount", "compressionType", "format", "permanent", "sensorType"],
    raster_band_properties=["height", "isInteger", "meanCellHeight", "meanCellWidth", "noDataValue", "pixelType", "primaryField", "tableType", "width"],
    raster_band_properties_ex=["MINIMUM", "MAXIMUM", "MEAN", "STD", "UNIQUEVALUECOUNT", "TOP", "LEFT", "RIGHT", "BOTTOM", "CELLSIZEX", "CELLSIZEY", "VALUETYPE",
                               "COLUMNCOUNT", "ROWCOUNT", "BANDCOUNT", "ANYNODATA", "ALLNODATA", "SENSORNAME", "PRODUCTNAME", "ACQUSITIONDATE", "SOURCETYPE",
                               "SUNELEVATION", "CLOUDCOVER", "SUNAZIMUTH", "SENSORAZIMUTH", "SENSORELEVATION", "OFFNADIR", "WAVELENGTH"])


@result
class BandPropetiesRasterTool(BaseTool):
    def __init__(self):

        BaseTool.__init__(self, tool_settings)

        self.execution_list = [self.iterate]

        return

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:"])
    @input_output_table
    def getParameterInfo(self):

        return BaseTool.getParameterInfo(self)

    def iterate(self):

        self.iterate_function_on_tableview(self.describe, "raster_table", ["geodata"], return_to_results=True)

        return

    def describe(self, data):

        ras = data["geodata"]

        validate_geodata(ras, raster=True)

        self.info("Getting properties for {0}".format(ras))

        r = Describe(ras)

        desc = {"raster_{}".format(p): getattr(r, p, None) for p in describe_field_groups["raster"]}

        bands = [b.name for b in getattr(r, "children", [])]

        for band in bands:
            b = join(ras, band)
            rb = Describe(b)
            desc2 = {"{}_{}".format(band, att): getattr(rb, att, None) for att in describe_field_groups["raster_band_properties"]}
            desc.update(desc2)
            desc2 = {}
            for p in describe_field_groups["raster_band_properties_ex"]:  #have to wrap this, UNIQUEVALUECOUNT not present for floats
                try:
                    desc2["{}_{}".format(band, p)] = GetRasterProperties_management(ras, p, band).getOutput(0)
                except:
                    desc2["{}_{}".format(band, p)] = None

            # desc2 = {"{}_{}".format(band, p): GetRasterProperties_management(ras, p, band).getOutput(0) for p in describe_field_groups["raster_band_properties_ex"]}
            desc.update(desc2)

        # return an ordered dictionary
        od = OrderedDict()
        od["geodata"] = ras
        for i, attributes in sorted(desc.items()):
            od[i] = attributes

        return od
