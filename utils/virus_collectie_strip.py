'''
11-7-2017
    start with script, ment to yield stuff from the virus collection to be used in the django commands
'''

from naktdata.settings import BASE_DIR
from collectie.utils import id_manigement

import sys, re, datetime
import csv

class Viralcollectie():

    def __init__(self):
        self.virus_file = BASE_DIR+"/collectie/utils/lookup_tables/viruscollectievriezer.csv"
        self.virus_ncbi_file = BASE_DIR+"/collectie/utils/lookup_tables/fixed_virus_codes.csv"
        self.host_ncbi_file = BASE_DIR+"/collectie/utils/lookup_tables/fixed_host_species_codes.csv"
        self.origin_code_file =  BASE_DIR+"/collectie/utils/lookup_tables/fixed_origin_codes.csv"
        #####
        self.virus = self.get_lookup_lib(self.virus_ncbi_file)
        self.host = self.get_lookup_lib(self.host_ncbi_file)
        self.origin_lib = self.get_lookup_lib(self.origin_code_file)

    def fix_date(self,dateline):
        """
        takes the date from the csv file and makes a datetime object from it.
        :param dateline: string with date in it from infile
        :return: datetime object
        """
        try:
            return datetime.datetime.strptime(dateline, "%d-%m-%Y")
        except ValueError:
            try:
                return datetime.datetime.strptime(dateline, "%Y-%m-%d")
            except ValueError:
                try:
                    return datetime.datetime.strptime(dateline, "%m/%d/%Y")
                except ValueError:
                    try:
                        return datetime.datetime.strptime(dateline, "%Y")
                    except ValueError:
                        splitdate = [x.strip() if x else '1' for x in dateline.split('-')]
                        if len(splitdate) == 1:
                            if len(splitdate[0]) == 8:
                                fixdate = '{Y:04d}-{m:02d}-{d:02d}'.format(Y=int(splitdate[0][:4]),
                                                                           m=int(splitdate[0][4:6]),
                                                                           d=int(splitdate[0][6:]))
                            elif splitdate[0][-1] == '?':
                                fixdate = '{Y:04d}-{m:02d}-{d:02d}'.format(Y=int(splitdate[0].split()[0]), m=1, d=1)
                            else:
                                print('1', splitdate)
                        elif len(splitdate) == 3 and len(splitdate[0]) == 4:
                            if splitdate[2] == '. .' or splitdate[2] == '00':
                                splitdate[2] = '1'
                            elif splitdate[0][-1] == '?':
                                # print('made year into 2005', splitdate)
                                splitdate[0] = '2005'
                            fixdate = '{Y:04d}-{m:02d}-{d:02d}'.format(Y=int(splitdate[0]), m=int(splitdate[1]),
                                                                       d=int(splitdate[2]))
                        elif splitdate[0] == '. . . .':
                            splitdate[0] = '2007'
                            fixdate = '{Y:04d}-{m:02d}-{d:02d}'.format(Y=int(splitdate[0]), m=int(splitdate[1]),
                                                                       d=int(splitdate[2]))
                        elif splitdate[0][-1] == '?':
                            # print('made year into 2005', splitdate)
                            splitdate[0] = splitdate[0][:4]
                            fixdate = '{Y:04d}-{m:02d}-{d:02d}'.format(Y=int(splitdate[0]), m=int(splitdate[1]),
                                                                       d=int(splitdate[2]))
                        else:
                            print('3', splitdate)
                        return datetime.datetime.strptime(fixdate, "%Y-%m-%d")


    def get_lookup_lib(self, file):
        """
         openes fixed_fungal_codes.csv and puts the fixed values in a dictionary
        :return: dictionary with raw data as keys and fixed data as values
        """
        output = {}
        with open(file, 'r') as csvfile:
            #has_header = csv.Sniffer().has_header(pathogencsv.read(2048))
            has_header = True
            csvfile.seek(0)
            data = csv.reader(csvfile, delimiter=';', quotechar='"')
            if has_header:
                header = next(data, None)
            for splitline in data:
                ids = splitline[3].split(',')
                given_names = splitline[1].split(',')
                output[splitline[0].strip('" ')] = [(int(ids[i].strip()),given_names[i].strip()) for i in range(len(ids))]
        return output

    def clean_ins(self, in_txt, year=None):
        output = None
        if in_txt[:3].upper() == 'INS':
            split_txt = re.split('[;, ]+',in_txt)
            ins = [split_txt[0]]
            for x in split_txt[1:]:
                if x and x[0] == '-':
                    ins.append('-'.join(ins[0].split('-')[:3])+x)
            output = ins
        elif year:
            split_txt = in_txt.split()[0].split('-')
            if split_txt[0] == year:
                if len(split_txt[1]) != 5:
                    if len(split_txt[1]) == 4:
                        split_txt[1] = '{:05}'.format(int(split_txt[1]))
                        output = 'INS-' + '-'.join(split_txt)
                    elif split_txt[1][5] == '_':
                        split_txt.append('{:05}'.format(int(split_txt[1][6:])))
                        split_txt[1]=split_txt[1][:5]
                        output = 'INS-' + '-'.join(split_txt)
                    elif split_txt[1][5] == '/':
                        output = ['INS-'+split_txt[0]+'-'+'{:05}'.format(int(split_txt[1][:5]))]
                        output.append('INS-'+split_txt[0]+'-'+'{:05}'.format(int(split_txt[1][6:])))
                    else:
                        print('INS could not be fixed:'+in_txt)
                else:
                    output = 'INS-' + '-'.join(split_txt)
            elif len(split_txt) > 1 and len(split_txt[0]) == 2:
                if len(split_txt[1]) == 5:
                    output = 'INS-' + '-'.join(split_txt)
                else:
                    None # these should not be INS codes, probably TCH
            elif int(year) >= 5 and len(re.split('[- ()]+',in_txt)[0]) == 5 and re.split('[- ()]+',in_txt)[0].isdigit():
                output = 'INS-' + year + '-' + re.split('[- ]+',in_txt.strip(')'))[0]
            else:
                None  # these should not be INS codes, among witch the old (pre 2005) inscrijfcodes
        elif len(in_txt.split('-')[0]) == 2 and len(in_txt.split('-')[1]) == 5:
            output = 'INS-' + in_txt
        else:
            None # these should not be INS codes
        return output

    def strip_accessions(self, pre_process=True):
        with open(self.virus_file) as viruscsv:
            has_header = csv.Sniffer().has_header(viruscsv.read(1024))
            viruscsv.seek(0)  # rewind
            viruscol = csv.reader(viruscsv, delimiter=';', quotechar='"')
            if has_header:
                headers = next(viruscol, None)
            for splitline in viruscol:
                output = {}
                if splitline[0]:
                    output['doosnr'] = splitline[0]
                if splitline[1]:
                    output['monsternr'] = int(splitline[1])
                if splitline[2]:
                    output['opslag'] = splitline[2]
                if splitline[3]:
                    output['aantal'] = int(splitline[3])
                if splitline[4]:
                    output['pathogeen'] = splitline[4]
                if splitline[5]:
                    output['virusegroep'] = splitline[5]
                if splitline[6]:
                    output['gewas'] = splitline[6]
                if splitline[7]:
                    output['toetsplant'] = splitline[7]
                if splitline[8]:
                    output['code'] = splitline[8]
                if splitline[9]:
                    output['materiaal'] = splitline[9]
                if splitline[10]:
                    output['herkomst'] = splitline[10]
                if splitline[11]:
                    output['opmerkingen'] = splitline[11]
                if splitline[12]:
                    output['datum80'] = self.fix_date(splitline[12].strip('"'))
                # some extra stuff for easy processing
                if pre_process:
                    if 'gewas' in output:
                        host = self.host[output['gewas'].strip()][0]
                        output['gewas_id'] = host[0]
                        output['gewas_txt'] = host[1]
                    # getting country of origin
                    if 'herkomst' in output:
                        if output['herkomst'] in self.origin_lib: #TODO figure out what to do with unknown locations
                            origin = self.origin_lib[output['herkomst']][0]
                            output['origin_id'] = origin[0]
                            output['origin_txt'] = origin[1]
                    # id's for this isolate
                    output['codes'] = {}
                    if 'doosnr' in output:
                        box = 'box:'+'-'.join([x for x in re.split('[-/_ ]+', output['doosnr']) if x.isdigit()])
                    else:
                        box = ''
                    nr = 'nr:'+str(output['monsternr'])
                    output['codes']['Sample'] = box+nr
                    if splitline[8]:
                        if 'datum80' in output:
                            year = output['datum80'].strftime("%y")
                        else:
                            year = None
                        ins = self.clean_ins(output['code'], year)
                        if ins:
                            output['codes']['INS'] = ins
                    #adding Verification tests info
                    output['tests'] = {}
                    if 'toetsplant' in output:
                        output['tests']['pathogeniteit'] = output['toetsplant']
                    #adding information as comments
                    output['comments'] = {}
                    if 'opmerkingen' in output:
                        output['comments']['Comment'] = output['opmerkingen']
                    if 'aantal' in output:
                        output['comments']['Amount stored'] = str(output['aantal'])
                    if 'opslag' in output:
                        # G/K/B: G = Grote buis 50 ml, K = klein wit potje, B = 15 ml-buis
                        if output['opslag'] == 'G' or output['opslag'] == 'g':
                            storidge = '50 ml-buis '
                        elif output['opslag'] == 'K' or output['opslag'] == 'k':
                            storidge = 'klein wit potje'
                        elif output['opslag'] == 'B' or output['opslag'] == 'b':
                            storidge = '15 ml-buis'
                        elif output['opslag'] == 'Z':
                            storidge = 'in zak'
                        else:
                            storidge = output['opslag']
                        output['comments']['Storidge'] = storidge
                    # sample dates
                    output['dates'] = {}
                    if splitline[12]:
                        output['dates']['datum -80'] = output['datum80']
                    # dealing with multiple pathogen
                    if splitline[4].strip('" ') in self.virus:
                        # each virus in the sample is seperatly yielded. This creates multiple entries.
                        pathogen_info = self.virus[splitline[4].strip('" ')]
                        nvc_sub = ""
                        nvc_count = 0
                        for virusid in pathogen_info:
                            if len(pathogen_info) > 1:
                                # hope the is no entry with more then 26 virus in one sample
                                nvc_count += 1
                                nvc_sub = '-'+chr(96+nvc_count)
                            output['nvc'] = 'NVC-' + id_manigement.prepolutate_virus_id(
                                splitline[1], 'Virus_cryo') + nvc_sub
                            output['pathogeen_id'] = int(virusid[0])
                            output['pathogeen_txt'] = virusid[1]
                            yield output
                    else:
                        # gives false when raw entry is not in fixed_virus_codes.csv, but that's why it should have been updated.
                        output['nvc'] = 'NVC-' + id_manigement.prepolutate_virus_id(
                            splitline[1], 'Virus_cryo')
                        # 10239 is the id of virus
                        output['pathogeen_id'] = 10239
                        if output['pathogeen'].strip('" ') != '':
                            output['pathogeen_txt'] = output['pathogeen'].strip('" ')
                        else:
                            output['pathogeen_txt'] = 'unknown Virus'
                        yield output
                else:
                    yield output

def main(arguments):
    foo = Viralcollectie()
    for i in foo.strip_accessions():
        print(i)

if __name__ == "__main__":
    main(sys.argv[1:])
