import zoneinfo

from django.utils import timezone


class SaudiArabiaTimeZoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        timezone.activate(zoneinfo.ZoneInfo('Asia/Riyadh'))
        response = self.get_response(request)
        return response
