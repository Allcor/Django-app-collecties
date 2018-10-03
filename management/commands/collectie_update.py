#!/usr/bin/python3

'''
Script to fetch data from collection (old acces)
    X:\O&O\Bacteriecollectie
    X:\O&O\ASSO en O-Datamap\Collecties
    
For now it takes a copy from /home/arlo/Desktop/collectie/Bacteriecode.csv but it should grab 
these accessions and put them in the database

21-6-2017
    made to be able to search the yielded names in the local NCBI_names table.
22-6-2017
    now yields dictionaries.
    no resolution in _get_names_lib if there is no exact match.
26-6-2017
    checking NBC-nr as identyfyer.
27-6-2017
    all sample dates are entered
3-7-2017
    now can add location of sample
'''


from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from naktdata.settings import BASE_DIR
from collectie.utils.bact_collectie_strip import Bactcollectie
from collectie.utils.schimmel_collectie_strip import Fungcollectie
from collectie.utils.virus_collectie_strip import Viralcollectie
from collectie.utils.isolaten_collectie_strip import Isolatecollectie
from collectie.utils.virus_weefsel_strip import Weefselcollectie
from collectie.utils.virus_greenhouse_strip import Kascollectie
from collectie.models import NCBI_nodes, Collection_id, Original_host, Origin_pathogen, CountryCode, Pathogen, Collection
from collectie.models import Bacteriecollectie, Schimmelcollectie, Viruscollectie, Isolatencollectie, VirusWeefsel, VirusKas

import sys, datetime, logging

