/**
 * General javascript snippets for Stemweb.
 * 
 * 
 * 
 * 
 * */



$.ajaxSetup({ 
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
         }
         return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     } 
});


var sURL = unescape(window.location.pathname);

function refresh() {
	
	location.reload();
	load_previous_runs_table();
	$('#algorithm_tabs').tabs('option', 'select', 2);

}

function prev() {
	window.history.go(-1);
}

function next() {
	window.history.go(1);
}


function returnObjById( id )
{
    if (document.getElementById)
        var returnVar = document.getElementById(id);
    else if (document.all)
        var returnVar = document.all[id];
    else if (document.layers)
        var returnVar = document.layers[id];
    return returnVar;
}

function delete_runs() {
	var arr = new Array();
	checkboxes = document.getElementsByName('run_delete');
	for(var i = 0; i < checkboxes.length; i++) {
		if (checkboxes[i].type == 'checkbox') {
			if (checkboxes[i].checked == true) {
				arr.push( checkboxes[i].value );
			}
		}
    }
	arr = arr.join(" ")
	$.post("/algorithms/delete/", 
			{ 'runs': arr }, 
			function(data) {
				/* Fix this */
				location.reload();

			});
}

$(document).ready(function() {
	var arr = new Array();
	checkboxes = document.getElementsByName('run_delete');
	for(var i = 0; i < checkboxes.length; i++) {
		if (checkboxes[i].type == 'checkbox') {
			if (checkboxes[i].checked == true) {
				checkboxes[i].checked = false;
			}
		}
    }
});

$(document).ready(function() {
    $('#subpage_index_table tr').click(function() {
        var href = $(this).find("a").attr("href");
        if(href) {
            window.location = href;
        }
    });
});


var go_to_results = function go_to_results(e) {
	var href = $(this.parentNode).find("a").attr("href");
    if(href) {
        window.location = href;
    }
}

$(document).ready(function() { 
	$("#previous_runs_table").tablesorter( { locale: 'eu', 
											headers: { 0: { sorter: 'shortDate' },
													   1: { sorter: 'shortDate' },
													   4: { sorter: false} }}); 
	
	/* Little bit hacky solution */
	var table = returnObjById("previous_runs_table");
	if (table == null) return;
	
	for (var i = 1, row; row = table.rows[i]; i++) {	
		for (var j = 0, cell; cell = row.cells[j]; j++) {
			if (cell.className != 'delete_run') {
				cell.addEventListener('click', go_to_results, false);
			}
		}
	}
});

function load_previous_runs_table() {
	$("#previous_runs_table").tablesorter( { headers: { 4: { sorter: false} }}); 
	
	$('#previous_runs_table td').click(function() {
        var href = $(this).find("a").attr("href");
        if(href) {
            window.location = href;
        }
    });
}

$(document).ready(function() {  
    $('#algorithm_tabs').tabs({ fx: { height: 'toggle', opacity: 'toggle' } });  
}); 
/*
$(document).ready(function () {
    $("#algorithm_tabs").bind('tabsselect', function(event, ui) {
        window.location.href=ui.tab;
    });
});
*/


