import json
import logging

try:
	from urllib.request import Request, urlopen  # Python 3
except ImportError:
	from urllib2 import Request, urlopen  # Python 2

from django.conf import settings

def infoip(func):
	def wrap(request, *args, **kwargs):
		info = None
		try:
			info = __get_geoip_info(request)
		except Exception as e:
			logging.error(e)

		request.infoip = info

		return func(request)
	return wrap

def __get_client_ip(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[0]
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip

def __get_geoip_info(request):
	protocol = "http"
	if hasattr(settings, 'INFOIP_USE_HTTPS') and settings.INFOIP_USE_HTTPS:
		protocol = "https"

	url = "{0}://api.infoip.io/{1}".format(protocol, __get_client_ip(request))
	
	q = Request(url)

	if hasattr(settings, 'INFOIP_API_KEY') and settings.INFOIP_API_KEY:
		q.add_header('x-infoip-token', settings.INFOIP_API_KEY)
	else:
		logging.debug("No infoip API key found. Rate limiting may occur!")

	data = urlopen(q).read().decode("utf-8")
	return json.loads(data)