{% extends "base.nix" %}
{% block build_function %}buildPerl{% endblock %}
{% block fetch_function %}fetchurl{% endblock %}
{% block nameversion %}
  version = "{{pkg.version}}";
  name = "{{pkg.name}}-${version}";
{%endblock %}

{% block inputs %}
{% if pkg.propagated_build_inputs|length > 0 %}
  propagatedBuildInputs = [ {{ pkg.propagated_build_inputs|join(' ') }} ];
{% endif %}
{% if pkg.native_build_inputs|length > 0 %}
  nativeBuildInputs = [ {{ pkg.native_build_inputs|join(' ') }} ];
{% endif %}
{% endblock %}

{% block src %}
    url = "{{pkg.url}}";
{% endblock %}
