'''
11-7-2017
    start with script, ment to yield stuff from the fungal collection to be used in the django commands
'''

from naktdata.settings import BASE_DIR
import sys, datetime, re
import csv

class Fungcollectie():

    def __init__(self):
        self.fungal_file = BASE_DIR + '/collectie/utils/lookup_tables/schimmelcollectie_2018-2-12.csv'
        self.fungal_code_file = BASE_DIR + '/collectie/utils/lookup_tables/fixed_fungal_codes.csv'
        self.host_code_file = BASE_DIR + '/collectie/utils/lookup_tables/fixed_host_species_codes.csv'
        self.origin_code_file = BASE_DIR + '/collectie/utils/lookup_tables/fixed_origin_codes.csv'
        #####
        self.fungus = self.get_lookup_lib(self.fungal_code_file)
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

    def clean_ins(self, in_txt, year=None):
        output = None
        split_txt = re.split('[- ]+', in_txt)
        if split_txt[0].upper() == 'INS':
            if len(split_txt) > 4:
                if split_txt[-1] and split_txt[-1][-1] == ')':
                    output = [('-'.join(split_txt[:4])), ('-'.join(split_txt[:3])+ '-' + split_txt[3][:-1]+split_txt[4].strip('()'))]
                else:
                    output = '-'.join(split_txt[:4]) + '_' + ''.join([x for x in split_txt[4:] if x])
            else:
                output = '-'.join([x for x in split_txt if x and x[0] != '('])
        elif split_txt[0] == year and split_txt[1].split('_')[0].isdigit():
            if len(split_txt) > 3:
                output = 'INS-' + '-'.join(split_txt[:3]) + '_' + ''.join([x for x in split_txt[3:] if x.isdigit()])
            elif len(split_txt) == 2:
                foo = split_txt[1].split('_')
                if len(foo) == 1:
                    output = 'INS-' + split_txt[0] + '-' + '{:05}'.format(int(split_txt[1]))
                else:
                    output = 'INS-' + split_txt[0] + '-' + '{:05}'.format(int(foo[0])) + '_' + foo[1]
            else:
                output = 'INS-' + '-'.join(split_txt)
        elif len(split_txt[0]) == 2 and split_txt[0].isdigit() and len(split_txt[1]) == 5:
            if len(split_txt) > 3:
                output = 'INS-' + '-'.join(split_txt[:3]) + '_' + ''.join([x for x in split_txt[3:] if x.isdigit()])
            else:
                output = 'INS-' + '-'.join(split_txt[:3])
        else:
            None #there are some 5 digit codes that might be INS
        return output

    def strip_accessions(self, pre_process=True):
        with open(self.fungal_file) as fungicsv:
            has_header = csv.Sniffer().has_header(fungicsv.read(1024))
            fungicsv.seek(0)  # rewind
            fungicol = csv.reader(fungicsv, delimiter=';', quotechar='"')
            if has_header:
                headers = next(fungicol, None)
            for splitline in fungicol:
                output = {}
                output['naam_schimmel'] = splitline[0]
                if splitline[1]:
                    output['gewas'] = splitline[1]
                if splitline[2]:
                    output['materiaal'] = splitline[2]
                if splitline[3]:
                    output['symptomen'] = splitline[3]
                if splitline[4]:
                    output['herkomst'] = splitline[4]
                if splitline[5]:
                    output['ins_nummer'] = splitline[5]
                if splitline[6]:
                    output['monstercode'] = splitline[6]
                if splitline[7]:
                    output['jaar'] = int(splitline[7].split('\n')[0]) #need to split for that one fucked up entry
                if splitline[8]:
                    output['opmerkingen'] = splitline[8]
                if splitline[9]:
                    output['datum80'] = datetime.datetime.strptime(splitline[9],"%d-%m-%Y %H:%M:%S")
                if splitline[10]:
                    output['nummer'] = int(splitline[10])
                if splitline[11]:
                    output['controle80'] = datetime.datetime.strptime(splitline[11],"%d-%m-%Y %H:%M:%S")
                if splitline[12]:
                    output['grond4'] = datetime.datetime.strptime(splitline[12],"%d-%m-%Y %H:%M:%S")
                if splitline[13]:
                    output['code4'] = int(splitline[13])
                if splitline[14]:
                    output['controle4'] = datetime.datetime.strptime(splitline[14],"%d-%m-%Y %H:%M:%S")
                if splitline[15]:
                    output['datum4'] = datetime.datetime.strptime(splitline[15],"%d-%m-%Y %H:%M:%S")
                if splitline[16]:
                    output['nummer4'] = int(splitline[16])
                if splitline[17]:
                    output['controlebuis4'] = datetime.datetime.strptime(splitline[17],"%d-%m-%Y %H:%M:%S")
                if splitline[18]:
                    if int(splitline[18]) == 1:
                        output['dienstverlening'] = True
                    else:
                        output['dienstverlening'] = False
                if splitline[19]:
                    output['autonummer'] = int(splitline[19])
                if splitline[20]:
                    output['medewerker'] = splitline[20]
                if splitline[21]:
                    output['sequence'] = splitline[21]
                # some extra stuff for easy processing
                if pre_process:
                    output['nfc'] = 'NFC-' + str(output['autonummer'])
                    output['codes'] = {}
                    if 'ins_nummer' in output:
                        if 'datum80' in output:
                            year = output['datum80'].strftime('%y')
                        elif 'jaar' in output:
                            year = str(output['jaar'])[2:]
                        else:
                            year = None
                        ins = self.clean_ins(output['ins_nummer'], year)
                        if ins:
                            output['codes']['INS'] = ins
                    if 'nummer' in output:
                        output['codes']['Location ID'] = 'POS-'+str(output['nummer'])
                    # fixing confusing user entries
                    if 'medewerker' in output:
                        if output['medewerker'] == 'maa':
                            output['medewerker'] = 'Maa'
                    output['dates'] = {}
                    if 'jaar' in output:
                        if len(splitline[7].split('\n')[0]) != 4:
                            print(splitline[7]+ " could not be made into a 'year'")
                        else:
                            output['dates']['year of isolation'] = datetime.datetime.strptime(splitline[7].split('\n')[0],"%Y")
                    if 'datum80' in output:
                        output['dates']['datum -80'] = output['datum80']
                    if 'controle80' in output:
                        output['dates']['check -80'] = output['controle80']
                    if 'grond4' in output:
                        output['dates']['datum earth -4'] = output['grond4']
                    if 'controle4' in output:
                        output['dates']['check earth -4'] = output['controle4']
                    if 'datum4' in output:
                        output['dates']['datum -4'] = output['datum4']
                    if 'controlebuis4' in output:
                        output['dates']['check -4'] = output['controlebuis4']
                    # getting country of origin
                    if 'herkomst' in output:
                        if output['herkomst'] in self.origin_lib: #TODO figure out what to do with unknown locations
                            origin = self.origin_lib[output['herkomst']][0]
                            output['origin_id'] = origin[0]
                            output['origin_txt'] = origin[1]
                    # getting the NCBI_taxon id for the host species
                    if 'gewas' in output:
                        host = self.host_lib[output['gewas']][0]
                        output['gewas_id'] = host[0]
                        output['gewas_txt'] = host[1]
                    # -- adding tests --
                    output['tests'] = {}
                    #if 'opmerkingen' in output:
                    #    output['tests']['comments'] = output['opmerkingen']
                    # -- adding comments --
                    output['comments'] = {}
                    if 'opmerkingen' in output:
                        output['comments']['Comment'] = output['opmerkingen']
                    #if 'symptomen' in output:
                    #    output['comments']['Observed symptoms'] = output['symptomen']
                    #getting the NCBI_taxon id for the pathogen species
                    if output['naam_schimmel'].strip('" ') in self.fungus:
                        # each virus in the sample is seperatly yielded. This creates multiple entries.
                        for fungusid in self.fungus[output['naam_schimmel'].strip('" ')]:
                            output['pathogeen_id'] = fungusid[0]
                            output['pathogeen_txt'] = fungusid[1]
                            yield output
                    else:
                        # 4751 is the id of Fungi
                        output['pathogeen_id'] = 4751
                        if output['naam_schimmel'].strip('" ') != '':
                            output['pathogeen_txt'] = output['naam_schimmel'].strip('" ')
                        else:
                            output['pathogeen_txt'] = 'unknown Fungi'
                        yield output
                else:
                    yield output

def main(arguments):
    foo = Fungcollectie()
    foo.strip_accessions()

if __name__ == "__main__":
    main(sys.argv[1:])