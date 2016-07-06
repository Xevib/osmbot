{% if 'name' in data.tag %}{% if not user_config['lang_set'] -%}
*{{ _("Tags for")}} {{data.tag['name']}} *
{% else %}{% if 'name:' + user_config['lang'] in data.tag -%}
*{{ _('Tags for') }} {{data.tag['name:'+user_config['lang']]}} *
{% else -%}
*{{ _("Tags for")}} {{data.tag['name']}} *
{% endif %}{% endif %}{% endif %}
{% if data.tag.admin_level == '2' -%}
{% if 'Europe' in data.tag['is_in:continent'] -%}
{{'\U0001F30D'}} {{_("European country")}}
{% elif 'Europa' in data.tag['is_in:continent'] -%}
{{'\U0001F30D'}} {{ _("European country") }}
{% elif 'Africa' in data.tag['is_in:continent'] -%}
{{'\U0001F30D'}} {{ _("African country") }}
{% elif 'South America' in data.tag['is_in:continent'] -%}
{{'\U0001F30E'}} {{ _("South american country") }}
{% elif "Latin America" in data.tag['is_in:continent'] -%}
{{'\U0001F30E'}} {{_("South american country")}}
{% elif 'America del Sur' in data.tag['is_in:continent'] -%}
{{'\U0001F30E'}} {{_("South american country")}}
{% elif "North America" in data.tag['is_in:continent'] -%}
{{'\U0001F30E'}} {{_("North american country")}}
{% elif 'Amérique du Nord' in data.tag['is_in:continent'] -%}
{{'\U0001F30E'}} {{_("North american country")}}
{% elif "Central America" in data.tag['is_in:continent'] -%}
{{'\U0001F30E'}} {{_("Central american country")}}
{% elif "América" in data.tag["is_in:continent"] -%}
{{'\U0001F30E'}} {{_("American country")}}
{% elif "America" in data.tag["is_in:continent"] -%}
{{'\U0001F30E'}} {{_("American country")}}
{% elif "Asia" in data.tag["is_in:continent"] -%}
{{'\U0001F30F'}} {{_("Asian country")}}
{% elif "Oceania" in data.tag["is_in:continent"] -%}
{{'\U0001F30F'}} {{_("Oceanian country")}}
{% elif "Australia" in data.tag["is_in:continent"] -%}
{{'\U0001F30F'}} {{_("Oceanian country")}}
{% elif "Eurasia" in data.tag["is_in:continent"] -%}
{{'\U0001F30D'}} {{'\U0001F30F'}} {{_("Eurasian country")}}
{% elif "Europe; Asia" in data.tag["is_in:continent"] -%}
{{'\U0001F30D'}} {{'\U0001F30F'}} {{_("Eurasian country") }}
{% endif %}{% endif %}{% if 'flag' in data.tag -%}
{{'\U0001F6A9'}} [{{_("Flag")}}]({{data.tag['flag']}})
{% endif %}{% if 'currency' in data.tag -%}
{{'\U0001F4B5'}} {{data.tag['currency']}}
{% endif %}{% if 'timezone' in data.tag -%}
{{'\U0001F552'}}{{'\U0001F310'}} {{data.tag['timezone']}}
{% endif %}{% if 'is_in:continent' or 'flag' or 'currency' or 'timezone' in data.tag -%}

{% endif -%}
{% if 'addr:full' in data.tag -%}
{{'\U0001F4EC'}} {{data.tag['addr:full']}}
{% endif -%}{% if 'addr:full' in data.tag -%}

{% endif -%}
{% if 'addr:housenumber' and 'addr:street' in data.tag -%}
{{'\U0001F4EE'}} {{data.tag['addr:street']}}, {{data.tag['addr:housenumber']}}
{% else %}{% if 'addr:housenumber' in data.tag -%}
{{'\U0001F4EE'}} {{data.tag['addr:housenumber']}}
{% else %}{% if 'addr:street' in data.tag -%}
{{'\U0001F4EE'}} {{data.tag['addr:street']}}
{% endif %}{% endif %}{% endif %}{% if 'addr:housename' in data.tag -%}
  {{ data.tag['addr:housename']}}
{% endif %}{% if 'addr:city' in data.tag -%}
  {{ data.tag['addr:city']}}
{% endif %}{% if 'addr:postcode' in data.tag -%}
  {{ data.tag['addr:postcode']}}
{% endif -%}{% if 'addr:district' in data.tag -%}
  {{data.tag['addr:district']}}
{% endif -%}{% if 'addr:suburb' in data.tag -%}
  {{data.tag['addr:suburb']}}
{% endif -%}{% if 'addr:province' in data.tag -%}
  {{data.tag['addr:province']}}
{% endif -%}{% if 'addr:state' in data.tag -%}
  {{data.tag['addr:state']}}
{% endif -%}{% if 'addr:country' in data.tag -%}
  {{data.tag['addr:country']}}
{% endif -%}{% if 'addr:housenumber' or 'addr:street' or 'addr:housename' or 'addr:city' or 'addr:postcode' or 'addr:district' or 'addr:suburb' or 'addr:province' or 'addr:state' or 'addr:country' in data.tag -%}

{% endif -%}
{% if 'ref' in data.tag -%}
{{'\U0001F6E3'}} {{data.tag['ref']}}
{% endif -%}{% if 'ref' in data.tag -%}

