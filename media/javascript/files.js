$(document).ready(function() {  
    $('#one_file_tabs').tabs({ fx: { height: 'toggle', opacity: 'toggle' } });  
    $("#one_file_tabs").bind('tabsselect', function(event, ui) {
        window.location.href=ui.tab;
    });
}); 

$(document).ready(function() {  
    $('#all_files_tabs').tabs({ fx: { height: 'toggle', opacity: 'toggle' } });  
}); 



$(document).ready(function () {
	$('#files_home_tabs').tabs({ fx: { height: 'toggle', opacity: 'toggle' } });
    $("#files_home_tabs").bind('tabsselect', function(event, ui) {
        window.location.href=ui.tab;
    });
});

$(document).ready(function() {
	$("#user_files_table").tablesorter( { headers: { 4: { sorter: false} }}); 
    $('#user_files_table tr').click(function() {
        var href = $(this).find("a").attr("href");
        if(href) {
            window.location = href;
        }
    });
});