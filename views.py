import json

from django.db.models.expressions import F, Q
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.postgres.search import TrigramSimilarity
from django.shortcuts import get_object_or_404, render, redirect
from django.core import serializers
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.conf import settings

from .models import NCBI_nodes, NCBI_names, Collection, Collection_id, Collection_comment, Changelog, Pathogen
from .models import Original_host, Origin_pathogen, Sample, UserSelected, Table_descriptions
from .models import PCR_seq, PCR_set

from collectie.utils import id_manigement, label_creation, datatables_integration


@login_required()
def detail(request, taxon_id):
    taxon = get_object_or_404(NCBI_nodes, tax_id=taxon_id)
    return render(request, 'collectie/taxon_detail.html', {'taxon': taxon})


@login_required()
def accession(request, accession_nr):
    accession = get_object_or_404(Collection, nakt_id=accession_nr)
    return render(request, 'collectie/accession_detail.html', {'accession': accession})

@login_required()
def accession_experiment(request):
    columns = {
        'html':[
            {'name':'Pathogen Of Isolate','class':'initiallyHidden'},
            {'name':'pathogen official','class':False},
            {'name':'pathogen synonyms', 'class':'initiallyHidden'},
            {'name':'host','class':'initiallyHidden'},
            {'name':'host official','class':False},
            {'name':'host synonyms', 'class':'initiallyHidden'},
            {'name':'first date','class':False},
            {'name':'rein controle datum','class':'initiallyHidden'},
            {'name':'country','class':False},
            {'name':'in use as reference','class':'initiallyHidden'},
            {'name':'material','class':'initiallyHidden'},
            {'name':'tests performed','class':'initiallyHidden'},
            {'name':'id','class':False},
            {'name':'INS','class':False},
            {'name':'location','class':'initiallyHidden'},
            {'name':'ID location','class':'initiallyHidden'},
            {'name':'other_id','class':'initiallyHidden'},
            {'name':'old_location','class':False},
            {'name':'test_pcr','class':'initiallyHidden'},
            {'name':'test_serology','class':'initiallyHidden'},
            {'name':'test_patholegy','class':'initiallyHidden'},
            {'name':'test_sequencing','class':'initiallyHidden'},
            {'name':'comments','class':'initiallyHidden'},
            {'name':'path_pathogen','class':'initiallyHidden'},#'class':'noVis'},
            {'name':'path_host','class':'initiallyHidden'},#'class':'noVis'},
        ],
        'javascript':[
            {"data":'pathogen__given_name'},
            {"data":'pathogen__scientific_name'},
            {"data":'pathogen__synonyms'},
            {"data":'host__given_name'},
            {"data":'host__scientific_name'},
            {"data":'host__synonyms'},
            {"data":'first_date', "className": 'MinWidth60'},
            {"data":'sample__date', "className": 'MinWidth60', "searchable": 'false'},
            {"data":'origin__country__name'},
            {"data":'confidential'},
            {"data":'material'},
            {"data":'tests_performed'},
            {"data":'id_collectie', "className": 'MinWidth60'},
            {"data":'id_ins', "className": 'MinWidth80'},
            {"data":'pathogen_location'},
            {"data":'id_storidge'},
            {"data":'id_other'},
            {"data":'id_original'},
            {"data":'test_pcr'}, #"searchable": 'false'},
            {"data":'test_serology'}, #"searchable": 'false'},
            {"data":'test_patholegy'}, #"searchable": 'false'},
            {"data":'test_sequencing'}, #"searchable": 'false'},
            {"data":'comment'}, #"searchable": 'false'},
            {"data":'pathogen_tree'}, #"className": 'noVis'},
            {"data":'host_tree'}, #"className": 'noVis'}
        ]}
    return render(request, 'collectie/accession_index.html', {'columns': columns})

@login_required()
def accession_experiment_data(request):
    object_list = datatables_integration.Datatables_data(Collection)
    return object_list.json_response(request)

@login_required()
def accession_edit(request):
    if request.user.groups.filter(name='collection admin').count() == 0:
        # if the user is not supposed te be on the edit page, redirect to the main page.
        return redirect('/')
    return render(request, 'collectie/accession_edit.html')


