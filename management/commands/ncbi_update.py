#!/usr/bin/python3

'''
Script to read the names.dmp file from NCBI taxonemy ftp.
        ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump_readme.txt
        ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz
        
as of now just populates the database, should be modified so it can be used to update.


6-6-2017:
    made a file handeler in collectie/utils
    
    now a function to add the data to the website database
    https://docs.djangoproject.com/en/dev/howto/custom-management-commands/
7-6-2017:
    decided to play it safe and add nodes only when parent node is alreaddy present,
    Use Django models to check if id exists and add/change if nessesary
8-6-2017:
    had to make tax_id 1 in the shell. 
    names are also added with the .create() function on the node.
'''

import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from naktdata.settings import BASE_DIR
from collectie.utils.ncbi_taxdump import Dump_files
from collectie.models import NCBI_nodes, NCBI_names

#TODO show last update on site 

#TODO what if a node is deleted? how to detect.

#TODO how often is a node remade? should the local specific names be moved.
#TODO how often is a parent_node changed? should be improved.

#TODO make a logger instance specific for NCBI changes found wile checking

class Command(BaseCommand):
    help = 'help string here'
    
    def _check_nodes(self):
        #for comparing the NCBI_taxonemy and local taxonemy node table.
        
        # adding the parent_node_id derectly to 'parent_tax_id_id' should work,
        # using ncbi_nodes_set.create() should be a safer way to populate
        # Django creates a set in the parent of the foreighnkey relations
        # if parent tax_id is not present, the node is saved so the connection can be made later
        parent_dict = {} # {parent_id:[(tax_id,rank)]}
        
        def node_set_create(parent_node, new_id, new_rank):
            # recursive inner function to create entries
            new_node = parent_node.ncbi_nodes_set.create(tax_id=new_id, rank=new_rank)
            if new_id in parent_dict:
                parent_list = parent_dict.pop(new_id)
                for next_id,next_rank in parent_list:
                    node_set_create(new_node,next_id,next_rank)
        
        
        # itterates over NCBI_taxonemy node id's
        # checks if node exists and makes changes when needed.
        for node_lib in self.dmp.fetch_nodes():
            #TODO not all availeble variables are yielded, only those shown here.
            check_tax_id = node_lib['node_id']
            check_parent_tax_id = node_lib['parent_node_id']
            check_rank = node_lib['node_rank']
            check_hidden = node_lib['hidden']
            #check if the id exists
            if NCBI_nodes.objects.filter(tax_id=check_tax_id).exists():
                #check if changes are required
                n = NCBI_nodes.objects.get(tax_id=check_tax_id)
                if n.rank != check_rank:
                    n.rank = check_rank
                    n.save()
                if n.parent_tax_id_id != check_parent_tax_id:
                    #TODO not sure how to handel this yet, how to add something to a ncbi_nodes_set of a parent does not exist?
                    #   could add to the parent_dict? and remove current instance?
                    #   https://docs.djangoproject.com/en/1.11/topics/db/queries/#additional-methods-to-handle-related-objects
                    n.parent_tax_id_id = check_parent_tax_id
                    n.save()
            else:
                #add new id to database
                if NCBI_nodes.objects.filter(tax_id=check_parent_tax_id).exists():
                    p = NCBI_nodes.objects.get(tax_id=check_parent_tax_id)
                    node_set_create(p,check_tax_id,check_rank)
                else:
                    if check_parent_tax_id in parent_dict:
                        parent_dict[check_parent_tax_id].append((check_tax_id,check_rank))
                    else:
                        parent_dict[check_parent_tax_id] = [(check_tax_id,check_rank)]
    
    def _check_names(self):
        #itterates on NCBI_taxonemy names
        #checks if name exists and makes changes if needed.
        for name_lib in self.dmp.fetch_names():
            #the 'unique_name' variable is not yielded,
            check_tax_id = name_lib['node_id']
            check_name_txt = name_lib['synonym']
            check_name_class = name_lib['label']
            #the tax_id is not checked as the nodes are created beforehand
            n = NCBI_nodes.objects.get(tax_id=check_tax_id)
            # TODO not sure what needs to be checked, original has a id,name,class combined key
            if check_name_class == 'scientific name' and  n.ncbi_names_set.filter(name_class=check_name_class).exists():
                name = n.ncbi_names_set.get(name_class='scientific name')
                if name != check_name_txt:
                    name.name_txt = check_name_txt
                    name.save()
                    n.scientific_name = check_name_txt
                    n.save()
            elif not n.ncbi_names_set.filter(name_txt=check_name_txt, name_class=check_name_class).exists():
                #create new name entry
                n.ncbi_names_set.create(name_txt=check_name_txt, name_class=check_name_class)
    
    def handle(self, *args, **options):
        logging.basicConfig(filename=BASE_DIR+'/logs/ncbi_update.log',level=logging.DEBUG, filemode='a+')
        #fetching the newest dump
        self.dmp = Dump_files()
        #update nodes
        with transaction.atomic():
            self._check_nodes()
        #update names
        with transaction.atomic():
            self._check_names()
