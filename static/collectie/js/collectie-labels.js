$(document).ready(function () {
    var selectedTable = $('#selectedTable');
    editor = new $.fn.dataTable.Editor({
        ajax: {
            url:window.location.pathname + "user_selected/",
            rowId: 'id'
        },
        table: "#selectedTable"
    });

    // Remove isolate
    selectedTable.on('click', 'button.remove-btn', function (e) {
        editor.remove( $(this).closest('tr'), {
            title: '<h3>Deselect isolate</h3>',
            message: 'Are you sure you want to remove this isolate from your selected isolates?',
            buttons: {
                className: "btn btn-danger",
                fn: function () {
                    this.submit();
                },
                label: 'Deselect'
            }
        } );
    });

    //table creation
    var table = selectedTable.DataTable({
        //sDom: "rt<'row'<'col-sm-3'l><'col-sm-4'i><'col-sm-5'p>>",
        sDom: "rt",
        pageLength: -1,
        select: true,
        "ajax": {
            url:window.location.pathname + "user_selected/",
            rowId: 'id'
        },
        columns: userSelected_columns.concat([{
                data: null,
                orderable: false,
                className: "text-center",
                defaultContent: '<div class="btn-group btn-group-xs">' +
                                    '<button type="button" class="btn btn-default remove-btn">' +
                                        '<i class="glyphicon glyphicon-remove" style="color:red"></i>' +
                                    '</button>' +
                                '</div>'
            }]),
        initComplete: function() {
            var api = this.api();
            var buttons1 = new $.fn.dataTable.Buttons(api, {
                buttons: [
                    {
                        extend: 'copy',
                        text: '<i class="glyphicon glyphicon-copy"></i>',
                        titleAttr: "Copy table to clipboard."
                    },{
                        text: '<i class="glyphicon glyphicon-print"></i>',
                        titleAttr: "print labels for selected",
                        action: function (e, dt, node, config) {
                            if (table.rows( { selected: true } ).count() === 0) {
                                var select_rows = table.rows()
                            } else {
                                var select_rows = table.rows( { selected: true } )
                            }
                            var data = select_rows.data();
                            var collection_ids = {};
                            for (var i=0; i< data.length ;i++){
                                collection_ids[i] = data[i]['select_collection_id']
                            }
                            //console.log(collection_ids);
                            $.ajax({
                                type: "POST",
                                url: window.location.pathname + 'user_selected_print/',
                                data: collection_ids
                            });
                        }
                    }
                ],
                dom: {
                    container: {
                        className: 'dt-buttons btn-group pull-right'
                    },
                    button: {
                        tag: 'button',
                        className: 'dt-button btn btn-default btn-sm'
                    },
                    buttonLiner: {
                        tag: null
                    }
                }
            });
            var buttons2 = new $.fn.dataTable.Buttons(api, {
                buttons: [
                    {
                        extend:'selectAll',
                        text:'<i class="glyphicon glyphicon-hand-up"></i>',
                        titleAttr:"select all isolates"
                    },{
                        text:'<i class="glyphicon glyphicon-trash"></i>',
                        titleAttr:"remove selected item",
                        action: function ( e, dt, node, config) {
                            if (table.rows( { selected: true } ).count() === 0) {
                                var to_remove = ''
                            } else {
                                var to_remove = '.selected'
                            }
                            editor.remove( to_remove, {
                                title: '<h3>Deselect isolate</h3>',
                                message: 'Are you sure you want to remove these selected isolates?',
                                buttons: {
                                    className: "btn btn-danger",
                                    fn: function () {
                                        this.submit();
                                    },
                                    label: 'Deselect'
                                }
                            } );
                        }
                    }
                ],
                dom: {
                    container: {
                        className: 'dt-buttons btn-group pull-right'
                    },
                    button: {
                        tag: 'button',
                        className: 'dt-button btn btn-default btn-sm'
                    },
                    buttonLiner: {
                        tag: null
                    }
                }
            });
            buttons1.container().appendTo('#selectedControlls');
            buttons2.container().appendTo('#selectedControlls');

            $('.dt-button').tooltip({
                placement: "bottom",
                container: "body"
            });
        }
    });

    // Page to detail on doubleclick
    selectedTable.on('dblclick', 'tr', function () {
        var isolate = table.row(this).data().select_collection_id;
        var url = window.location.protocol + "//" + window.location.host + "/" + isolate + "/";
        window.location=url
    });

    // update header_select_badge
    editor.on('postRemove', function () {
        is_sucsessful = header_select_update();
        if (is_sucsessful === false){
            editor.ajax().reload();
        }
    })
});
console.log(userSelected_columns.concat([{
                data: null,
                orderable: false,
                className: "text-center",
                defaultContent: '<div class="btn-group btn-group-xs">' +
                                    '<button type="button" class="btn btn-default remove-btn">' +
                                        '<i class="glyphicon glyphicon-remove" style="color:red"></i>' +
                                    '</button>' +
                                '</div>'
            }]));