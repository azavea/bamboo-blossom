"""A Falcon class to represent the root resource of the web
application. The application is intended to emit an iCal calendar
representation of all employee hire dates throughout the year.
"""
import os
import logging
import falcon
import redis

from icalendar import Calendar, Event

from bamboo_blossom.core import Company

CACHE = redis.from_url(os.environ.get('REDIS_URL', 'redis://cache'))


class AuthMiddleware(object):
    """Request authentication handler for API."""

    def process_request(self, req, _):
        """A method that accepts or rejects requests based on configured API key.

        Args:
            req (object): An object that represents the HTTP request.
            resp (object): An object that represents the HTTP response.
        """
        req_secret_key = req.get_param('key', None)
        secret_key = os.environ.get('BB_API_SECRET_KEY', None)

        # No secret key was provided by administrator; disable
        # request authorization.
        if secret_key is None or secret_key == '':
            return

        # If no key was provided by the user; unauthorized request.
        if req_secret_key is None:
            raise falcon.HTTPUnauthorized('Secret key required',
                                          'Please provide a secret key as part of the request.',
                                          [])

        # If request key doesn't match administrator key; unauthorized
        # request.
        if req_secret_key != secret_key:
            raise falcon.HTTPUnauthorized('Authentication required',
                                          'The provided secret key is not valid.',
                                          [])


class RootResource(object):
    """A Falcon class of the root web resource."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler())
        self.logger.setLevel(logging.INFO)

    def on_get(self, _, resp):
        """A method that corresponds to ``GET`` for the root resource."""
        cal = Calendar()
        cal.add('prodid', '-//Azavea//NONSGML bamboo-blossom//EN')
        cal.add('version', '2.0')

        for employee in Company().get_employees():
            employee_ical = CACHE.get('employee:{}'.format(employee.id))

            if employee_ical is not None:
                self.logger.debug('HIT: For employee [%s]', employee.id)
                event = Event.from_ical(employee_ical)
            else:
                self.logger.debug('MISS: For employee [%s]', employee.id)
                event = Event.from_ical(employee.to_ical())

            cal.add_component(event)

        resp.content_type = 'text/calendar'
        resp.data = cal.to_ical()


api = falcon.API(middleware=[
    AuthMiddleware(),
])
api.add_route('/', RootResource())
