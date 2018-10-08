$(document).ready(function () {
    $('#testTable').on('dblclick', 'tr', function () {
        var url_root = window.location.protocol + "//" + window.location.host + "/";
        var d = table.row(this).data();
        var pcr_nr = d.primer_nr.replace(/\D/g,'');
        window.location = url_root + 'pcr/' + pcr_nr +'/'
    });
});

function rowcallback_function(row, data, index) {
    if (data.status == "Niet meer in gebruik") {
        $(row).addClass('grayedout')
    } else if (data.status == "In protocol opgenomen") {
        $(row).addClass('mellowyellow')
    } else if (data.status == "Voor onderzoeksdoeleinden") {
        $(row).addClass('mellowblue')
    } else if (data.status == "Toepassing incidenteel") {
        $(row).addClass('mellowred')
    }
}