{% endif -%}
{% if 'phone' in data.tag -%}
{{'\U0001F4DE'}} {{data.tag['phone']}}
{% endif %}{% if 'contact:phone' in data.tag -%}
{{'\U0001F4DE'}} {{data.tag['contact:phone']}}
{% endif %}{% if 'fax' in data.tag -%}
{{'\U0001F4E0'}} {{data.tag['fax']}}
{% endif %}{% if 'contact:fax' in data.tag -%}
{{'\U0001F4E0'}} {{data.tag['contact:fax']}}
{% endif %}{% if 'email' in data.tag -%}
{{'\U00002709'}} {{data.tag['email']}}
{% endif %}{% if 'contact:email' in data.tag -%}
{{'\U00002709'}} {{data.tag['contact:email']}}
{% endif %}{% if 'website' in data.tag -%}
{{'\U0001F30D'}} {{data.tag['website']}}
{% endif %}{% if 'contact:website' in data.tag -%}
{{'\U0001F30D'}} {{data.tag['contact:website']}}
{% endif %}{% if 'opening_hours' in data.tag -%}
{{'\U0001F55E'}} {{data.tag['opening_hours']}}
{% endif %}{% if 'internet_access' in data.tag -%}
{{'\U0001F4F6'}} {{data.tag['internet_access']}}
{% endif %}{% if 'internet_access:fee' in data.tag -%}
{{'\U0001F4F6'}}{{'\U0001F4B8'}} {{data.tag['internet_access:fee']}}
{% endif %}{% if '1' in data.tag['stars'] -%}
{{'\U00002733'}} {{'\U00002B50'}}
{% elif '1S' in data.tag['stars'] -%}
{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002795'}}
{% elif '2' in data.tag['stars'] -%}
{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002B50'}}
{% elif '2S' in data.tag['stars'] -%}
{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002795'}}
{% elif '3' in data.tag['stars'] -%}
{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}
{% elif '3S' in data.tag['stars'] -%}
{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002795'}}
{% elif '4' in data.tag['stars'] -%}
{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}
{% elif '4S' in data.tag['stars'] -%}
{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002795'}}
{% elif '5' in data.tag['stars'] -%}
{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}
{% elif '5S' in data.tag['stars'] -%}
{{'\U00002733'}} {{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002B50'}}{{'\U00002795'}}
{% endif %}{% if 'beds' in data.tag -%}
{{'\U0001F6CF'}} {{data.tag['beds']}}
{% endif %}{% if 'toilets' in data.tag -%}
{{'\U0001F6BE'}} {{data.tag['toilets']}}
{% endif %}{% if 'wheelchair' in data.tag -%}
{{'\U0000267F'}} {{data.tag['wheelchair']}}
{% endif %}{% if 'toilets:wheelchair' in data.tag -%}
{{'\U0001F6BE'}}{{'\U0000267F'}} {{data.tag['toilets:wheelchair']}}
{% endif %}{% if 'dogs' in data.tag -%}
{{'\U0001F415'}} {{data.tag['dogs']}}
{% endif %}{% if 'smoking' in data.tag -%}
{{'\U0001F6AC'}} {{data.tag['smoking']}}
{% endif %}{% if 'brand' in data.tag -%}
{{'\U0001F4BC'}}{{'\U0001F3EC'}} {{data.tag['brand']}}
{% endif %}{% if 'operator' in data.tag -%}
{{'\U0001F4BC'}} {{data.tag['operator']}}
{% endif %}{% if 'cuisine' in data.tag -%}
{{'\U0001F373'}} {{data.tag['cuisine']}}
{% endif %}{% if 'clothes' in data.tag -%}
{{'\U0001F454'}}{{'\U0001F45A'}} {{data.tag['clothes']}}
{% endif %}{% if 'male' in data.tag -%}
{{'\U0001F6B9'}} {{data.tag['male']}}
{% endif %}{% if 'female' in data.tag -%}
{{'\U0001F6BA'}} {{data.tag['female']}}
{% endif %}{% if 'unisex' in data.tag -%}
{{'\U0001F6BB'}}{{'\U0001F469'}} {{data.tag['unisex']}}
{% endif %}{% if 'phone' or 'contact:phone' or 'fax' or 'contact:fax' or 'email' or 'contact:email' or 'website' or 'contact:website' or 'opening_hours' or 'internet_access' or 'internet_access:fee' or 'stars' or 'beds' or 'toilets' or 'wheelchair' or 'toilets:wheelchair' or 'dogs' or 'smoking' or 'brand' or 'operator' or 'cuisine' or 'clothes' or 'male' or 'female' or 'unisex' in data.tag -%}

{% endif -%}
{% if 'population' in data.tag %}{% if 'population:date' in data.tag -%}
{{'\U0001F46A'}} {{data.tag['population']}} {{_("inhabitants")}} {{_("at")}} {{data.tag['population:date']}}
{% else -%}
{{'\U0001F46A'}} {{data.tag['population']}} {{_("inhabitants")}}
{% endif %}{% endif -%}
{% if 'ele' in data.tag -%}
{{'\U00002195'}}{{'\U0001F4CF'}} {{data.tag['ele']}} {{_("meters")}}
{% endif -%}{% if 'population' or 'ele' in data.tag -%}

{% endif -%}
{% if 'wikidata' in data.tag -%}
{{'\U0001F4D7'}} [{{_("Wikidata")}}](https://www.wikidata.org/wiki/{{data.tag["wikidata"]}})
{% endif -%}
{% if 'wikipedia' in data.tag -%}
{{'\U0001F4D2'}} [{{_("Wikipedia")}}](http://wikipedia.org/wiki/{{data.tag["wikipedia"]|replace(' ','%20')}})
{%- endif %}{% if 'wikidata' or 'wikipedia' in data.tag -%}

{% endif -%}
{{'\U000000A9'}} {{_('OpenStreetMap contributors')}}
