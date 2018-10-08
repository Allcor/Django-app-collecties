$(document).ready(function () {
    var hiddenArray = [];
    $('.initiallyHidden').each(function () {
        hiddenArray.push($(this).index())
    });
    var table = $('#collectionTable').DataTable( {
        pageLength: 20,
        "lengthMenu": [[10,20,50,-1],[10,20,50,"all"]],
        "scrollX": true,
        "processing": true,
        "serverSide": true,
        select: true,
        "ajax": {
            url: window.location.pathname + "data/",
            dataSrc: 'data',
            "cache":true,
            "data": function ( d ) {
                $.each($('#collectionTable').dataTable().fnSettings().aoColumns, function (c) {
                    d.columns[c].isvisible = $('#collectionTable').dataTable().fnSettings().aoColumns[c].bVisible;
                });
            }
        },
        sDom: "rt<'row'<'col-sm-3'l><'col-sm-4'i><'col-sm-5'p>>",
        aoColumnDefs: [{ "bVisible": false, "aTargets": hiddenArray}],
        bStateSave: true,
        // all should only be used together with a filter, when saved data has length 'all', reset to default.
        stateLoadCallback: function(settings) {
            var state_data_check = JSON.parse(localStorage.getItem( 'DataTables_' + settings.sInstance + '_/' ));
            if(state_data_check != null) {
                if (state_data_check.length === -1) {
                    state_data_check.length = 20;
                    console.log(state_data_check);
                }
            }
            return state_data_check
        },
        columns: collectControlls_columns,
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
                var url_root = window.location.protocol + "//" + window.location.host + "/";
                window.location = url_root + this.id+'/'
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
                    return item.DT_RowId
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

//get visible columns
