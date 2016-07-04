{% if 'name' in data.tag %}{% if not user_config['lang_set'] %}
*{{ _("Tags for")}} {{data.tag['name']}} *
{% else %}{% if 'name:' + user_config['lang'] in data.tag %}
*{{ _('Tags for') }} {{data.tag['name:'+user_config['lang']]}} *
{% else %}
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
{% endif %}{% if 'addr:housenumber' and 'addr:street' in data.tag -%}
{{'\U0001F4EE'}} {{data.tag['addr:street']}}, {{data.tag['addr:housenumber']}}
{% else %}{% if 'addr:housenumber' in data.tag -%}
{{'\U0001F4EE'}} {{data.tag['addr:housenumber']}}
{% else %}{% if 'addr:street' in data.tag -%}
{{'\U0001F4EE'}} {{data.tag['addr:street']}}
{% endif %}{% endif %}{% endif %}{% if 'addr:city' in data.tag -%}
  {{ data.tag['addr:city']}}
{% endif -%}{% if 'addr:country' in data.tag -%}
  {{data.tag['addr:country']}}
{% endif -%}

{% if 'phone' in data.tag -%}
{{'\U0001F4DE'}} {{data.tag['phone']}}
{% endif %}{% if 'contact:phone' in data.tag -%}
{{'\U0001F4DE'}} {{data.tag['contact:phone']}}
{% endif %}{% if 'fax' in data.tag -%}
{{'\U0001F4E0'}} {{data.tag['fax']}}
{% endif %}{% if 'email' in data.tag -%}
{{'\U00002709'}} {{data.tag['email']}}
{% endif %}{% if 'website' in data.tag -%}
{{'\U0001F30D'}} {{data.tag['website']}}
{% endif %}{% if 'opening_hours' in data.tag -%}
{{'\U0001F55E'}} {{data.tag['opening_hours']}}
{% endif %}{% if 'internet_access' in data.tag -%}
{{'\U0001F4F6'}} {{data.tag['internet_access']}}
{% endif %}{% if 'wheelchair' in data.tag -%}
{{'\U0000267F'}} {{data.tag['wheelchair']}}
{% endif %}{% if 'population' in data.tag %}{% if 'population:date' in data.tag %}
{{'\U0001F46A'}} {{data.tag['population']}} {{_("inhabitants")}} {{_("at")}} {{data.tag['population:date']}}
{% else -%}
{{'\U0001F46A'}} {{data.tag['population']}} {{_("inhabitants")}}
{% endif %}{% endif -%}
{% if 'ele' in data.tag %}
{{'\U0001F4CF'}} {{data.tag['ele']}} {{_("meters")}}
{% endif -%}

{% if 'wikidata' in data.tag -%}
{{'\U0001F4D7'}} [{{_("Wikidata")}}](https://www.wikidata.org/wiki/{{data.tag["wikidata"]}})
{% endif -%}
{% if 'wikipedia' in data.tag -%}
{{'\U0001F4D2'}} [{{_("Wikipedia")}}](http://wikipedia.org/wiki/{{data.tag["wikipedia"]}})
{%- endif %}

{{'\U000000A9'}} {{_('OpenStreetMap contributors')}}
