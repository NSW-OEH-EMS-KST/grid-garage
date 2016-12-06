from base.base_tool import BaseTool
from base.class_decorators import results, geodata
from base.method_decorators import input_tableview, input_output_table, parameter
from base.geodata import DoesNotExistError, get_search_cursor_rows
from base.utils import get_ordered_dict_from_keys, split_up_filename, find_date
from arcpy import MakeFeatureLayer_management, Clip_management

tool_settings = {"label": "Zonal Counts",
                 "description": "Zonal counts...",
                 "can_run_background": "True",
                 "category": "Raster"}


@results
@geodata
class ZonalCountsRasterTool(BaseTool):
    def __init__(self):
        BaseTool.__init__(self, tool_settings)
        self.execution_list = [self.initialise, self.iterate]
        self.zone = None
        self.zone_field = None
        self.zone_vals = None
        self.value_keys = None
        self.value_dict = None
        self.total_count = 0
        self.zone_ids = None
        self.zone_layers = {}

    @input_tableview("raster_table", "Table for Rasters", False, ["raster:geodata:none"])
    @parameter("zone", "Zone Features", "GPFeatureLayer", "Required", False, "Input", ["Polygon"], None, None, None)
    @parameter("zone_field", "Field of Interest", "Field", "Required", False, "Input", None, None, ["zone"], None)
    @parameter("zone_vals", "Values to Count (comma separated)", "GPString", "Required", False, "Input", None, None, None, None)
    @input_output_table
    def getParameterInfo(self):
        return BaseTool.getParameterInfo(self)

    def initialise(self):
        p = self.get_parameter_dict()
        self.zone = p["zone"]
        self.zone_field = p["zone_field"]
        self.zone_vals = sorted([float(v) for v in p["zone_vals"].split(",")])
        self.value_keys = ['val_{0}'.format(k) for k in self.zone_vals]
        self.value_dict = None
        self.zone_ids = get_search_cursor_rows(self.zone, ['OID@', self.zone_field])
        # create single feature data sets
        self.send_info('Extracting individual zone features from {0}'.format(self.zone))
        _, __, vec_name, vec_ext = split_up_filename(self.zone)
        for zone_id in self.zone_ids:
            zl = self.geodata.make_vector_name('zone_{0}'.format(zone_id), self.results.output_workspace, vec_ext)
            MakeFeatureLayer_management(self.zone_ids, zl, where_clause='OBJECTID={0}'.format(zone_id))
            self.zone_layers[zone_id] = zl

    def iterate(self):
        self.iterate_function_on_tableview(self.count, "raster_table", ["raster"])
        return

    def count(self, data):
        r_in = data["raster"]
        if not self.geodata.exists(r_in):
            raise DoesNotExistError(r_in)

        _, __, ras_name, ras_ext = split_up_filename(r_in)

        for zone_id in self.zone_ids:
            self.send_info('Processing {0} against zone {1}'.format(r_in, zone_id))
            lyr_zone = self.zone_layers[zone_id]

            # clip the source raster to current zone
            self.send_info("...clipping to feature...")
            ras_clip = self.make_raster_name('{0}_{1}_clip'.format(r_in, zone_id), ext=ras_ext)
            Clip_management(r_in, '#', ras_clip, lyr_zone, "#", "ClippingGeometry")

            # get class counts - set up cursor
            self.send_info("...counting values...")
            where = 'VALUE=' + ' OR VALUE='.join([str(v) for v in self.zone_vals])
            sc = get_search_cursor_rows(ras_clip, ['VALUE', 'COUNT'], where)

            # init the value dict
            self.value_dict = get_ordered_dict_from_keys(self.zone_vals, 0)

            # suck up the counts
            for val, cnt in sc:
                self.value_dict[val] = int(cnt)

            dt = find_date(ras_name)[0]
            res = {"geodata": r_in, "source_geodata": r_in, "date_time": dt,
                   "zone_data": self.zone_ids, "zone_field": self.zone_field, "zone_id": zone_id}.update(self.value_dict)
            self.results.add(res)

        return
