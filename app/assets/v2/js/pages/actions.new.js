
$(document).ready(function() {
  $(document).on('click', '.new_quest_background', function(e) {
    e.preventDefault();
    $('.new_quest_background').removeClass('selected');
    var clone = $(this).addClass('selected');

    $('#background').val($(this).data('value'));

    dupe_me.after(clone);
  });
});
