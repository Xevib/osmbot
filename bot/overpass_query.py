type_query = {
	'hospital':
	    {'query': 'node["amenity"="hospital"]({0});way["amenity"="hospital"]({0});relation["amenity"="hospital"]({0});', 'distance': 10000},
	'bar':
		{'query': 'node["amenity"="bar"]({0});way["amenity"="bar"]({0});relation["amenity"="bar"]({0});', 'distance': 10000},
	'bbq':
		{'query': 'node["amenity"="bbq"]({0});way["amenity"="bbq"]({0});relation["amenity"="bbq"]({0});', 'distance': 10000},
	'biergarten':
		{'query': 'node["amenity"="biergarten"]({0});way["amenity"="biergarten"]({0});relation["amenity"="biergarten"]({0});', 'distance': 10000},
	'cafe':
		{'query': 'node["amenity"="cafe"]({0});way["amenity"="cafe"]({0});relation["amenity"="cafe"]({0});', 'distance': 10000},
	'water':
		{'query': 'node["amenity"="drinking_water"]({0});way["amenity"="drinking_water"]({0});relation["amenity"="drinking_water"]({0});', 'distance': 10000},
	'fastfood':
		{'query': 'node["amenity"="fast_food"]({0});way["amenity"="fast_food"]({0});relation["amenity"="fast_food"]({0});', 'distance': 10000},
	'defibrillator':
		{'query': 'node["emergency"="defibrillator"]({0});way["emergency"="defibrillator"]({0});relation["emergency"="defibrillator"]({0});', 'distance': 10000}

}
