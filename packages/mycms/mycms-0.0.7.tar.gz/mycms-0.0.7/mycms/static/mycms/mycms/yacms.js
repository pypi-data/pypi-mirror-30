function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

/*$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        console.log("Doing ajaxSetup");
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});*/

//var csrftoken = Cookies.get('csrftoken');

$('input[name=title]').change(function() {
    var page_title = $("#CreateTitle").val();
    $("#CreateSlug").val(convertToSlug(page_title));

});


function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        //console.log("Doing ajax Setup")
        var csrftoken = Cookies.get('csrftoken');
        //console.log("csrftoken: " + csrftoken);
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken",csrftoken);
        }
    }
});
