{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{% for key in keys %}{{typeemoji[key]}} {{key}}
{% endfor %}