@login_required()
def accession_labels(request):
    # the fields need to be added to get_select function as well
    columns = {
        'html':[
            {'name':'NAKtuinbouw ID'},
            {'name':'pathogeen'},
            {'name':'Datum opslag'},
            {'name':'Locatie ID'},
            {'name':'INS'},
            {'name':'isolaat nr'}
        ],
        'javascript':[
            {"data":'id_collectie'},
            {"data":'pathogen__given_name'},
            {"data":'first_date'},
            {"data":'id_storidge'},
            {"data":'id_ins'},
            {"data":'colonynumber'}
        ]}
    return render(request, 'collectie/accession_labels.html', {'columns': columns})

@login_required()
def test_pcr(request):
    toets_columns = [
        {'head':'primer_nr',"data": 'primer_nr'},
        {'head':'oligo_naam', "data": 'oligo_naam'},
        {'head':'sequence', "data": 'sequence'},
        {'head':'status', "data": 'status'},
        {'head':'researcher','headerClass':'initiallyHidden', "data": 'researcher'},
        {'head':'stock_opl','headerClass':'initiallyHidden','data':'stock_opl'},
        {'head':'werk_opl','headerClass':'initiallyHidden','data':'werk_opl'},
        {'head':'fabrication_year','headerClass':'initiallyHidden','data':'fabrication_year'},
        {'head':'label5','headerClass':'initiallyHidden','data':'label5'},
        {'head':'label3','headerClass':'initiallyHidden','data':'label3'},
        {'head':'groep','data':'containing_set__groep'},
        {'head':'pathogeen','data':'containing_set__pathogeen'},
        {'head':'literatuur','headerClass':'initiallyHidden','data':'containing_set__literatuur'},
        {'head':'comment','headerClass':'initiallyHidden','data':'containing_set__comment'},
        {'head':'pcr_product','headerClass':'initiallyHidden','data':'containing_set__pcr_product'}
    ]
    return render(request, 'collectie/toets_tableview.html', {'toets_columns':toets_columns})

@login_required()
def test_pcr_data(request):
    object_list = datatables_integration.Datatables_data(PCR_seq)
    return object_list.json_response(request)

@login_required()
def test_pcr_detail(request, pcr_nr):
    toets = get_object_or_404(PCR_set, pcr_nr=pcr_nr)
    return render(request, 'collectie/toets_pcr_detail.html', {'toets': toets})
'''
##### AJAX/JSON lookup stuff #####
'''


@login_required()
def update_database(request, isolate, edit_table):
    command = request.POST
    action = ''
    data = {}
    edited = []
    # deciphering request
    for key, value in command.items():
        split_key = [x.strip(']') for x in key.split('[')]
        if split_key[0] == 'data':
            data.setdefault(split_key[1], {})[split_key[2]] = value
        elif split_key[0] == 'action':
            action = value
    # implementing
    for code_id, code_data in data.items():
        # loging change
        Changelog.objects.create(dtuser=request.user.username, dtaction=action,
                                 dtvalues=json.dumps({edit_table.model._meta.db_table: code_data}),
                                 dtrow=code_id)
        if action == 'create':
            # INSERT
            edited.append(edit_table.create(nakt_id=isolate, **code_data))
        elif action == 'edit':
            # UPDATE
            if edit_table.model.__name__ == 'Collection_id':
                item = edit_table.get(pk=code_id)
                if item.code_class[:4] == 'old_':
                    edited = {'error': "this id can not be removed"}
                else:
                    code_data['code_class'] = item.code_class
                    edited.append(edit_table.create(nakt_id=isolate, **code_data))
                    item.code_class = 'old_' + item.code_class
                    item.save()
            else:
                item = edit_table.get(pk=code_id)
                for key, value in code_data.items():
                    item.__dict__[key] = value
                item.save()
                edited.append(item)
        elif action == 'remove':
            if edit_table.model.__name__ == 'Collection_id':
                item = edit_table.get(pk=code_id)
                if item.code_txt == isolate.id_collectie:
                    #return an error if the id is used as isolate identification
                    edited = {'error':"this id can not be removed"}
                else:
                    if item.code_class[:4] == 'old_':
                        item.delete()
                    else:
                        item.code_class = 'old_'+item.code_class
                        item.save()
            else:
                #DELETE
                edit_table.get(pk=code_id).delete()
    isolate.update_static()
    return edited

