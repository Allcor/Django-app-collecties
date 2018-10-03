#!/usr/bin/python3

'''
Script to fetch common names from eol.
    http://eol.org/api/docs/search_by_provider
    http://eol.org/api/docs/pages
    
for now it takes all the nodes and quiries names of each

8-6-2017:
    fetch the name data from eol.org/api and add them to the NCBI_names
12-6-2017:
    this process toakes f*cking long (the net request), adding option so updateing can be done in stages.
21-6-2017:
    ended up using wikidata instead as it was way faster. This could be revived for individual quiries.
'''

from django.core.management.base import BaseCommand
from django.db import transaction

from collectie.utils.eol_names import EOL_query
from collectie.models import NCBI_names, NCBI_nodes

import requests
import sys

class Command(BaseCommand):
    args = 'start = <number>'
    help = 'help string here'
    
    def _fetch_eol_names(self, start=0):
        #the label used to identify this name class
        NAME_LABLE = 'eol_vernacular'
        #loops on all tax_id
        count = 0
        for node in NCBI_nodes.objects.all().iterator():
            if count % 100 == 0:
                sys.stdout.write('\r')
                sys.stdout.write("nodes checked: "+str(count))
                sys.stdout.flush()
            count += 1 
            if count >= start:
                tax_id = node.tax_id
                #yields all dutch names on eol for this tax_id
                for name in self.eol_quiry.fetch_dutch_verniculars(tax_id):
                    node.ncbi_names_set.create(name_txt=name, name_class=NAME_LABLE)
        sys.stdout.write('\r')
        sys.stdout.flush()
        print ("nodes checked: "+str(count))
    
    def handle(self, *args, **options):
        self.eol_quiry = EOL_query()
        if "start" in options:
            start = options["start"]
        else:
            start = 0
        with transaction.atomic():
            self._fetch_eol_names(start)
