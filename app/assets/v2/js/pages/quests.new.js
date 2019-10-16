
$(document).ready(function() {
  $('.add_answer').click(function(e) {
    e.preventDefault();
    var dupe_me = $(this).parents('.form-group').find('span:last');
    var clone = dupe_me.clone();

    dupe_me.after(clone);
  });
  $('.add_question').click(function(e) {
    e.preventDefault();
    var dupe_me = $('.form-group.question:last');
    var clone = dupe_me.clone();

    dupe_me.after(clone);
  });

});