# not a view!
def fetch_options_field(fields, edit_table):
    response_options = {}
    for field in fields:
        response_options[field] = [
            {"label": obj[field], "value": obj[field]}
            for obj in edit_table.values(field).distinct().order_by(field)
        ]
    return response_options


@login_required()
def get_accession_comment(request, accession_nr):
    isolate = Collection.objects.get(nakt_id=accession_nr)
    edit_table = Collection_comment.objects.all()

    if request.method == 'POST':
        if request.user.is_authenticated() and \
                request.user.groups.filter(name='collection admin').exists():
            edited = update_database(request, isolate, edit_table)
            return JsonResponse({"data": [obj.as_table_row() for obj in edited]})
        else:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        # give table info
        response_options = fetch_options_field(['comment_label'], edit_table)
        response_data = [obj.as_table_row() for obj in edit_table.filter(nakt_id=accession_nr)]
        return JsonResponse({"data": response_data, "options": response_options})


@login_required()
def get_accession_id(request, accession_nr):
    isolate = Collection.objects.get(nakt_id=accession_nr)
    edit_table = Collection_id.objects.all() #.exclude(code_class__startswith='old_')

    if request.method == 'POST':
        #check if the user is allowed to change the id:
        if request.user.is_authenticated() and \
                request.user.groups.filter(name='collection admin').exists():
            edited = update_database(request, isolate, edit_table)
            if isinstance(edited, dict):
                return JsonResponse(edited)
            else:
                return JsonResponse({"data": [obj.as_table_row() for obj in edited]})
        else:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    elif request.method == 'GET':
        if 'id_type' in request.GET:
            response_data = edit_table.filter(nakt_id=accession_nr,code_class=request.GET["id_type"])
            if response_data.exists():
                output_txt = response_data.first().code_txt
            else:
                output_txt = "ID not found"
            return HttpResponse(output_txt, content_type="text/plain")
        else:
            # give table info
            response_options = fetch_options_field(['code_class'], edit_table)
            response_data = [obj.as_table_row() for obj in edit_table.filter(nakt_id=accession_nr)]
            return JsonResponse({"data": response_data, "options": response_options})
    else:
        return JsonResponse({"error":"Http request method not understood"})


@login_required()
def get_sample_update(request, accession_nr):
    isolate = Collection.objects.get(nakt_id=accession_nr)
    edit_table = Sample.objects.all()

    if request.method == 'POST':
        if request.user.is_authenticated() and \
                request.user.groups.filter(name='collection admin').exists():
            edited = update_database(request, isolate, edit_table)
            return JsonResponse({"data": [obj.as_table_row() for obj in edited]})
        else:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        # give table info
        response_options = fetch_options_field(['action'], edit_table)
        response_data = [obj.as_table_row() for obj in edit_table.filter(nakt_id=accession_nr)]
        return JsonResponse({"data": response_data, "options": response_options})


@login_required()
def get_test_description(request, accession_nr):
    '''
    this is a one-to-one connection and works a little different.
    Should find a better way to do this.
    imo, in the detail screen the one-to-many works better.
    '''
    isolate = Collection.objects.get(nakt_id=accession_nr)
    fields = ['test_pcr', 'test_serology', 'test_patholegy', 'test_sequencing']

    if request.method == 'POST':
        if request.user.is_authenticated() and \
                request.user.groups.filter(name='collection admin').exists():
            command = request.POST
            action = ''
            data = {}
            edited = []
            # deciphering request
            for key, value in command.items():
                split_key = [x.strip(']') for x in key.split('[')]
                if split_key[0] == 'data':
                    data.setdefault(split_key[1], {})[split_key[2]] = value
                elif split_key[0] == 'action':
                    action = value
            # looping on changes
            for key, value in data.items():
                # Formating
                if action == 'create':
                    field = value['property']
                else:
                    field = key
                # implementing
                if 'data' in value:
                    Changelog.objects.create(
                        dtuser=request.user.username, dtaction=action,
                        dtvalues=json.dumps({isolate._meta.db_table: {field: value['data']}}),
                        dtrow=accession_nr
                    )
                    if action == 'create':
                        isolate.__dict__[field] = value['data']
                        edited.append(field)
                    elif action == 'edit':
                        isolate.__dict__[field] = value['data']
                        edited.append(field)
                    elif action == 'remove':
                        isolate.__dict__[field] = ''
                else:
                    return JsonResponse({'error': 'no changes'})
            isolate.update_static()
            isolate.save()
            return JsonResponse({'data': isolate.as_table(edited)})
        else:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    else:
        # give table info
        response_data = isolate.as_table(fields)
        missing = [field for field in fields if field not in [x['DT_RowId'] for x in response_data]]
        response_options = {
            'property': [
                {
                    'label': isolate._meta.get_field(field).verbose_name.title(),
                    'value': field
                }
                for field in missing]
        }
        return JsonResponse({"data": response_data, "options": response_options})


