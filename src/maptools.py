import requests
import math

WGS84_a = 6378137.0  # Major semiaxis [m]
WGS84_b = 6356752.3  # Minor semiaxis [m]

def download(bbox,imageformat='png',zoom=19):
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
    params['bbox'] = ",".join(map(str,bbox))
    params['format'] = imageformat
    params['scale'] = scale_zoom[int(zoom)]
    print "params:"+str(params)
    response = requests.get("http://render.openstreetmap.org/cgi-bin/export", params=params)
    if response.content =='<html>\n<head>\n<title>Error</title>\n</head>\n<body>\n<h1>Error</h1>\n<p>Map too large</p>\n</body>\n</html>\n':
        raise ValueError('Map too large,reduce the bounding box or the zoom')
    if response.content =='<html>\n<head>\n<title>Error</title>\n</head>\n<body>\n<h1>Error</h1>\n<p>Invalid bounding box</p>\n</body>\n</html>\n':
        raise ValueError('Invalid bounding box')
    if response.status_code !=200:
        raise ValueError('Error ocurred')
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
    return math.sqrt( (An*An + Bn*Bn)/(Ad*Ad + Bd*Bd) )

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
    return (rad2deg(lonMin), rad2deg(latMin), rad2deg(lonMax), rad2deg(latMax))


def dps2deg(degrees, primes, seconds):
    return degrees + primes/60.0 + seconds/3600.0

def deg2dps(degrees):
    intdeg = math.floor(degrees)
    primes = (degrees - intdeg)*60.0
    intpri = math.floor(primes)
    seconds = (primes - intpri)*60.0
    intsec = round(seconds)
    return (int(intdeg), int(intpri), int(intsec))
