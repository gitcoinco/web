
$(document).ready(function() {

  $(document).on('form#newkudos', 'submit', function(e) {
    // e.preventDefault();
    // console.log($(this).formdata);
    // alert('hi');
  });
  
  $(document).on('click', '.add_answer', function(e) {
    e.preventDefault();
    var dupe_me = $(this).parents('.form-group').find('span:last');
    var clone = dupe_me.clone();

    dupe_me.after(clone);
  });

  $(document).on('click', '.add_question', function(e) {
    e.preventDefault();
    var dupe_me = $('.form-group.question:last');
    var clone = dupe_me.clone();

    dupe_me.after(clone);
  });


  $(document).on('click', '.close_answer', function(e) {
    e.preventDefault();
    if ($(this).parents('.question').find('span').length <= 1) {
      alert('you cannot have 0 answers per question');
      return;
    }
    var ele = $(this).parents('span');

    ele.remove();
  });


  $(document).on('click', '.close_question', function(e) {
    e.preventDefault();
    if ($(this).parents('div.question').length <= 1) {
      alert('you cannot have 0 questsions');
      return;
    }
    var ele = $(this).parents('div.question');

    ele.remove();
  });

});
