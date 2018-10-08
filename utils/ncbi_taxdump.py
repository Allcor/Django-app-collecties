#!/usr/bin/python3

'''
Script to read the names.dmp file from NCBI taxonemy ftp.
        ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump_readme.txt
        ftp://ftp.ncbi.nih.gov/pub/taxonomy/taxdump.tar.gz
        
thinking of having this work like a generator. yielding names/nodes to add to the database

1-6-2017:
    Before adding them to the database first need to read the file.
    first the node dump, with all the tax_id and related info, 
    then the name dump, with all the scientific and common names.
6-6-2017:
    NCBI taxdump download. checks for newest vertion.
    the fetch_nodes and fetch_names functions can then be used to itterate over the respective files.
    
    now a function to add the data to the website database, (making it in /management/commands/ncbi_update.py)
'''

import logging
import sys,os
import urllib.request, tarfile, hashlib
from optparse import OptionParser


MAIN_PATH = "/nfs/BigData01/postgresql"
CHANGELOG_PATH = MAIN_PATH+"/"
FOLDER = MAIN_PATH+"/ncbi_dump"
URL = "ftp://ftp.ncbi.nih.gov/pub/taxonomy/"
TAR_FILE = "/taxdump.tar.gz"
MD5_FILE = "/taxdump.tar.gz.md5"


######################
# NCBI files handeler
######################

class Dump_files():
    """
    updates the NCBI taxdump file and can be used to return the nodes/names
    """
    
    def __init__(self, folder= FOLDER, tar_file = TAR_FILE):
        self.folder = folder
        if not os.path.isdir(folder):
            os.mkdir(folder)
        self.file_location = folder+tar_file
        tar = self.fetch_tar()
        tar.extract(tar.getmember("names.dmp"),folder)
        self.names_file = folder + "/names.dmp"
        tar.extract(tar.getmember("nodes.dmp"),folder)
        self.nodes_file = folder + "/nodes.dmp"
        tar.close()

    def fetch_nodes(self):
        #generator function for nodes.dmp
        with open(self.nodes_file, 'r') as nodes:
            for node in nodes:
                _node = node.strip('\t|\n').split('\t|\t')
                #-- node id in GenBank taxonomy database
                tax_id = int(_node[0])
                #-- parent node id in GenBank taxonomy database
                parent = int(_node[1])
                #-- rank of this node ( no rank, superkingdom, kingdom, subkingdom ,superphylum, phylum, subphylum, 
                #                       superclass, class, subclass, infraclass, superorder, order, cohort, suborder, infraorder, parvorder, 
                #                       superfamily, family, subfamily, tribe, subtribe, genus, subgenus, species group, species subgroup, 
                #                       species, subspecies, varietas, forma)
                rank = _node[2]
                #-- locus-name prefix; not unique
                embl_code = _node[3]
                #-- see division.dmp file
                division_id = _node[4]
                #-- 1 if node inherits division from parent
                div_flag = _node[5]
                #-- see gencode.dmp file
                genetic_id = _node[6]
                #-- 1 if node inherits genetic code from parent
                GC_flag = _node[7]
                #-- see gencode.dmp file (mitochondreon genetic code id)
                mito_id = _node[8]
                #-- 1 if node inherits mitochondrial gencode from parent
                MGC_flag = _node[9]
                #-- 1 if name is suppressed in GenBank entry lineage
                GenBank_flag = _node[10]
                #-- 1 if this subtree has no sequence data yet
                hidden_flag = _node[11]
                #-- free-text comments and citations (only 'uncultured' on NCBI)
                try:
                    comments = _node[12]
                except IndexError:
                    comments = ""
                ###
                yield {"node_id":tax_id, "parent_node_id":parent, "node_rank":rank, "hidden":GenBank_flag}

    def fetch_names(self):
        #generator function for the names.dmp
        with open(self.names_file, 'r') as names:
            for name in names:
                _name = name.strip('\t|\n').split('\t|\t')
                # the id of node associated with this name
                tax_id = int(_name[0])
                # name itself
                name_txt = _name[1]
                # the unique variant of this name if name not unique
                unique_name = _name[2]
                # (scientific name, common name, genbank common name, synonym, genbank synonym, 
                #  equivalent name, misnomer, misspelling, acronym, genbank acronym, 
                #  anamorph, genbank anamorph, teleomorph, includes, in-part, type material, authority, blast name)
                name_class = _name[3]
                ####
                yield {"node_id":tax_id, "synonym":name_txt, "label":name_class}

    def fetch_tar(self):
        if self.check_md5():
            logging.debug("NCBI_dump files are still up to date")
            return(tarfile.open(self.file_location))
        else:
            logging.debug("fetching new NCBI_dump files")
            self.cleanup_taxdump()
            self.download_tar()
            return(tarfile.open(self.file_location))

    def check_md5(self):
        #check if local tar is most current
        if os.path.isfile(self.file_location):
            with open(self.file_location,'rb') as file_to_check:
                data = file_to_check.read()
                local_checksum = hashlib.md5(data).hexdigest()
            with urllib.request.urlopen(URL+MD5_FILE) as checkfile:
                current_checksum = checkfile.readline().strip().split()[0].decode("utf-8")
            if current_checksum == local_checksum:
                return(True)
            else:
                return(False)
        else:
            return(False)

    def download_tar(self):
        #fetching the dump (zipped)
        urllib.request.urlretrieve(URL+TAR_FILE, self.file_location)
        #check if download was not corrupted,
        if not self.check_md5:
            self.download_tar()

    def cleanup_taxdump(self):
        #checking if old files need to be removed
        for the_file in os.listdir(FOLDER):
            file_path = os.path.join(FOLDER, the_file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logging.error(e)

######################
# main stuff
######################

def main(arguments):
    parser = OptionParser()
    #parser.add_option("-s", "--sam", action="append", type="string", dest="samfile", help="sam formated FILE to add in the dictionary", metavar="FILE")
    #parser.add_option("-d", "--db", type="string", dest="db_file", help="database FILE where the SQLite database is saved", metavar="FILE")
    (options, args) = parser.parse_args(arguments)
    logfile = CHANGELOG_PATH+"changelog"+time.strftime("%m-%y",time.gmtime(time.time()))
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', filename=logfile)

    foo = Dump_files()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
