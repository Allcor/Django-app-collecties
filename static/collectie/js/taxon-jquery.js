

$(document).ready(function () {
    var table = $('#taxonSamples').DataTable( {
        lengthChange: false,
        "scrollY": "30%",
        "scrollCollapse": true,
        paging: false,
        "info": false,
        bStateSave: true,
        sDom: 'rt',

        initComplete: function(){
            var api = this.api();

            new $.fn.dataTable.Buttons(api, {
                buttons: [
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
                        exportOptions: {
                            columns: ':visible'
                        }
                    },
                    {
                        extend:'pdf',
                        text:'<i class="glyphicon glyphicon-picture"></i>',
                        titleAttr:"Save table as .pdf",
                        exportOptions: {
                            columns: ':visible'
                        }
                    },
                    {
                        extend:'colvis',
                        text:'<i class="glyphicon glyphicon-eye-close"></i>',
                        titleAttr:"hide and show columns"
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
            api.buttons().container().appendTo('#tableControlls');

            $('.dt-button').tooltip({
                placement: "bottom",
                container: "body"
            })
        }
    } );
    $('#tableSearch').keyup(function () {
        table.search(this.value).draw();
    });
});

$(function () {
  $('[data-toggle="tooltip"]').tooltip({
      placement: "bottom",
      container: "body"
  });
});

$('#filterCheckbox').click(function () {
    $('.toggle-hidden').toggleClass('hidden')
});
