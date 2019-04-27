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

var match_data = {};

function hide_match_cards() {
    $('#matches_none').css("display", "block");
    $('.card_game').css("display", "none");
}


function show_match_cards() {
    $('#matches_none').css("display", "none");
    $('.card_game').css("display", "flex");
}



var card_tmpl = $.templates("#match_card_template");


function* make_card_iterator() {
    for (var i = 0; i < match_data["undecided"].length; i++){
        displayed_card_index = i;
        var html = card_tmpl.render(match_data["undecided"][i])
        $('#match_card').html(html);
        show_match_cards();
        yield;
    };
    hide_match_cards()
}


function fill_match_history_tmpl() {
    let template_data = {
        'count': match_data["matched"].length, 
        'matched_orgs': match_data["matched"]}
    let history_tmpl = $.templates("#match_history_template");
    let html = history_tmpl.render(template_data)
    $('#pastmatches').html(html);
}


function hide_match_row(handle) {
    $('#row_' + handle).css("display", "none");
}


function load_more_cards() {
    // Placeholder waiting for org paging api.
}


function refresh_match_cards() {
    retrieve_match_data(
        'undecided', 
        function() {
            iter_match_card = make_card_iterator()
            iter_match_card.next()
        },
    )
}


function refresh_match_history() {
    retrieve_match_data(
        'matched', 
        function() {
            fill_match_history_tmpl()
        },
    )
}


function retrieve_match_data(query_param, callback = function() {}) {
    $.ajax({
        type: 'GET',
        url: '/matches_api/',
        success: function(data) {
            match_data = {}
            for (var grouped_orgs in data['result']) {
                match_data[grouped_orgs] = JSON.parse(data['result'][grouped_orgs])
            }
            callback()
        },
        error: function(xhr, status, error) {
            //
        }
    });
}


function post_interest(is_matched = true) {
    $.ajax({
        type: 'POST',
        data: {
            'action': 'update',
            'org_handle': match_data["undecided"][displayed_card_index].fields.handle, 
            'matched': is_matched,
            'csrfmiddlewaretoken': csrftoken,
        },
        url: '/matches_api/',
        success: function(data) {
            //
        },
        error: function(xhr, status, error) {
            //
        }
    });
    iter_match_card.next();
}


function delete_match(handle) {
    hide_match_row(handle);
    $.ajax({
        type: 'POST',
        data: {
            'action': 'delete',
            'org_handle': handle, 
            'matched': 'delete',
            'csrfmiddlewaretoken': csrftoken,
        },
        url: '/matches_api/',
        success: function(data) {
            //
        },
        error: function(xhr, status, error) {
            //
        }
    });
}

refresh_match_cards();
refresh_match_history();
