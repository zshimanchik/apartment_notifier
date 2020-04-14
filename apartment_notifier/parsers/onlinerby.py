import logging
from urllib.parse import urlparse, parse_qs

import requests

from apartment_notifier.models import Apartment

_LOGGER = logging.getLogger(__name__)


class OnlinerbyParser:
    NAME = 'onlinerby'

    def __init__(self, url):
        url = url.replace('#bounds', '&bounds')
        parsed_url = urlparse(url)
        self.q_params = parse_qs(parsed_url.query)


    def parse(self):
        url = 'https://ak.api.onliner.by/search/apartments?rent_type'
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:74.0) Gecko/20100101 Firefox/74.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5"
        }

        params = self.q_params
        params['page'] = 1
        _LOGGER.debug('Getting page 1')
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        last_page = data['page']['last']

        for item in data['apartments']:
            yield self.item_to_model(item)

        for page in range(2, last_page+1):
            params['page'] = page
            _LOGGER.debug('Getting page %s', page)
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            for item in data['apartments']:
                yield self.item_to_model(item)

    def item_to_model(self, item):
        return Apartment(
            self.NAME,
            item['id'],
            item['location']['user_address'],
            item['photo'],
            item['price']['amount'],
            item['price']['currency'],
            item['url'],
            item['created_at'],
            item['last_time_up'],
        )
