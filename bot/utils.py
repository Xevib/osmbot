from osmapi import OsmApi
import psycopg2


def get_data_db(idenfiticador, geom_type=None, host='localhost', database='osm', user=None, password=None):
    conn = psycopg2.connect(host=host, database=database, user=user, password=password)
    psycopg2.extras.register_hstore(conn)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if geom_type == 'nod':
        cursor.execute('SELECT tags FROM planet_osm_point WHERE osm_id=%s limit 1;', (idenfiticador,))
    elif geom_type == 'way':
        cursor.execute('SELECT tags FROM planet_osm_line WHERE osm_id=%s limit 1;', (idenfiticador,))
    elif geom_type == 'rel':
        cursor.execute('SELECT tags FROM planet_osm_polygon WHERE osm_id=%s limit 1;', (idenfiticador,))
    else:
        return {}
    data = cursor.fetchone()
    if data:
        return {'tag': data[0], 'id': idenfiticador}
    else:
        return {}


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