class Command(BaseCommand):
    help = 'adds the bacteria collection to the database'

    def add_arguments(self, parser):
        #optional arguments
        parser.add_argument('--populate_raw',
                            action='store_true',
                            dest='crude',
                            default=False,
                            help='adds all the data to the raw data tables instead of the relational schema'
                            )
        parser.add_argument('--virus',
                            action='store_true',
                            dest='update_virus',
                            default=False,
                            help='only adds the data of the Virus collection instead of all collections'
                            )
        parser.add_argument('--bacteria',
                            action='store_true',
                            dest='update_bacteria',
                            default=False,
                            help='only adds the data of the Bacteria collection instead of all collections'
                            )
        parser.add_argument('--fungus',
                            action='store_true',
                            dest='update_fungus',
                            default=False,
                            help='only adds the data of the Fungal collection instead of all collections'
                            )
        parser.add_argument('--weefsel',
                            action='store_true',
                            dest='update_weefsel',
                            default=False,
                            help='only adds the data of the Weefselkweek virus collection instead of all collections'
                            )
        parser.add_argument('--kas',
                            action='store_true',
                            dest='update_kas',
                            default=False,
                            help='only adds the data of the Greenhouse virus collection instead of all collections'
                            )
        #parser.add_argument('--isolaten',
        #                    action='store_true',
        #                    dest='update_isolaten',
        #                    default=False,
        #                    help='only adds the data of the Fungal collection instead of all collections'
        #                    )


    ##### db handeling #####

    def _add_accession_id(self,codes,accession):
        """
           takes all codes/id's of a Collection instance and adds them to this accession in the database
        """
        for key,value in codes.items():
            if isinstance(value, list):
                for code in value:
                    if not accession.collection_id_set.filter(code_txt=code, code_class=key).exists():
                        id = accession.collection_id_set.create(code_txt=code, code_class=key)
                        id.save()
            else:
                if not accession.collection_id_set.filter(code_class=key).exists():
                    id = accession.collection_id_set.create(code_txt=value, code_class=key)
                    id.save()

    def _add_accession_comment(self,comments,accession):
        """
        adding information to the accession as comments.

        :param comments: a library with label, comment combinations.
        :param accession: the Collection item to add the comments to.
        :return: saved changes to the accession object.
        """
        for key,value in comments.items():
            if not accession.collection_comment_set.filter(comment_txt=value).exists():
                accession.collection_comment_set.create(comment_label=key,comment_txt=value)

    def _add_sample(self,samples,accession):
        for item in samples:
            date = timezone.make_aware(samples[item],timezone.get_current_timezone())
            if not accession.sample_set.filter(date=date).exists():
                accession.sample_set.create(date=date,action=item)

    def _add_pathogen(self,pathogenid,accession,original_value):
        if Pathogen.objects.filter(given_name=original_value).exists():
            accession.pathogen = Pathogen.objects.get(given_name=original_value)
            accession.save()
        else:
            tax_id = NCBI_nodes.objects.get(tax_id=pathogenid)
            accession.pathogen = tax_id.pathogen_set.create(given_name=original_value)
            accession.save()

    def _add_origninal_host(self,hostid,accession,original_value):
        if Original_host.objects.filter(given_name=original_value).exists():
            accession.host = Original_host.objects.get(given_name=original_value)
            accession.save()
        else:
            tax_id = NCBI_nodes.objects.get(tax_id=hostid)
            accession.host = tax_id.original_host_set.create(given_name=original_value)
            accession.save()
    
    def _add_location(self,country_id,accession,original_value):
        if Origin_pathogen.objects.filter(given_name=original_value).exists():
            accession.origin = Origin_pathogen.objects.get(given_name=original_value)
            accession.save()
        else:
            country = CountryCode.objects.get(id=country_id)
            accession.origin = country.origin_pathogen_set.create(given_name=original_value)
            accession.save()

    def _add_vertification(self,tests,accession):
        #if accession.tests:
        #    vertification = accession.tests
        #else:
        #    vertification = Verification.objects.create()
        #    accession.tests = vertification
        #    accession.save()
        other_list = []
        for key,value in tests.items():
            if key == 'pcr':
                if accession.test_pcr != value:
                    accession.test_pcr = value
            elif key == 'serologie':
                if accession.test_serology != value:
                    accession.test_serology = value
            elif key == 'pathogeniteit':
                if accession.test_patholegy != value:
                    accession.test_patholegy = value
            elif key == 'sequencing':
                if accession.test_sequencing != value:
                    accession.test_sequencing = value
            else:
                other_list.append(value)
        other_txt = ', '.join(other_list)
        if accession.comment != other_txt:
            accession.comment = other_txt
        accession.save()

    def _add_symptomen(self, symptom, accession):
        if accession.symptom != symptom:
            accession.symptom = symptom
            accession.save()

    def _add_material(self, material, accession):
        if accession.material != material:
            accession.material = material
            accession.save()

    def _add_colonynumber(self, number, accession):
        if accession.colonynumber != number:
            accession.colonynumber = number
            accession.save()

    def _add_employee(self, name, accession):
        try: #needed because not everyone has logged in yet.
            user_obj = User.objects.get(username__iexact=name)
            if accession.add_user != user_obj:
                accession.add_user = user_obj
                accession.save()
        except User.DoesNotExist:
            if name in self.missing_users:
                self.missing_users[name] += 1
            else:
                self.missing_users[name] = 1

    ##### main function #####

    def _virus_compare(self):
        """
            Yields data from Virus collection and has them added to postgres with appropriate relations
        """

        def add_virus(entry):
            # create new collection object
            accession = Collection(pathogen_location='Virus_cryo')
            accession.save()
            # add pathogen
            self._add_pathogen(entry['pathogeen_id'], accession, entry['pathogeen_txt'])
            # create ID
            accession.collection_id_set.create(code_txt=entry['nvc'], code_class='NVC')
            # add other id's
            if entry['codes'] != {}:
                self._add_accession_id(entry['codes'], accession)
            # add host plant
            if 'gewas_id' in entry:
                self._add_origninal_host(entry['gewas_id'], accession, entry['gewas_txt'])
            # create sample object
            if entry['dates'] != {}:
                self._add_sample(entry['dates'], accession)
            # add vertification tests
            if entry['tests'] != {}:
                self._add_vertification(entry['tests'], accession)
            # add comments
            if entry['comments'] != {}:
                self._add_accession_comment(entry['comments'], accession)
            # add origin
            if 'origin_id' in entry:
                self._add_location(entry['origin_id'], accession, entry['origin_txt'])
            # add material
            if 'materiaal' in entry:
                self._add_material(entry['materiaal'], accession)
            return accession

        def fix_virus(entry, accession):
            # check for new id's
            if accession.collection_id_set.count() != (len(entry['codes']) + 1):  # +1 for the NBC
                self._add_accession_id(entry['codes'], accession)
                logging.info("updated " + str(accession.nakt_id) + " id's.")
            # check for new samples
            if accession.sample_set.count() != len(entry['dates']) and entry['dates'] != {}:
                self._add_sample(entry['dates'], accession)
                logging.info("updated " + str(accession.nakt_id) + " samples.")
            # check new host
            if not accession.host:
                if 'gewas_id' in entry:
                    self._add_origninal_host(entry['gewas_id'], accession, entry['gewas_txt'])
                    logging.info("updated " + str(accession.nakt_id) + " host species.")
            # check new tests
            if entry['tests'] != {}:
                self._add_vertification(entry['tests'], accession)
                logging.info("updated " + str(accession.nakt_id) + " verification tests")
            # add comments
            if entry['comments'] != {}:
                self._add_accession_comment(entry['comments'], accession)
                logging.info("updated " + str(accession.nakt_id) + " comments")
            # check new origin
            if not hasattr(accession, 'origin_pathogen'):
                if 'origin_id' in entry:
                    self._add_location(entry['origin_id'], accession, entry['origin_txt'])
                    logging.info("updated " + str(accession.nakt_id) + " origin.")
            #check material
            if 'materiaal' in entry:
                self._add_material(entry['materiaal'],accession)
            return accession

        virus = Viralcollectie()
        for entry in virus.strip_accessions():
            #check if the eccession exists
            if len(entry['nvc'].split()) > 2:
                nvc = '-'.join(entry['nvc'].split('-')[:2])+'-'
                accessions = Collection_id.objects.filter(code_txt__contains=nvc)
            else:
                accessions = Collection_id.objects.filter(code_txt=entry['nvc'])
            if accessions.exists():
                if entry['pathogeen_txt'] in [x.nakt_id.pathogen.given_name for x in accessions]:
                    '''
                    If the lookup table has been changed things might go wrong. This is part of finding these conflicts. 
                    '''
                    try:
                        _accession = accessions.get(nakt_id__pathogen__taxon_id=entry['pathogeen_id']).nakt_id
                    except Collection_id.DoesNotExist:
                        print("id of saved pathogen_txt ("+ entry['pathogeen_txt'] +
                              ") different of given. saved:"+
                              str(Pathogen.objects.get(given_name=entry['pathogeen_txt']).taxon_id)+
                              ", given:"+str(entry['pathogeen_id']))
                        print("using saved value,")
                        _accession = accessions.get(nakt_id__pathogen__given_name=entry['pathogeen_txt']).nakt_id
                    except Collection_id.MultipleObjectsReturned:
                        print('doeble NVC id present')
                        print(accessions.filter(nakt_id__pathogen__taxon_id=entry['pathogeen_id']))
                        quit()
                    accession = fix_virus(entry, _accession)
                else:
                    print("pathogen of saved isolate (" + entry['nvc'] +
                          ") different of given. saved:" +
                          str(accessions.first().pathogen.given_name) +
                          ", given:" + str(entry['pathogeen_txt']))
                    #accession = add_virus(entry)
            else:
                accession = add_virus(entry)
            if self.update_static:
                accession.update_static()



    def _bact_compare(self):
        """
        Yields data from Bacteria file and has them added to postgres with appropriate relations
        """

        def add_bact(entry):
            # create new collection object
            accession = Collection(pathogen_location='Bacteria_cryo')
            accession.save()
            # create main ID
            accession.collection_id_set.create(code_txt=entry['nbc'], code_class='NBC')
            # add pathogen
            self._add_pathogen(entry['bact_id'], accession, entry['bact_txt'])
            # add other id's
            if entry['codes'] != {}:
                self._add_accession_id(entry['codes'], accession)
            # add host plant data
            if 'gewas_id' in entry:
                self._add_origninal_host(entry['gewas_id'], accession, entry['gewas_txt'])
            # create sample object
            if entry['dates'] != {}:
                self._add_sample(entry['dates'], accession)
            # add origin
            if 'herkomst_id' in entry:
                self._add_location(entry['herkomst_id'], accession, entry['herkomst_txt'])
            # add vertification tests
            if entry['tests'] != {}:
                self._add_vertification(entry['tests'], accession)
            # add material
            if 'materiaal' in entry:
                self._add_symptomen(entry['materiaal'], accession)
            # add isolaatnummer
            if 'isolaatnummer' in entry:
                self._add_colonynumber(entry['isolaatnummer'], accession)
            # add dienstverlening
            if entry['dienstverlening']:
                accession.confidential = True
                accession.save()
            # add comments
            if entry['comments'] != {}:
                self._add_accession_comment(entry['comments'], accession)
            # add employee
            if 'medewerker' in entry:
                self._add_employee(entry['medewerker'], accession)
            logging.info("added accession " + str(accession.nakt_id) + " with nbc " + str(entry['nbc']))
            return accession

        def fix_bact(entry,accession):
            # check for new id's
            if accession.collection_id_set.count() != (len(entry['codes']) + 1):  # +1 for the NBC
                self._add_accession_id(entry['codes'], accession)
                logging.info("updated " + str(accession.nakt_id) + " id's.")
            # check for new samples
            if accession.sample_set.count() != len(entry['dates']) and entry['dates'] != {}:
                self._add_sample(entry['dates'], accession)
                logging.info("updated " + str(accession.nakt_id) + " samples.")
            # check new tests
            if entry['tests'] != {}:
                self._add_vertification(entry['tests'], accession)
                logging.info("updated " + str(accession.nakt_id) + " verification tests")
            # add comments
            if entry['comments'] != {}:
                self._add_accession_comment(entry['comments'], accession)
                logging.info("updated " + str(accession.nakt_id) + " comments")
            # check new host
            if not accession.host:
                if 'gewas_id' in entry:
                    self._add_origninal_host(entry['gewas_id'], accession, entry['gewas_txt'])
                    logging.info("updated " + str(accession.nakt_id) + " host species.")
            # check new origin
            if not hasattr(accession, 'origin_pathogen'):
                if 'herkomst_id' in entry:
                    self._add_location(entry['herkomst_id'], accession, entry['herkomst_txt'])
                    logging.info("updated " + str(accession.nakt_id) + " origin.")
            # check confidential
            if entry['dienstverlening']:
                accession.confidential = True
                accession.save()
            #check material
            if 'materiaal' in entry:
                self._add_symptomen(entry['materiaal'],accession)
            # add isolaatnummer
            if 'isolaatnummer' in entry:
                self._add_colonynumber(entry['isolaatnummer'], accession)
            # add employee
            if 'medewerker' in entry:
                self._add_employee(entry['medewerker'], accession)
            return accession

        bact = Bactcollectie()
        for entry in bact.strip_accessions():
            # check if nbc is in database
            accessions = Collection_id.objects.filter(code_txt=entry['nbc'])
            if accessions.exists():
                if entry['bact_txt'] in [x.nakt_id.pathogen.given_name for x in accessions]:
                    '''
                    If the lookup table has been changed things might go wrong. This is part of finding these errors. 
                    '''
                    try:
                        _accession = accessions.get(nakt_id__pathogen__taxon_id=entry['bact_id']).nakt_id
                    except Collection_id.DoesNotExist:
                        print("id of saved pathogen_txt ("+ entry['bact_id'] +") different of given. saved:"+str(Pathogen.objects.get(given_name=entry['bact_txt']).taxon_id)+", given:"+str(entry['bact_id']))
                        print("using saved value,")
                        _accession = accessions.get(nakt_id__pathogen__given_name=entry['bact_txt']).nakt_id
                    except Collection_id.MultipleObjectsReturned:
                        print('double NBC id present')
                        print(accessions.filter(nakt_id__pathogen__taxon_id=entry['bact_id']))
                        quit()
                    # to check if pathogen_txt alreaddy exist with a different id.
                    accession = fix_bact(entry, _accession)
                else:
                    print("pathogen of saved isolate (" + entry['nbc'] + ") different of given. saved:" + str(accessions.first().pathogen.given_name) + ", given:" + str(
                        entry['bact_txt']))
                    #accession = add_bact(entry)
            else:
                accession = add_bact(entry)
            if self.update_static:
                accession.update_static()

    def _fungal_compare(self):
        """
        Yields data from Fungal collection file and has them added to postgres with appropriate relations
        """

        def add_fung(entry):
            # create new collection object
            accession = Collection(pathogen_location='Fungi_cryo')
            accession.save()
            # create main ID
            accession.collection_id_set.create(code_txt=entry['nfc'], code_class='NFC')
            # add pathogen
            self._add_pathogen(entry['pathogeen_id'], accession, entry['pathogeen_txt'])
            # add other id's
            if entry['codes'] != {}:
                self._add_accession_id(entry['codes'], accession)
            # add host plant
            if 'gewas_id' in entry:
                self._add_origninal_host(entry['gewas_id'], accession, entry['gewas_txt'])
            # create sample object
            if entry['dates'] != {}:
                self._add_sample(entry['dates'], accession)
            # add comments
            if entry['comments'] != {}:
                self._add_accession_comment(entry['comments'], accession)
            # add origin
            if 'origin_id' in entry:
                self._add_location(entry['origin_id'], accession, entry['origin_txt'])
            #check material
            if 'materiaal' in entry:
                self._add_material(entry['materiaal'],accession)
            #check material
            if 'symptomen' in entry:
                self._add_symptomen(entry['symptomen'],accession)
            # check confidential
            if entry['dienstverlening']:
                accession.confidential = True
                accession.save()
            # add vertification tests
            if entry['tests'] != {}:
                self._add_vertification(entry['tests'], accession)
            # add employee
            if 'medewerker' in entry:
                self._add_employee(entry['medewerker'], accession)
            return accession

        def fix_fung(entry,accession):
            # check for new id's
            if accession.collection_id_set.count() != (len(entry['codes']) + 1):  # +1 for the NFC
                self._add_accession_id(entry['codes'], accession)
                logging.info("updated " + str(accession.nakt_id) + " id's.")
            # check new host
            if not accession.host:
                if 'gewas_id' in entry:
                    self._add_origninal_host(entry['gewas_id'], accession, entry['gewas_txt'])
                    logging.info("updated " + str(accession.nakt_id) + " host species.")
            # check for new samples
            if accession.sample_set.count() != len(entry['dates']) and entry['dates'] != {}:
                self._add_sample(entry['dates'], accession)
                logging.info("updated " + str(accession.nakt_id) + " samples.")
            # check new origin
            if not hasattr(accession, 'origin_pathogen'):
                if 'origin_id' in entry:
                    self._add_location(entry['origin_id'], accession, entry['origin_txt'])
                    logging.info("updated " + str(accession.nakt_id) + " origin.")
            # add comments
            if entry['comments'] != {}:
                self._add_accession_comment(entry['comments'], accession)
                logging.info("updated " + str(accession.nakt_id) + " comments")
            # check new tests
            if entry['tests'] != {}:
                self._add_vertification(entry['tests'], accession)
                logging.info("updated " + str(accession.nakt_id) + " verification tests")
            #check material
            if 'materiaal' in entry:
                self._add_material(entry['materiaal'],accession)
            #check symptomen
            if 'symptomen' in entry:
                self._add_symptomen(entry['symptomen'],accession)
            # check confidential
            if entry['dienstverlening']:
                accession.confidential = True
                accession.save()
            # add employee
            if 'medewerker' in entry:
                self._add_employee(entry['medewerker'], accession)
            return accession

        fungus = Fungcollectie()
        for entry in fungus.strip_accessions():
            accessions = Collection_id.objects.filter(code_txt=entry['nfc'])
            if accessions.exists():
                '''
                If the lookup table has been changed things might go wrong. This is part of finding these errors.
                '''
                if entry['pathogeen_txt'] in [x.nakt_id.pathogen.given_name for x in accessions]:
                    try:
                        _accession = accessions.get(nakt_id__pathogen__taxon_id=entry['pathogeen_id']).nakt_id
                    except Collection_id.DoesNotExist:
                        print("id of saved pathogen_txt ("+ entry['pathogeen_txt'] +
                              ") different of given. saved:" +
                              str(Pathogen.objects.get(given_name=entry['pathogeen_txt']).taxon_id)+
                              ", given:"+str(entry['pathogeen_id']))
                        print("using saved value,")
                        _accession = accessions.get(nakt_id__pathogen__given_name=entry['pathogeen_txt']).nakt_id
                    except Collection_id.MultipleObjectsReturned:
                        print('double NFC id present')
                        print(accessions.filter(nakt_id__pathogen__taxon_id=entry['pathogeen_id']))
                        quit()
                    accession = fix_fung(entry, _accession)
                else:
                    print("pathogen of saved isolate (" + entry['nfc'] +
                          ") different of given. saved:" +
                          str(accessions.first().pathogen.given_name) +
                          ", given:" + str(entry['pathogeen_txt']))
                    #accession = add_fung(entry)
            else:
                add_fung(entry)
            if self.update_static:
                accession.update_static()

    def _weefsel_compare(self):
        def add_weefsel(entry):
            # create new collection object
            accession = Collection(pathogen_location='Virus_tissue_culture')
            accession.save()
            # create main ID
            accession.collection_id_set.create(code_txt=entry['nvc'], code_class='NVC')
            # add other id's
            if entry['codes'] != {}:
                self._add_accession_id(entry['codes'], accession)
            # add pathogen
            self._add_pathogen(entry['pathogeen_id'], accession, entry['pathogeen_txt'])
            # add host plant data
            if 'gewas_id' in entry:
                self._add_origninal_host(entry['gewas_id'], accession, entry['gewas_txt'])
            # add origin
            if 'origin_id' in entry:
                self._add_location(entry['origin_id'], accession, entry['origin_txt'])
            # create sample object
            if entry['dates'] != {}:
                self._add_sample(entry['dates'], accession)
            # add comments
            if entry['comments'] != {}:
                self._add_accession_comment(entry['comments'], accession)
            return accession

        def fix_weefsel(entry, accession):
            # check for new id's
            if accession.collection_id_set.count() != (len(entry['codes']) + 1):  # +1 for the NVC
                self._add_accession_id(entry['codes'], accession)
                logging.info("updated " + str(accession.nakt_id) + " id's.")
            # check new host
            if not accession.host:
                if 'gewas_id' in entry:
                    self._add_origninal_host(entry['gewas_id'], accession, entry['gewas_txt'])
                    logging.info("updated " + str(accession.nakt_id) + " host species.")
            # check new origin
            if not hasattr(accession, 'origin_pathogen'):
                if 'origin_id' in entry:
                    self._add_location(entry['origin_id'], accession, entry['origin_txt'])
                    logging.info("updated " + str(accession.nakt_id) + " origin.")
            # check for new samples
            if accession.sample_set.count() != len(entry['dates']) and entry['dates'] != {}:
                self._add_sample(entry['dates'], accession)
                logging.info("updated " + str(accession.nakt_id) + " samples.")
            # add comments
            if entry['comments'] != {}:
                self._add_accession_comment(entry['comments'], accession)
                logging.info("updated " + str(accession.nakt_id) + " comments")
            return accession

        virus = Weefselcollectie()
        for entry in virus.strip_accessions():
            #check if the eccession exists
            if len(entry['nvc'].split()) > 2:
                nvc = '-'.join(entry['nvc'].split('-')[:2])+'-'
                accessions = Collection_id.objects.filter(code_txt__contains=nvc)
            else:
                accessions = Collection_id.objects.filter(code_txt=entry['nvc'])
            if accessions.exists():
                '''
                If the lookup table has been changed things might go wrong. This is part of finding these conflicts. 
                '''
                if entry['pathogeen_txt'] in [x.nakt_id.pathogen.given_name for x in accessions]:
                    try:
                        _accession = accessions.get(nakt_id__pathogen__taxon_id=entry['pathogeen_id']).nakt_id
                    except Collection_id.DoesNotExist:
                        print("id of saved pathogen_txt ("+ entry['pathogeen_txt'] +
                              ") different of given. saved:"+
                              str(Pathogen.objects.get(given_name=entry['pathogeen_txt']).taxon_id)+
                              ", given:"+str(entry['pathogeen_id']))
                        print("using saved value,")
                        _accession = accessions.get(nakt_id__pathogen__given_name=entry['pathogeen_txt']).nakt_id
                    except Collection_id.MultipleObjectsReturned:
                        print('doeble NVC id present')
                        print(accessions.filter(nakt_id__pathogen__taxon_id=entry['pathogeen_id']))
                        quit()
                    accession = fix_weefsel(entry, _accession)
                else:
                    print("pathogen of saved isolate (" + entry['nvc'] +
                          ") different of given. saved:" +
                          str(accessions.first().pathogen.given_name) +
                          ", given:" + str(entry['pathogeen_txt']))
                    #add_greenhouse(entry)
            else:
                add_weefsel(entry)
            if self.update_static:
                accession.update_static()


    def _greenhouse_compare(self):
        def add_greenhouse(entry):
            # create new collection object
            accession = Collection(pathogen_location='Virus_greenhouse')
            accession.save()
            # add pathogen
            self._add_pathogen(entry['pathogeen_id'], accession, entry['pathogeen_txt'])
            # create main ID
            accession.collection_id_set.create(code_txt=entry['nvc'], code_class='NVC')
            # add other id's
            if entry['codes'] != {}:
                self._add_accession_id(entry['codes'], accession)
            # add comments
            if entry['comments'] != {}:
                self._add_accession_comment(entry['comments'], accession)
            # create sample object
            if entry['dates'] != {}:
                self._add_sample(entry['dates'], accession)
            # add host plant
            if 'gewas_id' in entry:
                self._add_origninal_host(entry['gewas_id'], accession, entry['gewas_txt'])
            return accession

        def fix_greenhouse(entry, accession):
            # check for new id's
            if accession.collection_id_set.count() != (len(entry['codes']) + 1):  # +1 for the NVC
                self._add_accession_id(entry['codes'], accession)
                logging.info("updated " + str(accession.nakt_id) + " id's.")
            # add comments
            if entry['comments'] != {}:
                self._add_accession_comment(entry['comments'], accession)
                logging.info("updated " + str(accession.nakt_id) + " comments")
            # check for new samples
            if accession.sample_set.count() != len(entry['dates']) and entry['dates'] != {}:
                self._add_sample(entry['dates'], accession)
                logging.info("updated " + str(accession.nakt_id) + " samples.")
            # check new host
            if not accession.host:
                if 'gewas_id' in entry:
                    self._add_origninal_host(entry['gewas_id'], accession, entry['gewas_txt'])
                    logging.info("updated " + str(accession.nakt_id) + " host species.")
            return accession

        virus = Kascollectie()
        for entry in virus.strip_accessions():
            #check if the eccession exists
            if len(entry['nvc'].split()) > 2:
                nvc = '-'.join(entry['nvc'].split('-')[:2])+'-'
                accessions = Collection_id.objects.filter(code_txt__contains=nvc)
            else:
                accessions = Collection_id.objects.filter(code_txt=entry['nvc'])
            if accessions.exists():
                '''
                If the lookup table has been changed things might go wrong. This is part of finding these conflicts. 
                '''
                if entry['pathogeen_txt'] in [x.nakt_id.pathogen.given_name for x in accessions]:
                    try:
                        _accession = accessions.get(nakt_id__pathogen__taxon_id=entry['pathogeen_id']).nakt_id
                    except Collection_id.DoesNotExist:
                        print("id of saved pathogen_txt ("+ entry['pathogeen_txt'] +
                              ") different of given. saved:"+
                              str(Pathogen.objects.get(given_name=entry['pathogeen_txt']).taxon_id)+
                              ", given:"+str(entry['pathogeen_id']))
                        print("using saved value,")
                        _accession = accessions.get(nakt_id__pathogen__given_name=entry['pathogeen_txt']).nakt_id
                    except Collection_id.MultipleObjectsReturned:
                        print('doeble NVC id present')
                        print(accessions.filter(nakt_id__pathogen__taxon_id=entry['pathogeen_id']))
                        quit()
                    accession = fix_greenhouse(entry, _accession)
                else:
                    print("pathogen of saved isolate (" + entry['nvc'] +
                          ") different of given. saved:" +
                          str(', '.join([x.nakt_id.pathogen.given_name for x in accessions])) +
                          ", given:" + str(entry['pathogeen_txt']))
                    #add_greenhouse(entry)
            else:
                add_greenhouse(entry)
            if self.update_static:
                accession.update_static()


    def _Isolate_compare(self):
        """
        Yields data from Isolate collection file and has them added to postgres with appropriate relations
        """
        def add_isol(entry):
            # create new collection object
            accession = Collection(pathogen_location='Resistance')
            accession.save()
            # create main ID
            accession.collection_id_set.create(code_txt=entry['nic'], code_class='NRC')
            # add pathogen
            self._add_pathogen(entry['pathogeen_id'], accession, entry['pathogeen_txt'])
            # add host plant
            if 'gewas_id' in entry:
                self._add_origninal_host(entry['gewas_id'], accession, entry['gewas_txt'])
            # create sample object
            if entry['dates'] != []:
                self._add_sample(entry['dates'], accession)
            # add origin
            if 'origin_id' in entry:
                self._add_location(entry['origin_id'], accession, entry['origin_txt'])
            return accession

        def fix_isol(entry,accession):
            # check new host
            if not accession.host:
                if 'gewas_id' in entry:
                    self._add_origninal_host(entry['gewas_id'], accession, entry['gewas_txt'])
                    logging.info("updated " + str(accession.nakt_id) + " host species.")
            # check for new samples
            if accession.sample_set.count() != len(entry['dates']) and entry['dates'] != {}:
                self._add_sample(entry['dates'], accession)
                logging.info("updated " + str(accession.nakt_id) + " samples.")
            # check new origin
            if not hasattr(accession, 'origin_pathogen'):
                if 'origin_id' in entry:
                    self._add_location(entry['origin_id'], accession, entry['origin_txt'])
                    logging.info("updated " + str(accession.nakt_id) + " origin.")
            return accession

        isolaten = Isolatecollectie()
        for entry in isolaten.strip_accessions():
            accessions = Collection_id.objects.filter(code_txt=entry['nic'])
            if accessions.exists():
                if entry['pathogeen_txt'] in [x.nakt_id.pathogen.given_name for x in accessions]:
                    # to check if pathogen_txt alreaddy exist with a different id.
                    accession = accessions.get(nakt_id__pathogen__taxon_id=entry['pathogeen_id']).nakt_id
                    fix_isol(entry, accession)
                else:
                    add_isol(entry)
            else:
                add_isol(entry)


    def _populate_crude_bact(self):
        """
            add all fields of the bacteriacollection file in unchanged form
        """
        # want to pass dictionary with everything to add, made option pre_process for this.
        bact = Bactcollectie()
        for entry in bact.strip_accessions(pre_process=False):
            if not Bacteriecollectie.objects.filter(nbc_nummer=entry['nbc_nummer']).exists():
                b = Bacteriecollectie(**entry)
                b.save()

    def _populate_crude_fungal(self):
        """
            add all fields of the fungalcollection file in unchanged form
        """
        fungus = Fungcollectie()
        for entry in fungus.strip_accessions(pre_process=False):
            if not Schimmelcollectie.objects.filter(autonummer=entry['autonummer']).exists():
                s = Schimmelcollectie(**entry)
                s.save()

    def _populate_crude_virus(self):
        """
            add all fields of the viralcollection file in unchanged form
        """
        virus = Viralcollectie()
        for entry in virus.strip_accessions(pre_process=False):
            if not Viruscollectie.objects.filter(monsternr=entry['monsternr']).exists():
                v = Viruscollectie(**entry)
                v.save()

    def _populate_crude_isolaten(self):
        """
            add all fields of the isolatencollection file in unchanged form
        """
        isolaten = Isolatecollectie()
        for entry in isolaten.strip_accessions(pre_process=False):
            if not Isolatencollectie.objects.filter(monsternummer=entry['monsternummer']).exists():
                i = Isolatencollectie(**entry)
                i.save()

    def _populate_crude_weefsel(self):
        """
            add all fields of the weefselkweek file in unchanged form
        """
        weefsel = Weefselcollectie()
        for entry in weefsel.strip_accessions(pre_process=False):
            if not VirusWeefsel.objects.filter(monsternr=entry['monsternr']).exists():
                v = VirusWeefsel(**entry)
                v.save()

    def _populate_crude_greenhouse(self):
        """
            add all fields of the virus_greenhouse file in unchanged form
        """
        greenhouse = Kascollectie()
        for entry in greenhouse.strip_accessions(pre_process=False):
            if not VirusKas.objects.filter(autonumber=entry['autonumber']).exists():
                v = VirusKas(**entry)
                v.save()

    def handle(self, *args, **options):
        logging.basicConfig(filename=BASE_DIR+'/logs/bact_collectie.log',level=logging.DEBUG, filemode='a+')
        self.missing_users = {}
        self.update_static = True
        if options['crude']:
            print("checking crude data collection")
            self._populate_crude_bact()
            self._populate_crude_fungal()
            self._populate_crude_virus()
            #self._populate_crude_isolaten()
            self._populate_crude_weefsel()
            self._populate_crude_greenhouse()
        elif options['update_virus']:
            print("checking Virus_cryo collection")
            self._virus_compare()
        elif options['update_bacteria']:
            print("checking Bacteria_cryo collection")
            self._bact_compare()
        elif options['update_fungus']: #'--fungus'
            print("checking Fungal_cryo collection")
            self._fungal_compare()
        #elif options['update_isolaten']:
        #    self._Isolate_compare()
        elif options['update_weefsel']:
            print("checking Virus_kweek collection")
            self._weefsel_compare()
        elif options['update_kas']:
            print("checking Virus_kas collection")
            self._greenhouse_compare()
        '''else:
            print("checking Bacteria collection")
            self._populate_crude_bact()
            self._bact_compare()
            print("checking Virus collection")
            self._populate_crude_virus()
            self._virus_compare()
            self._populate_crude_weefsel()
            self._weefsel_compare()
            self._populate_crude_greenhouse()
            self._greenhouse_compare()
            print("checking Fungal collection")
            self._populate_crude_fungal()
            self._fungal_compare()
            #print("checking Isolate collection")
            #self._Isolate_compare()
        '''
        # disabled default, loading samples from files should not be used anymore now new entries are done with site
        if self.missing_users != {}:
            print("could not find users: "+ ', '.join([x[0]+' x'+str(x[1]) for x in self.missing_users.items()]))
