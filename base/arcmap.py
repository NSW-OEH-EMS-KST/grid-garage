"""
Description
-----------
    This module provides some arcpy convenience functions

Author
------
    D.Bye, NSW OEH EMS KST

**Ecosystem Management Science**

**Knowledge Services Team**

Implementation
--------------
"""

import arcpy
refresh_active_view = arcpy.RefreshActiveView
refresh_toc = arcpy.RefreshTOC


def save_mxd():
    """ See:  https://desktop.arcgis.com/en/arcmap/10.4/analyze/arcpy-mapping/mapdocument-class.htm

    Returns:

    """

    return arcpy.mapping.MapDocument("CURRENT").save()


def list_layers():
    """ See:  https://desktop.arcgis.com/en/arcmap/10.4/analyze/arcpy-mapping/listlayers.htm

    Returns:

    """

    return arcpy.mapping.ListLayers(arcpy.mapping.MapDocument("CURRENT"), "*")  # if mxd else None


def get_dataframe0():
    """ See:  https://desktop.arcgis.com/en/arcmap/10.4/analyze/arcpy-mapping/listdataframes.htm

    Returns:
        dataframe (object): first of the dataframes in the mxd
    """

    return arcpy.mapping.ListDataFrames(arcpy.mapping.MapDocument("CURRENT"), "*")[0]  # if mxd else None


def add_tableview(table):
    """ See:  https://desktop.arcgis.com/en/arcmap/10.4/analyze/arcpy-mapping/addtableview.htm

    Args:
        table:
    """

    return arcpy.mapping.AddTableView(get_dataframe0(), arcpy.mapping.TableView(table))


def make_layer(item):
    """ See:  https://desktop.arcgis.com/en/arcmap/10.4/analyze/arcpy-mapping/layer.htm

    Args:
        item (str): path to layer source

    Returns:
        layer (object): the layer object

    """
    try:
        lyr = arcpy.mapping.Layer(item)

    except:
        msg = "Error creating layer from source {0}: {1}".format(item, arcpy.GetMessages())
        raise ValueError(msg)

    return lyr


def add_layer(geodata, add_position="AUTO_ARRANGE"):
    """ See:  https://desktop.arcgis.com/en/arcmap/10.4/analyze/arcpy-mapping/addlayer.htm

    Args:
        geodata (str): full path to geodata
        add_position (str):

    Returns:

    """
    lyr = make_layer(geodata)
    lyr.visible = False
    df = get_dataframe0()

    return arcpy.mapping.AddLayer(df, lyr, add_position)
