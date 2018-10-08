$(document).ready(function () {
    var hiddenArray = [];
    $('.initiallyHidden').each(function () {
        hiddenArray.push($(this).index())
    });
    var table = $('#collectionTable').DataTable( {
        pageLength: 20,
        "lengthMenu": [[10,20,50,-1],[10,20,50,"all"]],
        bStateSave: true,
        "scrollX": true,
        select: true,
        "ajax": {
            url: "/static/collectie/php/isolates.php",
            dataSrc: 'data',
            "cache":true
        },
        sDom: "rt<'row'<'col-sm-3'l><'col-sm-4'i><'col-sm-5'p>>",
        aoColumnDefs: [
            { "bVisible": false, "aTargets": hiddenArray},
            { type: 'natural', targets: 9}
        ],
        columns: [
            {data:'collectie_pathogen.given_name'},
            {data:'collectie_pathogen.scientific_name'},
            {data:'collectie_original_host.given_name'},
            {data:'collectie_original_host.scientific_name'},
            {data:'collectie_collection.first_date', className: 'MinWidth60'},
            {data:'collectie_countrycode.name'},
            {data:'collectie_collection.confidential', render: function (data, type, row) {
                return type === 'display' && data === false ?
                    '' : data;
            }},
            {data:'collectie_collection.material'},
            {data:'collectie_collection.tests_performed'},
            {data:'collectie_collection.id_collectie', className: 'MinWidth60'},
            {data:'collectie_collection.id_ins', className: 'MinWidth80'},
            {data:'collectie_collection.pathogen_location'},
            {data:'collectie_collection.id_storidge'},
            {data:'collectie_collection.pathogen_tree', className: 'noVis'},
            {data:'collectie_collection.host_tree', className: 'noVis'},
            {data:'collectie_collection.id_other', className: 'noVis'}
        ],
        initComplete: function(){
            var api = this.api();

            new $.fn.dataTable.Buttons(api, {
                buttons: [
                    {
                        extend:'selectAll',
                        text:'<i class="glyphicon glyphicon-hand-up"></i>',
                        titleAttr:"select all isolates",
                        action : function(e) {
                            e.preventDefault();
                            table.rows().deselect();
                            table.rows({ search: 'applied'}).select();
                        }
                    },
                    {
                        extend:'copy',
                        text:'<i class="glyphicon glyphicon-copy"></i>',
                        titleAttr:"Copy table to clipboard",
                        exportOptions: {
                            columns: ':visible'
                        }
                    },
                    {
                        extend:'excel',
                        text:'<i class="glyphicon glyphicon-list-alt"></i>',
                        titleAttr:"Save table as .xlsx",
                        filename: function () {return getExportFilename();},
                        exportOptions: {
                            columns: ':visible'
                        }
                    },
                    {
                        extend:'pdf',
                        text:'<i class="glyphicon glyphicon-picture"></i>',
                        titleAttr:"Save table as .pdf",
                        filename: function () {return getExportFilename();},
                        exportOptions: {
                            columns: ':visible'
                        }
                    },
                    {
                        extend:'colvis',
                        text:'<i class="glyphicon glyphicon-eye-close"></i>',
                        titleAttr:"hide and show columns",
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
            api.buttons().container().appendTo( '#collectControlls' );
            api.search($('#collectSearch').val()).draw();

            $('#collectionTable tbody').on('dblclick', 'tr', function () {
                window.location=this.id.split('_')[1]+'/'
            });

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
    } );
    $('#collectSearch').keyup(function () {
        table.search(this.value).draw();
    });
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

$(function () {
  $('[data-toggle="tooltip"]').tooltip({
      placement: "bottom",
      container: "body"
  });
});