from __future__ import absolute_import, unicode_literals
from osmapi import OsmApi


def getData(id, geom_type='nod'):
    osm_data = None
    api = OsmApi()
    if geom_type == 'nod':
        osm_data = api.NodeGet(int(id))
    elif geom_type == 'way':
        osm_data = api.WayGet(int(id))
    elif geom_type == 'rel':
        osm_data = api.RelationGet(int(id))
    return osm_data
