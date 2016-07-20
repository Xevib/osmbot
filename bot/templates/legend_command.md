{% for key in keys %}{% if is_rtl -%}{{'\U0000200F'}}{% endif -%}{{typeemoji[key]}} {{key}}
{% endfor %}
