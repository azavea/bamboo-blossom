from unittest.mock import patch

from datetime import date

import pytest

from mockredis import mock_redis_client

import falcon
from falcon import testing

from bamboo_blossom.app import api
from bamboo_blossom.core import Company, Employee, Event


@pytest.fixture
def client():
    return testing.TestClient(api)


@patch('bamboo_blossom.app.CACHE', mock_redis_client())
def test_employee_calendar(client):
    employee = Employee({
        'id': 1,
        'firstName': 'Hector',
        'lastName': 'Castro',
        'preferredName': 'H',
    })

    event = Event()
    event.add('title', 'H Castro (Started: 2002-03-03)')
    event.add('dtstart', date(2018, 3, 3))
    event.add('dtend', date(2018, 3, 4))

    ical = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Azavea//NONSGML bamboo-blossom//EN
BEGIN:VEVENT
DTSTART;VALUE=DATE:20180303
DTEND;VALUE=DATE:20180304
TITLE:H Castro (Started: 2002-03-03)
END:VEVENT
END:VCALENDAR
""".replace('\n', '\r\n')

    with patch.object(Company, 'get_employees', return_value=[employee]) as _:
        with patch.object(Employee, 'to_ical', return_value=event.to_ical()) as _:
            response = client.simulate_get('/')

    assert response.status == falcon.HTTP_OK
    assert response.headers['content-type'] == 'text/calendar'
    assert response.text == ical
