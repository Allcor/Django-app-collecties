'''
uses wikidata sparql quiry to fetch dutch names for NCBI taxonemy id's

https://query.wikidata.org/

13-6-2017
    made generator in utils fetching names for 10000 possible tax_id 's
    now itterate on all those pools and add the names
16-6-2017
    some names yielded this way are the same as the scientific name, those are not added anymore.
'''
import logging

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from naktdata.settings import BASE_DIR
from collectie.models import NCBI_names, NCBI_nodes
from collectie.utils.wiki_names import WikiQuery

class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    NAME_LABEL = 'dutch_vernacular'

    def _add_dutch_tax_names(self):
        pools = int(int(self.wiki_query.all_ncbi_tax())/10000)
        for pool in range(pools+1):
            if pool == 0: pool = ''
            logging.debug("currently adding all tax_id between "+str(pool)+"0000 and "+str(pool)+"9999")
            with transaction.atomic():
                for new_tax_id,new_names in self.wiki_query.fetch_ncbi_tax_nl(pool):
                    try:
                        p = NCBI_nodes.objects.get(tax_id = new_tax_id)
                        sci_name = p.ncbi_names_set.get(name_class='scientific name').name_txt
                        for new_name in new_names:
                            if new_name != sci_name:
                                p.ncbi_names_set.create(name_txt = new_name, name_class = self.NAME_LABEL)
                    except ObjectDoesNotExist:
                        logging.warning("tax_id "+str(new_tax_id)+" not found, names not added: "+', '.join(new_names))

    def handle(self, *args, **options):
        logging.basicConfig(filename=BASE_DIR+'/logs/dutch_names.log',level=logging.DEBUG, filemode='a+')
        #logging.getLogger().addHandler(logging.StreamHandler())
        self.wiki_query = WikiQuery()
        self._add_dutch_tax_names()

