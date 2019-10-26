
$(document).ready(function() {
  const QUESTIONS_LIMIT = 6;

  $(document).on('form#newkudos', 'submit', function(e) {
    // e.preventDefault();
    // console.log($(this).formdata);
    // alert('hi');
  });

  $(document).on('click', '.add_answer', function(e) {
    e.preventDefault();

    var dupe_me = $(this).parents('.form-group').find('span:last');
    var clone = dupe_me.clone();

    // Clean element copied
    clone.find('input').val('');
    clone.find('option').attr('selected', false);
    dupe_me.after(clone);
  });
  $(document).on('click', '.new_quest_background', function(e) {
    e.preventDefault();
    $('.new_quest_background').removeClass('selected');
    var clone = $(this).addClass('selected');

    $('#background').val($(this).data('value'));

    dupe_me.after(clone);
  });

  $(document).on('click', '.add_question', function(e) {
    e.preventDefault();
    if ($('.form-group.question').length > QUESTIONS_LIMIT) {
      alert('Questions limit exceed');
      return;
    }

    var dupe_me = $('.form-group.question:last');
    var clone = dupe_me.clone();

    // Clean element copied
    clone.find('input').val('');
    clone.find('option').attr('selected', false);
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
  $(document).on('click', '.remove', function(e) {
    e.preventDefault();
    $(this).parents('.form-group').find('.hidden').removeClass('hidden');
    $(this).parents('.form-group').find('.default_kudos').remove();
    $(this).parents('.form-group').find('input[name=enemy]').remove();
    $(this).parents('.form-group').find('[name=enemy2]').attr('name', 'enemy');
    $(this).parents('.form-group').find('[name=reward2]').attr('name', 'reward');
    $(this).remove();
  });


  $(document).on('click', '.close_question', function(e) {
    e.preventDefault();
    if ($('div.question').length <= 1) {
      alert('you cannot have 0 questsions');
      return;
    }
    var ele = $(this).parents('div.question');

    ele.remove();
  });

});
