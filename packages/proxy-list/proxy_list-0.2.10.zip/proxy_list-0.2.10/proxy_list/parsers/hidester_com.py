import json
import requests
from iso3166 import countries

group = 'hidester.com'

def hidester_com():

    response = requests.get(

        'https://hidester.com/proxydata/php/data.php',

        headers = {

            'Host': 'hidester.com',
            'Referer': 'https://hidester.com/proxylist/'
        },

        params = {

            'limit': 100000,
            'mykey': 'data',
            'offset': 0,
            'orderBy': 'latest_check',
            'sortOrder': 'DESC',
        }
    )

    proxies, data = [], json.loads(response.text)

    for proxy in data:

        countries_iso3166 = {

            'VENEZUELA': 'Venezuela, Bolivarian Republic of',
            'CURACAO': 'Curaçao',
            'KOREA': 'Korea, Republic of',
            'MOLDOVA': 'Moldova, Republic of',
            'PALESTINIAN TERRITORY': 'Palestine, State of',
            'UNITED KINGDOM': 'United Kingdom of Great Britain and Northern Ireland',
            'VIETNAM': 'Viet Nam',
            'CZECH REPUBLIC': 'Czechia',
            'IRAN': 'Iran, Islamic Republic of',
            'BOLIVIA': 'Bolivia, Plurinational State of'
        }

        if proxy['country'] in countries_iso3166:

            proxy['country'] = countries_iso3166[proxy['country']]

        proxies.append({

            'ip': proxy['IP'],
            'port': str(proxy['PORT']),

            'type': proxy['type'],

            'country': countries.get(proxy['country']).alpha2
        })

    return proxies

parsers = [hidester_com]