@login_required()
def get_accession_data(request, accession_nr):
    isolate = Collection.objects.get(nakt_id=accession_nr)
    fields = ['pathogen', 'host', 'origin', 'material', 'symptom', 'confidential', 'colonynumber']
    if request.method == 'POST':
        if request.user.is_authenticated() and \
                request.user.groups.filter(name='collection admin').exists():
            command = request.POST
            action = ''
            data = {}
            edited = []
            # deciphering request
            for key, value in command.items():
                split_key = [x.strip(']') for x in key.split('[')]
                if split_key[0] == 'data':
                    data.setdefault(split_key[1], {})[split_key[2]] = value
                elif split_key[0] == 'action':
                    action = value
            # looping on changes
            for key, value in data.items():
                # Formating
                if 'confidential' in value:
                    value['confidential'] = True
                else:
                    value['confidential'] = False
                if action == 'create':
                    field = value['property']
                else:
                    field = key
                if action == 'remove':
                    value[field] = value['data']
                if isolate._meta.get_field(field).is_relation:
                    dict_field = field + '_id'
                else:
                    dict_field = field
                # implementing
                if value[field]:
                    Changelog.objects.create(
                        dtuser=request.user.username,
                        dtaction=action,
                        dtvalues=json.dumps({isolate._meta.db_table: {field: value[field]}}),
                        dtrow=accession_nr
                    )
                    if action == 'create':
                        isolate.__dict__[dict_field] = value[field]
                        edited.append(field)
                    elif action == 'edit':
                        isolate.__dict__[dict_field] = value[field]
                        edited.append(field)
                    elif action == 'remove':
                        isolate.__dict__[dict_field] = isolate._meta.get_field(field).default
                else:
                    return JsonResponse({'error': 'no changes'})
            isolate.update_static()
            isolate.save()
            return JsonResponse({'data': isolate.as_table(edited)})
        else:
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
    elif request.method == 'GET':
        if 'field_name' in request.GET:
            field = request.GET["field_name"]
            response_data = Collection.objects.values(field).filter(nakt_id=accession_nr)
            if response_data.exists():
                output_txt = response_data.first()[field]
            else:
                output_txt = "ID not found"
            return HttpResponse(output_txt, content_type="text/plain")
        else:
            response_data = isolate.as_table(fields)
            missing = [field for field in fields if field not in [x['DT_RowId'] for x in response_data]]
            response_options = {
                'property': [
                    {
                        'label': isolate._meta.get_field(field).verbose_name.title(),
                        'value': field
                    } for field in missing
                ],
                'pathogen': [
                    {
                        'label': pat.scientific_name + ' - (' + pat.given_name + ')',
                        'value': pat.pk
                    } for pat in Pathogen.objects.exclude(is_choice=False)
                ],
                'host': [
                    {
                        'label': host.scientific_name + ' - (' + host.given_name + ')',
                        'value': host.pk
                    } for host in Original_host.objects.exclude(is_choice=False)
                ],
                'origin': [
                    {
                        'label': ori.country.name + ' - (' + ori.given_name + ')',
                        'value': ori.pk
                    } for ori in Origin_pathogen.objects.exclude(is_choice=False)
                ]
            }
            return JsonResponse({"data": response_data, "options": response_options})
    else:
        return JsonResponse({"error":"could not handle this request method"})


