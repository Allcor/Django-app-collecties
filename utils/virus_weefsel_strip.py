from naktdata.settings import BASE_DIR
from collectie.utils import id_manigement
from collectie.models import NCBI_names
import sys, datetime, re
import csv

class Weefselcollectie():

    def __init__(self):
        self.virus_file = BASE_DIR + '/collectie/utils/lookup_tables/virus_weefselkweek.csv'
        self.virus_ncbi_file = BASE_DIR+"/collectie/utils/lookup_tables/fixed_virus_codes.csv"
        #self.host_code_file = BASE_DIR + '/collectie/utils/lookup_tables/fixed_host_species_codes.csv'
        #self.origin_code_file = BASE_DIR + '/collectie/utils/lookup_tables/fixed_origin_codes.csv'
        #####
        self.virus = self.get_lookup_lib(self.virus_ncbi_file)
        #self.host_lib = self.get_lookup_lib(self.host_code_file)
        #self.origin_lib = self.get_lookup_lib(self.origin_code_file)

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

    def fix_date(self, datefield):
        try:
            return datetime.datetime.strptime(datefield, "%d-%m-%Y")
        except ValueError:
            try:
                return datetime.datetime.strptime(datefield, "%d-%m-%y")
            except ValueError:
                try:
                    return datetime.datetime.strptime(datefield, "?-%m-%Y")
                except ValueError:
                    try:
                        return datetime.datetime.strptime(datefield, "%d%m-%Y")
                    except ValueError:
                        try:
                            return datetime.datetime.strptime(datefield, "%d-%m-0%y")
                        except ValueError:
                            try:
                                return datetime.datetime.strptime(datefield, "%Y(voor)")
                            except ValueError:
                                print(datefield)

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
                    output['monsternr'] = int(splitline[0])
                if splitline[1]:
                    output['gewas_la'] = splitline[1]
                if splitline[2]:
                    output['gewas_nl'] = splitline[2]
                if splitline[3]:
                    output['gewas_old'] = splitline[3]
                if splitline[4]:
                    output['proefnr'] = int(splitline[4])
                if splitline[5]:
                    output['virus_mlo'] = splitline[5]
                if splitline[6]:
                    output['labnr'] = splitline[6]
                if splitline[7]:
                    output['land'] = splitline[7]
                if splitline[8]:
                    output['herkomst'] = splitline[8]
                if splitline[9]:
                    output['extr_nr'] = splitline[9]
                if splitline[10]:
                    output['extra_info'] = splitline[10]
                if splitline[11]:
                    output['datum_kweek'] = self.fix_date(splitline[11].strip('"'))
                # some extra stuff for easy processing
                if pre_process:
                    if 'gewas_la' in output:
                        taxon = NCBI_names.objects.filter(name_txt=output['gewas_la'])
                        if taxon.count() == 1:
                            output['gewas_id'] = taxon.first().tax_id_id
                        elif output['gewas_la'] == "Dahlia":
                            output['gewas_id'] = 41562
                        elif output['gewas_la'] == "Echinacea":
                            output['gewas_id'] = 53747
                        elif output['gewas_la'] == 'Feragaria':
                            output['gewas_id'] = 3746
                        elif output['gewas_la'] == 'Alliium …':
                            output['gewas_id'] = 4682
                        elif output['gewas_la'] == "Solanum jasminoïdes":
                            output['gewas_id'] = 205558
                        elif output['gewas_la'] == "Streptosolen ":
                            output['gewas_id'] = 310463
                        elif output['gewas_la'] == "Nierenbergia":
                            output['gewas_id'] = 144307
                        else:
                            raise ValueError(
                                "{} is not a valid entry for gewas_la".format(output['gewas_la']))
                    else:
                        raise ValueError("there was not entry for gewas_la")
                    if 'gewas_nl' in output:
                        output['gewas_txt'] = output['gewas_nl']
                    else:
                        output['gewas_txt'] = output['gewas_old']
                    # -- adding dates --
                    output['dates'] = {}
                    output['dates']['Cultivation date'] = output['datum_kweek']
                    # -- adding id's --
                    output['codes'] = {}
                    # add INS id
                    if 'labnr' in output:
                        if output['labnr'] != '?' :
                            ins = output['labnr'].strip('INS').strip('-')
                            if len(ins) == 5:
                                ins = output['datum_kweek'].strftime('%y-')+ins
                            output['codes']['INS'] = 'INS-'+ins
                    # add the Sample id
                    output['codes']['Sample'] = output['gewas_old']+' '+str(output['proefnr'])
                    # -- adding comments --
                    output['comments'] = {}
                    if 'extra_info' in output:
                        output['comments']['Comment'] = output['extra_info']
                    if 'herkomst' in output:
                        output['comments']['Obtained from'] = output['herkomst']
                    # getting country of origin
                    if 'land' in output:
                        if output['land'] == 'Japan':
                            output['origin_id'] = 111
                            output['origin_txt'] = 'Japan'
                        if output['land'] == 'Israël':
                            output['origin_id'] = 108
                            output['origin_txt'] = 'Israël'
                        if output['land'] == 'Nederland':
                            output['origin_id'] = 156
                            output['origin_txt'] = 'Nederland'
                        if output['land'] == 'DLd':
                            output['comments']['Obtained from'] = output['land']
                    # dealing with multiple pathogen
                    if 'virus_mlo' in output:
                        # each virus in the sample is seperatly yielded. This creates multiple entries.
                        pathogen_info = self.virus[output['virus_mlo'].strip()]
                        nvc_sub = ""
                        nvc_count = 0
                        for virusid in pathogen_info:
                            if len(pathogen_info) > 1:
                                # hope the is no entry with more then 26 virus in one sample
                                nvc_count += 1
                                nvc_sub = '-'+chr(96+nvc_count)
                            output['nvc'] = 'NVC-' + str(id_manigement.prepolutate_virus_id(
                                output['monsternr'], 'Virus_tissue_culture')) + nvc_sub
                            output['pathogeen_id'] = int(virusid[0])
                            output['pathogeen_txt'] = virusid[1]
                            yield output
                    else:
                        # gives false when raw entry is not in fixed_virus_codes.csv, but that's why it should have been updated.
                        output['nvc'] = 'NVC-' + str(id_manigement.prepolutate_virus_id(
                            output['monsternr'],'Virus_tissue_culture'))
                        # 10239 is the id of virus
                        output['pathogeen_id'] = 10239
                        if output['virus_mlo'].strip() != '':
                            output['pathogeen_txt'] = output['virus_mlo'].strip()
                        else:
                            output['pathogeen_txt'] = 'unknown Virus'
                        yield output
                else:
                    yield output

def main(arguments):
    foo = Weefselcollectie()
    for i in foo.strip_accessions():
        print(i)

if __name__ == "__main__":
    main(sys.argv[1:])