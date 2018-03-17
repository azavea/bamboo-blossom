# bamboo-blossom

[![Build Status](https://travis-ci.org/azavea/bamboo-blossom.svg?branch=master)](https://travis-ci.org/azavea/bamboo-blossom)

A web application that publishes BambooHR employee hire dates to an iCal feed.

## Getting Started

First, ensure that the following environment variables are set inside of a local `.env` file at the root of the repository. Use `.env.example` as a guide.

- `BB_API_SECRET_KEY` - User-defined secret key required for `?key=` request authorization
- `BAMBOOHR_SUBDOMAIN` - Subdomain name of your BambooHR organization
- `BAMBOOHR_API_KEY` - BambooHR API key

Next, bring up the development environment (a Falcon WSGI application, and Redis) using Docker Compose.

```bash
$ docker-compose up
```

Then, populate the Redis cache with employee hire dates. This step isn't 100% necessary, but it helps to populate the cache outside the context of a request/response cycle to avoid timeouts if you have more than a handful of employees.

```bash
$ docker-compose run --rm app python populate.py
```

Lastly, interact with the API to retrieve employee hire dates as an iCal calendar.

```bash
$ http "localhost:8000?key=..."
HTTP/1.1 200 OK
Connection: close
Date: Sat, 17 Mar 2018 14:59:53 GMT
Server: gunicorn/19.7.1
content-length: 214
content-type: text/calendar

BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Azavea//NONSGML bamboo-blossom//EN
BEGIN:VEVENT
DTSTART;VALUE=DATE:20180815
DTEND;VALUE=DATE:20180816
TITLE:John Doe (Started: 2013-03-03)
END:VEVENT
END:VCALENDAR
```

## Testing

To execute the linter and test suite use `pylint` and `pytest`, respectively.

```bash
$ docker-compose run --rm app pylint bamboo_blossom
$ docker-compose run --rm -e BB_API_SECRET_KEY= app pytest tests
```
