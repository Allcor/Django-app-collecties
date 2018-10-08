'''
probably should delete this and use Django serializers
https://docs.djangoproject.com/en/dev/topics/serialization/#serialization-formats-json
'''

import sys
import csv, json, datetime

from naktdata.settings import BASE_DIR
from collectie.models import Original_host, Collection
from pathlib import Path


class Line():

    def __init__(self, collection_object):
        self.line = collection_object
        self.isolate = {}
        self.line_dict = {"DT_RowId": self.line.pk, "isolate": self.isolate}

    def add_pathogen(self):
        self.isolate['pathogen_official'] = self.line.pathogen_txt
        self.isolate['pathogen'] = self.line.pathogen.given_name

    def add_host(self):
        if self.line.host:
            self.isolate['host'] = self.line.host_id
            host_dic = {}
            host_dic['name'] = self.line.host.given_name
            host_dic['official'] = self.line.host.taxon.get_name
            self.line_dict["host"] = host_dic
        else:
            self.isolate['host'] = None
            self.line_dict["host"] = {'name': None, 'official': None}

    def add_first_date(self):
        if self.line.sample_set.exists():
            self.isolate['first_date'] = self.line.get_first_date().strftime('%Y-%m-%d')
        else:
            self.isolate['first_date'] = None

class Data_structure():

    def __init__(self):
        self.model = Collection
        self.data = []
        self.options = {}
        self.files = []
        self.json_dic = {'data': self.data, 'options': self.options, 'files': self.files}

    def write_json(self, outfile):
        self._get_lines()
        self._get_range()
        with outfile.open(mode='w+') as json_file:
            json.dump(self.json_dic, json_file)

    def _get_lines(self):
        for line in self.model.objects.all():
            line_obj = Line(line)
            line_obj.add_pathogen()
            line_obj.add_host()
            line_obj.add_first_date()
            self.data.append(line_obj.line_dict)

    def _get_range(self):
        range = []
        for host in Original_host.objects.filter(is_choice=True):
            range.append({"label": host.taxon.get_name, "value": host.pk})
        self.options["isolate.host"] = range

def main(args):
    infile = Path(BASE_DIR + '/collectie/utils/lookup_tables/collectie_2017-8-18.csv')
    outfile = Path(BASE_DIR + '/static/collectie/JSON/foo.json')
    ###
    foo = Data_structure()
    foo.write_json(outfile)

if __name__ == "__main__":
    main(sys.argv[1:])