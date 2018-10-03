from django.contrib import admin
from django import forms
from .models import Pathogen, Original_host, Origin_pathogen, NCBI_nodes, Changelog, Table_descriptions
import json

class PathogenForm(forms.ModelForm):
    class Meta:
        fields = []
        model = Pathogen

    def __init__(self, *args, **kwargs):
        super(PathogenForm, self).__init__(*args, **kwargs)
        self.fields['taxon'].queryset = NCBI_nodes.objects.exclude(has_data=False).order_by('scientific_name')

class PathogenAdmin(admin.ModelAdmin):
    fields = ['given_name', 'taxon', 'is_choice']
    form = PathogenForm
    list_display = ('scientific_name', 'given_name', 'is_choice')
    search_fields = ['scientific_name', 'given_name']

    def save_model(self, request, obj, form, change):
        Changelog.objects.create(dtuser=request.user.username, dtaction='admin_save',
             dtvalues=json.dumps({obj._meta.db_table: form.changed_data}),
             dtrow=obj.pk if obj.pk else 0)
        super(PathogenAdmin, self).save_model(request, obj, form, change)
        obj.scientific_name = obj.taxon.get_name
        obj.save()

class HostForm(forms.ModelForm):
    class Meta:
        fields = []
        model = Original_host

    def __init__(self, *args, **kwargs):
        super(HostForm, self).__init__(*args, **kwargs)
        self.fields['taxon'].queryset = NCBI_nodes.objects.exclude(has_data=False).order_by('scientific_name')

class HostAdmin(admin.ModelAdmin):
    fields = ['given_name', 'taxon', 'is_choice', 'comment']
    form = HostForm
    list_display = ('scientific_name', 'given_name', 'is_choice', 'comment')
    search_fields = ['scientific_name', 'given_name']

    def save_model(self, request, obj, form, change):
        Changelog.objects.create(dtuser=request.user.username, dtaction='admin_save',
             dtvalues=json.dumps({obj._meta.db_table: form.changed_data}),
             dtrow=obj.pk if obj.pk else 0)
        super(HostAdmin, self).save_model(request, obj, form, change)
        obj.scientific_name = obj.taxon.get_name
        obj.save()

class OriginAdmin(admin.ModelAdmin):
    fields = ['given_name', 'country', 'is_choice', 'comment']
    list_display = ('country', 'given_name', 'is_choice', 'comment')

class TaxonAdminForm(forms.ModelForm):
    def save(self, commit=True):
        m = super(CallResultTypeForm, self).save(commit=False)
        # do custom stuff
        if commit:
            m.save()
        return m

class TaxonAdmin(admin.ModelAdmin):
    fields = ['get_name', 'tax_id', 'has_data']
    list_display = ('get_name', 'tax_id', 'has_data')
    list_filter = ('has_data', 'rank')
    readonly_fields = ('get_name', 'tax_id')
    ordering = ['scientific_name']
    search_fields = ['scientific_name']

    def get_search_results(self, request, queryset, search_term):
        try:
            search_term_as_int = int(search_term)
        except ValueError:
            queryset, use_distinct = super(TaxonAdmin, self).get_search_results(request, queryset, search_term)
        else:
            queryset = self.model.objects.filter(tax_id=search_term_as_int)
            use_distinct = False
        return queryset, use_distinct

    def has_add_permission(self, request):
        return False

class DiscriptionAdmin(admin.ModelAdmin):
    fields = ['description','placeholder']
    list_filter = ('table', 'auto_created')
    list_display = ('__str__','description','placeholder')
    readonly_fields = ['table', 'column']

    def has_add_permission(self, request):
        return False

admin.site.register(NCBI_nodes, TaxonAdmin)
admin.site.register(Pathogen, PathogenAdmin)
admin.site.register(Original_host, HostAdmin)
admin.site.register(Origin_pathogen, OriginAdmin)
admin.site.register(Table_descriptions, DiscriptionAdmin)