

$(document).ready(function () {
    var table = $('#oldcrap').DataTable( {
        paging: false,
        select: true,
        initComplete: function(){
            var api = this.api();

            new $.fn.dataTable.Buttons(api, {
                buttons: [ 'copy', 'excel', 'pdf' ]
            });

            api.buttons().container().appendTo( '#' + api.table().container().id + ' .col-sm-6:eq(0)' );
        }
    } );
});

$('#filterButton').click(function () {
    $('.toggle-hidden').toggleClass('hidden')
});

$('.dt-button').tooltip({
    placement: "bottom",
    container: "body"
});