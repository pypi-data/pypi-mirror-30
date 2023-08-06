# $FreeBSD$

{% macro depends(kind, deps) %}
{{ kind }}_DEPENDS=
    {%- for dep in deps %}
      {%- if loop.first %}
	{{ dep|reqformat }}
      {%- else %}
		{{ dep|reqformat }}
      {%- endif %}
      {% if not loop.last %} \
      {% endif %}
    {% endfor %}
{% endmacro -%}

PORTNAME=	{{ pkg.portname }}
DISTVERSION=	{{ pkg.version }}
CATEGORIES=	{{ pkg.categories|join(' ') }}
MASTER_SITES=	{{ pkg.master_sites }}
PKGNAMEPREFIX=	{{ pkg.pkgnameprefix }}

MAINTAINER=	{{ pkg.maintainer }}
COMMENT=	{{ pkg.summary }}

LICENSE=	{{ pkg.licenses }}
LICENSE_FILE=	${WRKSRC}/XXX

{# TODO: Perl usually has the same run/build deps.
 # Find out the right thing to do.
 # https://www.freebsd.org/doc/en/books/porters-handbook/makefile-depend.html
#}
{%- set build_depends = pkg.build_depends -%}
{%- set run_depends = pkg.run_depends -%}
{%- set test_depends = pkg.test_depends -%}

{% if build_depends %}
{{ depends('BUILD', build_depends) }}
{% endif %}
{% if run_depends %}
{{ depends('RUN', run_depends) }}
{% endif %}
{% if test_depends %}
{{ depends('TEST', test_depends) }}
{% endif %}

{% block use %}{% endblock %}

.include <bsd.port.mk>
