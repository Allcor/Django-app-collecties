'''
https://query.wikidata.org/#SELECT%20%3FtaxonLabel%20%3FNCBI_Taxonomy_ID%20%3Ftaxon_common_name%20WHERE%20%7B%0A%20%20%3Ftaxon%20wdt%3AP31%20wd%3AQ16521.%0A%20%20%3Ftaxon%20wdt%3AP685%20%3FNCBI_Taxonomy_ID%20.%0A%20%20SERVICE%20wikibase%3Alabel%20%7B%20bd%3AserviceParam%20wikibase%3Alanguage%20%22nl%22.%20%7D%0A%20%20OPTIONAL%20%7B%20%3Ftaxon%20wdt%3AP1843%20%3Ftaxon_common_name%20filter%20%28lang%28%3Ftaxon_common_name%29%20%3D%20%22nl%22%29%7D%0A%20%20FILTER%20regex%28%3FNCBI_Taxonomy_ID%2C%20%22%5E1%5B0-9%5D%7B3%7D%24%22%29%0A%7D

SELECT ?taxonLabel ?NCBI_Taxonomy_ID ?taxon_common_name WHERE {
  ?taxon wdt:P31 wd:Q16521.
  ?taxon wdt:P685 ?NCBI_Taxonomy_ID .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "nl". }
  OPTIONAL { ?taxon wdt:P1843 ?taxon_common_name filter (lang(?taxon_common_name) = "nl")}
  FILTER regex(?NCBI_Taxonomy_ID, "^1[0-9]{3}$")
}
'''

import sys
import requests

class WikiQuery():
    
    sparql_url = "https://query.wikidata.org/sparql?query="
    sparql_options = "&format=json"
    
    def all_ncbi_tax(self):
        query = "SELECT (max(xsd:integer(?NCBI_Taxonomy_ID)) as ?count) WHERE { ?taxon wdt:P31 wd:Q16521. ?taxon wdt:P685 ?NCBI_Taxonomy_ID.}"
        count = requests.get(self.sparql_url+query+self.sparql_options).json()
        return count['results']['bindings'][0]['count']['value']
    
    def fetch_ncbi_tax_nl(self,num_prefix=''):
        if num_prefix == 0: num_prefix=''
        query = ''' SELECT  ?taxonLabel ?NCBI_Taxonomy_ID 
                    (GROUP_CONCAT(DISTINCT(?taxon_common_name); separator=", ") as ?all_names)
                    WHERE { ?taxon wdt:P31 wd:Q16521. ?taxon wdt:P685 ?NCBI_Taxonomy_ID .
                    SERVICE wikibase:label { bd:serviceParam wikibase:language "nl". }
                    OPTIONAL { ?taxon wdt:P1843 ?taxon_common_name filter (lang(?taxon_common_name) = "nl")}
                    FILTER regex(?NCBI_Taxonomy_ID, "^%s[0-9]{4}$")
                    } GROUP BY ?taxonLabel ?NCBI_Taxonomy_ID
                ''' % num_prefix
        names_query = requests.get(self.sparql_url+query+self.sparql_options).json()
        for result in names_query['results']['bindings']:
            names = []
            tax_id = result['NCBI_Taxonomy_ID']
            names.append(result['taxonLabel']['value'])
            if 'all_names' in result:
                #print(result['all_names'])
                for common in result['all_names']['value'].split(', '):
                    if common not in names and common != '':
                        names.append(common)
            yield (tax_id['value'],names)

def main(arguments):
    foo = WikiQuery()
    for name in foo.fetch_ncbi_tax_nl():
        print (name)

if __name__ == "__main__":
    main(sys.argv[1:])
