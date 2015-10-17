type_query = {
    'hospital':
        {'query': 'node["amenity"="hospital"]({0});way["amenity"="hospital"]({0});relation["amenity"="hospital"]({0});','distance': 10000},
    'bar':
        {'query': 'node["amenity"="bar"]({0});way["amenity"="bar"]({0});relation["amenity"="bar"]({0});', 'distance': 10000},
    'defibrillator':
        {'query': 'node["emergency"="defibrillator"]({0});way["emergency"="defibrillator"]({0});relation["emergency"="defibrillator"]({0});', 'distance': 10000}

}