@login_required()
def get_new_id(request):
    if request.method == 'POST' and request.user.groups.filter(
            name='collection admin').count() != 0:
        command = request.POST
        data = {}
        return_values = {}
        # deciphering request
        for key, value in command.items():
            split_key = key.strip(']').split('[')
            if split_key[0] == 'row':
                # will be added with edit, so only will continue with create
                return JsonResponse({})
            elif split_key[0] == 'values':
                data[split_key[1]] = value
        #check id's
        if data["collectie_collection.pathogen_location"] == '':
            return JsonResponse({})
        else:
            #location is defined, collection id can be created
            collection_id,location_id = id_manigement.new_collection_id(data["collectie_collection.pathogen_location"])
            # check if id_collectie needs to be changed
            if data["collectie_collection.id_collectie"] == "" or not Collection_id.objects.filter(
                code_txt=data["collectie_collection.id_collectie"]).exists():
                return_values["collectie_collection.id_collectie"] = collection_id
            # check if id_storidge needs to be changed
            if data["collectie_collection.id_storidge"] == "" or not Collection_id.objects.filter(
                code_txt=data["collectie_collection.id_storidge"]).exists():
                if location_id:
                    return_values["collectie_collection.id_storidge"] = location_id
                else:
                    # returning a empty value so existing values are removed,
                    # needed as not all databases get a Location_ID currently
                    return_values["collectie_collection.id_storidge"] = ''
            else:
                # returning a empty value so existing values are removed,
                # needed as not all databases get a Location_ID currently
                return_values["collectie_collection.id_storidge"] = ''
        return JsonResponse({"values": return_values})
    else:
        return HttpResponseBadRequest()


@login_required()
def get_update_static(request):
    data = request.GET
    for key, value in data.items():
        if key[-9:] == '[nakt_id]':
            isolate = Collection.objects.get(nakt_id=value)
            isolate.update_static()
            # check if isolate has just been added
            if isolate.get_just_added() and request.user.is_authenticated:
                user = User.objects.get(username=request.user)
                isolate.add_user = user
                isolate.save()
                UserSelected.objects.create(select_user=user, select_collection=isolate)
    # returned data is not being used just yet.
    # Hopefully will be able to update table with all fields filled in
    return JsonResponse({'data': data})


@login_required()
def get_field_info(request):
    #loops over fields and returns the availeble info of these fields
    if request.method == 'GET':
        discriptions = {}
        placeholders = {}
        for item in Table_descriptions.objects.filter(table='collectie_collection'):
            if item.description != '':
                discriptions[item.table+'.'+item.column] = item.description
            if item.placeholder != '':
                placeholders[item.table+'.'+item.column] = item.placeholder
        return JsonResponse({'discriptions':discriptions,'placeholders':placeholders})


@login_required()
def get_select_nr(request):
    user = request.user
    if request.method == 'GET':
        return JsonResponse({'selected_count':UserSelected.objects.filter(select_user=user).count()})


@login_required()
def get_select_print(request):
    if request.method == 'POST':
        printer = label_creation.zpl_label()
        command = request.POST
        # TODO sort the labels in the command by nakt_id, number and prefix seperatly.
        label_list = sorted(command.items(), key=lambda kv: int(kv[1]))
        for key,item in label_list:
            zpl = printer.create_for_id(item)
            try:
                printer.send_zpl_to_printer(zpl)
            except Exception as e:
                return JsonResponse({'error': e})
            # loging print
            Changelog.objects.create(
                dtuser=request.user.username,
                dtaction='Print',
                dtvalues=json.dumps([x.strip() for x in zpl.split('\n') if x.strip() != '']),
                dtrow=item)
        return JsonResponse({})


