
from naktdata.settings import BASE_DIR
import sys, datetime
import csv

class Isolatecollectie():

    def __init__(self):
        self.isolaten_file = BASE_DIR + '/collectie/utils/lookup_tables/isolatencollectie.csv'
        self.isolaten_code = BASE_DIR + '/collectie/utils/lookup_tables/fixed_isolaten_codes.csv'
        self.host_code_file = BASE_DIR + '/collectie/utils/lookup_tables/fixed_host_species_codes.csv'
        self.origin_code_file = BASE_DIR + '/collectie/utils/lookup_tables/fixed_origin_codes.csv'
        #####
        self.isolaten = self.get_lookup_lib(self.isolaten_code)
        self.host_lib = self.get_lookup_lib(self.host_code_file)
        self.origin_lib = self.get_lookup_lib(self.origin_code_file)

    def get_lookup_lib(self, file):
        """
         openes fixed_fungal_codes.csv and puts the fixed values in a dictionary
        :return: dictionary with raw data as keys and fixed data as values
        """
        output = {}
        with open(file, 'r') as pathogencsv:
            #has_header = csv.Sniffer().has_header(pathogencsv.read(2048))
            has_header = True
            pathogencsv.seek(0)
            pathogendata = csv.reader(pathogencsv, delimiter=';', quotechar='"')
            if has_header:
                header = next(pathogendata, None)
            for splitline in pathogendata:
                ids = splitline[3].split(',')
                given_names = splitline[1].split(',')
                output[splitline[0].strip('" ')] = [[int(ids[i].strip()),given_names[i].strip()] for i in range(len(ids))]
        return output

    def strip_accessions(self, pre_process=True):
        with open(self.isolaten_file) as fungicsv:
            reader = csv.DictReader(fungicsv, delimiter=';', quotechar='"')
            for row in reader:
                output = {}
                output['monsternummer'] = int(row['monsternummer'])
                output['collectie_class'] = row['in collectie']
                output['in_collectie'] = bool(int(row['COLLECTIE']))
                if row['ISF Code']:
                    output['isf_Code'] = row['ISF Code']
                if row['Veld1']:
                    output['aantal'] = row['Veld1']
                if row['Pathogeen']:
                    output['pathogeen'] = row['Pathogeen']
                if row['Gewas']:
                    output['gewas'] = row['Gewas'].strip()
                if row['Stam / Fysio']:
                    output['fysio_class'] = row['Stam / Fysio']
                if row['Stam / Fysio nummer']:
                    output['fysio_txt'] = row['Stam / Fysio nummer']
                if row['Isolaat']:
                    output['isolaat_class'] = row['Isolaat']
                if row['Herkomst']:
                    output['herkomst_class'] = row['Herkomst']
                if row['Herkomst code']:
                    output['herkomst_txt'] = row['Herkomst code']
                if row['Backup bedrijf']:
                    output['backup_bedrijf'] = row['Backup bedrijf']
                if row['Beheertype']:
                    output['beheertype'] = row['Beheertype']
                output['overzet_3mnds'] = bool(int(row['3mnds overzetten?']))
                if row['medium overzetten']:
                    output['overzet_medium'] = row['medium overzetten']
                output['in_freez_low'] = bool(int(row['in -80°C?']))
                output['in_grond'] = bool(int(row['in grond?']))
                output['gevriesdroogd'] = bool(int(row['gevriesdroogd?']))
                if row['# vriesdroog']:
                    output['vriesdroog_nr'] = row['# vriesdroog']
                if row['Proefnummer']:
                    output['proefnummer'] = datetime.datetime.strptime(row['Proefnummer'],"%d-%m-%Y %H:%M:%S")
                output['opstart_bron'] = bool(int(row['jaarlijks opstarten uit -80°C of grond?']))
                if row['jaarlijks opstarten opmerking']:
                    output['opstart_opm'] = row['jaarlijks opstarten opmerking']
                if row['# -80°C']:
                    output['freez_low_nr'] = int(row['# -80°C'])
                if row['-80°C lokatie']:
                    output['freez_low_lok'] = row['-80°C lokatie']
                if row['-80°C datum']:
                    output['freez_low_datum'] = datetime.datetime.strptime(row['-80°C datum'],"%d-%m-%Y %H:%M:%S")
                if row['-80°C opm']:
                    output['freez_low_opm'] = row['-80°C opm']
                output['in_freezer'] = bool(int(row['in -20°C?']))
                if row['opm']:
                    output['opm'] = row['opm']
                if row['ook/was']:
                    output['ook_was'] = row['ook/was']
                # some extra stuff for easy processing
                if pre_process:
                    output['nic'] = 'NIC-' + output['collectie_class'] + '-' + str(output['monsternummer'])
                    # dates of samples
                    output['dates'] = {}
                    if row['-80°C datum']:
                        output['dates']['datum -80'] = output['freez_low_datum']
                    # getting country of origin
                    if 'herkomst_class' in output:
                        if output['herkomst_class'] in self.origin_lib: #TODO figure out what to do with unknown locations
                            origin = self.origin_lib[output['herkomst_class']][0]
                            output['origin'] = origin[1]
                            output['_origin'] = origin[0]
                    # getting the NCBI_taxon id for the host species
                    if 'gewas' in output:
                        host = self.host_lib[output['gewas']][0]
                        output['gewas_id'] = host[0]
                        output['gewas_txt'] = host[1]
                    # pathogen NCBI_taxon id
                    if row['Pathogeen'].strip('" ') in self.isolaten:
                        # each virus in the sample is seperatly yielded. This creates multiple entries.
                        for fungusid in self.isolaten[row['Pathogeen'].strip('" ')]:
                            output['pathogeen_id'] = fungusid[0]
                            output['pathogeen_txt'] = fungusid[1]
                            yield output
                    else:
                        # 12908 is the id of unclassified sequences
                        output['pathogeen_id'] = 12908
                        if row['Pathogeen'].strip('" ') != '':
                            output['pathogeen_txt'] = row['Pathogeen'].strip('" ')
                        else:
                            output['pathogeen_txt'] = 'unknown Isolate'
                        yield output
                else:
                    yield output

def main(arguments):
    foo = Isolatecollectie()
    foo.strip_accessions()

if __name__ == "__main__":
    main(sys.argv[1:])