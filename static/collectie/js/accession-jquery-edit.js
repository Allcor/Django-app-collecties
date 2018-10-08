$(document).ready(function () {
    var table1 = $('#oldcrap').DataTable( {
        paging: false,
        initComplete: function(){
            var api = this.api();

            new $.fn.dataTable.Buttons(api, {
                buttons: [ 'copy', 'excel', 'pdf' ]
            });
            api.buttons().container().appendTo( '#' + api.table().container().id + ' .col-sm-6:eq(0)' );
        }
    } );

    //****
    //
    // the accession's info table
    //
    //****

    var info_editor = new $.fn.dataTable.Editor( {
        ajax: {
            url:window.location.pathname + "info/"
        },
        table: "#infoTable",
        formOptions: {
                main: {
                    focus: null
                }
            },
        fields: [
            {
                // needs to stay on top
                label: "Isolate property:",
                name: 'property',
                type: "select2"
            },{
                label: "isolated pathogen:",
                name: "pathogen",
                type: "select2"
            },{
                label: "found on species:",
                name: "host",
                type: "select2"
            },{
                label: "country of origin:",
                name: "origin",
                type: "select2"
            },{
                label: "isolated of:",
                name: "material",
                type: "text"
            },{
                label: "Observed symptoms:",
                name: "symptom",
                type: "text"
            },{
                label: "confidentiality:",
                name: "confidential",
                type: "checkbox",
                options: [
                    { label: "Dienstverlening", value: 'Dienstverlening' }
                ]
            },{
                label: "Isolaatnummer:",
                name: "colonynumber",
                type: "text"
            }
        ]
    });
    var fields_to_hide = info_editor.order().slice();
    fields_to_hide.shift();
    info_editor.dependent( 'property', function (val) {
        if (val) {
            info_editor.hide(fields_to_hide);
            return {show: val}
        }
    });
    info_editor.on('initEdit', function (e, node, data) {
        info_editor.hide();
        info_editor.set(data.DT_RowId,data.data);
        info_editor.show(data.DT_RowId);
    });
    info_editor.on('initCreate', function () {
        info_editor.hide();
        info_editor.show('property');
    });

    var info_table = $('#infoTable').dataTable( {
        "ajax": {
            url: window.location.pathname + "info/",
            dataSrc: 'data'
        },
        sDom: "rt",
        columns: [
            {data:'property', "cellType": "th"},
            {data:'data', "render": function (data, type, row, meta) {
                var data_shown = data;
                if (typeof row.label !== 'undefined') {
                    data_shown = row.label
                }
                if (typeof row.link !== 'undefined') {
                    return '<a href="' + row.link + '">' + data_shown + '</a>';
                } else {
                    return data_shown
                }
            }}
        ],
        select: {
            style: 'os',
            blurable: true
        },
        initComplete: function() {
            var api = this.api();

            var tests_buttons = new $.fn.dataTable.Buttons(api, {
                buttons: [
                    {
                        extend: "create",
                        text:'<i class="glyphicon glyphicon-plus"></i>',
                        titleAttr:"Create new item",
                        editor: info_editor
                    },{
                        extend: "edit",
                        text:'<i class="glyphicon glyphicon-pencil"></i>',
                        titleAttr:"Edit selected item",
                        editor: info_editor
                    },{
                        extend: "remove",
                        text:'<i class="glyphicon glyphicon-trash"></i>',
                        titleAttr:"Delete selected item",
                        editor: info_editor
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
            tests_buttons.container().appendTo( '#infoControlls' );

            $('.dt-button').tooltip({
                placement: "bottom",
                container: "body"
            });
        }
    });

    //****
    //
    // the Associated ID's table
    //
    //****

    var id_editor = new $.fn.dataTable.Editor( {
        ajax: {
            url:window.location.pathname + "ids/"
        },
        table: '#id_table',
        formOptions: {
                main: {
                    focus: null
                }
            },
        fields: [
            {
                label: "ID group:",
                name: 'code_class',
                type: "select2",
                "opts": {
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
                label: "ID code",
                name: 'code_txt',
                type: "text"
            }
        ]
    });

    $('#id_table').on( 'click', 'tbody td', function (e) {
        id_editor.inline( this, {
            buttons: {label: '&gt;', fn: function () { this.submit(); } }
        } );
    } );

    var id_table = $('#id_table').dataTable({
        "ajax": {
            url: window.location.pathname + "ids/",
            dataSrc: 'data'
        },
        sDom: "rt",
        columns: [
            {data:'code_class'},
            {data:'code_txt'}
        ],
        select: {
            style: 'os',
            blurable: true
        },
        initComplete: function() {
            var api = this.api();

            var id_buttons = new $.fn.dataTable.Buttons(api, {
                buttons: [
                    {
                        extend: "create",
                        text:'<i class="glyphicon glyphicon-plus"></i>',
                        titleAttr:"Create new item",
                        editor: id_editor
                    },{
                        extend: "remove",
                        text:'<i class="glyphicon glyphicon-trash"></i>',
                        titleAttr:"Delete selected item",
                        editor: id_editor
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
            id_buttons.container().appendTo( '#idControlls' );
            
            $(function () {
                $("tr:contains('old_')").addClass('toggle-hidden hidden')
            });

            $('.dt-button').tooltip({
                placement: "bottom",
                container: "body"
            });
        }
    });

    //****
    //
    // the Sample History table
    //
    //****

    var sample_editor = new $.fn.dataTable.Editor( {
        ajax: {
            url:window.location.pathname + "samples/"
        },
        table: "#sampleTable",
        formOptions: {
                main: {
                    focus: null
                }
            },
        fields: [ {
                label: "date:",
                name: "date",
                type: "datetime"
            },{
                label: "change made:",
                name: 'action',
                type: "select2",
                "opts": {
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
                label: "note:",
                name: "note",
                type: "text"
            }
        ]
    });

    $('#sampleTable').on( 'click', 'tbody td', function (e) {
        sample_editor.inline( this, {
            buttons: {label: '&gt;', fn: function () { this.submit(); } }
        } );
    } );

    var sample_table = $('#sampleTable').dataTable( {
        "ajax": {
            url: window.location.pathname + "samples/",
            dataSrc: 'data'
        },
        sDom: "rt",
        columns: [
            {data:'date'},
            {data:'action'},
            {data:'note'}
        ],
        select: {
            style: 'os',
            blurable: true
        },
        initComplete: function() {
            var api = this.api();

            var sample_buttons = new $.fn.dataTable.Buttons(api, {
                buttons: [
                    {
                        extend: "create",
                        text:'<i class="glyphicon glyphicon-plus"></i>',
                        titleAttr:"Create new item",
                        editor: sample_editor
                    },{
                        extend: "remove",
                        text:'<i class="glyphicon glyphicon-trash"></i>',
                        titleAttr:"Delete selected item",
                        editor: sample_editor
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
            sample_buttons.container().appendTo( '#sample_controls' );

            $('.dt-button').tooltip({
                placement: "bottom",
                container: "body"
            });
        }
    });

    //****
    //
    // the Vertification test table
    //
    //****

    var tests_editor = new $.fn.dataTable.Editor( {
        ajax: {
            url:window.location.pathname + "tests/"
        },
        table: "#testsTable",
        formOptions: {
                main: {
                    focus: null
                }
            },
        fields: [
            {
                label: "test performed:",
                name: 'property',
                type: "select2"
            },{
                label: "note:",
                name: "data",
                type: "text"
            }
        ]
    });

    $('#testsTable').on( 'click', 'tbody td:not(:first-child)', function (e) {
        tests_editor.inline( this, {
            buttons: {label: '&gt;', fn: function () { this.submit(); } }
        } );
    } );

    tests_editor.on('initEdit', function () {
        tests_editor.show();
        tests_editor.hide('property')
    });
    tests_editor.on('initCreate', function () {
        tests_editor.show()
    });

    var tests_table = $('#testsTable').dataTable( {
        "ajax": {
            url: window.location.pathname + "tests/",
            dataSrc: 'data'
        },
        sDom: "rt",
        columns: [
            {data:'property'},
            {data:'data'}
        ],
        select: {
            style: 'os',
            blurable: true
        },
        initComplete: function() {
            var testapi = this.api();

            var tests_buttons = new $.fn.dataTable.Buttons(testapi, {
                buttons: [
                    {
                        extend: "create",
                        text:'<i class="glyphicon glyphicon-plus"></i>',
                        titleAttr:"Create new item",
                        editor: tests_editor
                    },{
                        extend: "remove",
                        text:'<i class="glyphicon glyphicon-trash"></i>',
                        titleAttr:"Delete selected item",
                        editor: tests_editor
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
            tests_buttons.container().appendTo( '#testsControlls' );

            $('.dt-button').tooltip({
                placement: "bottom",
                container: "body"
            });
        }
    });

    //****
    //
    // the Comments table
    //
    //****

    var comment_editor = new $.fn.dataTable.Editor( {
        ajax: {
            url:window.location.pathname + "comment/"
        },
        table: '#commentTable',
        formOptions: {
                main: {
                    focus: null
                }
            },
        fields: [
            {
                label: "comment group:",
                name: 'comment_label',
                type: "select2",
                "opts": {
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
                label: "comment text",
                name: 'comment_txt',
                type: "text"
            }
        ]
    });

    $('#commentTable').on( 'click', 'tbody td', function (e) {
        comment_editor.inline( this, {
            buttons: {label: '&gt;', fn: function () { this.submit(); } }
        } );
    } );

    var comment_table = $('#commentTable').dataTable( {
        "ajax": {
            url: window.location.pathname + "comment/",
            dataSrc: 'data'
        },
        sDom: "rt",
        columns: [
            {data:'comment_label'},
            {data:'comment_txt'}
        ],
        select: {
            style: 'os',
            blurable: true
        },
        initComplete: function() {
            var commentapi = this.api();

            var comment_buttons = new $.fn.dataTable.Buttons(commentapi, {
                buttons: [
                    {
                        extend: "create",
                        text:'<i class="glyphicon glyphicon-plus"></i>',
                        titleAttr:"Create new item",
                        editor: comment_editor
                    },{
                        extend: "remove",
                        text:'<i class="glyphicon glyphicon-trash"></i>',
                        titleAttr:"Delete selected item",
                        editor: comment_editor
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
            comment_buttons.container().appendTo( '#comment_controls' );

            $('.dt-button').tooltip({
                placement: "bottom",
                container: "body"
            });
        }
    });
});


// selected functionality
function header_select_add(){
    var id_list = [window.location.pathname.split('/')[1]];
    header_select_ajax(id_list)
}
// header_select_add needs to be defined before show_header_select_btn is run
show_header_select_btn(header_select_add);


$('#filterButton').click(function () {
    $('.toggle-hidden').toggleClass('hidden')
});
