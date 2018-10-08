from django.http import JsonResponse
from django.db.models.expressions import F, Q, Value, Func
from django.db.models.functions import Cast
from django.db.models import IntegerField


class Datatables_data:
    def __init__(self,model):
        self.model = model
        #the fields expected by datatables:
        self.data = self.model.objects.all()
        self.options = []
        self.files = []
        self.draw = 0
        self.recordsTotal = self.model.objects.all().count()
        self.recordsFiltered = self.recordsTotal
        #things adjusted for response
        self.slice_lower = 0
        self.slice_upper = self.recordsTotal
        self.columns = {}
        self.search = {}
        self.order = {}

    def json_response(self, request):
        '''
        Function to deal with a AJAX request and send appropriate data back.
        :param request: Django request object
        :return: page with data in json format
        '''
        if request.GET:
            self.process_get_request(request.GET)
        field_data = [obj.as_dict() for obj in self.data[self.slice_lower:self.slice_upper]]
        #sending back json
        return JsonResponse({
            "data":field_data,
            "options":self.options,
            "files":self.files,
            "draw":self.draw,
            "recordsTotal":self.recordsTotal,
            "recordsFiltered":self.recordsFiltered
        })

    def process_get_request(self, request_lib):
        '''
        Reads the GET request and applies the options passed by DataTables

        :param request_lib: request.GET object
        :return: changes values of self
        '''
        self.columns = self.combine_flag_double(request_lib, 'columns')
        #applying the draw number
        self.draw = request_lib['draw']
        #the pagination
        self.slice_lower = int(request_lib['start'])
        if request_lib['length'] == '-1': #showing all is indicated with a page length of -1
            self.slice_upper = self.recordsTotal
        else:
            max_slice_upper = int(request_lib['start'])+int(request_lib['length'])
            self.slice_upper = min([self.recordsTotal,max_slice_upper])
        #filtering
        self.search = self.combine_flag(request_lib, 'search')
        self.process_search(self.search['value'])
        self.recordsFiltered = self.data.count()
        #ordering
        self.order = self.combine_flag_double(request_lib, 'order')
        self.apply_sorting(self.order)

    def process_search(self, search_string):
        '''
        takes search string and extracts all the elements to search on.
        :param search_string:
        :return: applies filters for each element
        '''
        for sub_string in search_string.split():
            sub_string = sub_string.strip()
            if sub_string:
                self.apply_filter(sub_string)

    def apply_filter(self, search_txt):
        '''
        Applies filter given on all columns of the table

        :param search_txt: the string to filter on
        :return: changes self.data
        '''
        filters = Q()
        #loop on each field and apply filters on them
        for column_nr,column_info in self.columns.items():
            if column_info['searchable'] == 'true':
                if 'isvisible' in column_info:
                    if column_info['isvisible'] == 'true':
                        field_ref = column_info['data'] + '__icontains'
                        filters.add(Q(**{field_ref: search_txt}), Q.OR)
                else:
                    field_ref = column_info['data']+'__icontains'
                    filters.add(Q(**{field_ref:search_txt}),Q.OR)
        self.data = self.data.filter(filters)

    def apply_sorting(self, order_lib):
        '''
        Applies ordering on the columns and direction as given
        the order of importeance is determined by the number after the 'order' flag.

        :param order_lib: the columns to sort
        :return: changes self.data
        '''
        order_lib = sorted([(int(k),i) for k,i in order_lib.items()])
        order_list = []
        for key,value in order_lib:
            sort_string = self.columns[value['column']]['data']
            sort_list = []
            if sort_string in ["id_collectie"]:
                str_name = sort_string+'_str'
                int_name = sort_string+'_int'
                self.data = self.data.annotate(**{
                    str_name:Func(
                        F(sort_string),
                        Value('[^A-Z]'),
                        Value(''),
                        Value('g'),
                        function='regexp_replace')
                })
                self.data = self.data.annotate(**{
                    int_name:Cast(Func(
                        F(sort_string),
                        Value('[^\d]'),
                        Value(''),
                        Value('g'),
                        function='regexp_replace'
                    ), IntegerField())
                })
                sort_list.append(str_name)
                sort_list.append(int_name)
            else:
                sort_list.append(sort_string)
            if value['dir'] == 'desc':
                for item in sort_list:
                    order_list.append("-" + item)
            else:
                order_list += sort_list
        self.data = self.data.order_by(*order_list)

    ''' 
    combining the data of the GET request so similar data is stored together
    '''
    def combine_flag(self, request_lib, flag):
        flag_dict = {}
        for key,value in request_lib.items():
            _key = [x.strip(']') for x in key.split('[')]
            if _key[0] == flag:
                flag_dict[_key[1]] = value
        return flag_dict

    def combine_flag_double(self, request_lib, flag):
        columns_dict = {}
        for key,value in request_lib.items():
            _key = [x.strip(']') for x in key.split('[')]
            if _key[0] == flag:
                columns_dict.setdefault(_key[1],{})[_key[2]] = value
        return columns_dict
