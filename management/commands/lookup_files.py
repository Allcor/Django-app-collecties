from django.core.management.base import BaseCommand
from django.db.models import Count

from naktdata.settings import BASE_DIR
from collectie.models import NCBI_names, CountryCode
from pathlib import Path

import csv

class Command(BaseCommand):
    help = 'Creates files to look up NCBI_id for species in the collection'

    def add_arguments(self, parser):
        #optional argument
        parser.add_argument('--virus',
                            action='store_true',
                            dest='checking_virus',
                            default=False,
                            help='creates the sepecies lookup table for the virus collection'
                            )
        parser.add_argument('--fungus',
                            action='store_true',
                            dest='checking_fungus',
                            default=False,
                            help='creates the species lookup table for the fungal collection'
                            )
        parser.add_argument('--bacteria',
                            action='store_true',
                            dest='checking_bacteria',
                            default=False,
                            help='creates the species lookup table for the bacteria collection'
                            )
        parser.add_argument('--isolaten',
                            action='store_true',
                            dest='checking_isolaten',
                            default=False,
                            help='creates the species lookup table for the isolaten collection'
                            )
        parser.add_argument('--host',
                            action='store_true',
                            dest='checking_host',
                            default=False,
                            help='creates the lookup table for the host species'
                            )
        parser.add_argument('--origin',
                            action='store_true',
                            dest='checking_country',
                            default=False,
                            help='creates the lookup table for the origin of the isolate'
                            )
        parser.add_argument('--material',
                            action='store_true',
                            dest='checking_material',
                            default=False,
                            help='creates the lookup table for the origin of the isolate'
                            )

    def _check_tables(self, column_data, lookupfile):
        if lookupfile.is_file():
            with lookupfile.open() as csvfile:
                reader = csv.DictReader(csvfile, delimiter=';', quotechar='"')
                existing_values = {}
                for row in reader:
                    existing_values[row[self.fieldnames[0]]] = row
        else:
            with lookupfile.open(mode='w+') as newfile:
                csvwriter = csv.DictWriter(newfile, fieldnames=self.fieldnames, delimiter=';', quotechar='"')
                csvwriter.writeheader()
            existing_values = {}
        self._init_names(lookupfile, column_data, existing_values)
        self._check_names(lookupfile)


    def _check_names(self, lookuptable):
        """
            takes lookup table scientific names and adds the associating NCBI_id's write these in a new file.
        """
        outfile = lookuptable.with_name('fixed_' + lookuptable.name)
        fixed_data = []
        with lookuptable.open() as infile:
            csvreader = csv.DictReader(infile, delimiter=';', quotechar='"')
            for line in csvreader:
                raw_value = line[self.fieldnames[0]]
                if line[self.fieldnames[1]]:
                    save_as = line[self.fieldnames[1]].split(',')
                else:
                    save_as = [raw_value]
                if line[self.fieldnames[2]] != '':
                    excepted_name = line[self.fieldnames[2]].split(',')
                    if line[self.fieldnames[3]] != '':
                        tax_id = line[self.fieldnames[3]].split(',')
                    else:
                        tax_id = ['' for i in range(len(excepted_name))]
                    id_list = []
                    if self.validation_type == 'Taxon':
                        for i in range(len(excepted_name)):
                            id = self._taxon_fixed_lookup(excepted_name[i].strip('" '),tax_id[i])
                            if id:
                                id_list.append(str(id))
                    elif self.validation_type == 'Country':
                        country = ','.join(excepted_name)
                        id = self._country_fixed_lookup(country.strip('" '))
                        if id:
                            id_list.append(str(id))
                    else:
                        id = None
                        if id:
                            id_list.append(str(id))
                    if len(save_as) == len(id_list):
                        fixed_data.append({self.fieldnames[0]: raw_value, self.fieldnames[1]: ','.join(save_as), self.fieldnames[2]: ','.join(excepted_name), self.fieldnames[3]: ','.join(id_list)})
                    else:
                        print("given_names not set:", save_as, id_list)
                else:
                    print("not added to fixed: ", line[self.fieldnames[0]])
        #write to file
        with outfile.open(mode='w+') as fixedfile:
            csvwriter = csv.DictWriter(fixedfile, fieldnames=self.fieldnames, delimiter=';', quotechar='"')
            csvwriter.writeheader()
            for line in fixed_data:
                csvwriter.writerow(line)


    def _taxon_lookup(self,lookup_value):
        names = []
        for id in NCBI_names.objects.filter(name_txt=lookup_value):
            name = NCBI_names.objects.get(name_class='scientific name', tax_id=id.tax_id_id).name_txt
            names.append(name)
        return names

    def _taxon_fixed_lookup(self, name, tax_id):
        try:
            id = NCBI_names.objects.get(name_txt=name, name_class='scientific name').tax_id.tax_id
            return id
        except NCBI_names.MultipleObjectsReturned:
            if tax_id != '':
                return tax_id
            else:
                print('multiple taxon possible: ', name)
        except NCBI_names.DoesNotExist:
            print("ncbi_name no proper scientific name: ", name)

    def _country_lookup(self,lookup_value):
        names = []
        for id in CountryCode.objects.filter(name__iexact=lookup_value):
            name = id.name
            names.append(name)
        for id in CountryCode.objects.filter(code__iexact=lookup_value):
            name = id.name
            names.append(name)
        return names

    def _list_lookup(self, name):
        names = []
        for item in self.material_options:
            if item in name.lower():
                names.append(item)
        if names != []:
            print(names)
        return names

    def _country_fixed_lookup(self, name):
        if name == 'Unknown':
            name = ''
        try:
            id = CountryCode.objects.get(name=name).pk
            return id
        except CountryCode.DoesNotExist:
            print("name no proper Countrycode: ", name)


    def _init_names(self, filepath, data_range, existing_values):
        """
            takes a table and column, looks up all the values in specified column, writes it in a file.
            skips values that are in existing_values
        """
        counts = {}
        #for entry in tablename.objects.values(fieldname).order_by(fieldname).annotate(the_count=Count(fieldname)):
        for value,count in data_range.items():
            if value in counts:
                counts[value] += count
            else:
                counts[value] = count
        #make new file
        with filepath.open(mode='a') as outfile:
            for key, value in counts.items():
                if not key in existing_values:
                    if self.validation_type == 'Taxon':
                        names = self._taxon_lookup(key)
                    elif self.validation_type == 'Country':
                        names = self._country_lookup(key)
                    elif self.validation_type == 'Other':
                        names = self._list_lookup(key)
                    outfile.write(key + ";;" + ','.join(names) + ";\n")


    def _get_data_range(self, sourcefile, column_nr, data_range=None):
        """
        reads a table column and returns all the values that it holds.
        :param sourcefile: CSV document
        :param column_nr: The column index of column to be read
        :return: values and count of column
        """
        if not data_range:
            data_range = {}
        with open(sourcefile) as sourcecsv:
            data = csv.DictReader(sourcecsv, delimiter=';', quotechar='"')
            header = data.fieldnames
            for line in data:
                value = line[header[column_nr]].strip()
                if value in data_range:
                    data_range[value] += 1
                else:
                    data_range[value] = 1
        return data_range


    def handle(self, *args, **options):

        self.validation_type = 'Taxon'
        self.fieldnames = ['Value','Value_fix','NCBI_name','NCBI_id']

        #source
        self.fungal_file = BASE_DIR + '/collectie/utils/lookup_tables/schimmelcollectie_2018-2-12.csv'
        self.isolaten_file = BASE_DIR + '/collectie/utils/lookup_tables/isolatencollectie.csv'
        self.virus_file = BASE_DIR + "/collectie/utils/lookup_tables/viruscollectievriezer.csv"
        self.bacteria_file = BASE_DIR + "/collectie/utils/lookup_tables/bactcollectie_2018-2-2.csv"
        self.weefsel_file = BASE_DIR + "/collectie/utils/lookup_tables/virus_weefselkweek.csv"
        self.kas_file = BASE_DIR + "/collectie/utils/lookup_tables/Virus_kas_roelofarendveen.csv"
        #lookup
        self.virus_lookuptable = Path(BASE_DIR+'/collectie/utils/lookup_tables/virus_codes.csv')
        self.fungal_lookuptable = Path(BASE_DIR + '/collectie/utils/lookup_tables/fungal_codes.csv')
        self.bacteria_lookuptable = Path(BASE_DIR + '/collectie/utils/lookup_tables/bactria_codes.csv')
        self.isolaten_lookuptable = Path(BASE_DIR + '/collectie/utils/lookup_tables/isolaten_codes.csv')
        self.host_lookuptable = Path(BASE_DIR + '/collectie/utils/lookup_tables/host_species_codes.csv')
        self.origin_lookuptable = Path(BASE_DIR + '/collectie/utils/lookup_tables/origin_codes.csv')
        self.material_lookuptable = Path(BASE_DIR + '/collectie/utils/lookup_tables/material_options.csv')

        if options['checking_fungus']:
            column_data = self._get_data_range(self.fungal_file, 0)
            self._check_tables(column_data, self.fungal_lookuptable)
        elif options['checking_virus']:
            column_data = self._get_data_range(self.virus_file, 4)
            column_data = self._get_data_range(self.weefsel_file, 5, column_data)
            column_data = self._get_data_range(self.kas_file, 3, column_data)
            column_data = self._get_data_range(self.kas_file, 4, column_data)
            self._check_tables(column_data, self.virus_lookuptable)
        elif options['checking_bacteria']:
            column_data = self._get_data_range(self.bacteria_file, 0)
            self._check_tables(column_data, self.bacteria_lookuptable)
        elif options['checking_isolaten']:
            column_data = self._get_data_range(self.isolaten_file, 5)
            self._check_tables(column_data, self.isolaten_lookuptable)
        elif options['checking_host']:
            column_data = self._get_data_range(self.fungal_file, 1)
            column_data = self._get_data_range(self.bacteria_file, 5, column_data)
            column_data = self._get_data_range(self.bacteria_file, 6, column_data)
            column_data = self._get_data_range(self.virus_file, 6, column_data)
            column_data = self._get_data_range(self.isolaten_file, 6, column_data)
            self._check_tables(column_data, self.host_lookuptable)
        elif options['checking_country']:
            self.validation_type = 'Country'
            self.fieldnames = ['Value', 'Value_fix', 'ISO_name', 'ISO_id']
            column_data = self._get_data_range(self.fungal_file, 4)
            column_data = self._get_data_range(self.bacteria_file, 8, column_data)
            column_data = self._get_data_range(self.virus_file, 10, column_data)
            column_data = self._get_data_range(self.isolaten_file, 10, column_data)
            self._check_tables(column_data, self.origin_lookuptable)
        elif options['checking_material']:
            self.validation_type = 'Other'
            self.material_options = ['tak', 'bloem', 'stengel', 'vrucht', 'bol', 'knol', 'blad', 'wortel', 'zaad']
            self.fieldnames = ['Value', 'Value_fix', 'material', '?']
            column_data = self._get_data_range(self.fungal_file, 2)
            column_data = self._get_data_range(self.bacteria_file, 7, column_data)
            column_data = self._get_data_range(self.virus_file, 9, column_data)
            print(column_data)
            #self._check_tables(column_data, self.material_lookuptable)
        else:
            print("Checking Virus codes")
            column_data = self._get_data_range(self.virus_file, 4)
            column_data = self._get_data_range(self.weefsel_file, 5, column_data)
            column_data = self._get_data_range(self.kas_file, 3, column_data)
            column_data = self._get_data_range(self.kas_file, 4, column_data)
            self._check_tables(column_data, self.virus_lookuptable)
            print("Checking Bacteria codes")
            column_data = self._get_data_range(self.bacteria_file, 0)
            self._check_tables(column_data, self.bacteria_lookuptable)
            print("Checking Fungal codes")
            column_data = self._get_data_range(self.fungal_file, 0)
            self._check_tables(column_data, self.fungal_lookuptable)
            print("Checking Isolate codes")
            column_data = self._get_data_range(self.isolaten_file, 5)
            self._check_tables(column_data, self.isolaten_lookuptable)
            print("Checking host codes")
            column_data = self._get_data_range(self.fungal_file, 1)
            column_data = self._get_data_range(self.bacteria_file, 5, column_data)
            column_data = self._get_data_range(self.bacteria_file, 6, column_data)
            column_data = self._get_data_range(self.virus_file, 6, column_data)
            column_data = self._get_data_range(self.isolaten_file, 6, column_data)
            column_data = self._get_data_range(self.kas_file, 6, column_data)
            self._check_tables(column_data, self.host_lookuptable)
            print('Checking country codes')
            self.validation_type = 'Country'
            self.fieldnames = ['Value', 'Value_fix', 'ISO_name', 'ISO_id']
            column_data = self._get_data_range(self.fungal_file, 4)
            column_data = self._get_data_range(self.bacteria_file, 8, column_data)
            column_data = self._get_data_range(self.virus_file, 10, column_data)
            column_data = self._get_data_range(self.isolaten_file, 10, column_data)
            self._check_tables(column_data, self.origin_lookuptable)