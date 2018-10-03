from django.db import models
from django.utils.functional import cached_property
from django.forms.models import model_to_dict
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from datetime import datetime, timedelta
import pytz

'''
#####   Libraries   #####
'''


class CountryCode(models.Model):
    """
        python class representation of the table public.collectie_countrycode in postgress
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=2, unique=True)

    def __str__(self):
        return u'{0} - {1}'.format(self.name, self.code)


'''
#####    NCBI Taxonemy data     #####
'''


class NCBI_nodes(models.Model):
    """
        python class representation of the table public.collectie_ncbi_nodes in postgress
    """
    tax_id = models.PositiveIntegerField(primary_key=True, default=0)
    scientific_name = models.CharField(max_length=128, default='')
    parent_tax_id = models.ForeignKey('self', on_delete=models.CASCADE, default=0, db_index=True)
    rank = models.CharField(max_length=32, db_index=True, default='')
    has_data = models.BooleanField(default=False)

    def __str__(self):
        return (self.get_name + " id:" + str(self.tax_id) + " as " + self.rank)

    def path_to_root(self):
        if self.tax_id == 1:  # this is the root
            return []
        else:
            path = self.parent_tax_id.path_to_root()
            path.append(self)
            return path

    def branch_name_sort(self):
        branches = self.ncbi_nodes_set.all()
        return sorted(branches, key=lambda x: x.get_name)

    def count_branching_samples(self):
        count = self.get_all_collection().count()
        for node in self.ncbi_nodes_set.all():
            if node.has_data:
                count += node.count_branching_samples()
        return count

    def get_all_collection(self):
        return Collection.objects.filter(models.Q(host__taxon=self) | models.Q(pathogen__taxon=self))

    @cached_property
    def get_name(self):
        if self.tax_id == 1:  # this is the root
            return ''
        try:
            name = self.ncbi_names_set.get(name_class='scientific name').name_txt
        except NCBI_names.DoesNotExist:
            name = "No scientific name"
        return name

    def get_special_name(self, from_class="scientific name", show_rank=False):
        try:
            name = self.ncbi_names_set.get(name_class=from_class).name_txt
        except NCBI_names.DoesNotExist:
            name = "Missing " + from_class
        if show_rank:
            name = self.rank + ': ' + name
        return name

    def make_hasdata(self):
        if not self.has_data:
            self.has_data = True
            self.save()
            self.parent_tax_id.make_hasdata()


@receiver(post_save, sender=NCBI_nodes)
def node_save_handler(sender, instance, **kwargs):
    if instance.has_data == True:
        instance.parent_tax_id.make_hasdata()


class NCBI_names(models.Model):
    """
        python class representation of the table public.collectie_ncbi_names in postgress
    """
    tax_id = models.ForeignKey(NCBI_nodes, on_delete=models.CASCADE, default=0)
    name_txt = models.CharField(max_length=255, db_index=True, default='')
    name_class = models.CharField(max_length=32, db_index=True, default='')

    def __str__(self):
        return (self.name_txt + ' saved as ' + self.name_class)


'''
#####   NAKtuinbouw collectie   #####
'''


class Pathogen(models.Model):
    """
            python class representation of the table public.collectie_ ??? in postgress
    """
    given_name = models.CharField(max_length=128, db_index=True, default='', blank=True, unique=True)
    scientific_name = models.CharField(max_length=128, db_index=True, default='')
    synonyms = models.TextField(db_index=True, default='')
    taxon = models.ForeignKey(NCBI_nodes, on_delete=models.PROTECT, default=0)
    is_choice = models.BooleanField(default=True)

    def __str__(self):
        return ("NCBI name: " + str(self.taxon.get_name) + " - referenced as: " + self.given_name)

    @cached_property
    def get_name(self):
        return self.scientific_name


class Original_host(models.Model):
    """
        python class representation of the table public.collectie_original_host in postgress
    """
    # species where the isolation was discovered on.
    given_name = models.CharField(max_length=128, db_index=True, default='', blank=True, unique=True)
    scientific_name = models.CharField(max_length=128, db_index=True, default='')
    taxon = models.ForeignKey(NCBI_nodes, on_delete=models.PROTECT, default=0)
    synonyms = models.TextField(db_index=True, default='')
    is_choice = models.BooleanField(default=True)
    comment = models.CharField(max_length=512, default='')

    def __str__(self):
        return ("NCBI id: " + str(self.taxon.get_name) + " - referenced as: " + self.given_name)

    @cached_property
    def get_name(self):
        return self.scientific_name


class Origin_pathogen(models.Model):
    """
        python class representation of the table public.collectie_origin_pathogen in postgress
    """
    # country where the isolation originated from.
    given_name = models.CharField(max_length=32, db_index=True, default='', blank=True, unique=True)
    country = models.ForeignKey(CountryCode, on_delete=models.CASCADE, default=0)
    is_choice = models.BooleanField(default=True)
    comment = models.CharField(max_length=512, default='')

    def __str__(self):
        return ("Cauntry: " + str(self.country.name) + " - referenced as: " + self.given_name)

    @cached_property
    def get_name(self):
        return self.country.name


class Collection(models.Model):
    """
        python class representation of the table public.collectie_collection in postgress
    """
    # main class of the collection, each entety represents a isolation.
    nakt_id = models.AutoField(primary_key=True)
    add_date = models.DateTimeField(auto_now_add=True)
    add_user = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True, default=None)
    pathogen_location = models.CharField(max_length=32, db_index=True, default='')
    first_date = models.DateField(null=True)
    host = models.ForeignKey(Original_host, on_delete=models.CASCADE, blank=True, null=True, default=None,
                             verbose_name="original host")
    host_tree = models.CharField(max_length=1024, db_index=True, default='', null=True)
    origin = models.ForeignKey(Origin_pathogen, on_delete=models.CASCADE, blank=True, null=True, default=None,
                               verbose_name="country of origin")
    pathogen = models.ForeignKey(Pathogen, on_delete=models.CASCADE, blank=True, null=True, default=None,
                                 verbose_name="pathogen of isolate")
    pathogen_tree = models.CharField(max_length=1024, db_index=True, default='', null=True)
    id_collectie = models.CharField(max_length=100, default='', null=True)
    id_storidge = models.CharField(max_length=100, default='', null=True)
    id_ins = models.CharField(max_length=100, default='', null=True)
    id_original = models.CharField(max_length=100, default='', null=True) #going to repurpose this for the location in the original freezer
    id_other = models.CharField(max_length=100, default='', null=True)
    material = models.CharField(max_length=100, default='', verbose_name="isolated from", null=True)
    symptom = models.CharField(max_length=100, default='', null=True, verbose_name="Observed symptom")
    confidential = models.BooleanField(db_index=True, default=False, verbose_name="dienstverlening")
    colonynumber = models.CharField(max_length=100, default='', null=True, verbose_name="nr. of colony used")
    tests_performed = models.CharField(max_length=100, default='', null=True)
    test_pcr = models.CharField(max_length=500, db_index=True, default='')
    test_serology = models.CharField(max_length=500, db_index=True, default='')
    test_patholegy = models.CharField(max_length=500, db_index=True, default='')
    test_sequencing = models.CharField(max_length=500, db_index=True, default='')
    comment = models.CharField(max_length=1000, db_index=True, default='')

    collectie_id_keys = {
        'Virus_cryo': 'NVC',
        'Bacteria_cryo': 'NBC',
        'Fungi_cryo': 'NFC',
        'Resistance': 'NRC',
        'Virus_tissue_culture': 'NVC',
        'Virus_greenhouse': 'NVC'
    }

    def as_dict(self):
        data_lib = {
            "DT_RowId": self.pk,
            'first_date': self.first_date,
            'confidential': self.confidential,
            'material': self.material,
            'tests_performed': self.tests_performed,
            'id_collectie': self.id_collectie,
            'id_ins': self.id_ins,
            'pathogen_location': self.pathogen_location,
            'id_storidge': self.id_storidge,
            'pathogen_tree': self.pathogen_tree,
            'host_tree': self.host_tree,
            'id_other': self.id_other,
            'id_original': self.id_original,
            'test_pcr': self.test_pcr,
            'test_serology': self.test_serology,
            'test_patholegy': self.test_patholegy,
            'test_sequencing': self.test_sequencing,
            'comment': self.comment
        }
        if self.pathogen:
            data_lib['pathogen__given_name'] = self.pathogen.given_name
            data_lib['pathogen__scientific_name'] = self.pathogen.scientific_name
            data_lib['pathogen__synonyms'] = self.pathogen.synonyms
        else:
            data_lib['pathogen__given_name'] = ''
            data_lib['pathogen__scientific_name'] = ''
            data_lib['pathogen__synonyms'] = ''
        if self.host:
            data_lib['host__given_name'] = self.host.given_name
            data_lib['host__scientific_name'] = self.host.scientific_name
            data_lib['host__synonyms'] = self.host.synonyms
        else:
            data_lib['host__given_name'] = ''
            data_lib['host__scientific_name'] = ''
            data_lib['host__synonyms'] = ''
        if self.origin:
            data_lib['origin__country__name'] = self.origin.country.name
        else:
            data_lib['origin__country__name'] = ''
        # one to many
        if self.sample_set and self.sample_set.filter(action='Rein check').exists():
            check = self.sample_set.filter(action='Rein check').first()
            data_lib['sample__date'] = check.date
        else:
            data_lib['sample__date'] = ''
        return data_lib

    def as_table(self, fields):
        result = []
        for field in fields:
            _field = self._meta.get_field(field)
            field_value = getattr(self, field)
            if field_value:
                line = {
                    'DT_RowId': field,
                    'property': _field.verbose_name.title()
                }
                if _field.is_relation:
                    line['data'] = field_value.pk
                    line['label'] = field_value.get_name
                else:
                    line['data'] = getattr(self, field)
                if hasattr(field_value, 'taxon_id'):
                    line['link'] = reverse('collectie:taxon_detail', kwargs={'taxon_id': field_value.taxon_id})
                result.append(line)
        return result

    def __str__(self):
        return (self.pathogen_location + " added at " + self.add_date.strftime('%m/%d/%Y'))

    def get_name(self):
        from_class = self.collectie_id_keys[self.pathogen_location]
        try:
            name = self.collection_id_set.get(code_class=from_class).code_txt
        except Collection_id.DoesNotExist:
            name = 'Missing ' + from_class
        return name

    def get_name_ins(self):
        ins_numbers = self.collection_id_set.filter(code_class='INS')
        name = ' / '.join([x.code_txt for x in ins_numbers])
        return name

    def get_sample_id(self):
        sample_id = self.collection_id_set.filter(code_class='Sample')
        name = ', '.join([x.code_txt for x in sample_id])
        return name

    def get_just_added(self):
        # returns true if isolate was just added
        time_threshold = datetime.now(pytz.utc) - timedelta(hours=1)
        return self.add_date > time_threshold

    def get_raw_data(self):
        if hasattr(self, 'bacteriecollectie'):
            return model_to_dict(self.bacteriecollectie)
        elif hasattr(self, 'schimmelcollectie'):
            return model_to_dict(self.schimmelcollectie)
        elif hasattr(self, 'viruscollectie'):
            return model_to_dict(self.viruscollectie)
        elif hasattr(self, 'isolatencollectie'):
            return model_to_dict(self.isolatencollectie)
        elif hasattr(self, 'virusweefsel'):
            return model_to_dict(self.virusweefsel)
        elif hasattr(self, 'viruskas'):
            return model_to_dict(self.viruskas)
        else:
            return {'error': 'no raw data found'}

    def get_latest_change(self):
        return self.sample_set.latest('date').date

    def get_first_date(self):
        return self.sample_set.earliest('date').date

    def update_static(self):
        if self.sample_set.all().exists():
            self.first_date = self.get_first_date()
        if self.pathogen:
            self.pathogen_tree = ' '.join([node.get_name for node in self.pathogen.taxon.path_to_root()])
        if self.host:
            self.host_tree = ' '.join([node.get_name for node in self.host.taxon.path_to_root()])
        self.tests_performed = self.give_tests_availeble()
        self.update_static_id()
        self.update_static_comment()
        self.save()

    def give_tests_availeble(self):
        result = []
        if self.test_pcr:
            result.append('pcr')
        if self.test_serology:
            result.append('serology')
        if self.test_patholegy:
            result.append('patholegy')
        if self.test_sequencing:
            result.append('sequencing')
        return '/'.join(result)

    def update_static_id(self):
        def _backup_and_change(old_id_item, new_id):
            if old_id_item.code_txt != new_id:
                # the value in the collection table was editted. needs to be applied.
                Collection_id.objects.create(nakt_id=self,
                                             code_class='old_' + old_id_item.code_class,
                                             code_txt=old_id_item.code_txt)
                old_id_item.code_txt = new_id
                old_id_item.save()

        # main id
        id_collectie = self.id_collectie
        idtype = self.collectie_id_keys[self.pathogen_location]
        if not Collection_id.objects.filter(nakt_id=self.nakt_id).exists():
            # creating the id for new entries
            self.collection_id_set.create(code_txt=self.id_collectie, code_class=idtype)
            if self.id_ins:
                self.collection_id_set.create(code_txt=self.id_ins, code_class='INS')
            if self.id_storidge:
                self.collection_id_set.create(code_txt=self.id_storidge, code_class='Location ID')
            if self.id_original:
                self.collection_id_set.create(code_txt=self.id_original, code_class='Original')
            self.sample_set.create(date=self.add_date, action='added to database')
        _id_collectie = Collection_id.objects.get(nakt_id=self.nakt_id, code_class=idtype)
        # setting the default
        if id_collectie == '':
            self.id_collectie = _id_collectie.code_txt
        else:
            # checking changes
            pass
            #_backup_and_change(_id_collectie, id_collectie)

        # sample id
        id_storidge = self.id_storidge
        #check for deletion
        if Collection_id.objects.filter(nakt_id=self.nakt_id, code_txt=id_storidge, code_class__icontains="old_"):
            self.id_storidge = ''
        #check for changes
        if Collection_id.objects.filter(nakt_id=self.nakt_id, code_class='Location ID').exists():
            _id_storidge = Collection_id.objects.get(nakt_id=self.nakt_id, code_class='Location ID')
        elif Collection_id.objects.filter(nakt_id=self.nakt_id, code_class='Sample').exists():
            # these are still used with virus for some reason
            _id_storidge = Collection_id.objects.get(nakt_id=self.nakt_id, code_class='Sample')
        else:
            _id_storidge = None
        if _id_storidge:
            # setting the default
            self.id_storidge = _id_storidge.code_txt
            '''
            if id_storidge == '':
                self.id_storidge = _id_storidge.code_txt
            else:
                # checking changes
                _backup_and_change(_id_storidge, id_storidge)
            '''
        #for some reason location id's from the table were not showing up in the list.
        #so if the list returns empty and there is a value, copy it.
        elif self.id_storidge:
            self.collection_id_set.create(code_txt=self.id_storidge, code_class='Location ID')

        # inschrijf id
        id_ins = self.id_ins
        #check for deletion
        if Collection_id.objects.filter(nakt_id=self.nakt_id, code_txt=id_ins, code_class__icontains="old_"):
            self.id_ins = ''
        #checking the main ID location for the 'INS' id. 
        if Collection_id.objects.filter(nakt_id=self.nakt_id, code_class='INS').exists():
            try:
                _id_ins = Collection_id.objects.get(nakt_id=self.nakt_id, code_class='INS')
            except Collection_id.MultipleObjectsReturned:
                # print(Collection_id.objects.filter(nakt_id=collection_item.nakt_id, code_class='INS'))
                _id_ins = Collection_id.objects.filter(nakt_id=self.nakt_id, code_class='INS').first()
        else:
            _id_ins = None
        if _id_ins:
            self.id_ins = _id_ins.code_txt
            '''
            # setting the default
            if id_ins == '':
                self.id_ins = _id_ins.code_txt
            else:
                # checking changes
                _backup_and_change(_id_ins, id_ins)
            '''
        #for some reason location id's from the table were not showing up in the list.
        #so if the list returns empty and there is a value, copy it.
        elif self.id_ins:
            self.collection_id_set.create(code_txt=self.id_ins, code_class='INS')

        # id_original
        # repurposing this for location id in previous freezer 2018-9-10
        id_original = self.id_original
        #check for deletion
        if Collection_id.objects.filter(nakt_id=self.nakt_id, code_txt=id_original, code_class__icontains="old_"):
            self.id_original = ''
        #if Collection_id.objects.filter(nakt_id=self.nakt_id, code_class='Original').exists():
        if Collection_id.objects.filter(nakt_id=self.nakt_id, code_class='BacterieCode').exists():
            try:
                #_id_original = Collection_id.objects.get(nakt_id=self.nakt_id, code_class='Original')
                _id_original = Collection_id.objects.get(nakt_id=self.nakt_id, code_class='BacterieCode')
            except Collection_id.MultipleObjectsReturned:
                #_id_original = Collection_id.objects.filter(nakt_id=self.nakt_id, code_class='Original').first()
                _id_original = Collection_id.objects.filter(nakt_id=self.nakt_id, code_class='BacterieCode').first()
        else:
            _id_original = None
        if _id_original:
            self.id_original = _id_original.code_txt
            '''
            # setting the default
            if id_original == '':
                self.id_original = _id_original.code_txt
            else:
                # checking changes
                _backup_and_change(_id_original, id_original)
            '''
        #for some reason location id's from the table were not showing up in the list.
        #so if the list returns empty and there  is a value, copy it.
        elif self.id_original:
            #self.collection_id_set.create(code_txt=self.id_original, code_class='Original')
            # don't think i want to create these outside of detail screen (directly into collection_id)
            pass


        # other id's
        id_other = self.id_other
        #other_id_dic = Collection_id.objects.filter(nakt_id=self.nakt_id).exclude(
        #    code_class__in=[idtype, 'Sample', 'Original'])
        # with the bacteriecode seperate from the location id, it makes more sense to use Bacteriecode as 'original'
        other_id_dic = Collection_id.objects.filter(nakt_id=self.nakt_id).exclude(
            code_class__in=[idtype, 'Sample', 'Location ID', 'INS', 'BacterieCode'])
        if other_id_dic.exists():
            _id_other = ', '.join([x.code_txt for x in other_id_dic])
        else:
            _id_other = None
        if _id_other:
            # setting the default
            self.id_other = _id_other
        else:
            self.id_other = ''
            '''
            if id_other == '':
                self.id_other = _id_other
            # checking changes
            '''
            '''
            for key,value in [x.split(':') for x in id_other.strip('{}').split(', ')]:
                if key in [id.code_class for id in other_id_dic]:
                    _backup_and_change(other_id_dic.get(code_class=key),value)
                else:
                    #does not exist yet, just create.
                    Collection_id.objects.create(nakt_id=collection_item,
                                                 code_class=key,
                                                 code_txt=value)
            '''

    def update_static_comment(self):
        '''
        part of the update_static function. Checks static values of comments.
        The isolate should be saved outside check functions like this, only saving once.
        :return: makes appropriate changes to self
        '''
        def _create_comment():
            self.collection_comment_set.create(
                comment_label='Comment',
                comment_txt=self.comment
            )

        comment = self.comment
        _comment = Collection_comment.objects.filter(nakt_id=self.nakt_id, comment_label='Comment')
        if _comment.exists():
            if comment == '':
                # set self.comment
                self.comment = _comment.first().comment_txt
            else:
                #create comment if it does not exist
                if not _comment.filter(comment_txt=comment).exists():
                    _create_comment()
        else:
            #creating comment object
            if comment != '':
                _create_comment()


    def update_raw_data(self):
        if self.pathogen_location == 'Virus_cryo':
            monster_nr = int(self.collection_id_set.get(code_class="NVC").code_txt.split('-')[1])
            try:
                data = Viruscollectie.objects.get(monsternr=monster_nr)
                data.nakt_object = self
                data.save()
            except Viruscollectie.DoesNotExist:
                print("No original data for nakt_id: {}".format(self.nakt_id))
        elif self.pathogen_location == 'Bacteria_cryo':
            nbc_nr = int(self.collection_id_set.get(code_class="NBC").code_txt.split('-')[1])
            try:
                data = Bacteriecollectie.objects.get(nbc_nummer=nbc_nr)
                data.nakt_object = self
                data.save()
            except Bacteriecollectie.DoesNotExist:
                print("No original data for nakt_id: {}".format(self.nakt_id))
        elif self.pathogen_location == 'Fungi_cryo':
            autonummer = int(self.collection_id_set.get(code_class="NFC").code_txt.split('-')[1])
            try:
                data = Schimmelcollectie.objects.get(autonummer=autonummer)
                data.nakt_object = self
                data.save()
            except Schimmelcollectie.DoesNotExist:
                print("No original data for nakt_id: {}".format(self.nakt_id))
        elif self.pathogen_location == 'Resistance':
            monsternummer = int(self.collection_id_set.get(code_class="NRC").code_txt.split('-')[1])
            try:
                data = Isolatencollectie.objects.get(monsternummer=monsternummer)
                data.nakt_object = self
                data.save()
            except Isolatencollectie.DoesNotExist:
                print("No original data for nakt_id: {}".format(self.nakt_id))
        elif self.pathogen_location == 'Virus_tissue_culture':
            monster_nr = int(self.collection_id_set.get(code_class="NVC").code_txt.split('-')[1])
            try:
                data = VirusWeefsel.objects.get(monsternr=(monster_nr-1000)) #todo would be nicer if this calculation was not hardcoded
                data.nakt_object = self
                data.save()
            except VirusWeefsel.DoesNotExist:
                print("No original data for nakt_id: {}".format(self.nakt_id))
        elif self.pathogen_location == 'Virus_greenhouse':
            monster_nr = int(self.collection_id_set.get(code_class="NVC").code_txt.split('-')[1])
            try:
                data = VirusKas.objects.get(autonumber=(monster_nr-2000)) #todo would be nicer if this calculation was not hardcoded
                data.nakt_object = self
                data.save()
            except VirusWeefsel.DoesNotExist:
                print("No original data for nakt_id: {}".format(self.nakt_id))
        else:
            if self.pathogen_location:
                loc = self.pathogen_location
            else:
                loc = 'this group.'
            print("The raw data link needs to be defined for " + loc)


class PCR_seq(models.Model):
    """
        this class will hold sequences of primers and probes used in pcr tests.
    """
    primer_nr = models.CharField(max_length=64, db_index=True, default='')
    oligo_naam = models.CharField(max_length=64, db_index=True, default='')
    containing_set = models.ForeignKey('PCR_set', on_delete=models.PROTECT)
    sequence = models.CharField(max_length=128)#5'to 3'
    status = models.CharField(max_length=64, db_index=True, default='')
    researcher = models.CharField(max_length=64, db_index=True, default='')
    stock_opl = models.CharField(max_length=64, db_index=True, default='')
    werk_opl = models.CharField(max_length=64, db_index=True, default='')
    fabrication_year = models.DateField(db_index=True, null=True, default=None)
    label5 = models.CharField(max_length=64, db_index=True, default='')
    label3 = models.CharField(max_length=64, db_index=True, default='')

    def as_dict(self):
        return {
            "DT_RowId": self.pk,
            "primer_nr": self.primer_nr,
            "oligo_naam": self.oligo_naam,
            "sequence": self.sequence,
            "status": self.status,
            "researcher": self.researcher,
            "stock_opl": self.stock_opl,
            "werk_opl": self.werk_opl,
            "fabrication_year": self.fabrication_year,
            "label5": self.label5,
            "label3": self.label3,
            "containing_set__groep": self.containing_set.groep,
            "containing_set__pathogeen": self.containing_set.pathogeen,
            "containing_set__literatuur": self.containing_set.literatuur,
            "containing_set__comment": self.containing_set.comment,
            "containing_set__pcr_product": self.containing_set.pcr_product,
        }
'''
class PCR_reaction(models.Model):
    """
        this class will hold sequences of oligo pairs that are used in pcr tests.
    """
    product_description = models.CharField(max_length=64, db_index=True, default='')
    containing_set = models.ForeignKey('PCR_set', on_delete=models.PROTECT,  blank=True, null=True)
    forward_seq = models.ForeignKey(PCR_seq, on_delete=models.PROTECT)
    reverse_seq = models.ForeignKey(PCR_seq, on_delete=models.PROTECT)
    probe_seq = models.ForeignKey(PCR_seq, on_delete=models.PROTECT,  blank=True, null=True)
    bp_product = models.IntegerField()

'''
class PCR_set(models.Model):
    """
        this class will hold PCR primer sets that are used for pathogen detection.
    """
    pcr_nr = models.IntegerField()
    #variations = models.BooleanField(default=False)
    #main_reaction = models.ForeignKey(PCR_reaction, on_delete=models.PROTECT, blank=True, null=True)
    groep = models.CharField(max_length=64, db_index=True)
    pathogeen = models.CharField(max_length=64, db_index=True, default='')
    literatuur = models.CharField(max_length=256, db_index=True, default='')
    comment = models.CharField(max_length=256, db_index=True, default='')
    pcr_product = models.CharField(max_length=128, db_index=True, default='')

TEST_CHOISES = (
    (1, "PCR"),
)

class Collection_tests(models.Model):
    """
        this class will hold information on the PCR tests performed on the Collection objects.
    """
    nakt_id = models.ForeignKey(Collection, on_delete=models.CASCADE, blank=True, null=True)
    toets = models.CharField(max_length=32, db_index=True, choices=TEST_CHOISES)
    pcr_set = models.ForeignKey(PCR_set, on_delete=models.PROTECT,  blank=True, null=True)
    result = models.NullBooleanField(db_index=True, blank=True, null=True, default=None)
    comment = models.CharField(max_length=500, db_index=True, default='')

class Collection_id(models.Model):
    """
        python class representation of the table public.collectie_collection_id in postgress
    """
    # various codes and id's of the isolates in the collection
    nakt_id = models.ForeignKey(Collection, on_delete=models.CASCADE)
    code_txt = models.CharField(max_length=64, default='')
    code_class = models.CharField(max_length=32, db_index=True, default='')

    main_code_classes = ['INS','Location ID','NBC','NFC','NVC']

    def __str__(self):
        return (self.code_class + ' id: ' + self.code_txt)

    def is_old(self):
        if self.code_class[:4] == 'old_':
            return True
        else:
            return False

    def as_table_row(self):
        return {
            "DT_RowId": self.pk,
            "code_txt": self.code_txt,
            "code_class": self.code_class
        }


class Collection_comment(models.Model):
    '''
    class to add comments to isolates in the collection
    '''
    nakt_id = models.ForeignKey(Collection, on_delete=models.CASCADE)
    comment_txt = models.CharField(max_length=1000)
    comment_label = models.CharField(max_length=64)

    def as_table_row(self):
        return {
            "DT_RowId": self.pk,
            "comment_txt": self.comment_txt,
            "comment_label": self.comment_label
        }


class Sample(models.Model):
    """
        python class representation of the table public.collectie_sample in postgress
    """
    nakt_id = models.ForeignKey(Collection, on_delete=models.CASCADE)
    date = models.DateField('date of storage')
    action = models.CharField(max_length=32, db_index=True, default='')
    note = models.CharField(max_length=1024, db_index=True, default='')

    # container       =   models.CharField(max_length=32, db_index=True, default = '')

    def as_table_row(self):
        return {
            "DT_RowId": self.pk,
            "date": self.date,
            "action": self.action,
            "note": self.note
        }


'''
#####  collectie oud #####
'''


class Bacteriecollectie(models.Model):
    nakt_object = models.OneToOneField(Collection, on_delete=models.SET_NULL, blank=True, null=True)
    bacteriecode = models.CharField(max_length=32, default='')
    nummer = models.IntegerField(default=0)
    isolaatnummer = models.CharField(max_length=32, default='')
    originele_code = models.CharField(max_length=32, default='')
    monsternummer = models.CharField(max_length=32, default='')
    gewas = models.CharField(max_length=32, default='')
    gewasoud = models.CharField(max_length=64, default='')
    materiaal = models.CharField(max_length=64, default='')
    herkomst = models.CharField(max_length=32, default='')
    jaar = models.IntegerField(default=0)
    serologie = models.CharField(max_length=128, default='')
    qpcr = models.CharField(max_length=512, default='')
    pathogeniteit = models.CharField(max_length=128, default='')
    opmerkingen = models.CharField(max_length=1024, default='')
    datum20 = models.DateTimeField(null=True)
    datum80 = models.DateTimeField(null=True)
    controle80 = models.DateTimeField(null=True)
    controle20 = models.DateTimeField(null=True)
    dienstverlening = models.BooleanField()
    selectiecode = models.BooleanField()
    nbc_nummer = models.IntegerField(primary_key=True)
    indicatie_naam = models.CharField(max_length=64, default='')
    lmg_code = models.CharField(max_length=32, default='')
    ncppb_code = models.CharField(max_length=32, default='')
    icmp_code = models.CharField(max_length=32, default='')
    pd_nvwa_code = models.CharField(max_length=32, default='')
    cfbp_code = models.CharField(max_length=32, default='')
    overige_code = models.CharField(max_length=64, default='')
    bevestigde_naam = models.CharField(max_length=64, default='')
    bevestig_meto = models.CharField(max_length=32, default='')
    sequentie = models.CharField(max_length=32, default='')
    medewerker = models.CharField(max_length=32, default='')

    class Meta:
        db_tablespace = 'bigspace'


class Schimmelcollectie(models.Model):
    nakt_object = models.OneToOneField(Collection, on_delete=models.SET_NULL, blank=True, null=True)
    naam_schimmel = models.CharField(max_length=64, default='')
    gewas = models.CharField(max_length=32, default='')
    materiaal = models.CharField(max_length=64, default='')
    symptomen = models.CharField(max_length=128, default='')
    herkomst = models.CharField(max_length=32, default='')
    ins_nummer = models.CharField(max_length=32, default='')
    monstercode = models.CharField(max_length=32, default='')
    jaar = models.IntegerField(default=0)
    opmerkingen = models.CharField(max_length=640, default='')
    datum80 = models.DateTimeField(null=True)
    nummer = models.IntegerField(default=0)
    controle80 = models.DateTimeField(null=True)
    grond4 = models.DateTimeField(null=True)
    code4 = models.IntegerField(default=0)
    controle4 = models.DateTimeField(null=True)
    datum4 = models.DateTimeField(null=True)
    nummer4 = models.IntegerField(default=0)
    controlebuis4 = models.DateTimeField(null=True)
    dienstverlening = models.BooleanField()
    autonummer = models.IntegerField(primary_key=True)
    medewerker = models.CharField(max_length=8, default='')
    sequence = models.CharField(max_length=8, default='')

    class Meta:
        db_tablespace = 'bigspace'


class Viruscollectie(models.Model):
    nakt_object = models.OneToOneField(Collection, on_delete=models.SET_NULL, blank=True, null=True)
    doosnr = models.CharField(max_length=32, default='')
    monsternr = models.IntegerField(primary_key=True)
    opslag = models.CharField(max_length=16, default='')
    aantal = models.IntegerField(default=0)
    pathogeen = models.CharField(max_length=128, default='')
    virusegroep = models.CharField(max_length=32, default='')
    gewas = models.CharField(max_length=32, default='')
    toetsplant = models.CharField(max_length=32, default='')
    code = models.CharField(max_length=32, default='')
    materiaal = models.CharField(max_length=32, default='')
    herkomst = models.CharField(max_length=32, default='')
    opmerkingen = models.CharField(max_length=256, default='')
    datum80 = models.DateTimeField(null=True)

    class Meta:
        db_tablespace = 'bigspace'


class VirusKas(models.Model):
    nakt_object = models.OneToOneField(Collection, on_delete=models.SET_NULL, blank=True, null=True)
    autonumber = models.IntegerField(primary_key=True)
    compartment = models.IntegerField(default=0)
    table = models.IntegerField(default=0)
    code = models.CharField(max_length=32, default='')
    acronym = models.CharField(max_length=32, default='')
    virus_species = models.CharField(max_length=128, default='')
    virus_genus = models.CharField(max_length=32, default='')
    plant_genus = models.CharField(max_length=32, default='')
    plant_nl = models.CharField(max_length=32, default='')
    datum = models.CharField(max_length=32, default='')
    comment = models.CharField(max_length=256, default='')

    class Meta:
        db_tablespace = 'bigspace'


class VirusWeefsel(models.Model):
    nakt_object = models.OneToOneField(Collection, on_delete=models.SET_NULL, blank=True, null=True)
    monsternr   =   models.IntegerField(primary_key=True)
    gewas_la    =   models.CharField(max_length=32, default='')
    gewas_nl    =   models.CharField(max_length=32, default='')
    gewas_old   =   models.CharField(max_length=32, default='')
    proefnr     =   models.IntegerField()
    virus_mlo   =   models.CharField(max_length=128, default='')
    labnr       =   models.CharField(max_length=32, default='')
    land        =   models.CharField(max_length=32, default='')
    herkomst    =   models.CharField(max_length=32, default='')
    extr_nr     =   models.CharField(max_length=128, default='')
    extra_info  =   models.CharField(max_length=256, default='')
    datum_kweek =   models.DateField(null=True)

    class Meta:
        db_tablespace = 'bigspace'


class Isolatencollectie(models.Model):
    nakt_object = models.OneToOneField(Collection, on_delete=models.SET_NULL, blank=True, null=True)
    monsternummer = models.IntegerField(primary_key=True)
    collectie_class = models.CharField(max_length=8, default='')
    in_collectie = models.BooleanField()
    isf_Code = models.CharField(max_length=32, default='')
    aantal = models.CharField(max_length=32, default='')
    pathogeen = models.CharField(max_length=64, default='')
    gewas = models.CharField(max_length=64, default='')
    fysio_class = models.CharField(max_length=16, default='')
    fysio_txt = models.CharField(max_length=64, default='')
    isolaat_class = models.CharField(max_length=16, default='')
    herkomst_class = models.CharField(max_length=32, default='')
    herkomst_txt = models.CharField(max_length=64, default='')
    backup_bedrijf = models.CharField(max_length=32, default='')
    beheertype = models.CharField(max_length=8, default='')
    overzet_3mnds = models.BooleanField()
    overzet_medium = models.CharField(max_length=64, default='')
    in_freez_low = models.BooleanField()
    in_grond = models.BooleanField()
    gevriesdroogd = models.BooleanField()
    vriesdroog_nr = models.CharField(max_length=64, default='')
    proefnummer = models.DateTimeField(null=True)
    opstart_bron = models.BooleanField()
    opstart_opm = models.CharField(max_length=64, default='')
    freez_low_nr = models.IntegerField(default=0)
    freez_low_lok = models.CharField(max_length=8, default='')
    freez_low_datum = models.DateTimeField(null=True)
    freez_low_opm = models.CharField(max_length=64, default='')
    in_freezer = models.BooleanField()
    opm = models.CharField(max_length=128, default='')
    ook_was = models.CharField(max_length=32, default='')

    class Meta:
        db_tablespace = 'bigspace'


'''
##### utils tables
'''


class UserSelected(models.Model):
    select_user = models.ForeignKey(User, on_delete=models.CASCADE)
    select_collection = models.ForeignKey(Collection, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("select_user", "select_collection")


class Changelog(models.Model):
    dtuser = models.CharField(max_length=64, default='')
    dtaction = models.CharField(max_length=16, default='')
    dtvalues = JSONField()
    dtrow = models.IntegerField(default=0)
    dtwhen = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_tablespace = 'bigspace'


class Table_descriptions(models.Model):
    table = models.CharField(max_length=64)
    column = models.CharField(max_length=64)
    auto_created = models.BooleanField(default=False)
    description = models.CharField(max_length=128, default='')
    placeholder = models.CharField(max_length=128, default='')

    def __str__(self):
        return ("Information on " + self.table + '.' + self.column)