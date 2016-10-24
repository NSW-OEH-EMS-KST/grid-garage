import arcpy


class ArcmapUtils(object):
    def __init__(self):
        self.get_mxd = get_mxd
        self.save_mxd = save_mxd
        self.list_layers = list_layers
        self.get_dataframe0 = get_dataframe0
        self.add_tableview = add_tableview
        self.add_layer = add_layer
        self.refresh_active_view = arcpy.RefreshActiveView
        self.refresh_toc = arcpy.RefreshTOC
        return


def get_mxd():
    return arcpy.mapping.MapDocument("CURRENT")


def save_mxd():
    mxd = get_mxd()
    if mxd:
        mxd.save()
    return


def list_layers(self):
    mxd = self.get_mxd()
    return arcpy.mapping.ListLayers(mxd, "*") if mxd else None


def get_dataframe0():
    mxd = get_mxd()
    return arcpy.mapping.ListDataFrames(mxd, "*")[0] if mxd else None


def add_tableview(table):
    arcpy.mapping.AddTableView(get_dataframe0(), arcpy.mapping.TableView(table))


def make_layer(item):
    try:
        lyr = arcpy.mapping.Layer(item)
    except:
        msg = "Error creating layer from source {0}: {1}".format(item, arcpy.GetMessages())
        raise ValueError(msg)
    return lyr


def add_layer(geodata, add_position="AUTO_ARRANGE"):
    lyr = make_layer(geodata)
    lyr.visible = False
    df = get_dataframe0()
    arcpy.mapping.AddLayer(df, lyr, add_position)
    return
