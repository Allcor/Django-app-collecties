#!/usr/bin/python3

'''
10-7-2017
    not tested yet, will only import missing countries at this point.
'''

from django.core.management.base import BaseCommand

from collectie.utils import country_code

from collectie.models import CountryCode

class Command(BaseCommand):
    args = 'start = <number>'
    help = 'help string here'

    def _populate_countries(self):
        for country in country_code.fetch_country_code():
            if not CountryCode.objects.get(name=country['Name'], code=country['Code']).exists():
                c = CountryCode(name=country['Name'], code=country['Code'])
                c.save()

    def handle(self, *args, **options):
        self._populate_countries()