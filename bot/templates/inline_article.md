{% if 'name' in data.tag %}{% if not user_config['lang_set'] -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}*{{ _("Tags for")}} {{data.tag['name']}} *
{% else %}{% if 'name:' + user_config['lang'] in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}*{{ _('Tags for') }} {{data.tag['name:'+user_config['lang']]}} *
{% else -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}*{{ _("Tags for")}} {{data.tag['name']}} *
{% endif -%}{% endif -%}{% endif -%}

{% if data.tag.admin_level == '2' or data.tag.place == 'country' -%}
{% if 'is_in:continent' in data.tag %}{% if data.tag['is_in:continent'] == 'Europe' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30D'}} {{_("European country")}}
{% elif  data.tag['is_in:continent'] == 'Europa' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30D'}} {{ _("European country") }}
{% elif data.tag['is_in:continent'] == 'Africa' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30D'}} {{ _("African country") }}
{% elif data.tag['is_in:continent']  == 'South America' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30E'}} {{ _("South american country") }}
{% elif data.tag['is_in:continent']  == 'Latin America' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30E'}} {{_("South american country")}}
{% elif data.tag['is_in:continent'] == 'America del Sur' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30E'}} {{_("South american country")}}
{% elif data.tag['is_in:continent']  == 'North America' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30E'}} {{_("North american country")}}
{% elif data.tag['is_in:continent'] == 'Amérique du Nord' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30E'}} {{_("North american country")}}
{% elif data.tag['is_in:continent'] == 'Central America' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30E'}} {{_("Central american country")}}
{% elif data.tag['is_in:continent'] == 'América' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30E'}} {{_("American country")}}
{% elif data.tag['is_in:continent']  == 'America' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30E'}} {{_("American country")}}
{% elif data.tag['is_in:continent'] == 'Asia' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30F'}} {{_("Asian country")}}
{% elif data.tag['is_in:continent'] == 'Oceania' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30F'}} {{_("Oceanian country")}}
{% elif data.tag['is_in:continent'] == 'Australia' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30F'}} {{_("Oceanian country")}}
{% elif data.tag['is_in:continent'] == 'Eurasia' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30D'}}{{'\U0001F30F'}} {{_('Eurasian country')}}
{% elif data.tag['is_in:continent'] == 'Europe; Asia' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30D'}}{{'\U0001F30F'}} {{_('Eurasian country') }}
{% endif %}{% endif %}{% endif %}{% if 'flag' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F6A9'}} [{{_("Flag")}}]({{data.tag['flag']|url_escape()}})
{% endif %}{% if 'currency' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F4B5'}} {{data.tag['currency']}}
{% endif %}{% if 'timezone' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F552'}}{{'\U0001F310'}} {{data.tag['timezone']}}
{% endif %}{% if 'is_in:continent' in data.tag or 'flag' in data.tag or 'currency' in data.tag or 'timezone' in data.tag %}
{% endif -%}
{% if 'addr:full' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F4EC'}} {{data.tag['addr:full']}}
{% endif -%}{% if 'addr:full' in data.tag %}
{% endif -%}
{% if 'addr:housenumber' and 'addr:street' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F4EE'}} {{data.tag['addr:street']}}, {{data.tag['addr:housenumber']}}
{% else %}{% if 'addr:housenumber' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F4EE'}} {{data.tag['addr:housenumber']}}
{% else %}{% if 'addr:street' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F4EE'}} {{data.tag['addr:street']}}
{% endif %}{% endif %}{% endif %}{% if 'addr:housename' in data.tag -%}
  {% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{ data.tag['addr:housename']}}
{% endif %}{% if 'addr:city' in data.tag -%}
  {% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{ data.tag['addr:city']}}
{% endif %}{% if 'addr:postcode' in data.tag -%}
  {% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{ data.tag['addr:postcode']}}
{% endif -%}{% if 'addr:district' in data.tag -%}
  {% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{data.tag['addr:district']}}
{% endif -%}{% if 'addr:suburb' in data.tag -%}
  {% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{data.tag['addr:suburb']}}
{% endif -%}{% if 'addr:province' in data.tag -%}
  {% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{data.tag['addr:province']}}
{% endif -%}{% if 'addr:state' in data.tag -%}
  {% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{data.tag['addr:state']}}
{% endif -%}{% if 'addr:country' in data.tag -%}
  {% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{data.tag['addr:country']}}
{% endif -%}{% if 'addr:housenumber' in data.tag or 'addr:street' in data.tag or 'addr:housename' in data.tag or 'addr:city' in data.tag or 'addr:postcode' in data.tag or 'addr:district' in data.tag or 'addr:suburb' in data.tag or 'addr:province' in data.tag or 'addr:state' in data.tag or 'addr:country' in data.tag %}
{% endif -%}
{% if 'ref' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F6E3'}} {{data.tag['ref']}}
{% endif -%}{% if 'lanes' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F68D'}}{{'\U00002797'}}{{'\U0001F698'}} {{data.tag['lanes']}}
{% endif -%}{% if 'maxspeed' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F6AB'}} {{data.tag['maxspeed']}}
{% endif -%}{% if 'access' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F513'}} {{data.tag['access']}}
{% endif -%}{% if 'foot' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F513'}}{{'\U0001F6B6'}} {{data.tag['foot']}}
{% endif -%}{% if 'horse' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F513'}}{{'\U0001F40E'}} {{data.tag['horse']}}
{% endif -%}{% if 'bicycle' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F513'}}{{'\U0001F6B2'}} {{data.tag['bicycle']}}
{% endif -%}{% if 'motor_vehicle' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F513'}}{{'\U0001F3CD'}}{{'\U0001F697'}}{{'\U0001F69A'}}{{'\U0001F69C'}} {{data.tag['motor_vehicle']}}
{% endif -%}{% if 'motorcycle' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F513'}}{{'\U0001F3CD'}} {{data.tag['motorcycle']}}
{% endif -%}{% if 'motorcar' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F513'}}{{'\U0001F697'}} {{data.tag['motorcar']}}
{% endif -%}{% if 'hgv' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F513'}}{{'\U0001F69A'}} {{data.tag['hgv']}}
{% endif -%}{% if 'agricultural' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F513'}}{{'\U0001F69C'}} {{data.tag['agricultural']}}
{% endif -%}{% if 'bus' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F513'}}{{'\U0001F68C'}} {{data.tag['bus']}}
{% endif -%}{% if 'taxi' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F513'}}{{'\U0001F695'}} {{data.tag['taxi']}}
{% endif -%}{% if 'emergency' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F513'}}{{'\U0001F6A8'}} {{data.tag['emergency']}}
{% endif -%}{% if 'ref' in data.tag or 'lanes' in data.tag or 'maxspeed' in data.tag or 'access' in data.tag or 'foot' in data.tag or 'horse' in data.tag or 'bicycle' in data.tag or 'motor_vehicle' in data.tag or 'motorcycle' in data.tag or 'motorcar' in data.tag or 'hgv' in data.tag or 'agricultural' in data.tag or 'bus' in data.tag or 'taxi' in data.tag or 'emergency' in data.tag in data.tag %}
{% endif -%}
{% if 'phone' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F4DE'}} {% if is_rtl -%}{{'\U0000200E'}}{% endif -%}{{data.tag['phone']}}
{% endif %}{% if 'contact:phone' in data.tag -%}{% if data.tag.phone != data.tag['contact:phone'] -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F4DE'}} {% if is_rtl -%}{{'\U0000200E'}}{% endif -%}{{data.tag['contact:phone']}}
{% endif %}{% endif %}{% if 'fax' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F4E0'}} {% if is_rtl -%}{{'\U0000200E'}}{% endif -%}{{data.tag['fax']}}
{% endif %}{% if 'contact:fax' in data.tag -%}{% if data.tag.fax != data.tag['contact:fax'] -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F4E0'}} {% if is_rtl -%}{{'\U0000200E'}}{% endif -%}{{data.tag['contact:fax']}}
{% endif %}{% endif %}{% if 'email' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U00002709'}} {{data.tag['email']}}
{% endif %}{% if 'contact:email' in data.tag -%}{% if data.tag.mail != data.tag['contact:mail'] -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U00002709'}} {{data.tag['contact:email']}}
{% endif %}{% endif %}{% if 'website' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30D'}} {% if is_rtl -%}{{'\U0000200E'}}{% endif -%}{{data.tag['website']}}
{% endif %}{% if 'contact:website' in data.tag -%}{% if data.tag.website != data.tag['contact:website'] -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F30D'}} {% if is_rtl -%}{{'\U0000200E'}}{% endif -%}{{data.tag['contact:website']}}
{% endif %}{% endif %}{% if 'opening_hours' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F55E'}} {{data.tag['opening_hours']}}
{% endif %}{% if 'internet_access' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F4F6'}} {{data.tag['internet_access']}}
{% endif %}{% if 'internet_access:fee' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F4F6'}}{{'\U0001F4B8'}} {{data.tag['internet_access:fee']}}
{% endif %}{% if 'stars' in data.tag -%}{% if data.tag['stars'] == '1' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U00002733'}} {{'\U00002B50'}}
{% elif data.tag['stars'] == '1S' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002795'}}
{% elif data.tag['stars'] == '2' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002B50'}}
{% elif data.tag['stars'] == '2S'-%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002795'}}
{% elif data.tag['stars'] == '3' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}
{% elif data.tag['stars'] == '3S' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002795'}}
{% elif data.tag['stars'] == '4' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}
{% elif data.tag['stars'] == '4S' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002795'}}
{% elif data.tag['stars'] == '5' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}
{% elif data.tag['stars'] == '5S' -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002795'}}
{% endif %}{% endif %}{% if 'rooms' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F511'}} {{data.tag['rooms']}}
{% endif %}{% if 'beds' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F6CF'}} {{data.tag['beds']}}
{% endif %}{% if 'toilets' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F6BE'}} {{data.tag['toilets']}}
{% endif %}{% if 'wheelchair' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0000267F'}} {{data.tag['wheelchair']}}
{% endif %}{% if 'toilets:wheelchair' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F6BE'}}{{'\U0000267F'}} {{data.tag['toilets:wheelchair']}}
{% endif %}{% if 'dogs' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F415'}} {{data.tag['dogs']}}
{% endif %}{% if 'smoking' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F6AC'}} {{data.tag['smoking']}}
{% endif %}{% if 'brand' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F4BC'}}{{'\U0001F3EC'}} {{data.tag['brand']}}
{% endif %}{% if 'operator' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F4BC'}} {{data.tag['operator']}}
{% endif %}{% if 'cuisine' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F373'}} {{data.tag['cuisine']}} {% if data.tag['cuisine'] == 'barbecue' -%}{{'\U0001F525'}}{% elif data.tag['cuisine'] == 'burger' -%}{{'\U0001F354'}}{% elif data.tag['cuisine'] == 'cake' -%}{{'\U0001F370'}}{% elif data.tag['cuisine'] == 'chicken' -%}{{'\U0001F357'}}{% elif  data.tag['cuisine'] == 'coffee_shop' -%}{{'\U00002615'}}{% elif data.tag['cuisine'] == 'curry' -%}{{'\U0001F35B'}}{% elif data.tag['cuisine'] == 'donut' -%}{{'\U0001F369'}}{% elif data.tag['cuisine'] == 'fish_and_chips' -%}{{'\U0001F41F'}}{{'\U0001F35F'}}{% elif  data.tag['cuisine'] == 'ice_cream' -%}{{'\U000FE977'}}{% elif data.tag['cuisine'] == 'gyros' -%}{{'\U0001F32E'}}{% elif data.tag['cuisine'] == 'kebab' -%}{{'\U0001F32E'}}{% elif data.tag['cuisine'] == 'pasta' -%}{{'\U0001F35D'}}{% elif data.tag['cuisine'] == 'pizza' -%}{{'\U0001F355'}}{% elif data.tag['cuisine'] == 'sandwich' -%}{{'\U0001F32D'}}{% elif data.tag['cuisine'] == 'sausage' -%}{{'\U0001F32D'}}{% elif data.tag['cuisine'] == 'seafood' -%}{{'\U0001F41F'}}{{'\U0001F980'}}{% elif data.tag['cuisine'] == 'soup' -%}{{'\U0001F372'}}{% elif data.tag['cuisine'] == 'steak_house' -%}{{'\U0001F356'}}{% elif data.tag['cuisine'] == 'sushi' -%}{{'\U0001F363'}}{% elif data.tag['cuisine'] == 'tapas' -%}{{'\U0001F364'}}{{'\U0001F37A'}}{% elif data.tag['cuisine'] == 'italian' -%}{{'\U0001F1EE\U0001F1F9'}}{% endif -%}
{% endif %}{% if 'clothes' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F454'}}{{'\U0001F45A'}} {{data.tag['clothes']}}
{% endif %}{% if 'male' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F6B9'}} {{data.tag['male']}}
{% endif %}{% if 'female' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F6BA'}} {{data.tag['female']}}
{% endif %}{% if 'unisex' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F6BB'}}{{'\U0001F469'}} {{data.tag['unisex']}}
{% endif %}{% if 'phone' in data.tag or 'contact:phone' in data.tag or 'fax' in data.tag or 'contact:fax' in data.tag or 'email' in data.tag or 'contact:email' in data.tag or 'website' in data.tag or 'contact:website' in data.tag or 'opening_hours' in data.tag or 'internet_access' in data.tag or 'internet_access:fee' in data.tag or 'stars' in data.tag or 'rooms' in data.tag or 'beds' in data.tag or 'toilets' in data.tag or 'wheelchair' in data.tag or 'toilets:wheelchair' in data.tag or 'dogs' in data.tag or 'smoking' in data.tag or 'brand' in data.tag or 'operator' in data.tag or 'cuisine' in data.tag or 'clothes' in data.tag or 'male' in data.tag or 'female' in data.tag or 'unisex' in data.tag %}
{% endif -%}
{% if 'population' in data.tag %}{% if 'population:date' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F46A'}} {{data.tag['population']}} {{_("inhabitants")}} {{_("at")}} {{data.tag['population:date']}}
{% else -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F46A'}} {{data.tag['population']}} {{_("inhabitants")}}
{% endif %}{% endif -%}
{% if 'ele' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U00002195'}}{{'\U0001F4CF'}} {{data.tag['ele']}} {{_("meters")}}
{% endif -%}{% if 'population' in data.tag or 'ele' in data.tag %}
{% endif -%}
{% if 'wikidata' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F4D7'}} [{{_("Wikidata")}}](https://www.wikidata.org/wiki/{{data.tag["wikidata"]}})
{% endif -%}
{% if 'wikipedia' in data.tag -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F4D2'}} [{{_("Wikipedia")}}](http://wikipedia.org/wiki/{{data.tag["wikipedia"]|url_escape()}})
{% endif %}{% if 'wikidata' in data.tag or 'wikipedia' in data.tag %}
{% endif -%}
{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U0001F4CD'}}{{'\U0001F5FA'}} [{{_("Map")}}](http://www.openstreetmap.org/?minlat={{nominatim_data['boundingbox'][0]}}&maxlat={{nominatim_data['boundingbox'][1]}}&minlon={{nominatim_data['boundingbox'][3]}}&maxlon={{nominatim_data['boundingbox'][3]}}&mlat={{nominatim_data['lat']}}&mlon={{nominatim_data['lon']}})

{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{'\U000000A9'}} {{_('OpenStreetMap contributors')}}
