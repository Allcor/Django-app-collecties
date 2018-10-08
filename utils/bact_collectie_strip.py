'''
19-6-2017
    start of taking data out of the bacteria collection.
26-6-2017
    not fixing missing data, just skipping them to get a test set.
3-7-2017
    moved most data translation to this script.
10-7-2017
    added a option to strip_bact_eccestions so it yields raw data only
'''

from naktdata.settings import BASE_DIR
import sys, datetime, os.path, re
import csv
from optparse import Option, OptionParser
from collectie.utils.id_manigement import calculate_location

class Bactcollectie():
    
    def __init__(self):
        ##### TODO not hardcode this
        self.bact_samples_file = BASE_DIR+"/collectie/utils/lookup_tables/bactcollectie_2018-2-2.csv"
        self.bact_name_file = BASE_DIR + '/collectie/utils/lookup_tables/fixed_bactria_codes.csv'
        self.host_names_file = BASE_DIR+"/collectie/utils/lookup_tables/fixed_host_species_codes.csv"
        self.origin_code_file = BASE_DIR + '/collectie/utils/lookup_tables/fixed_origin_codes.csv'
        #####
        self.hosts = self.get_lookup_lib(self.host_names_file)
        self.bacts = self.get_lookup_lib(self.bact_name_file)
        self.loc = self.get_lookup_lib(self.origin_code_file)
    
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

    def clean_ins(self,input,year):
        """ takes the monsternummer and returns a cleaned up INS"""
        number = re.split('[ -]+', input)
        # not leading with INS
        if len(number[0]) == 2 and number[0].isdigit() and len(number) > 1:
            if number[1] != 'f':
                number.insert(0, 'INS')
        # leading with INS
        if number[0].upper() == 'INS':
            if len(number[1]) == 2 and len(number) > 2:
                if len(number[2].split('_')[0]) == 5:
                    number[0] = number[0].strip().upper()
                    return '-'.join(number)
                elif len(number[2]) == 6:
                    if number[2][0] == '0':
                        number[2] = number[2][1:]
                    elif number[2][-1] == 'A' or number[2][-1] == 'B':
                        number[2] = number[2][:5]
                    return '-'.join(number)
                elif len(number[2]) < 5 and number[2] != '':
                    number[2] = '{:05d}'.format(int(number[2]))
                    return '-'.join(number)
            elif len(number[1]) == 5:
                number.insert(1, year)
                return '-'.join(number)
            elif len(number[1]) == 7:
                number.insert(1, number[1][:2])
                number[2] = number[2][2:]
                return '-'.join(number)
        #else:
            #print(input)
            # elif 'INS' in splitline[4]:
            # number[0] = number[0][3:]
            # number.insert(0, 'INS')
            # output['codes']['INS'] = '-'.join(number)
    
    def strip_accessions(self, pre_process=True):
        with open(self.bact_samples_file) as bactcsv:
            has_header = csv.Sniffer().has_header(bactcsv.read(1024))
            bactcsv.seek(0)  # rewind
            bactcol = csv.reader(bactcsv, delimiter=';', quotechar='"')
            if has_header:
                headers = next(bactcol, None)
            for splitline in bactcol:
                output = {}
                output['bacteriecode'] = splitline[0]
                output['nummer'] = int(splitline[1])
                if splitline[2]:
                    output['isolaatnummer'] = splitline[2]
                if splitline[3]:
                    output['originele_code'] = splitline[3]
                if splitline[4]:
                    output['monsternummer'] = splitline[4]
                if splitline[5]:
                    output['gewas'] = splitline[5].strip('" ')
                if splitline[6]:
                    output['gewasoud'] = splitline[6].strip('" ')
                if splitline[7]:
                    output['materiaal'] = splitline[7]
                if splitline[8]:
                    output['herkomst'] = splitline[8]
                if splitline[9]:
                    output['jaar'] = int(splitline[9])
                if splitline[10]:
                    output['serologie'] = splitline[10]
                if splitline[11]:
                    output['qpcr'] = splitline[11]
                if splitline[12]:
                    output['pathogeniteit'] = splitline[12]
                if splitline[13]:
                    output['opmerkingen'] = splitline[13]
                if splitline[14]:
                    output['datum20'] = datetime.datetime.strptime(splitline[14],"%d-%m-%Y %H:%M:%S")
                if splitline[15]:
                    output['datum80'] = datetime.datetime.strptime(splitline[15], "%d-%m-%Y %H:%M:%S")
                if splitline[16]:
                    output['controle80'] = datetime.datetime.strptime(splitline[16], "%d-%m-%Y %H:%M:%S")
                if splitline[17]:
                    output['controle20'] = datetime.datetime.strptime(splitline[17], "%d-%m-%Y %H:%M:%S")
                if int(splitline[18]) == 1:
                    output['dienstverlening'] = True
                else:
                    output['dienstverlening'] = False
                if int(splitline[19]) == 1:
                    output['selectiecode'] = True
                else:
                    output['selectiecode'] = False
                output['nbc_nummer'] = int(splitline[20])
                if splitline[21]:
                    output['indicatie_naam'] = splitline[21]
                if splitline[22]:
                    output['lmg_code'] = splitline[22]
                if splitline[23]:
                    output['ncppb_code'] = splitline[23]
                if splitline[24]:
                    output['icmp_code'] = splitline[24]
                if splitline[25]:
                    output['pd_nvwa_code'] = splitline[25]
                if splitline[26]:
                    output['cfbp_code'] = splitline[26]
                if splitline[27]:
                    output['overige_code'] = splitline[27]
                if splitline[28]:
                    output['bevestigde_naam'] = splitline[28]
                if splitline[29]:
                    output['bevestig_meto'] = splitline[29]
                if splitline[30]:
                    output['sequentie'] = splitline[30]
                if splitline[31]:
                    output['medewerker'] = splitline[31]
                # some extra stuff for easy processing
                if pre_process:
                    output['nbc'] = 'NBC-' + splitline[20]
                    if splitline[5]:
                        if splitline[5].strip('" ') in self.hosts:
                            gewas_id = self.hosts[splitline[5].strip('" ')][0]
                            output['gewas_id'] = gewas_id[0]
                            output['gewas_txt'] = gewas_id[1]
                    elif splitline[6]:
                        if splitline[6].strip('" ') in self.hosts:
                            gewas_id = self.hosts[splitline[6].strip('" ')][0]
                            output['gewas_id'] = gewas_id[0]
                            output['gewas_txt'] = gewas_id[1]
                    if splitline[8]:
                        if output['herkomst'] in self.loc:
                            country = self.loc[splitline[8]][0]
                            output['herkomst_id'] = country[0]
                            output['herkomst_txt'] = country[1]
                    # fixing confusing user entries
                    if 'medewerker' in output:
                        if output['medewerker'] == 'Maa\nMaa':
                            output['medewerker'] = 'Maa'
                    # -- adding id's --
                    output['codes'] = {}
                    if splitline[4]:
                        if 'datum80' in output:
                            ins = self.clean_ins(splitline[4], output['datum80'].strftime('%y'))
                        elif 'jaar' in output:
                            ins = self.clean_ins(splitline[4], str(output['jaar'])[2:])
                        if ins:
                            if ins.split('-')[0] == 'INS' and len(ins.split('-')[1]) == 2 and len(ins.split('-')[2].split('_')[0]) == 5:
                                output['codes']['INS'] = ins
                    output['codes']['BacterieCode'] = output['bacteriecode']+' '+str(output['nummer'])
                    if splitline[3]:
                        output['codes']['Original'] = splitline[3]
                    # create location_id
                    storage_id = calculate_location(output['nbc'])
                    if storage_id:
                        output['codes']['Location ID'] = storage_id
                    '''
                    if splitline[4]:
                        output['codes']['monster'] = splitline[4]
                    if splitline[22]:
                        output['codes']['LMG'] = splitline[22]
                    if splitline[23]:
                        output['codes']['NCPPB'] = splitline[23]
                    if splitline[24]:
                        output['codes']['ICMP'] = splitline[24]
                    if splitline[25]:
                        output['codes']['nVWA'] = splitline[25]
                    if splitline[26]:
                        output['codes']['CFBP'] = splitline[26]
                    if splitline[27]:
                        output['codes']['overig'] = splitline[27]
                    '''
                    output['dates'] = {}
                    if splitline[9]:
                        if len(splitline[9]) != 4:
                            print(splitline[9]+ " could not be made into a 'year'")
                        else:
                            output['dates']['year of isolation'] = datetime.datetime.strptime(splitline[9],"%Y")
                    if splitline[14]:
                        output['dates']['datum -20'] = datetime.datetime.strptime(splitline[14],"%d-%m-%Y %H:%M:%S")
                    if splitline[15]:
                        output['dates']['datum -80'] = datetime.datetime.strptime(splitline[15],"%d-%m-%Y %H:%M:%S")
                    if splitline[16]:
                        output['dates']['check -80'] = datetime.datetime.strptime(splitline[16],"%d-%m-%Y %H:%M:%S")
                    if splitline[17]:
                        output['dates']['check -20'] = datetime.datetime.strptime(splitline[17],"%d-%m-%Y %H:%M:%S")
                    #adding Verification tests info
                    output['tests'] = {}
                    #TODO want to make these keys more specific. differentiate between immunostrip or IF, read primerset, if it was positive or negative
                    if splitline[10]:
                        output['tests']['serologie'] = splitline[10]
                    if splitline[11]:
                        output['tests']['pcr'] = splitline[11]
                    if splitline[12]:
                        output['tests']['pathogeniteit'] = splitline[12]
                    if splitline[30]:
                        output['tests']['sequentie'] = splitline[30]
                    #if splitline[13]:
                    #    output['tests']['comments'] = splitline[13]
                    #adding information as comments
                    output['comments'] = {}
                    if 'opmerkingen' in output:
                        output['comments']['Comment'] = output['opmerkingen']
                    if 'indicatie_naam' in output:
                        output['comments']['Indicative'] = output['indicatie_naam']
                    if 'bevestigde_naam' in output:
                        output['comments']['Confirmed'] = output['bevestigde_naam']
                    if 'bevestig_meto' in output:
                        output['comments']['Confirmation_method'] = output['bevestig_meto']
                    if splitline[0].strip('" ') in self.bacts:
                        for bacid in self.bacts[splitline[0].strip('" ')]:
                            output['bact_id'] = bacid[0]
                            output['bact_txt'] = bacid[1]
                            yield output
                    else:
                        #2 is the NCBI_id of bacteria
                        output['bact_id'] = 2
                        if splitline[0].strip('" ') != '':
                            output['bact_txt'] = splitline[0].strip('" ')
                        else:
                            output['bact_txt'] = 'unknown Bacteria'
                        yield output
                else:
                    yield output

def main(arguments):
    foo = Bactcollectie()

if __name__ == "__main__":
    main(sys.argv[1:])
