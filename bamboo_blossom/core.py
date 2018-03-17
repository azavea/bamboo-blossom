"""Core classes utilized to wrap BambooHR objects."""

import os
import uuid

from datetime import date, datetime
from dateutil.parser import parse

from PyBambooHR import PyBambooHR

from icalendar import Event

CLIENT = PyBambooHR.PyBambooHR(subdomain=os.environ.get('BAMBOOHR_SUBDOMAIN', ''),
                               api_key=os.environ.get('BAMBOOHR_API_KEY', ''))


class Company(object):
    """Class to house zero to many Employee objects."""

    def get_employees(self):
        """Returns a list of Employee objects.

        Returns:
            list: A list of Employee objects.
        """
        return [Employee(e) for e in CLIENT.get_employee_directory()]


class Employee(object):
    """Class to represent an employee with support for iCal."""

    def __init__(self, employee):
        self.id = employee['id']
        self.first_name = employee['firstName']
        self.last_name = employee['lastName']
        self.preferred_name = employee['preferredName']

    @property
    def hire_date(self):
        """Returns a ``datetime`` object representing employee hire date.

        Returns:
            datetime: A datetime object for employee hire date.
        """
        return parse(CLIENT.get_employee(self.id, ['hireDate'])['hireDate'])

    def to_ical(self):
        """Returns the iCal event representation of an employee hire date.

        Currently, the event only contains the following fields:

        - ``title``
        - ``dtstart``
        - ``dtend``

        The event is an all-day event because dates are specified vs. dates
        and times.

        Returns:
            str: The iCal event representation of an employee hire date.
        """
        current_year = date.today().year

        event = Event()
        event.add('uid', uuid.uuid4())
        event.add('summary', '{} {} (Started: {})'.format(
            self.preferred_name or self.first_name,
            self.last_name,
            self.hire_date.strftime('%Y-%m-%d')))

        event.add('dtstamp',
                  datetime(current_year, self.hire_date.month, self.hire_date.day))
        event.add('dtstart',
                  date(current_year, self.hire_date.month, self.hire_date.day))

        return event.to_ical()
