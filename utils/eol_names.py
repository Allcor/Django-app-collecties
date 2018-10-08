#!/usr/bin/python3

import requests
import logging


class EOL_query():
    
    base_url = "http://eol.org/api"
    search_url = "/search_by_provider/1.0.json?id="
    pages_url = "/pages/1.0.json?batch=false&id="
    search_options = "&hierarchy_id=1172"
    pages_options = "&common_names=true"
    
    logging.basicConfig(filename='example.log',level=logging.DEBUG)
    
    def fetch_dutch_verniculars(self,ncbi_id):
        #Encyclopedia of life API Search and Pages query for vernicular names
        #supossed to return dutch/common names
        #execute search quiry
        s_query = requests.get(self.base_url+self.search_url+str(ncbi_id)+self.search_options)
        if s_query.status_code != 200:
                logging.debug("EOL id "+str(ncbi_id)+" failed to return valid responce, error code: " + str(s_query.status_code))
        s_query = s_query.json()
        if s_query != []:
            page_id = s_query[0]['eol_page_id']
            p_query = requests.get(self.base_url+self.pages_url+str(page_id)+self.pages_options)
            if p_query.status_code != 200:
                logging.debug("EOL id "+str(page_id)+" failed to return valid responce, error code: " + str(p_query.status_code))
            p_query = p_query.json()
            #'identifier', 'vernacularNames', 'scientificName', 'taxonConcepts', 'richness_score', 'dataObjects'
            if type(p_query) is list:
                for item in p_query:
                    if 'error' in item:
                        logging.error("EOL request "+','.join(page_id)+" failed with error: "+item['error'])
            else:
                for vernicular in p_query['vernacularNames']:
                    #'vernacularName', 'language', ('eol_preferred')
                    if vernicular['language'] == 'nl':
                        yield vernicular['vernacularName']
