from naktdata.settings import BASE_DIR
from collectie.utils import id_manigement
from collectie.models import NCBI_names
import sys, datetime, re
import csv

class Kascollectie():

    def __init__(self):
        self.virus_file = BASE_DIR + '/collectie/utils/lookup_tables/Virus_kas_roelofarendveen.csv'
        self.virus_ncbi_file = BASE_DIR+"/collectie/utils/lookup_tables/fixed_virus_codes.csv"
        self.host_code_file = BASE_DIR + '/collectie/utils/lookup_tables/fixed_host_species_codes.csv'
        #self.origin_code_file = BASE_DIR + '/collectie/utils/lookup_tables/fixed_origin_codes.csv'
        #####
        self.virus = self.get_lookup_lib(self.virus_ncbi_file)
        self.host_lib = self.get_lookup_lib(self.host_code_file)
        #self.origin_lib = self.get_lookup_lib(self.origin_code_file)
        self.compartment = None
        self.table = None

    def get_lookup_lib(self, file):
        """
         openes fixed_fungal_codes.csv and puts the fixed values in a dictionary
        :return: dictionary with raw data as keys and fixed data as values
        """
        output = {}
        with open(file, 'r') as csvfile:
            # has_header = csv.Sniffer().has_header(pathogencsv.read(2048))
            has_header = True
            csvfile.seek(0)
            data = csv.reader(csvfile, delimiter=';', quotechar='"')
            if has_header:
                header = next(data, None)
            for splitline in data:
                ids = splitline[3].split(',')
                given_names = splitline[1].split(',')
                output[splitline[0].strip('" ')] = [
                    (int(ids[i].strip()), given_names[i].strip()) for i in range(len(ids))]
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
                if splitline[0] != '':
                    self.compartment = int(splitline[0])
                output['compartment'] = self.compartment
                if splitline[1] != '':
                    self.table = int(splitline[1])
                output['table'] =  self.table
                output['code'] = splitline[2]
                output['acronym'] = splitline[3]
                output['virus_species'] = splitline[4]
                output['virus_genus'] = splitline[5]
                output['plant_genus'] = splitline[6]
                output['plant_nl'] = splitline[7]
                output['datum'] = splitline[8]
                output['comment'] = splitline[9]
                output['autonumber'] = int(splitline[10])
                # some extra stuff for easy processing
                if pre_process:

                    # -- adding id's --
                    output['codes'] = {}
                    #nactuinbouw collection id
                    output['nvc'] = 'NVC-' + str(id_manigement.prepolutate_virus_id(
                        output['autonumber'],'Virus_greenhouse'))
                    # add the Sample id
                    output['codes']['Sample'] = output['code']

                    # -- adding comments --
                    output['comments'] = {}
                    output['comments']['current_table'] = 'Comp-' + str(output['compartment']) + ' tafel-' + str(output['table'])
                    if 'comment' in output:
                        output['comments']['Comment'] = output['comment']

                    # -- adding sample dates --
                    output['dates'] = {}
                    if output['datum'] != '':
                        if output['datum'] == '<2004' or output['datum'] == '< 2004':
                            output['dates']['obtained'] = datetime.datetime.strptime('2004', "%Y")
                            output['comments']['obtained remark'] = "Older then 2004"
                        elif output['datum'] == '?':
                            pass
                        else:
                            output['dates']['obtained'] = datetime.datetime.strptime(output['datum'], "%Y")

                    # -- adding the host plant --
                    if 'plant_genus' in output:
                        host = self.host_lib[output['plant_genus'].strip()][0]
                        output['gewas_id'] = host[0]
                        if output['plant_nl'] != '':
                            output['gewas_txt'] = output['plant_nl']
                        else:
                            output['gewas_txt'] = host[1]

                    # -- adding pathogen --
                    if output['acronym'] == '?':
                        if output['virus_species'] != '':
                            given_name = output['virus_species']
                        else:
                            given_name = output['acronym']
                    else:
                        given_name = output['acronym']
                    if given_name in self.virus:
                        # each virus in the sample is seperatly yielded. This creates multiple entries.
                        pathogen_info = self.virus[given_name]
                        nvc_sub = ""
                        nvc_count = 0
                        nvc_base = output['nvc']
                        for virusid in pathogen_info:
                            if len(pathogen_info) > 1:
                                # hope there is no entry with more then 26 virus in one sample
                                nvc_count += 1
                                nvc_sub = '-'+chr(96+nvc_count)
                                output['nvc'] = nvc_base + nvc_sub
                            output['pathogeen_id'] = int(virusid[0])
                            output['pathogeen_txt'] = virusid[1]
                            yield output
                    else:
                        # gives false when raw entry is not in fixed_virus_codes.csv, but that's why it should have been updated.
                        # 10239 is the id of virus (superkingdom)
                        output['pathogeen_id'] = 10239
                        if output['virus_species'] != '':
                            output['pathogeen_txt'] = output['virus_species']
                        elif output['acronym'] != '':
                            output['pathogeen_txt'] = output['acronym']
                        else:
                            output['pathogeen_txt'] = 'unknown Virus'
                        yield output
                else:
                    yield output

def main(arguments):
    foo = Kascollectie()
    for i in foo.strip_accessions():
        print(i)

if __name__ == "__main__":
    main(sys.argv[1:])