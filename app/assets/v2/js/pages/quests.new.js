function debounce(fn, time){
  let timeout;

  return function() {
    const functionCall = () => fn.apply(this, arguments);

    clearTimeout(timeout);
    timeout = setTimeout(functionCall, time);
  }
}

function updateCodeValidationOutput(type, title, text, otherInfo) {
  console.log(otherInfo);
  const codeValidationOutput = $('#code-validation-output');
  const codeValidationOutputTitle = $('#code-validation-output-title');
  const codeValidationOutputText = $('#code-validation-output-text');
  codeValidationOutputTitle.html(title);
  codeValidationOutputText.html(text);

  if (type === 'error') {
    codeValidationOutput.addClass('bg-danger').removeClass('bg-success');
  } else if (type === 'ok') {
    codeValidationOutput.addClass('bg-success').removeClass('bg-danger');
    const newText = (!otherInfo) ? text : `
      ${text}
      <p class="code-validation-other-info">
        You want that users write a function named
        <strong class="text-primary">"${otherInfo.name}"</strong>,
         accepting
        <strong class="text-primary">
        "${otherInfo.paramsNumber}"
        </strong>
        parameters.
      </p>
      <p> Write your test function in here and click on the "evaluate" button </p>
      <p>
        <input type="hidden" name="answer_correct[]" class="form__input" value="YES">
        <input id="boss-fight-answer" type="hidden" name="answer[]" class="form__input" value="YES">
        <textarea id="code-validation-test-function" cols="50" rows="3"></textarea>
      </p>
      <p><button class="btn btn-primary" id="evaluate-code">Evaluate</button></p>
      <p id="evaluation-result-text"></p>`;
    let questionText = `Write a function named "${otherInfo.name}" that accepts ${otherInfo.paramsNumber} parameters, `;
    codeValidationOutputText.html(newText);
    $('#evaluate-code').click(function (e) {
      e.preventDefault();
      const program = `
        ${document.getElementById('code-battle-quest-boss-fight-textarea').value}
        ${document.getElementById('code-validation-test-function').value}
      `;
      try {
        const evaluationResult = eval(program);
        questionText = `${questionText}so that calling "${document.getElementById('code-validation-test-function').value}" `;
        questionText = `${questionText}will return ${evaluationResult}`
        $('#evaluation-result-text').html(`Great, everything seems to work properly. The text of your question will be: <br/> <i><strong class="text-primary">${questionText}</strong></i>.`);
        $($('.boss_fight_question')[0]).find('input[name="question[]"]').val(questionText);
        $('#boss-fight-answer').val(`${document.getElementById('code-validation-test-function').value}---BOSS-FIGHT-ANSWER-DELIMITER---${evaluationResult}`);
        // $(evaluationResultText).insertAfter(e.target);
      } catch (err) {
        _alert(err);
      }
    });
    return true;
  }
};

function realTimeCodeValidation(e) {
  try {
    const parseResult = acorn.parse(e.target.value);
    const codeBody = parseResult.body;
    if (codeBody.length === 1) {
      const funct = _.find(codeBody, { type: "FunctionDeclaration" });
      const otherInfo = {
        name: funct.id.name,
        paramsNumber: 0,
      }
      updateCodeValidationOutput('ok', 'Great!', 'Your code seems to be valid', otherInfo);
      const functBody = funct.body;
      const functParams = funct.params;

      if (_.filter(functBody.body, { type: "FunctionDeclaration" }).length > 0) {
        updateCodeValidationOutput('error', 'No nested functions!', 'Currently, nested functions are not allowed');
      } else if (functParams.length > 0) {
        otherInfo.paramsNumber = functParams.length;
        updateCodeValidationOutput('ok', 'Great!', 'Your code seems to be valid', otherInfo);
      }

    } else if (codeBody.length > 1) {
      updateCodeValidationOutput('error', 'Too many stuffs!', 'Currently, only one function is allowed for the battle code quest!');
    } else {
      updateCodeValidationOutput('error', 'Too many functions!', 'Currently, only one function is allowed for the battle code quest!');
    }
  } catch (err) {
    if (err.name === 'SyntaxError') {
      updateCodeValidationOutput('error', 'Syntax Error!', 'It seems that your code contains errors. Please fix them!')
    }
  }
};