@login_required()
def get_select(request):
    user = request.user
    if request.method == 'GET':
        response_query = UserSelected.objects.filter(select_user=user).annotate(
            DT_RowId=F('pk')
        ).select_related('select_collection')
        response_query = response_query.annotate(id_ins=F('select_collection__id_ins'))
        response_query = response_query.annotate(id_collectie=F('select_collection__id_collectie'))
        response_query = response_query.annotate(first_date=F('select_collection__first_date'))
        response_query = response_query.annotate(id_storidge=F('select_collection__id_storidge'))
        response_query = response_query.annotate(colonynumber=F('select_collection__colonynumber'))
        response_query = response_query.annotate(pathogen__given_name=F('select_collection__pathogen__given_name'))
        return JsonResponse({'data': [entry for entry in response_query.values()]})
    else:  # request.method == 'POST':
        command = request.POST
        data = {}
        action = ''
        #get actions
        for key, value in command.items():
            split_key = [x.strip(']') for x in key.split('[')]
            if split_key[0] == 'data':
                data.setdefault(split_key[1], {})[split_key[2]] = value
            elif split_key[0] == 'action':
                action = value
        #do actions
        response_json = {}
        if action == 'remove':
            for key, value in data.items():
                UserSelected.objects.get(pk = value['id']).delete()
        elif action == 'add':
            for key, value in data.items():
                isolate = Collection.objects.get(pk = value['collection_id'])
                if not UserSelected.objects.filter(select_user = user, select_collection = isolate).exists():
                    UserSelected.objects.create(select_user = user, select_collection = isolate)
                else:
                    response_json.setdefault('alreaddy_selected', []).append(value['collection_id'])
            response_json['selected_count'] = UserSelected.objects.filter(select_user=user).count()
        return JsonResponse(response_json)


'''
##### legacy #####
'''


@login_required()
def index(request):
    latest_accessions = Collection.objects.order_by('-add_date')[:5]
    return render(request, 'collectie/index.html', {'accessions': latest_accessions})


class TaxonSearchListView(LoginRequiredMixin, ListView):
    # form_class=TaxonSearchForm
    template_name = 'collectie/taxon_list.html'
    paginate_by = 20
    model = NCBI_names
    context_object_name = 'taxon_list'

    def dispatch(self, request, *args, **kwargs):
        query = request.GET.get('q')
        if query:
            try:
                tax_id = self.model.objects.get(name_txt=query).tax_id.tax_id
                return redirect('collectie:taxon_detail', tax_id)
            except (self.model.DoesNotExist, self.model.MultipleObjectsReturned) as e:
                return super(TaxonSearchListView, self).dispatch(request, *args, **kwargs)
        else:
            return super(TaxonSearchListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        result = super(TaxonSearchListView, self).get_queryset()
        #
        query = self.request.GET.get('q')
        if query:
            # splitting quiry string
            # normspace=re.compile(r'\s{2,}').sub
            # findterms=re.compile(r'"([^"]+)"|(\S+)').findall
            # substrings = [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query)]
            # limit by name_class
            # class_space = Q()
            # for c in ['dutch_vernacular','scientific name']:
            #    class_space.add(Q(name_class__iexact = c), Q.OR)
            # limit tax_id__rank
            # rank_space = Q()
            # for r in ['species','genus','varietas']:
            #    rank_space.add(Q(tax_id__rank = r), Q.OR)
            # implementing search terms
            # search_space = Q()
            # for substring in substrings:
            #    search_space.add(Q(name_txt__icontains = substring), Q.AND)
            # implementing filters
            # result = result.filter(search_space & class_space & rank_space)
            # exclude sp.
            result = result.exclude(name_txt__icontains='sp.')
            # adding similarety score
            result = result.annotate(similarity=TrigramSimilarity('name_txt', query)).filter(
                similarity__gt=0.3).order_by('-similarity')
        return result


@login_required()
def accession_php(request):
    return render(request, 'collectie/accession_list_php.html')


class Accession_edit(UserPassesTestMixin, LoginRequiredMixin, ListView):
    model = Collection
    template_name = 'collectie/accession_edit.html'
    context_object_name = 'test_list'

    def test_func(self):
        return self.request.user.groups.filter(name='collection admin').count() != 0

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Accession_edit, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(Accession_edit, self).get_context_data(**kwargs)
        query = self.request.GET.get('q')
        context['get_q'] = query if query else ''
        context['max_entries'] = self.model.objects.all().count()
        return context

