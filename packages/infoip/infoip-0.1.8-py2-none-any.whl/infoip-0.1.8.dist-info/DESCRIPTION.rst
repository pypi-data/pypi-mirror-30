GeoIp info for your visitors
============================

This simple plugin connects to the `infoip <https://www.infoip.io>`__
API and retrieves the geoip information for the current request/visitor.
It works based on view decorators and not middleware to prevent slowing
down your application with unnecessary data.

The plugin uses an external API which is battle-tested and
enterprise-ready to satisfy any number of requests. Our database is
refreshed every single day in order to respond with up-to-date
information. The API offers ``1000`` free requests every day with a
rate-limiter set at ``1rps`` (one request per second). If you find that
to be too restrictive please consider subscribing to a `premium
plan <https://www.infoip.io/pricing>`__

Supported frameworks
~~~~~~~~~~~~~~~~~~~~

1. Django

Quick start Django
------------------

1. Install the package from pip

   ``pip install infoip``

2. Import the view decorator and use it to decorate the view where you
   need geoip info

   .. code:: python

       # django test view that simply prints the geoip data regarding the visitor

       from infoip.django import infoip
       from django.http import JsonResponse

       @infoip
       def index(request):
           # will respond to the request with user info
           # you can also use the geoip data in your views for custom processing:
           #  - request.infoip.country_long
           #  - request.infoip.country_short
           #  - ...
           return JsonResponse(request.infoip)

3. Tweak the settings

   1. (optional) Add your api key to your settings if you are a premium
      subscriber of `infoip <https://www.infoip.io>`__

      .. code:: python

          INFOIP_API_KEY = "your-api-key"

   2. (optional) Use ``https`` for communicating with our API (it uses
      ``http`` by default)

      .. code:: python

          INFOIP_USE_HTTPS = True

You want to help and contribute? Perfect!
=========================================

These are some contribution examples
------------------------------------

- Reporting issues to the bugtracker.

- Submitting pull requests from a forked infoip repo.

- Extending the documentation.


For pull requests, keep this in mind
------------------------------------

- Add a test which proves your fix and make it pass.

- Describe your change in CHANGES.rst

- Add yourself to the docs/credits.rst





