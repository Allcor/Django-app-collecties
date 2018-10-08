<?php

// DataTables PHP library
include( "/home/naktdata/collectie/DataTablesEditor/DataTables.php" );

// Alias Editor classes so they are easy to use
use
    DataTables\Editor,
    DataTables\Editor\Field,
    DataTables\Editor\Format,
    DataTables\Editor\Mjoin,
    DataTables\Editor\Options,
    DataTables\Editor\Upload,
    DataTables\Editor\Validate;

// Collectie edit page
Editor::inst( $db, 'collectie_collection', 'nakt_id' )
    ->field(
        Field::inst( 'collectie_collection.pathogen_location' ),
        Field::inst( 'collectie_original_host.given_name' ),
        Field::inst( 'collectie_original_host.scientific_name' ),
        Field::inst( 'collectie_pathogen.given_name' ),
        Field::inst( 'collectie_pathogen.scientific_name' ),
        Field::inst( 'collectie_countrycode.name' ),
        Field::inst( 'collectie_collection.first_date' ),
        Field::inst( 'collectie_collection.confidential' ),
        Field::inst( 'collectie_collection.id_collectie' ),
        Field::inst( 'collectie_collection.id_storidge' ),
        Field::inst( 'collectie_collection.id_ins' ),
        Field::inst( 'collectie_collection.id_other' ),
        Field::inst( 'collectie_collection.pathogen_tree' ),
        Field::inst( 'collectie_collection.host_tree' ),
        Field::inst( 'collectie_collection.material' ),
        Field::inst( 'collectie_collection.tests_performed' )
    )
    ->leftJoin( 'collectie_original_host',      'collectie_original_host.id',                   '=',    'collectie_collection.host_id' )
    ->leftJoin( 'collectie_pathogen',           'collectie_pathogen.id',                        '=',    'collectie_collection.pathogen_id' )
    ->leftJoin( 'collectie_origin_pathogen',    'collectie_origin_pathogen.id',                 '=',    'collectie_collection.origin_id')
    ->leftJoin( 'collectie_countrycode',        'collectie_origin_pathogen.country_id',         '=',    'collectie_countrycode.id')
    ->process($_POST)
    ->json();