$(document).ready(function() {
  const QUESTIONS_LIMIT = 10;
  const ANSWERS_LIMIT = 5;
  const question_template = $('.form-group.question:first').clone();
  const answer_template = question_template.children('span:last').clone();

  /**
   * Templates for questions and answers in code battle quest style
  */
  const question_type_select_template = `
    <div class="question_type_select_container form-group">
      <label class="form__label" for="question_type">${gettext('Question Type')}</label>
      <i class='fa fa-info-circle' data-placement="bottom" data-toggle="tooltip" data-html="true" title="
        <p>
          In code battle fight quests you can choose between two question types:
        </p>
        <p>
          <strong>Quiz: </strong> the usual question type. You can supply a question and multiple answer options.
        </p>
        <p>
          <strong>Boss Fight: </strong> here you will not be allowed to write your question text. You will need to write a sample
          function and a test function to evaluate it. If everything works properly, the text of your question and the correct answer
          will be full-filled automatically. You are allowed to write only one boss fight question per quest.
        </p>
      "></i>
      <select name="question_type" class="select2 question_type_select">
        <option value="quiz_question" selected="selected">Quiz</option>
        <option value="boss_fight_question">Boss Fight</option>
      </select>
    </div>
  `;
  const boss_fight_answer_template = `
    <hr>
    <div class="boss_fight_language_select_container form-group">
      <label class="form__label" for="answer_language[]">${gettext('Boss Fight Code Language')}</label>
      <select name="answer_language[]" class="select2 boss_fight_language_select">
      <option value="boss_fight_language_javascript" selected="selected">Javascript</option>
      <option value="boss_fight_language_solidity" disabled>Solidity - coming soon - </option>
      </select>
    </div>
    <span>
      <label class="form__label" for="points">${gettext('Insert the code for the boss fight')}</label>
      <textarea id="code-battle-quest-boss-fight-textarea" class="form__input" cols="50" rows="10" required></textarea>
    </span>
    <div id="code-validation-output" class="card text-white bg-success mb-3">
      <div id="code-validation-output-title" class="card-header">Start writing your code!</div>
      <div class="card-body">
        <p id="code-validation-output-text" class="card-text">Fill up the textarea above with your code. You are allowed to insert only one function. You'll see outputs of validation of your code here.</p>
      </div>
    </div>
    <hr>
  `;
  const question_code_battle_template = question_template.clone();
  const seconds_to_respond_label = question_code_battle_template.find('label')[1];

  if (question_code_battle_template.find('.question_type_select').length === 0) {
    $(question_type_select_template).insertBefore(seconds_to_respond_label);
  }

  /**
   * Controllers fot questions and answers in code battle quest style
   */
  // when question type is changed, updates the question templates and the answers template
  $(document).on('change', '.question_type_select', function(e) {
    e.preventDefault();
    // creates a new question battle code clone
    const new_question_code_battle = question_code_battle_template.clone();
    $(new_question_code_battle).find('input[name="question[]"]').val('').prop('disabled', true);

    // quiz type selected
    if (e.target.value === 'quiz_question') {
      // set 'quiz question' to the question type
      // new_question_code_battle.find('.form__input.question_type').val('quiz_question');
      // removes the current question and replace it with a fresh one
      $(e.target.parentNode.parentNode).replaceWith(new_question_code_battle);
      return false;
    }
    // boss fight selected
    // do nothing if the quest already contains a battle fight question
    if ($('.form__input.question_type[value=boss_fight_question]').length > 0 && e.target.value === 'boss_fight_question') {
      alert(gettext('A Code Battle Quest can have only one Boss Fight question'));
      $(e.target).val('quiz_question');
      return false;
    }
    // sets the class of the question to boss_fight_question
    new_question_code_battle.toggleClass('boss_fight_question');
    // removes all answers
    new_question_code_battle.find('span').remove();
    // removes the add answer button
    new_question_code_battle.find('.add_answer').remove();
    // set 'boss fight' to the question type
    new_question_code_battle.find('.form__input.question_type').val('boss_fight_question');
    // insert the text area for the boss fight code
    $(boss_fight_answer_template).insertAfter(new_question_code_battle.find('.form__input')[2]);
    new_question_code_battle.find('option[value=boss_fight_question]').attr('selected', 'selected');
    $(e.target.parentNode.parentNode).replaceWith(new_question_code_battle);

    const textArea = document.getElementById('code-battle-quest-boss-fight-textarea');
    $(textArea).keyup(debounce(realTimeCodeValidation, 250));

    $('[data-toggle="tooltip"]').bootstrapTooltip();
  });


  $(document).on('form#newkudos', 'submit', function(e) {
    // e.preventDefault();
    // console.log($(this).formdata);
    // alert('hi');

  });

  /**
   * Controller for question style selection
   */
  $(document).on('change', '#quest-style', function(e) {
    e.preventDefault();
    // removes all questions that were previously created
    $(e.target.parentNode.parentNode).find('.form-group.question').remove();
    if (e.target.value === 'Code Battle') {
      $('.questions-container').append(question_code_battle_template);
      // $(question_code_battle_template).insertBefore($(e.target.parentNode.parentNode).find('.add_question')[0]);
      return;
    }
    $('.questions-container').append(question_template);
    // $(question_template).insertBefore($(e.target.parentNode.parentNode).find('.add_question')[0]);
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
    // gets the current question
    const current_question = $(e.target.parentNode);

    // happens when a new question is created in quiz style
    if ($('#quest-style')[0].value !== 'Code Battle') {
      current_question.after(question_template.clone());
      $('[data-toggle="tooltip"]').bootstrapTooltip();
      return;
    }
    // happens when a new question is created in the code battle style
    current_question.after(question_code_battle_template.clone());
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
    var ele = $(e.target.parentNode);

    ele.remove();
  });

});
