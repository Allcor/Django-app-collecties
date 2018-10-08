
// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});


function header_select_update() {
    $.ajax({
        method: "GET",
        url: window.location.protocol + "//" + window.location.host + "/" + "labels/user_selected_nr/",
        success: function (data) {
            $("#header_select_badge").text(data.selected_count);
            return true
        },
        error: function(jqXHR, textStatus, errorThrown){
            return false
        }
    });
}

function header_select_ajax( id_list ) {
    var requestJSON = {action:"add"};
    $.each(id_list, function( index, value ) {
        requestJSON['data[' + index + '][collection_id]'] = value;
    });
    $.ajax({
        method: "POST",
        url: window.location.protocol + "//" + window.location.host + "/" + "labels/user_selected/",
        data: requestJSON,
        success: function (data) {
            $("#header_select_badge").text(data.selected_count);
        }
    })
}

function show_header_select_btn(select_add_function) {
    $("#header_select_group").prepend(
        '<button class="btn btn-default navbar-btn header-select-btn" title="add to selection">' +
        '<i class="glyphicon glyphicon-share-alt"></i></button>'
    );
    $(".header-select-btn").click(function () {
        select_add_function()
    });
    $('.navbar-btn').tooltip({
        placement: "bottom",
        container: "body"
    });
}

$(document).ready(function () {
    header_select_update();

    $('.navbar-btn').tooltip({
        placement: "bottom",
        container: "body"
    });
});

