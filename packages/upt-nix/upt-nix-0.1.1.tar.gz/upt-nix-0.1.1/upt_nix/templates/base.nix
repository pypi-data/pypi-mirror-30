{{ '{' }} stdenv, {% block build_function %}{% endblock %}, {% block fetch_function %}{% endblock %}

{% if pkg.propagated_build_inputs %}
, {{ pkg.propagated_build_inputs|join (', ') }}
{% endif %}
{% if pkg.native_build_inputs %}
, {{ pkg.native_build_inputs|join (', ') }}
{% endif %}
{{ '}' }}:

{{ self.build_function() }} rec {
{% block nameversion %}{% endblock%}

  src = {{ self.fetch_function() }} {
{% block src %}{% endblock %}
    sha256 = "{{ pkg.sha256 }}";
  };

{% block inputs %}{% endblock %}

  meta = with stdenv.lib; {
    description = "{{ pkg.summary }}";
    homepage = {{ pkg.homepage }};
    license = [ {{ pkg.licenses|join(' ') }} ];
  }
}
