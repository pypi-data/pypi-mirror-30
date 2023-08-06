from django_addons_formlib import forms


class Form(forms.BaseForm):
    languages = forms.CharField(
        'Languages',
        required=True,
        initial='["en", "de"]',
    )
    use_manifeststaticfilesstorage = forms.CheckboxField(
        'Hash static file names',
        required=False,
        initial=False,
        help_text=(
            'Use ManifestStaticFilesStorage to manage static files and set '
            'far-expiry headers. Enabling this option disables autosync for '
            'static files, and can cause deployment and/or 500 errors if a '
            'referenced file is missing. Please ensure that your test server '
            'works with this option enabled before deploying it to the live '
            'site.'
        )
    )
    enable_gis = forms.CheckboxField(
        'Enable django.contrib.gis',
        required=False,
        initial=False,
        help_text=(
            'Enable Geodjango (django.contrib.gis) related functionality.\n'
            'WARNING: Requires postgis (contact support to enable it for your '
            'project). For local development change "postgres:9.4" to '
            '"mdillon/postgis:9.4" in docker-compose.yml and run '
            '"aldryn project up" to re-create the db container.'
        )
    )
    disable_default_language_prefix = forms.CheckboxField(
        'Remove URL language prefix for default language',
        required=False,
        initial=False,
        help_text=(
            'For example, http://example.com/ rather than '
            'http://example.com/en/ if en (English) is the default language.'
        )
    )
    session_timeout = forms.NumberField(
        'Timeout for users session, in seconds.',
        required=False,
        initial=(60 * 60 * 24 * 7 * 2),
        help_text=(
            'By default it\'s two weeks (Django default).'
        ),
    )
