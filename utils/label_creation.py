
from collectie.models import Collection

import requests
import shutil
import socket

#/todo probably will need to change 'mm' as the label printer is not 72 dpi
#the TOSHIBA B-EX4T1 has 203 dpi (8 dots/mm)
#the zebra-gx430t has 300 dpi (12 dots/mm)
mm = 12

#label 'page' sizes
STIKKERVEL = (33*mm, 18*mm)
CRYOSTUCK = (34*mm, 25.4*mm) #<= printeble area, aditional 35*mm wrap
FREEZERBONDZ = (48.26*mm, 25.4*mm) #1.9x1 inch
ZEBRATEST = (70*mm, 30*mm)

TONERWIDTH = (64*mm)

LABEL_TEMPLATE = '''
            ^XA
            ^PW579
            ^PR1
            ^MD30
            ^FWB
            ^CFT
            ^FO200,30^FD{naktid}^FS
            ^CFR
            ^FO270,30^FD{pathogen}^FS
            ^FO310,30^FD{date}^FS
            ^FO350,30^FD{locationid}^FS
            ^FO390,30^FD{insid}^FS
            ^FO430,30^FD{isolate}^FS
            
            ^BY2
            ^FO530,20^BCB,40,Y,Y,A^FD{databaseid}^FS
            ^FO420,210^BQ ^FD   http://collecties.naktuinbouw.net/{databaseid}/^FS
            
            ^XZ
        '''

class zpl_label:
    def __init__(self):
        self.tcp_ip = '10.16.90.157'
        self.tcp_port = 9100
        self.template = LABEL_TEMPLATE

    def create_for_id(self, collection_id):
        isolate = Collection.objects.get(pk=collection_id)
        lable_data = {
            'date':isolate.first_date,
            'locationid':isolate.id_storidge,
            'naktid':isolate.id_collectie,
            'insid':isolate.id_ins,
            'isolate':isolate.colonynumber,
            'databaseid':isolate.nakt_id,
            'pathogen':isolate.pathogen.given_name
        }
        #formating the values
        if lable_data['isolate'] and len(lable_data['isolate']) < 5:
            #if there is a isolate number and it's not prepended with 'nummer' or 'isolaat' add it.
            lable_data['isolate'] = 'Isolaat '+str(lable_data['isolate'])
        return self.template.format(**lable_data)

    def send_zpl_to_printer(self, zpl):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.tcp_ip, self.tcp_port))
        s.send(bytes(zpl, "utf-8"))
        s.close()

    def apply_settings(self):
        #settings required after factory reset
        zpl = '''
        ~SD10
        '''
        #The ~JSa for sensor select, a= A (auto select),R (reflective sensor) ,T (transmissive sensor)
        #The ~JL command is used to set the label length.
        #The ~SD30 set the darkness of printing to 30 (00 to 30)
        #The ~JG command prints a graph (media sensor profile) of the sensor values
        #The ^PR command sets the print rate

        #setting for contineus media, label hight, en safe settings
        #^XA^MNN^LL345^XZ^XA^JUS^XZ
        self.send_zpl_to_printer(zpl)

    def print_test(self):
        zpl = self.create_for_id(76550)
        self.send_zpl_to_printer(zpl)

    def pdf_test(self):

        #zpl = '^xa^cfa,50^fo100,100^fdHello World^fs^xz'
        zpl = self.create_for_id(76550)

        # adjust print density (8dpmm), label width (4 inches), label height (6 inches), and label index (0) as necessary
        #url = 'http://api.labelary.com/v1/printers/8dpmm/labels/4x6/0/'
        #density = 12 & width = 69 & height = 25.4 & units = mm
        url = 'http://api.labelary.com/v1/printers/12dpmm/labels/1.34x1/0/'
        files = {'file': zpl}
        headers = {'Accept': 'application/pdf'}  # omit this line to get PNG images back
        response = requests.post(url, headers=headers, files=files, stream=True)

        if response.status_code == 200:
            response.raw.decode_content = True
            with open('label.pdf', 'wb') as out_file:  # change file name for PNG images
                shutil.copyfileobj(response.raw, out_file)
        else:
            print('Error: ' + response.text)

