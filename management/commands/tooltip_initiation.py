from django.core.management.base import BaseCommand

from collectie.models import Table_descriptions
from collectie.models import Collection, Bacteriecollectie, Schimmelcollectie, Viruscollectie, Isolatencollectie, VirusWeefsel, VirusKas


class Command(BaseCommand):
    help = 'Will initiate (not update) column name descriptions'

    def add_arguments(self, parser):
        # optional argument
        parser.add_argument('--init',
                            action='store_true',
                            dest='initiate_table',
                            default=False,
                            help='sets the hasdata flag of NCBI_nodes'
                            )

    def tooltip_initiate(self):
        tables = [Collection, Bacteriecollectie, Schimmelcollectie, Viruscollectie, VirusWeefsel, VirusKas]
        # Origin_pathogen, Original_host, Pathogen, Collection_id, Sample, UserSelected, Changelog
        for table in tables:
            self.add_column_names(table)

    def add_column_names(self, model_class):
        # This will not update the reference. only create new.
        _table = model_class._meta.db_table
        for column in model_class._meta._get_fields():
            if column.many_to_one:
                _column = column.name + '_id'
            else:
                _column = column.name
            _auto_created = column.auto_created
            if not Table_descriptions.objects.filter(table=_table, column=_column).exists():
                Table_descriptions.objects.create(table=_table, column=_column, auto_created=_auto_created)


    def handle(self, *args, **options):
        if options['initiate_table']:
            self.tooltip_initiate()
        else:
            print("options: --init")