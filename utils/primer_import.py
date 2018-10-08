from xlrd import open_workbook
from naktdata.settings import BASE_DIR
from collectie.models import PCR_set, PCR_seq

import sys
import re
import datetime


def get_rows(xls_file, sheet=None, header_index=None, start_index=0):
    '''
    Itterator for a excel file
    :param xls_file: the path to a older excel file (xls)
    :param sheet: the work sheet to be iterated on
    :param header_index: the row to read header labels from
    :param start_index: the row to start itteration from
    :return:
        yields rows of selected sheet one by one
    '''
    book = open_workbook(xls_file)
    if isinstance(sheet, str):
        s = book.sheet_by_name(sheet)
    elif isinstance(sheet, int):
        s = book.sheet_by_index(sheet)
    else:
        s = book.sheet_by_index(0)
    #getting header row
    if isinstance(header_index, int): #0 is also a valid option
        headers = [s.cell_value(header_index,i) for i in range(s.ncols)]
    else:
        headers = [x for x in range(s.ncols)]
    #getting start row
    if start_index: #if it's not 0 it takes prominence over header index
        start_row = start_index
    elif header_index:
        start_row = header_index+1
    else:
        start_row = 0
    #itterating on the rows
    for row_nr in range(start_row,s.nrows):
        row_data = {}
        for col_nr in range(s.ncols):
            row_data[headers[col_nr]] = s.cell_value(row_nr,col_nr)
        #stop when the row is empty
        if all(v is '' or v is 0 for v in row_data.values()):
            break
        row_data['number'] = row_nr
        yield row_data


def combine_primer_numbers(pcr_file):
    pcr_tests = {}
    pcr_nr = 0
    primers = []
    for row_data in get_rows(pcr_file,'Primerlijst',0,7):
        row_primer_nr = int(re.findall(r'\d+', str(row_data['Primer Nr.']))[0])
        if row_primer_nr > pcr_nr:
            if pcr_nr:
                pcr_tests[pcr_nr] = primers
                primers = []
            pcr_nr = row_primer_nr
        primers.append(row_data)
    return pcr_tests


def data_combine(primer_set, headers):
    to_combine = []
    combined = {}
    #checking if the colomns are the same and concatenating them if they are not.
    for col in headers:
        for oligo in primer_set:
            if isinstance(oligo[col], str):
                col_data = oligo[col].strip()
            elif isinstance(oligo[col], float):
                col_data = str(int(oligo[col]))
            else:
                print(oligo[col])
            if col_data not in to_combine and col_data != '':
                to_combine.append(col_data)
        combined[col] = ', '.join(to_combine)
        to_combine = []
    return combined


def add_pcr(data):
    '''
    This is where the PCR_set info in the database is checked.
    If the entry described by 'data' does not exist yet, the entry to PCR_set will be created.
    :param data: a dictionary with field names as keys.
    :return: the database model coresponding to the 'data'.
    '''
    if PCR_set.objects.filter(pcr_nr=data['pcr_nr']).exists():
        set = PCR_set.objects.get(pcr_nr=data['pcr_nr'])
        #adjust pcr_product
        set.pcr_product = data['pcr_product']
        set.save()
    else:
        set = PCR_set.objects.create(**data)
    return set


def add_oligo(data):
    if PCR_seq.objects.filter(primer_nr=data['primer_nr']).exists():
        oligo = PCR_seq.objects.get(primer_nr=data['primer_nr'])
    else:
        oligo = PCR_seq.objects.create(**data)
    return oligo


def populate_pcr_set():
    '''
    Finding all the sets of the primer file and adding them to the database
    basically the main function
    :return: populated PCR info in the database
    '''
    PCR_set_convertion = {
        'Groep':'groep',
        'Comment / Pathogeen':'pathogeen',
        'Literatuur':'literatuur',
        'Extra info (pathogenen)':'comment',
        'PCRproduct (bp bij PAGE)':'pcr_product'
    }
    pcr_oligo_convertion = {
        'Primer Nr.':'primer_nr',
        'Oligo Naam':'oligo_naam',
        "Oligo Sequence 5' to 3'":'sequence',
        'Status':'status',
        'Researcher Naam':'researcher',
        'Stock-opl.':'stock_opl',
        'Werk-opl.':'werk_opl',
        'Manufactory date':'fabrication_year',
        "Label 5'":'label5',
        "Label 3'":'label3'
    }
    pcr_file = BASE_DIR + '/collectie/utils/lookup_tables/sequenties_primers_en_probes.xls'
    #reading the excel file by tests
    pcr_info = combine_primer_numbers(pcr_file)
    #adding each pcr test
    for number,primer_set in pcr_info.items():

        #--- adding info of pcr, combined from oligo's ---
        meta_info = data_combine(primer_set, PCR_set_convertion.keys())
        #translating excel headers to database column names
        converted_info = {'pcr_nr':number}
        for header,data in meta_info.items():
            field = PCR_set_convertion[header]
            converted_info[field] = data
        #adding info on the combined set
        pcr_set = add_pcr(converted_info)

        #--- adding each oligo ---
        for line in primer_set:
            # translating excel headers to database column names
            converted_oligo = {'containing_set':pcr_set}
            for header,data in line.items():
                #changing date
                if header == 'Manufactory date':
                    if data != '':
                        fixed_date = datetime.date(int(data), 1, 1)
                        data = fixed_date
                    else:
                        data = None
                if header in pcr_oligo_convertion:
                    field = pcr_oligo_convertion[header]
                    converted_oligo[field] = data
            #adding info on the combined set
            add_oligo(converted_oligo)


def main(arguments):
    pcr_file = BASE_DIR + '/collectie/utils/lookup_tables/sequenties_primers_en_probes.xls'
    for row_data in get_rows(pcr_file,'Primerlijst',0,6):
        print(row_data)

if __name__ == "__main__":
    main(sys.argv[1:])