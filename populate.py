"""A command-line application to populate Redis with employee
information.
"""
import os
import logging
import click
import redis

from bamboo_blossom.core import Company

CACHE = redis.from_url(os.environ.get('REDIS_URL', 'redis://cache'))

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.INFO)


@click.command()
@click.option('--ttl', default=86400, help='Number of seconds to persist cache entries.')
def populate(ttl=86400):
    """Populates Redis with the iCal representation for each employee.

    Args:
        ttl (int): Number of seconds to persist cache entries.
    """
    for employee in Company().get_employees():
        LOGGER.info('CACHE: Adding employee [%s]', employee.id)
        CACHE.setex('employee:{}'.format(employee.id),
                    employee.to_ical(), ttl)


if __name__ == '__main__':
    populate()
