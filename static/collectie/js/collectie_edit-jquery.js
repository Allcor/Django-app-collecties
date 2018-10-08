$(document).ready(function () {
    var hiddenArray = [];
    $('.initiallyHidden').each(function () {
        hiddenArray.push($(this).index())
    });

    editor = new $.fn.dataTable.Editor( {
        ajax: {
            url: "/static/collectie/php/isolates_edit.php",
            dataSrc: 'data'
        },
        table: "#collectionTable",
        formOptions: {
                main:{
                    onReturn: function (e) {
                        var form_order = e.order();
                        var form_selected_i = 0;
                        for (i = 0; i < form_order.length; i++) {
                            var field_i = e.field(form_order[i]);
                            if (field_i.input()[0].id === document.activeElement.id) {
                                form_selected_i = i;
                            }
                        }
                        if (form_order[form_selected_i] === 'collectie_collection.id_ins') {
                            var ins = e.get('collectie_collection.id_ins');
                            if (ins.substr(0,5) === 'BAR-I'){
                                e.set('collectie_collection.id_ins','INS'+ins.substr(5));
                            }
                        }
                        var form_next_field = form_selected_i;
                        while ($.isNumeric(form_next_field)) {
                            form_next_field++;
                            if (form_next_field === form_order.length) {
                                form_next_field = 0
                            }
                            var putative_next_field = e.field(form_order[form_next_field]);
                            if (putative_next_field.input()[0].hidden === false) {
                                form_next_field = putative_next_field
                            }
                        }
                        form_next_field.focus();
                    },
                    onBlur: 'none'
                }
            },
        fields: [
            {
                label: "INS:",
                name: 'collectie_collection.id_ins',
                type: "text"
            },{
                label: "<i class='glyphicon glyphicon-asterisk'></i> Database:",
                name: 'collectie_collection.pathogen_location',
                type: "select2"
            },{
                label: "Naktuinbouw ID:",
                name: 'collectie_collection.id_collectie',
                type: "text"
            },{
                label: "<i class='glyphicon glyphicon-asterisk'></i> Pathogen:",
                name: "collectie_collection.pathogen_id",
                type: 'select2',
                "opts": {
                    placeholder: '',
                    allowClear: true
                }
            },{
                label: "isolaat:",
                name: 'collectie_collection.colonynumber',
                type: "text"
            },{
                label: "Host:",
                name: "collectie_collection.host_id",
                type: 'select2',
                "opts": {
                    placeholder: '',
                    allowClear: true
                }
            },{
                label: "Origin of sample:",
                name: "collectie_collection.origin_id",
                type: 'select2',
                "opts": {
                    placeholder: '',
                    allowClear: true
                }
            },{
                label: "Material:",
                name: 'collectie_collection.material',
                type: "select2",
                options: [
                    {label:"blad", value: "blad"},
                    {label:"plant", value: "plant"},
                    {label:"stengel", value: "stengel"},
                    {label:"water", value:"water"},
                    {label:"wortel", value: "wortel"},
                    {label:"zaad", value: "zaad"},
                    {label:"overig", value: "overig"}
                ],
                "opts": {
                    placeholder: '',
                    allowClear: true,
                    tags: true,
                    createTag: function (params) {
                        return {
                          id: params.term,
                          text: params.term,
                          newOption: true
                        }
                    },
                    templateResult: function (data) {
                        var $result = $("<span></span>");

                        $result.text(data.text);

                        if (data.newOption) {
                          $result.append(" <em>(new)</em>");
                        }

                        return $result;
                    }
                }
            },{
                label: "Observed symptoms:",
                name: 'collectie_collection.symptom',
                type: "text"
            },{
                label: "<i class='glyphicon glyphicon-asterisk'></i> Date of storage:",
                name: "collectie_collection.first_date",
                def: function () { return new Date(); },
                type: "datetime"
            },{
                label: "when this entry was created",
                name: 'collectie_collection.add_date',
                def: function () { return new Date(); },
                format:    'YYYY-M-DDTHH:mm:ss ',
                type: "datetime"
            },{
                label: "ID sample:",
                name: 'collectie_collection.id_storidge',
                type: "text"
            },{
                label: "ID origineel:",
                name: 'collectie_collection.id_original',
                type: "text"
            },{
                label: "Reference material:",
                name: "collectie_collection.confidential",
                type: "checkbox",
                options: [
                    {label: "yes", value:true}
                ],
                separator: '',
                unselectedValue: false
            },{
                label: "PCR test info:",
                name: "collectie_collection.test_pcr",
                type: "text"
            }, {
                label: "patholegy test info:",
                name: "collectie_collection.test_patholegy",
                type: "text"
            }, {
                label: "Serology test info:",
                name: "collectie_collection.test_serology",
                type: "text"
            }, {
                label: "sequence test info:",
                name: "collectie_collection.test_sequencing",
                type: "text"
            }, {
                label: "comment:",
                name: "collectie_collection.comment",
                type: "text"
            }
        ]
    });

    editor.dependent( 'collectie_collection.pathogen_location', "/edit/newids/");

    editor.on('initEdit', function (e, node, data) {
        editor.hide('collectie_collection.add_date');
    });
    editor.on('initCreate', function () {
        editor.hide('collectie_collection.add_date');
    });

    // this is for loading field information dynamically.
    editor.on('open', function ( e, mode, action ) {
        var tooltips = fieldInfo.discriptions;
        var placeholders = fieldInfo.placeholders;
        for (var key in tooltips) {
            //editor.field( key ).message( fieldInfo[key]);
            $( editor.node( key ) ).prop('title', tooltips[key])
        }
        for (var key in placeholders) {
            editor.field( key ).input().attr('placeholder', placeholders[key])
        }
    });

    // inline editing with double click
    $('#collectionTable').on( 'dblclick', 'tbody td.editable', function (e) {
        editor.inline( this, {
            buttons: {label: '&gt;', fn: function () { this.submit(); } }
        } );
    } );

    // updating the static values
    editor.on('postSubmit', function( e, json, data, action ) {
        var response = $.ajax({
            url: window.location.pathname + "update_static/",
            data: json,
            dataType: 'json',
            success: function () {
                header_select_update()
            }
        });
    });

    var table = $('#collectionTable').DataTable( {
        pageLength: 20,
        bStateSave: true,
        "ajax": {
            url: "/static/collectie/php/isolates_edit.php",
            dataSrc: 'data',
            type: "POST"
        },
        order: [[ 2, 'asc' ]],
        "deferRender": true,
        sDom: "rt<'row'<'col-sm-5'i><'col-sm-7'p>>",
        aoColumnDefs: [
            { "bVisible": false, "aTargets": hiddenArray},
            { type: 'natural', targets: 7}
        ],
        columns: [
            {
                data:'collectie_pathogen.given_name',
                editField: 'collectie_collection.pathogen_id',
                className: 'editable'
            },
            {
                data:'collectie_pathogen.scientific_name',
                editField: 'collectie_collection.pathogen_id',
                className: 'editable'
            },
            {
                data:'collectie_original_host.given_name',
                editField: 'collectie_collection.host_id',
                className: 'editable'
            },
            {
                data:'collectie_original_host.scientific_name',
                editField: 'collectie_collection.host_id',
                className: 'editable'
            },
            {
                data:'collectie_countrycode.name',
                editField: 'collectie_collection.origin_id',
                className: 'editable'
            },
            { data:'collectie_collection.material', className: 'editable' },
            { data:'collectie_collection.symptom', className: 'editable' },
            { data:'collectie_collection.id_collectie'},
            { data:'collectie_collection.id_storidge'},
            { data:'collectie_collection.id_ins'},
            { data:'collectie_collection.colonynumber', className: 'editable' },
            { data:'collectie_collection.first_date', className: 'editable' },
            { data:'collectie_collection.test_serology', className: 'editable' },
            { data:'collectie_collection.test_patholegy', className: 'editable' },
            { data:'collectie_collection.test_pcr', className: 'editable' },
            { data:'collectie_collection.test_sequencing', className: 'editable' },
            { data:'collectie_collection.comment', className: 'editable' },
            { data:'collectie_collection.id_other', className: 'noVis'},
            { data:'collectie_collection.pathogen_tree', className: 'noVis'},
            { data:'collectie_collection.host_tree', className: 'noVis'},
            { data:'collectie_collection.add_date', bSearchable: false}
        ],
        select: {
            style:      'os'
        },
        initComplete: function(){
            var api = this.api();

            var buttons1 = new $.fn.dataTable.Buttons(api, {
                buttons: [
                    {
                        extend:'copy',
                        text:'<i class="glyphicon glyphicon-copy"></i>',
                        titleAttr:"Copy table to clipboard."
                    },{
                        extend:'excel',
                        text:'<i class="glyphicon glyphicon-list-alt"></i>',
                        titleAttr:"Save table as .xlsx",
                        filename: function () {return getExportFilename();},
                        exportOptions: {
                            columns: ':visible'
                        }
                    },{
                        extend:'pdf',
                        text:'<i class="glyphicon glyphicon-picture"></i>',
                        titleAttr:"Save table as .pdf",
                        filename: function () {return getExportFilename();},
                        exportOptions: {
                            columns: ':visible'
                        }
                    },{
                        extend:'colvis',
                        text:'<i class="glyphicon glyphicon-eye-close"></i>',
                        titleAttr:"hide and show columns.",
                        columns: ':not(.noVis)'
                    }
                ],
                dom: {
                    container:{
                        className: 'dt-buttons input-group-btn'
                    },
                    button: {
                        tag: 'button',
                        className: 'dt-button btn btn-default'
                    },
                    buttonLiner: {
                        tag: null
                    }
                }
            });
            buttons1.container().appendTo( '#collectControlls' );

            var buttons2 = new $.fn.dataTable.Buttons(api, {
                buttons: [
                    {
                        extend: "create",
                        text:'<i class="glyphicon glyphicon-plus"></i>',
                        titleAttr:"Create new item",
                        editor: editor
                    },{
                        extend: "selected",
                        text: 'Duplicate',
                        titleAttr:"Create new, copying values from selected item",
                        action: function ( e, dt, node, config ) {
                            // Start in edit mode, and then change to create
                            var selected = table.rows( {selected: true} ).data()[0];
                            editor
                                .create( {
                                    title: 'Duplicate record',
                                    buttons: 'Create'
                                } )
                                .set('collectie_collection.id_ins',selected.collectie_collection.id_ins)
                                .set('collectie_collection.pathogen_id', selected.collectie_collection.pathogen_id)
                                .set('collectie_collection.pathogen_location', selected.collectie_collection.pathogen_location)
                                .set('collectie_collection.colonynumber', selected.collectie_collection.colonynumber)
                                .set('collectie_collection.host_id', selected.collectie_collection.host_id)
                                .set('collectie_collection.origin_id', selected.collectie_collection.origin_id)
                                .set('collectie_collection.material', selected.collectie_collection.material)
                                .set('collectie_collection.symptom', selected.collectie_collection.symptom)
                                .set('collectie_collection.first_date', selected.collectie_collection.first_date)
                                .set('collectie_collection.confidential', selected.collectie_collection.confidential)
                                .set('collectie_collection.test_pcr', selected.collectie_collection.test_pcr)
                                .set('collectie_collection.test_patholegy', selected.collectie_collection.test_patholegy)
                                .set('collectie_collection.test_serology', selected.collectie_collection.test_serology)
                                .set('collectie_collection.test_sequencing', selected.collectie_collection.test_sequencing)
                                .set('collectie_collection.comment', selected.collectie_collection.comment)
                        }
                    },{
                        extend: "edit",
                        text:'<i class="glyphicon glyphicon-pencil"></i>',
                        titleAttr:"Edit selected item",
                        editor: editor,
                        action: function (e, dt, node, config) {
                            //extending edit means something has to be selected
                            var select_rows = table.rows( { selected: true } );
                            var data = select_rows.data();
                            var collection_id = data["0"].collectie_collection.nakt_id;
                            window.location = window.location.protocol + "//" + window.location.host + "/" + collection_id + "/";
                        }
                    },{
                        extend: "remove",
                        text:'<i class="glyphicon glyphicon-trash"></i>',
                        titleAttr:"Delete selected item",
                        editor: editor
                    }
                ],
                dom: {
                    container: {
                        className: 'dt-buttons input-group-btn'
                    },
                    button: {
                        tag: 'button',
                        className: 'dt-button btn btn-default'
                    },
                    buttonLiner: {
                        tag: null
                    }
                }
            });
            buttons2.container().prependTo( '#collectControlls' );

            api.search($('#collectSearch').val()).draw();

            $('.dt-button').tooltip({
                placement: "bottom",
                container: "body"
            });

            // selected functionality
            // this function will be called by buttons with the header-select-btn class
            // needs to grab selected rows and send the id's
            function header_select_add(){
                id_list = $.map(table.rows( { selected: true } ).data(), function (item) {
                    return item.DT_RowId.split('_')[1]
                });
                header_select_ajax(id_list)
            }
            // header_select_add needs to be defined before show_header_select_btn is run
            show_header_select_btn(header_select_add);
        }
    });
    $('#collectSearch').keyup(function (e) {
        table.search(this.value).draw();
    });
});

//select2 text field losing focus after resize fix
$.fn.modal.Constructor.prototype.enforceFocus = $.noop;

var fieldInfo = null;
$.ajax({
    url: window.location.protocol + "//" + window.location.host + "/" + "field_info/",
    type: 'get',
    datatype: 'json',
    success: function (data) {
        fieldInfo = data;
    }
});

function getExportFilename() {
    var TodayDate = new Date();
    var d = TodayDate.getDate();
    var m = TodayDate.getMonth()+1;
    var y = TodayDate.getFullYear();
    var date_txt = y+'-'+m+'-'+d;
    var query_txt = $.trim($('#collectSearch').val()).replace(/ /g, '_');
    if (query_txt === "") {
        return 'collectie_' + date_txt;
    } else {
        return 'collectie_' + date_txt + '_' + query_txt;
    }
}