
$(document).ready(function () {
  const QUESTIONS_LIMIT = 10;
  const ANSWERS_LIMIT = 5;
  const question_template = $('.form-group.question:last').clone();
  const answer_template = question_template.children('span:last').clone();

  /**
   * Templates for questions and answers in code battle quest style
  */
  const question_type_select_template = `
    <div class="question_type_select_container form-group">
      <label class="form__label" for="question_type">${gettext('Question Type')}</label>
      <select name="question_type" class="select2 question_type_select">
        <option value="quiz_question" selected="selected">Quiz</option>
        <option value="boss_fight_question">Boss Fight</option>
      </select>
    </div>
  `;
  const boss_fight_answer_template = `
    <div class="boss_fight_language_select_container form-group">
      <label class="form__label" for="boss_fight_language">${gettext('Boss Fight Code Language')}</label>
      <select name="boss_fight_language" class="select2 boss_fight_language_select">
        <option value="boss_fight_language_solidity" selected="selected">Solidity</option>
        <option value="boss_fight_language_javascript">Javascript</option>
      </select>
    </div>
    <span>
      <hr>
      <label class="form__label" for="points">${gettext('Insert the code for the boss fight')}</label>
      <input type="hidden" name="answer_correct[]" class="form__input" value="YES">
      <textarea name="answer[]" class="form__input" cols="50" rows="10" required></textarea>
      <hr>
    </span>
  `;
  const question_code_battle_template = question_template.clone();
  const seconds_to_respond_label = question_code_battle_template.find('label')[1];
  $(question_type_select_template).insertBefore(seconds_to_respond_label);

  /**
   * Controllers fot questions and answers in code battle quest style
   */
  // when question type is changed, updates the question templates and the answers template
  $(document).on('change', '.question_type_select', function(e) {
    e.preventDefault();
    // creates a new question battle code clone
    const new_question_code_battle = question_code_battle_template.clone();
    // quiz type selected
    if (e.target.value === 'quiz_question') {
      // removes the current question and replace it with a fresh one
      $(e.target.parentNode.parentNode).replaceWith(new_question_code_battle);
      return;
    }
    // boss fight selected
    // do nothing if the quest already contains a battle fight question
    if ($('.boss_fight_question').length > 0) {
      alert(gettext('A Code Battle Quest can have only one Boss Fight question'));
      return false;
    }
    // sets the class of the question to boss_fight_question
    new_question_code_battle.toggleClass('boss_fight_question');
    // removes all answers
    new_question_code_battle.find('span').remove();
    // removes the add answer button
    new_question_code_battle.find('.add_answer').remove();
    // insert the text area for the boss fight code
    $(boss_fight_answer_template).insertAfter(new_question_code_battle.find('.form__input')[1]);
    new_question_code_battle.find('option[value=boss_fight_question]').attr('selected', 'selected');
    $(e.target.parentNode.parentNode).replaceWith(new_question_code_battle);
  })


  $(document).on('form#newkudos', 'submit', function(e) {
    // e.preventDefault();
    // console.log($(this).formdata);
    // alert('hi');

  });

  /**
   * Controller for question style selection
   */
  $(document).on('change', '#quest-style', function (e) {
    e.preventDefault();
    // removes all questions that were previously created
    $(e.target.parentNode.parentNode).find('.form-group.question').remove();
    if (e.target.value === 'code_battle') {
      $(question_code_battle_template).insertBefore($(e.target.parentNode.parentNode).find('.add_question')[0]);
      return;
    }
    $(question_template).insertBefore($(e.target.parentNode.parentNode).find('.add_question')[0]);
  });

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
    // happens when a new question is created in quiz style
    if ($('#quest-style')[0].value !== 'code_battle') {
      var last_question = $('.form-group.question:last');
      last_question.after(question_template.clone());
      $('[data-toggle="tooltip"]').bootstrapTooltip();
      return;
    }
    // happens when a new question is created in the code battle style
    var last_question = $('.form-group.question:last');
    last_question.after(question_code_battle_template.clone());
    $('[data-toggle="tooltip"]').bootstrapTooltip();
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
