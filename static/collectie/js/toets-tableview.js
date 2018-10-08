var table = null;
$(document).ready(function () {
    var hiddenArray = [];
    $('.initiallyHidden').each(function () {
        hiddenArray.push($(this).index())
    });
   table = $('#testTable').DataTable({
        pageLength: 20,
        "lengthMenu": [[10,20,50,-1],[10,20,50,"all"]],
        "scrollX": true,
        bStateSave: true,
        "processing": true,
        "serverSide": true,
        select: true,
        ajax: {
            url:window.location.pathname + "data/",
            dataSrc: 'data',
            "cache":true
        },
        sDom: "rt<'row'<'col-sm-3'l><'col-sm-4'i><'col-sm-5'p>>",
        aoColumnDefs: [{ "bVisible": false, "aTargets": hiddenArray}],
        rowCallback: rowcallback_function,
        columns: toets_columns,
        initComplete: function(){
            var api = this.api();

            new $.fn.dataTable.Buttons(api, {
                buttons: [
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
                        extend: 'colvis',
                        text: '<i class="glyphicon glyphicon-eye-close"></i>',
                        titleAttr: "hide and show columns",
                        columns: ':not(.noVis)'
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
            api.buttons().container().appendTo( '#testControlls' );
            api.search($('#testSearch').val()).draw(); //so the query from the GET get's searched on page load

            $('.dt-button').tooltip({
                placement: "bottom",
                container: "body"
            });
        }
    });
    $('#testSearch').keyup(function () {
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
        return 'toetsen_' + date_txt;
    } else {
        return 'toetsen_' + date_txt + '_' + query_txt;
    }
}
