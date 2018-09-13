var localStorage;

try {
  localStorage = window.localStorage;
} catch (e) {
  localStorage = {};
}

$(document).ready(function() {
  $(document).on('click', '.show_video', function(e) {
    e.preventDefault();
    $('#video').remove();
    var url = '/modal/get_quickstart_video';

    setTimeout(function() {
      $.get(url, function(newHTML) {
        $(newHTML).appendTo('body').modal();
      });
    }, 300);
  });

  $(document).on('change', '#dontshow', function(e) {
    if ($(this)[0].checked) {
      localStorage['quickstart_dontshow'] = true;
    } else {
      localStorage['quickstart_dontshow'] = false;
    }
  });
});
