from django.core.management.base import BaseCommand
from django.core.management import call_command

from collectie.models import Pathogen, Original_host, Collection, NCBI_nodes, NCBI_names

import csv

'''
This should not be needed anymore. 
Updating these values should happen anytime the value is changed. 
'''

class Command(BaseCommand):
    help = 'Updates static values from elsewhere in the database'

    def add_arguments(self, parser):
        # optional argument
        parser.add_argument('--pathogen',
                            action='store_true',
                            dest='ncbi_path',
                            default=False,
                            help='sets the hasdata flag of NCBI_nodes'
                            )
        parser.add_argument('--ncbi',
                            action='store_true',
                            dest='ncbi_name',
                            default=False,
                            help='sets the hasdata flag of NCBI_nodes'
                            )
        parser.add_argument('--species',
                            action='store_true',
                            dest='species_table',
                            default=False,
                            help='updates the static data of the Collection table'
                            )
        parser.add_argument('--index',
                            action='store_true',
                            dest='collection_table',
                            default=False,
                            help='updates the static data of the Collection table'
                            )
        parser.add_argument('--isolate',
                            nargs='?',
                            dest='singel_isolate',
                            help='updates the static data of a single isolate (given with nakt_id)'
                            )


    def taxon_name(self):
        for item in NCBI_nodes.objects.all():
            try:
                item.scientific_name = item.ncbi_names_set.get(name_class='scientific name').name_txt
            except NCBI_names.DoesNotExist:
                item.scientific_name = "No scientific name"
            item.save()

    def taxon_hasdata_path(self):
        for item in NCBI_nodes.objects.all():
            if item.has_data:
                item.parent_tax_id.make_hasdata()

    def species_update(self):
        for item in Pathogen.objects.all():
            item.scientific_name = item.taxon.get_name
            synonyms = item.taxon.ncbi_names_set.filter(name_class = "synonym").values("name_txt")
            item.synonyms = ", ".join([syn["name_txt"] for syn in synonyms])
            item.save()
        for item in Original_host.objects.all():
            item.scientific_name = item.taxon.get_name
            synonyms = item.taxon.ncbi_names_set.filter(name_class = "synonym").values("name_txt")
            item.synonyms = ", ".join([syn["name_txt"] for syn in synonyms])
            item.save()

    def collection(self):
        #call_command('collectie_update', '--populate_raw')
        for item in Collection.objects.all():
            item.update_static()
            item.update_raw_data()

    def path(self):
        for item in Pathogen.objects.all():
            item.taxon.make_hasdata()
        for item in Original_host.objects.all():
            item.taxon.make_hasdata()


    def handle(self, *args, **options):
        if options['collection_table']: #'--index'
            self.collection()
        elif options['ncbi_name']:
            self.taxon_name()
        elif options['ncbi_path']:
            self.taxon_hasdata_path()
            self.path()
        elif options['species_table']:
            self.species_update()
        elif options['singel_isolate']:
            Collection.objects.get(pk=options['singel_isolate']).update_static()
            print("updated static for isolate "+str(options['singel_isolate']))
        else:
            #print("update scientific names")
            #self.species_update()
            print("update static of collection items")
            self.collection()
            #print("update taxon_path of collection items")
            #self.path()