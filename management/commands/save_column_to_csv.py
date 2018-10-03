from django.core.management.base import BaseCommand
from django.db.models import Count
from naktdata.settings import BASE_DIR
from collectie.models import Collection

import os
import csv


class Command(BaseCommand):
    help = '''
        This creates a unique query for a column in collectie.collection.
        These are then written in a .csv file.'''

    def add_arguments(self, parser):
        #optional arguments
        parser.add_argument('-c','--column',
                            action='store',
                            dest='column',
                            required=True,
                            default=False,
                            help='specifies the column to summarise'
                            )
        parser.add_argument('-o', '--output',
                            action='store',
                            dest='output',
                            help='file to write the result to'
                            )

    def _read_column(self, col):
        col_values = Collection.objects.values(col,'pk')
        return col_values

    def _write_queryset(self,query,file):
        headers = query[0].keys()
        with open(file,'w') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=headers, delimiter=';', quotechar='"')
            writer.writeheader()
            writer.writerows(query)

    def handle(self, *args, **options):
        #checking outfile path
        if options["output"]:
            outfile = options["output"]
        else:
            file_name = options['column']+'_values.csv'
            outfile = os.path.join(BASE_DIR,'media','collectie',file_name)
        #getting data
        data = self._read_column(options['column'])
        #writing data
        self._write_queryset(data,outfile)