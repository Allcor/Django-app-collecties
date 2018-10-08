'''
https://coderwall.com/p/2z_e5g/import-iso-3166-1-countries-names-and-codes-in-a-django-model

previous use was like this,

:param model: Model holding the country code data, it must have at least two fields: name and code
:type model: Django model
:returns: boolean - state of import

from collectie.utils import country_code
country_code.populate_country_code(CountryCode)
True
'''

import requests

def fetch_country_code():
    try:
        r = requests.get('http://data.okfn.org/data/core/country-list/r/data.json')
    except requests.RequestException:
        return False
    countries = r.json()
    #makes countries a list with dictionaries, each with 'Name' and 'Code'
    for country in countries:
        yield country
