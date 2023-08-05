{% extends "base.nix" %}
{% block build_function %}buildPythonPackage{% endblock %}
{% block fetch_function %}fetchPypi{% endblock %}
{% block nameversion %}
  name = "${pname}-${version}";
  version = "{{pkg.version}}";
  pname = "{{pkg.name}}";
{%endblock %}

{% block inputs %}
{% if pkg.propagated_build_inputs|length > 0 %}
  propagatedBuildInputs = [ {{ pkg.propagated_build_inputs|join(' ') }} ];
{% endif %}
{% if pkg.native_build_inputs|length > 0 %}
  checkInputs = [ {{ pkg.native_build_inputs|join(' ') }} ];
{% endif %}
{% endblock %}

{% block src %}
    inherit pname version;
{% endblock %}
