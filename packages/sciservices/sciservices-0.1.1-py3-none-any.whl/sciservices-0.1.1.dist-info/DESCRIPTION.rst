=====
Sci Services
=====

Sci Services is a package containing utilities for utilizing DBMI Tech-Core's
authentication and authorization service infrastructure

Detailed documentation is in the "docs" directory.

Quick start
-----------

1. Add "sciservices" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'sciservices',
    ]

2. To ensure a valid user is signed in, decorate your views like so:

    from sciservices.auth import sciuser_required

    @sciuser_required
    def my_view(request):
        ...

