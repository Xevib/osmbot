from osmapi import OsmApi


def getData(id, geom_type=None):
    osm_data = None
    api = OsmApi()
    if geom_type is None:
        try:
            osm_data = api.NodeGet(int(id))
            if osm_data is None:
                try:
                    osm_data = api.WayGet(int(id))
                except:
                    osm_data = api.RelationGet(int(id))
        except:
            osm_data = None
    elif geom_type == 'nod':
        osm_data = api.NodeGet(int(id))
    elif geom_type == 'way':
            osm_data = api.WayGet(int(id))
    elif geom_type == 'rel':
        osm_data = api.RelationGet(int(id))
    return osm_data
