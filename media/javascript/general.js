$(document).ready(function() {

    $('#subpage_index_table tr').click(function() {
        var href = $(this).find("a").attr("href");
        if(href) {
            window.location = href;
        }
    });

});

$(document).ready(function() {

    $('#previous_runs_table tr').click(function() {
        var href = $(this).find("a").attr("href");
        if(href) {
            window.location = href;
        }
    });

});

$(document).ready(function() { 
	$("#previous_runs_table").tablesorter( { headers: { 4: { sorter: false} }}); 
}); 