'''
Because some ID's have been changing there are some subtle rules to account for.
This file is meant to keep track of them and have a central place to make adjustments.
'''

from django.db.models import IntegerField
from django.db.models.expressions import F, Value, Func
from django.db.models.functions import Cast

from collectie.models import Collection_id, Collection

def next_id(code_class, contains=None):
    '''
    Used in the Ajax request to help with creating the next id.
    :param code_class: the Collection_id code_class
    :param contains: the non numeric part of the id
    :return: returns a unique id conforming to the given rules
    '''
    q1 = Collection_id.objects.filter(code_class=code_class)
    if code_class == 'Location ID' and contains:
        #should have a 'contains' with the pathogen abbreviation used on the -80 boxes.
        if Collection_id.objects.filter(code_txt__icontains=contains).exists():
            q1 = q1.filter(code_txt__icontains=contains)
            pre = contains + '-'
        else:
            return ''
    elif code_class in ['NBC','NFC','NVC']:
        # this assumes the id to be an Naktuinbouw pathogen id
        pre = code_class + '-'
        #if code_class == 'NVC':
            # The virus from different locations have the same handel.
            # New entries should not to be in conflict with previous id's
    else:
        #should throw a error, other id
        return False
    q1 = q1.exclude(code_txt__isnull=True).exclude(code_txt__exact='')
    q1 = q1.annotate(
        code_int=Cast(Func(F('code_txt'), Value(r'[^\d]'), Value(''), Value('g'),
                           function='regexp_replace'),
                      IntegerField()))
    q1 = q1.order_by('-code_int').first()
    return pre + str(q1.code_int + 1)

def new_collection_id(location):
    '''
    Both collection_id and the location_id are dependent on the database
    This creates the next following to use in autofilling it in a form
    :param location: The Database where the Isolate will be saved at.
    :return: collection ID (NBC) and location ID (Box2-4B)
    '''
    code_class = Collection.collectie_id_keys[location]
    collection_id = next_id(code_class)
    if code_class == 'NFC':
        location_id = next_id('Location ID','POS')
    else:
        location_id = calculate_location(collection_id)
    return collection_id, location_id

def prepolutate_virus_id(samplenr, location):
    '''
    The virus from different locations have the same handel.
    New entries should not conflict with previous id's
    :param samplenr: the (auto)number used in the original file.
    :param location: used for continuity, adding the same amount for the dataset
    :return: returns a unique id
    '''
    range_start = {
        'Virus_cryo': 0,
        'Virus_tissue_culture': 1000,
        'Virus_greenhouse': 2000
    }
    return str(int(samplenr)+range_start[location])

def calculate_location(collection_nr):
    '''
    creates a location from the NBC id
    :param collection_nr: the NBC id
    :return: the location id
    '''
    template = "Box{box}-{row}{col}"
    box_size = (9,9)
    columns = [y+1 for y in range(box_size[1])]
    rows = [chr(x+65) for x in range(box_size[0])]

    if collection_nr[:3] in ['NBC']: #only the Bacteria get a Location ID for now
        number = (int(collection_nr[4:]))-1
        box = (number//(box_size[0]*box_size[1]))+1
        number = number%(box_size[0]*box_size[1])
        row = rows[number//box_size[0]]
        number = number%box_size[0]
        column = columns[number]
        return template.format(**{'box':box, 'row':row, 'col':column})
    else:
        return False