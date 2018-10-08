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

// log changes
function logChange ( $db, $action, $id, $values ) {
    $sess_handle = popen("/home/naktdata/manage.py get_user " . $_COOKIE["sessionid"], "r");
    $sess_id = fgets($sess_handle, 4096);
    pclose($sess_handle);
    $db->insert( 'collectie_changelog', array(
        'dtuser'   => $sess_id,
        'dtaction' => $action,
        'dtvalues' => json_encode( $values ),
        'dtrow'    => $id,
        'dtwhen'   => date('c')
    ) );
}

// Collectie edit page
Editor::inst( $db, 'collectie_collection', 'nakt_id' )
    ->field(
        // The host fields
        Field::inst( 'collectie_collection.nakt_id' ),
        Field::inst( 'collectie_collection.pathogen_location' )
            ->options( function() {
                global $db;
                $qText  = "SELECT DISTINCT pathogen_location AS label, pathogen_location AS value FROM collectie_collection ORDER BY label";
                return $db->sql($qText)->fetchAll();
            })
            ->validator( 'Validate::notEmpty' ),
        Field::inst( 'collectie_collection.host_id' )
            ->options( function() {
                global $db;
                $qText  = "SELECT DISTINCT CONCAT(collectie_original_host.scientific_name, ' - (', collectie_original_host.given_name, ')') AS label, collectie_original_host.id AS value ";
                $qText .= "FROM collectie_original_host ";
                $qText .= "WHERE is_choice=true ";
                $qText .= "ORDER BY label ";
                return $db->sql($qText)->fetchAll();
            } )
            ->setFormatter( 'Format::ifEmpty', null ),
        Field::inst( 'collectie_original_host.given_name' ),
        Field::inst( 'collectie_original_host.scientific_name' ),
        // The pathogen fields
        Field::inst( 'collectie_collection.pathogen_id' )
            ->options( function() {
                global $db;
                $qText  = "SELECT DISTINCT CONCAT(collectie_pathogen.scientific_name, ' - (', collectie_pathogen.given_name, ')') AS label, collectie_pathogen.id AS value ";
                $qText .= "FROM collectie_pathogen ";
                $qText .= "WHERE is_choice=true ";
                $qText .= "ORDER BY label ";
                return $db->sql($qText)->fetchAll();
            } )
            ->setFormatter( 'Format::ifEmpty', null )
            ->validator( 'Validate::notEmpty' ),
        Field::inst( 'collectie_pathogen.given_name' ),
        Field::inst( 'collectie_pathogen.scientific_name' ),
        // The origin field
        Field::inst( 'collectie_collection.origin_id' )
            ->options( function () {
                global $db;
                $qText  = "SELECT DISTINCT CONCAT(collectie_countrycode.name, ' - (', collectie_origin_pathogen.given_name, ')') AS label, collectie_origin_pathogen.id AS value ";
                $qText .= "FROM collectie_origin_pathogen ";
                $qText .= "INNER JOIN collectie_countrycode on collectie_origin_pathogen.country_id=collectie_countrycode.id ";
                $qText .= "WHERE is_choice=true ";
                $qText .= "ORDER BY label";
                return $db->sql($qText)->fetchAll();
            } )
            -> setFormatter( 'Format::ifEmpty', null )
            -> validator( 'Validate::dbValues', array(
                'table' => 'collectie_origin_pathogen',
                'field' => 'id',
                'valid' => array('')
            ) ),
        // other fields ...
        Field::inst( 'collectie_countrycode.name' ),
        Field::inst( 'collectie_collection.first_date' )
            ->validator( 'Validate::dateFormat', array(
                "format"  => Format::DATE_ISO_8601,
                "message" => "Please enter a date in the format yyyy-mm-dd"
            ) )
            ->validator( 'Validate::notEmpty' )
            ->setFormatter( 'Format::date_sql_to_format', Format::DATE_ISO_8601 )
            ->getFormatter( 'Format::date_format_to_sql', Format::DATE_ISO_8601 ),
        Field::inst( 'collectie_collection.id_collectie' )
            ->validator( 'Validate::unique' ),
        Field::inst( 'collectie_collection.id_storidge' )
            ->validator( 'Validate::unique' ),
        Field::inst( 'collectie_collection.colonynumber' ),
        Field::inst( 'collectie_collection.id_ins' ),
        Field::inst( 'collectie_collection.id_other' ),
        Field::inst( 'collectie_collection.id_original' ),
        Field::inst( 'collectie_collection.add_date' ),
        Field::inst( 'collectie_collection.confidential' ),
        Field::inst( 'collectie_collection.pathogen_tree' ),
        Field::inst( 'collectie_collection.host_tree' ),
        Field::inst( 'collectie_collection.symptom' ),
        Field::inst( 'collectie_collection.material' ),
        Field::inst( 'collectie_collection.comment' ),
        Field::inst( 'collectie_collection.test_pcr' ),
        Field::inst( 'collectie_collection.test_sequencing' ),
        Field::inst( 'collectie_collection.test_patholegy' ),
        Field::inst( 'collectie_collection.test_serology' )
    )
    // many-to-one joins
    ->leftJoin( 'collectie_original_host',      'collectie_original_host.id',                   '=',    'collectie_collection.host_id' )
    ->leftJoin( 'collectie_pathogen',           'collectie_pathogen.id',                        '=',    'collectie_collection.pathogen_id' )
    ->leftJoin( 'collectie_origin_pathogen',    'collectie_origin_pathogen.id',                 '=',    'collectie_collection.origin_id')
    ->leftJoin( 'collectie_countrycode',        'collectie_origin_pathogen.country_id',         '=',    'collectie_countrycode.id')
    // processing
    ->on( 'postCreate', function ( $editor, $id, $values ) {
        logChange( $editor->db(), 'create', $id, $values );
    } )
    ->on( 'postEdit', function ( $editor, $id, $values ) {
        logChange( $editor->db(), 'edit', $id, $values );
    } )
    ->on( 'postRemove', function ( $editor, $id, $values ) {
        logChange( $editor->db(), 'delete', $id, $values );
    } )
    //->debug( true )
    //->tryCatch( false )
    //->transaction( false )
    ->process($_POST)
    ->json();