

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
	'foodcourt':
		{'query': 'node["amenity"="food_court"]({0});way["amenity"="food_court"]({0});relation["amenity"="food_court"]({0});', 'distance': 10000},
	'ice cream':
		{'icecream': 'node["amenity"="ice_cream"]({0});way["amenity"="ice_cream"]({0});relation["amenity"="ice_cream"]({0});', 'distance': 10000},
	'pub':
		{'pub': 'node["amenity"="pub"]({0});way["amenity"="pub"]({0});relation["amenity"="pub"]({0});', 'distance': 10000},
	'restaurant':
		{'restaurant': 'node["amenity"="restaurant"]({0});way["amenity"="restaurant"]({0});relation["amenity"="restaurant"]({0});', 'distance': 10000},
	'college':
		{'query': 'node["amenity"="college"]({0});way["amenity"="college"]({0});relation["amenity"="college"]({0});', 'distance': 10000},
	'Kindergarten':
		{'query': 'node["amenity"="kindergarten"]({0});way["amenity"="kindergarten"]({0});relation["amenity"="kindergarten"]({0});', 'distance': 10000},
	'library':
		{'query': 'node["amenity"="library"]({0});way["amenity"="library"]({0});relation["amenity"="library"]({0});', 'distance': 10000},
	'publicbookcase':
		{'query': 'node["amenity"="public_bookcase"]({0});way["amenity"="public_bookcase"]({0});relation["amenity"="public_bookcase"]({0});', 'distance': 10000},
	'school':
		{'query': 'node["amenity"="school"]({0});way["amenity"="school"]({0});relation["amenity"="school"]({0});', 'distance': 10000},
	'university':
		{'query': 'node["amenity"="university"]({0});way["amenity"="university"]({0});relation["amenity"="university"]({0});', 'distance': 10000},
	'defibrillator':
		{'query': 'node["emergency"="defibrillator"]({0});way["emergency"="defibrillator"]({0});relation["emergency"="defibrillator"]({0});', 'distance': 10000}

}
