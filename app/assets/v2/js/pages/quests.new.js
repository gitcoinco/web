
$(document).ready(function() {
  const QUESTIONS_LIMIT = 10;
  const ANSWERS_LIMIT = 5;
  const question_template = $('.form-group.question:last').clone();
  const answer_template = question_template.children('span:last').clone();

  $('.select2').select2();

  const video_toggle = function(e) {
    var is_checked = $('#video_enabled').is(':checked');

    if (is_checked) {
      $('.new_quest_background.no_video_enabled').addClass('hidden');
      $('.new_quest_background.no_video_enabled').removeClass('selected');
    } else {
      $('.new_quest_background.no_video_enabled').removeClass('hidden');
    }
  };

  $(document).on('click', '#video_enabled', video_toggle);

  video_toggle();

  $(document).on('click', '.add_answer', function(e) {
    e.preventDefault();

    if ($(this).parents('.question').children('span').length >= ANSWERS_LIMIT) {
      _alert(gettext('The number of answers for each question are limited to ') + ANSWERS_LIMIT);
      return;
    }

    var last_answer = $(this).parents('.form-group.question').children('span:last');

    last_answer.after(answer_template.clone());
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
      _alert(gettext('The number of questions are limited to ') + QUESTIONS_LIMIT);
      return;
    }

    var last_question = $('.form-group.question:last');

    last_question.after(question_template.clone());
  });

  $(document).on('click', '.close_answer', function(e) {
    e.preventDefault();
    if ($(this).parents('.question').find('span').length <= 1) {
      alert(gettext('You cannot have 0 answers per question'));
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
      alert(gettext('you cannot have 0 questsions'));
      return;
    }
    var ele = $(this).parents('div.question');

    ele.remove();
  });

});
