import time
import datetime
from django import http

class TimezoneMiddleware:
    def get_expires(self, offset):
        offset = datetime.timedelta(hours=offset, minutes=30,
                                    seconds=time.timezone)
        date = datetime.datetime.utcnow() + offset
        return date.strftime('%a, %d-%b-%Y %H:%M:%S')

    def process_request(self, request):
        if 'tz_detect' not in request.COOKIES and \
           'tz_offset' not in request.COOKIES:
            response = http.HttpResponseRedirect(request.build_absolute_uri())
            response.set_cookie('tz_detect', True)
            for offset in xrange(-12, 12):
                response.set_cookie('tz_%s' % offset,
                                    expires=self.get_expires(offset))
            return response
        elif 'tz_offset' not in request.COOKIES:
            for offset in xrange(-12, 12):
                if 'tz_%s' % offset in request.COOKIES:
                    request.COOKIES['tz_offset'] = offset
                    break

    def process_response(self, request, response):
        if 'tz_offset' in request.COOKIES and \
           'tz_detect' in request.COOKIES:
            response.set_cookie('tz_offset', request.COOKIES['tz_offset'])
            response.delete_cookie('tz_detect')
            for offset in xrange(request.COOKIES['tz_offset'], 12):
                response.delete_cookie('tz_%s' % offset)
        return response
