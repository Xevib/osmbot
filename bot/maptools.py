# -*- coding: utf-8 -*-
import requests
import math


WGS84_a = 6378137.0  # Major semiaxis [m]
WGS84_b = 6356752.3  # Minor semiaxis [m]


def download(bbox, _, imageformat='png', zoom=19, scale=None):
    scale_zoom = {19: 804,
                  18: 1300,
                  17: 2600,
                  16: 5150,
                  15: 10500,
                  14: 20500,
                  13: 41000,
                  12: 82000,
                  11: 165000,
                  10: 330000,
                  9: 655000,
                  8: 1350000,
                  7: 2650000,
                  6: 5250000,
                  5: 10500000,
                  4: 21000000,
                  3: 42000000,
                  2: 77500000,
                  1: 180000000}
    if int(zoom) not in scale_zoom:
        zoom = 19
    params = {}
    params['bbox'] = ",".join(map(str, bbox))
    params['format'] = imageformat
    if scale is None:
        params['scale'] = scale_zoom[int(zoom)]
    else:
        params['scale'] = scale
    print str(params)
    try:
        response = requests.get("http://render.openstreetmap.org/cgi-bin/export", params=params, timeout=7)
    except:
        raise ValueError(_('Map too large!')+' \xF0\x9F\x98\xB1\n'+_('Please, reduce the bounding box')+' \xE2\x9C\x82 '+_('or the scale (zoom level)')+' \xF0\x9F\x94\x8D')
    if response.content =='<html>\n<head>\n<title>Error</title>\n</head>\n<body>\n<h1>Error</h1>\n<p>Map too large</p>\n</body>\n</html>\n':
        raise ValueError(_('Map too large!')+' \xF0\x9F\x98\xB1\n'+_('Please, reduce the bounding box')+' \xE2\x9C\x82 '+_('or the scale (zoom level)')+' \xF0\x9F\x94\x8D')
    if response.content =='<html>\n<head>\n<title>Error</title>\n</head>\n<body>\n<h1>Error</h1>\n<p>Invalid bounding box</p>\n</body>\n</html>\n':
        raise ValueError(_('Invalid bounding box!')+' \xF0\x9F\x98\xA7\n'+_('Please, try with /map minlon,minlat,maxlon,maxlat')+'\n'+_('Coordinates\' decimals need to be marked with a dot.')+'\n'+_('For example:')+' /map 1.5,41.0,2.5,42.0 png 10 \xE2\x9C\x8C')
    if response.status_code !=200:
        raise ValueError(_('Oh,oh... An error occurred')+' \xF0\x9F\x98\xB0\n'+_('You can try with another bounding box or scale (zoom level)')+' \xE2\x81\x89\n'+_('Good luck! ')+'\xF0\x9F\x98\x89')

    return response.content


def deg2rad(degrees):
    return math.pi*degrees/180.0


def rad2deg(radians):
    return 180.0*radians/math.pi


def WGS84EarthRadius(lat):
    An = WGS84_a*WGS84_a * math.cos(lat)
    Bn = WGS84_b*WGS84_b * math.sin(lat)
    Ad = WGS84_a * math.cos(lat)
    Bd = WGS84_b * math.sin(lat)
    return math.sqrt((An*An + Bn*Bn)/(Ad*Ad + Bd*Bd))


def genBBOX(latitudeInDegrees, longitudeInDegrees, halfSideInKm):
    lat = deg2rad(latitudeInDegrees)
    lon = deg2rad(longitudeInDegrees)
    halfSide = 1000*halfSideInKm

    # Radius of Earth at given latitude
    radius = WGS84EarthRadius(lat)
    # Radius of the parallel at given latitude
    pradius = radius*math.cos(lat)

    latMin = lat - halfSide/radius
    latMax = lat + halfSide/radius
    lonMin = lon - halfSide/pradius
    lonMax = lon + halfSide/pradius
    return rad2deg(lonMin), rad2deg(latMin), rad2deg(lonMax), rad2deg(latMax)


def dps2deg(degrees, primes, seconds):
    return degrees + primes/60.0 + seconds/3600.0


def deg2dps(degrees):
    intdeg = math.floor(degrees)
    primes = (degrees - intdeg)*60.0
    intpri = math.floor(primes)
    seconds = (primes - intpri)*60.0
    intsec = round(seconds)
    return int(intdeg), int(intpri), int(intsec)


def getScale(bounds):
    centerLat = (float(bounds[0]) +float(bounds[2]))/2
    halfWorldMeters = 6378137 * math.pi * math.cos(centerLat * math.pi / 180)
    meters = halfWorldMeters * (float(bounds[3]) -float( bounds[1])) / 180
    pixelsPerMeter = 256 / meters
    metersPerPixel = 1 / (92 * 39.3701)
    scale = round(1 / (pixelsPerMeter * metersPerPixel))
    return scale
