from django.conf.urls import url
from . import views

app_name = 'collectie'
urlpatterns = [
    # /
    url(r'^$', views.accession_experiment, name='index'),
    url(r'^data/$', views.accession_experiment_data, name='index_data'),
    # /1/
    url(r'^(?P<accession_nr>[0-9]+)/$', views.accession, name='accession'), #isolate detail
    url(r'^(?P<accession_nr>[0-9]+)/ids/$', views.get_accession_id),
    url(r'^(?P<accession_nr>[0-9]+)/samples/$', views.get_sample_update),
    url(r'^(?P<accession_nr>[0-9]+)/tests/$', views.get_test_description),
    url(r'^(?P<accession_nr>[0-9]+)/info/$', views.get_accession_data),
    url(r'^(?P<accession_nr>[0-9]+)/comment/$', views.get_accession_comment),
    # /edit
    url(r'^edit/$', views.accession_edit, name='edit'), #isolate edit list
    url(r'^edit/newids/$', views.get_new_id),
    url(r'^edit/update_static/$', views.get_update_static),
    # /labels/
    url(r'^labels/$', views.accession_labels, name='labels'), #user selected list
    url(r'^labels/user_selected/$', views.get_select),
    url(r'^labels/user_selected_print/$', views.get_select_print),
    url(r'^labels/user_selected_nr/$', views.get_select_nr),
    # /pcr/
    url(r'^pcr/$', views.test_pcr, name='pcr'), #oligo's used for pcr testing
    url(r'^pcr/data/$', views.test_pcr_data),
    # /pcr/1/
    url(r'^pcr/(?P<pcr_nr>[0-9]+)/$', views.test_pcr_detail, name='pcr_toets'), #pcr based tests
    # /taxon/1/
    url(r'^taxon/(?P<taxon_id>[0-9]+)/$', views.detail, name='taxon_detail'), #taxon information
    # ajax request pages
    url(r'^field_info/$', views.get_field_info),

    #legacy or test pages
    # /collectie/
    url(r'^collectie/$', views.index, name='old_index'),
    # /taxon/
    url(r'^taxon/$', views.TaxonSearchListView.as_view(), name='taxon_list'),
    # /old/
    url(r'old/^$', views.accession_php, name='old_index'),  # isolate list
]
