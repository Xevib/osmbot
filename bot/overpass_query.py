

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
		'fastfood':
		{'icecream': 'node["amenity"="ice_cream"]({0});way["amenity"="ice_cream"]({0});relation["amenity"="ice_cream"]({0});', 'distance': 10000},
		'fastfood':
		{'pub': 'node["amenity"="pub"]({0});way["amenity"="pub"]({0});relation["amenity"="pub"]({0});', 'distance': 10000},
		'fastfood':
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
		'fastfood':
		{'bikeparking': 'node["amenity"="bycicle_parking"]({0});way["amenity"="bycicle_parking"]({0});relation["amenity"="bycicle_parking"]({0});', 'distance': 10000},
		'bikerepair':
		{'query': 'node["amenity"="bycicle_repair_station"]({0});way["amenity"="bycicle_repair_station"]({0});relation["amenity"="bycicle_repair_station"]({0});', 'distance': 10000},
		'bikerent':
		{'query': 'node["amenity"="bycicle_rental"]({0});way["amenity"="bycicle_rental"]({0});relation["amenity"="bycicle_rental"]({0});', 'distance': 10000},
		'boatshare':
		{'query': 'node["amenity"="boat_sharing"]({0});way["amenity"="boat_sharing"]({0});relation["amenity"="boat_sharing"]({0});', 'distance': 10000},
		'bus':
		{'query': 'node["amenity"="bus_station"]({0});way["amenity"="bus_station"]({0});relation["amenity"="bus_station"]({0});', 'distance': 10000},
		'carrent':
		{'query': 'node["amenity"="car_rental"]({0});way["amenity"="car_rental"]({0});relation["amenity"="car_rental"]({0});', 'distance': 10000},
		'carshare':
		{'query': 'node["amenity"="car_sharing"]({0});way["amenity"="car_sharing"]({0});relation["amenity"="car_sharing"]({0});', 'distance': 10000},
		'carwash':
		{'query': 'node["amenity"="car_wash"]({0});way["amenity"="car_wash"]({0});relation["amenity"="car_wash"]({0});', 'distance': 10000},
		'carcharging':
		{'query': 'node["amenity"="charging_station"]({0});way["amenity"="charging_station"]({0});relation["amenity"="charging_station"]({0});', 'distance': 10000},
		'ferry':
		{'query': 'node["amenity"="ferry_terminal"]({0});way["amenity"="ferry_terminal"]({0});relation["amenity"="ferry_terminal"]({0});', 'distance': 10000},
		'fuel':
		{'query': 'node["amenity"="fuel"]({0});way["amenity"="fuel"]({0});relation["amenity"="fuel"]({0});', 'distance': 10000},
		'grit':
		{'query': 'node["amenity"="grit_bin"]({0});way["amenity"="grit_bin"]({0});relation["amenity"="grit_bin"]({0});', 'distance': 10000},
		'fastfood':
		{'motopark': 'node["amenity"="motorcycle_parking"]({0});way["amenity"="motorcycle_parking"]({0});relation["amenity"="motorcycle_parking"]({0});', 'distance': 10000},
		'parking':
		{'query': 'node["amenity"="parking"]({0});way["amenity"="parking"]({0});relation["amenity"="parking"]({0});', 'distance': 10000},
		'fastfood':
		{'parkingin': 'node["amenity"="parking_entrance"]({0});way["amenity"="parking_entrance"]({0});relation["amenity"="parking_entrance"]({0});', 'distance': 10000},
		'parking_':
		{'query': 'node["amenity"="parking_space"]({0});way["amenity"="parking_space"]({0});relation["amenity"="parking_space"]({0});', 'distance': 10000},
		'taxi':
		{'query': 'node["amenity"="taxi"]({0});way["amenity"="taxi"]({0});relation["amenity"="taxi"]({0});', 'distance': 10000},
		'atm':
		{'query': 'node["amenity"="atm"]({0});way["amenity"="atm"]({0});relation["amenity"="atm"]({0});', 'distance': 10000},
		'bank':
		{'query': 'node["amenity"="bank"]({0});way["amenity"="bank"]({0});relation["amenity"="bank"]({0});', 'distance': 10000},
		'fastfood':
		{'exchange': 'node["amenity"="bureau_de_change"]({0});way["amenity"="bureau_de_change"]({0});relation["amenity"="bureau_de_change"]({0});', 'distance': 10000},
		'fastfood':
		{'babyhatch': 'node["amenity"="baby_hatch"]({0});way["amenity"="baby_hatch"]({0});relation["amenity"="baby_hatch"]({0});', 'distance': 10000},
		'clinic':
		{'query': 'node["amenity"="clinic"]({0});way["amenity"="clinic"]({0});relation["amenity"="clinic"]({0});', 'distance': 10000},
		'dentist':
		{'query': 'node["amenity"="dentist"]({0});way["amenity"="dentist"]({0});relation["amenity"="dentist"]({0});', 'distance': 10000},
		'doctors':
		{'query': 'node["amenity"="doctors"]({0});way["amenity"="doctors"]({0});relation["amenity"="doctors"]({0});', 'distance': 10000},
		'nursing':
		{'query': 'node["amenity"="nursing_home"]({0});way["amenity"="nursing_home"]({0});relation["amenity"="nursing_home"]({0});', 'distance': 10000},
		'pharmacy':
		{'query': 'node["amenity"="pharmacy"]({0});way["amenity"="pharmacy"]({0});relation["amenity"="pharmacy"]({0});', 'distance': 10000},
		'social':
		{'query': 'node["amenity"="social_facility"]({0});way["amenity"="social_facility"]({0});relation["amenity"="social_facility"]({0});', 'distance': 10000},
		'veterinary':
		{'query': 'node["amenity"="veterinary"]({0});way["amenity"="veterinary"]({0});relation["amenity"="veterinary"]({0});', 'distance': 10000},
		'arts':
		{'query': 'node["amenity"="arts_centre"]({0});way["amenity"="arts_centre"]({0});relation["amenity"="arts_centre"]({0});', 'distance': 10000},
		'brothel':
		{'query': 'node["amenity"="brothel"]({0});way["amenity"="brothel"]({0});relation["amenity"="brothel"]({0});', 'distance': 10000},
		'casino':
		{'query': 'node["amenity"="casino"]({0});way["amenity"="casino"]({0});relation["amenity"="casino"]({0});', 'distance': 10000},
		'cinema':
		{'query': 'node["amenity"="cinema"]({0});way["amenity"="cinema"]({0});relation["amenity"="cinema"]({0});', 'distance': 10000},
		'community':
		{'query': 'node["amenity"="community_centre"]({0});way["amenity"="community_centre"]({0});relation["amenity"="community_centre"]({0});', 'distance': 10000},
		'fountain':
		{'query': 'node["amenity"="fountain"]({0});way["amenity"="fountain"]({0});relation["amenity"="fountain"]({0});', 'distance': 10000},
		'gambling':
		{'query': 'node["amenity"="gambling"]({0});way["amenity"="gambling"]({0});relation["amenity"="gambling"]({0});', 'distance': 10000},
		'fastfood':
		{'nightclub': 'node["amenity"="nightclub"]({0});way["amenity"="nightclub"]({0});relation["amenity"="nightclub"]({0});', 'distance': 10000},
		'planetarium':
		{'query': 'node["amenity"="planetarium"]({0});way["amenity"="planetarium"]({0});relation["amenity"="planetarium"]({0});', 'distance': 10000},
		'social':
		{'query': 'node["amenity"="social_centre"]({0});way["amenity"="social_centre"]({0});relation["amenity"="social_centre"]({0});', 'distance': 10000},
		'stripclub':
		{'query': 'node["amenity"="stripclub"]({0});way["amenity"="stripclub"]({0});relation["amenity"="stripclub"]({0});', 'distance': 10000},
		'studio':
		{'query': 'node["amenity"="studio"]({0});way["amenity"="studio"]({0});relation["amenity"="studio"]({0});', 'distance': 10000},
		'swingerclub':
		{'query': 'node["amenity"="swingerclub"]({0});way["amenity"="swingerclub"]({0});relation["amenity"="swingerclub"]({0});', 'distance': 10000},
		'theatre':
		{'query': 'node["amenity"="theatre"]({0});way["amenity"="theatre"]({0});relation["amenity"="theatre"]({0});', 'distance': 10000},
		'animalboard':
		{'query': 'node["amenity"="animal_boarding"]({0});way["amenity"="animal_boarding"]({0});relation["amenity"="animal_boarding"]({0});', 'distance': 10000},
		'animalshelter':
		{'query': 'node["amenity"="animal_shelter"]({0});way["amenity"="animal_shelter"]({0});relation["amenity"="animal_shelter"]({0});', 'distance': 10000},
		'bench':
		{'query': 'node["amenity"="bench"]({0});way["amenity"="bench"]({0});relation["amenity"="bench"]({0});', 'distance': 10000},
		'clock':
		{'query': 'node["amenity"="clock"]({0});way["amenity"="clock"]({0});relation["amenity"="clock"]({0});', 'distance': 10000},
		'courthouse':
		{'query': 'node["amenity"="courthouse"]({0});way["amenity"="courthouse"]({0});relation["amenity"="courthouse"]({0});', 'distance': 10000},
		'coworking':
		{'query': 'node["amenity"="coworking_space"]({0});way["amenity"="coworking_space"]({0});relation["amenity"="coworking_space"]({0});', 'distance': 10000},
		'crematorium':
		{'query': 'node["amenity"="crematorium"]({0});way["amenity"="crematorium"]({0});relation["amenity"="crematorium"]({0});', 'distance': 10000},
		'crypt':
		{'query': 'node["amenity"="crypt"]({0});way["amenity"="crypt"]({0});relation["amenity"="crypt"]({0});', 'distance': 10000},
		'dojo':
		{'query': 'node["amenity"="dojo"]({0});way["amenity"="dojo"]({0});relation["amenity"="dojo"]({0});', 'distance': 10000},
		'fastfood':
		{'embassy': 'node["amenity"="embassy"]({0});way["amenity"="embassy"]({0});relation["amenity"="embassy"]({0});', 'distance': 10000},
		'firefighters':
		{'query': 'node["amenity"="fire_station"]({0});way["amenity"="fire_station"]({0});relation["amenity"="fire_station"]({0});', 'distance': 10000},
		'game':
		{'query': 'node["amenity"="game_feeding"]({0});way["amenity"="game_feeding"]({0});relation["amenity"="game_feeding"]({0});', 'distance': 10000},
		'grave':
		{'query': 'node["amenity"="grave_yard"]({0});way["amenity"="grave_yard"]({0});relation["amenity"="grave_yard"]({0});', 'distance': 10000},
		'gym':
		{'query': 'node["amenity"="gym"]({0});way["amenity"="gym"]({0});relation["amenity"="gym"]({0});', 'distance': 10000},
		'hunting':
		{'query': 'node["amenity"="hunting_stand"]({0});way["amenity"="hunting_stand"]({0});relation["amenity"="hunting_stand"]({0});', 'distance': 10000},
		'kneipp':
		{'query': 'node["amenity"="kneipp_water_cure"]({0});way["amenity"="kneipp_water_cure"]({0});relation["amenity"="kneipp_water_cure"]({0});', 'distance': 10000},
		'marketplace':
		{'query': 'node["amenity"="marketplace"]({0});way["amenity"="marketplace"]({0});relation["amenity"="marketplace"]({0});', 'distance': 10000},
		'placeworship':
		{'query': 'node["amenity"="place_of_worship"]({0});way["amenity"="place_of_worship"]({0});relation["amenity"="place_of_worship"]({0});', 'distance': 10000},
		'police':
		{'query': 'node["amenity"="police"]({0});way["amenity"="police"]({0});relation["amenity"="police"]({0});', 'distance': 10000},
		'postbox':
		{'query': 'node["amenity"="post_box"]({0});way["amenity"="post_box"]({0});relation["amenity"="post_box"]({0});', 'distance': 10000},
		'postoffice':
		{'query': 'node["amenity"="post_office"]({0});way["amenity"="post_office"]({0});relation["amenity"="post_office"]({0});', 'distance': 10000},
		'prison':
		{'query': 'node["amenity"="prison"]({0});way["amenity"="prison"]({0});relation["amenity"="prison"]({0});', 'distance': 10000},
		'rangers':
		{'query': 'node["amenity"="ranger_station"]({0});way["amenity"="ranger_station"]({0});relation["amenity"="ranger_station"]({0});', 'distance': 10000},
		'register':
		{'query': 'node["amenity"="register_office"]({0});way["amenity"="register_office"]({0});relation["amenity"="register_office"]({0});', 'distance': 10000},
		'recycling':
		{'query': 'node["amenity"="recycling"]({0});way["amenity"="recycling"]({0});relation["amenity"="recycling"]({0});', 'distance': 10000},
		'rescue':
		{'query': 'node["amenity"="rescue_station"]({0});way["amenity"="rescue_station"]({0});relation["amenity"="rescue_station"]({0});', 'distance': 10000},
		'sauna':
		{'query': 'node["amenity"="sauna"]({0});way["amenity"="sauna"]({0});relation["amenity"="sauna"]({0});', 'distance': 10000},
		'shelter':
		{'query': 'node["amenity"="shelter"]({0});way["amenity"="shelter"]({0});relation["amenity"="shelter"]({0});', 'distance': 10000},
		'shower':
		{'query': 'node["amenity"="shower"]({0});way["amenity"="shower"]({0});relation["amenity"="shower"]({0});', 'distance': 10000},
		'phone':
		{'query': 'node["amenity"="telephone"]({0});way["amenity"="telephone"]({0});relation["amenity"="telephone"]({0});', 'distance': 10000},
		'toilet':
		{'query': 'node["amenity"="toilets"]({0});way["amenity"="toilets"]({0});relation["amenity"="toilets"]({0});', 'distance': 10000},
		'wc':
		{'query': 'node["amenity"="toilets"]({0});way["amenity"="toilets"]({0});relation["amenity"="toilets"]({0});', 'distance': 10000},
		'townhall':
		{'query': 'node["amenity"="townhall"]({0});way["amenity"="townhall"]({0});relation["amenity"="townhall"]({0});', 'distance': 10000},
		'vending':
		{'query': 'node["amenity"="vending_machine"]({0});way["amenity"="vending_machine"]({0});relation["amenity"="vending_machine"]({0});', 'distance': 10000},
		'wastebasket':
		{'query': 'node["amenity"="waste_basket"]({0});way["amenity"="waste_basket"]({0});relation["amenity"="waste_basket"]({0});', 'distance': 10000},
		'wastedisposal':
		{'query': 'node["amenity"="waste_disposal"]({0});way["amenity"="waste_disposal"]({0});relation["amenity"="waste_disposal"]({0});', 'distance': 10000},
		'watering':
		{'query': 'node["amenity"="watering_place"]({0});way["amenity"="watering_place"]({0});relation["amenity"="watering_place"]({0});', 'distance': 10000},
		'waterpoint':
		{'query': 'node["amenity"="water_point"]({0});way["amenity"="water_point"]({0});relation["amenity"="water_point"]({0});', 'distance': 10000},
		'defibrillator':
		{'query': 'node["emergency"="defibrillator"]({0});way["emergency"="defibrillator"]({0});relation["emergency"="defibrillator"]({0});', 'distance': 10000}


}

