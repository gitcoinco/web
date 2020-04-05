/* function debounce(fn, time){
  let timeout;

  return function() {
    const functionCall = () => fn.apply(this, arguments);

    clearTimeout(timeout);
    timeout = setTimeout(functionCall, time);
  }
} */

function updateHints(type, title, text, otherInfo) {
  const hintsContainer = $('#hints-boss-fight-answer-container');
  const hintsTitle = $('#hints-boss-fight-answer-title');
  const hintsText = $('#hints-boss-fight-answer-text');
  hintsTitle.html(title);
  hintsText.html(text);

  if (type === 'error') {
    hintsContainer.addClass('hints-color-red').removeClass('hints-color-white');
  } else if (type === 'ok') {
    hintsContainer.addClass('hints-color-white').removeClass('hints-color-red');
    return true;
  }
};

function realTimeCodeValidation(e) {
  try {
    let canContinue = true;
    const parseResult = acorn.parse(e.target.value, /* {
      onToken: function (t) {
        console.log(t);
      }
    } */);
    /* var tokens = [...acorn.tokenizer(e.target.value)];
    for (let i = 0; i <= tokens.length; i++) {
      if (tokens[i].value === 'return' && tokens[i + 1]) {
        const nextToken = tokens[i + 1];
        if (nextToken.value === e.data.testResult) {
          updateHints('error', 'DO NOT TRY TO CHEAT HIM!', `He will destroy you if you try to cheat him ... Are you using a simple "return ${nextToken.value}"? Come on, use your function arguments!`);
          canContinue = false;
        }
      }
    } */


    // things that must be avoided by players
    acorn.walk.simple(parseResult, {
      /* Function(node) {
        console.log(node);
      }, */
      ReturnStatement(node) {
        if (node.argument.value === e.data.testResult) {
          updateHints('error', 'DO NOT TRY TO USE SIMPLE WEAPONS TO HIM!', `He will destroy you if you use that sample return statement ... Come on do something cleaver (i.e. use your function arguments)!`);
          canContinue = false;
        }
      },
    });
    if (!canContinue) {
      return false;
    }

    const codeBody = parseResult.body;
    if (codeBody.length === 1) {
      const codeTextArea = $('#boss-fight-question').val();
      const program = `${codeTextArea}${e.data.testFunction}`;

      const funct = _.find(codeBody, { type: "FunctionDeclaration" });
      const functParams = funct.params;
      const functName = funct.id.name;
      if (functParams.length !== Number(e.data.testParams)) {
        updateHints('error', 'Wrong Code!', `No no no! Your function accepts ${functParams.length} params, not exactly what you need to defeat the boss! Read carefully the question and fix it! Come on!`);
        return false;
      }
      if (functName !== e.data.testFunctName) {
        updateHints('error', 'Wrong Code!', `No no no! Your function name is "${functName}", not exactly what you need to defeat the boss! Read carefully the question and fix it! Come on!`);
        return false;
      }
      try {
        const evaluationResults = eval(program);
        $('#boss-fight-question-answer').val(evaluationResults);
        if (evaluationResults === e.data.testResult) {
          updateHints('ok', 'Great!', 'Your code can defeat the boss! Submit it and smash the boss\' mouth');
          return true;
        } else {
          updateHints('error', 'Wrong Code!', `No no no! Your code returns "${evaluationResults}", not exactly what you need to defeat the boss! Fix it! Hurry up!`);
          return false;
        }
      } catch (err) {
        updateHints('error', 'Wrong Code!', 'Hey! Your code is not the correct one to defeat the boss! Fix it! Hurry up!');
        return false;
      }
    } else {
      updateHints('error', 'Strange Code!', 'Hey this will not work! Are you sure that all your code is wrapped in only one function? Fix your code! Hurry up!');
      return false;
    }
  } catch (err) {
    // console.log(err);
    if (err.name === 'SyntaxError') {
      updateHints('error', 'Syntax Error!', 'Hey this will not work! Fix it! Hurry up!');
      return false;
    }
  }
};

var start_quiz = async function() {
  document.quiz_started = true;
  var question_number = 0;
  var should_continue = true;

  start_music_midi(document.music);
  await sleep(1500);

  while (should_continue) {
    orb_state(Math.min(question_number + 1, 4));
    document.submitted_answer = false;
    var answers = [];
    var question_count = document.num_questions;

    // if the question is not of type boss_fight_question get the answers
    // if the question is of type boss_fight_question extracts and trims the code before sending it to the server
    for (var d = 0; d < $('.answer.selected').length; d += 1) {
      if ($('.answer.selected')[d].id !== 'boss-fight-question-answer') {
        answers[d] = $('.answer.selected a')[d].innerHTML;
      } else {
        answers.push($('#boss-fight-question-answer').val());
      }
    }
    var response = await post_state({
      'question_number': question_number,
      'answers': answers
    });

    // manage state transition
    for (var p = 0; p < 10; p += 1) {
      $('body').removeClass('question_number_' + p);
    }
    $('body').addClass('question_number_' + question_number);

    question_number += 1;
    var can_continue = response['can_continue'];
    var did_win = response['did_win'];

    if (did_win) {
      // won the game
      await winner(response['prize_url']);
      return;
    } else if (!can_continue) {
      // ded
      await death();
      return;
    }

    if (answers.length) {
      // got a question right
      $('#protagonist .heal').removeClass('hidden');
      setTimeout(function() {
        $('#protagonist .heal').addClass('hidden');
      }, 2000);
      await toggle_character_class($('#protagonist'), [ 'heal', '' ]);
      await toggle_character_class($('#enemy'), [ 'harm', '' ]);
    }

    var question_level_seconds_to_respond = response['question']['seconds_to_respond'];
    var prefix = '(' + question_number + '/' + question_count + ') - ';
    var question = prefix + response['question']['question'];
    var possible_answers = response['question']['responses'];

    var html = '';

    // if the question is not of type boss_fight_question loads the answers
    // if the question is of type boss_fight_question creates the text area for inserting the CODE
    if (response['question']['question_type'] !== 'boss_fight_question') {
      for (var i = 0; i < possible_answers.length; i += 1) {
        var ele = possible_answers[i]['answer'];

        html += '<li class=answer>(' + (i + 1) + ') <a href=#>' + ele + '</a></li>';
      }
    } else {
      html += '<textarea id="boss-fight-question" placeholder="Insert the code to fight the boss" cols="71" rows="20"></textarea>';
      html += '<input id="boss-fight-question-answer" class="answer selected" type="hidden" />';
      html += `<div id="hints-boss-fight-answer-container" class="hints-color-white">
        <p>
          <img id="hints-concierge-img" src="/static/v2/images/quests/enemies/helpful_guide.svg">
          <span id="hints-boss-fight-answer-title">
          Hurry up! Start writing your code, I will give you helpful hints here!</span>
          <span id="hints-boss-fight-answer-text"></span>
        </p>
      </div>`
    }


    $('#enemy .attack').removeClass('hidden');
    setTimeout(function() {
      $('#enemy .attack').addClass('hidden');
    }, 2000);
    $('#enemy').effect('bounce');
    await $('#cta_button a').html('Submit Response 📨');
    await $('#header').html(question);
    await $('#desc').html(html);

    // do stuffs when the question is the boss fight question
    const textArea = document.getElementById('boss-fight-question');
    if (textArea) {
      const testFunction = possible_answers[0].answerTokenized[0];
      const testResult = possible_answers[0].answerTokenized[1];
      const testParams = possible_answers[0].answerTokenized[2];
      const testFunctName = possible_answers[0].answerTokenized[3];
      $(textArea).keyup({
        testFunction: testFunction,
        testResult: testResult,
        testParams: testParams,
        testFunctName: testFunctName,
      }, realTimeCodeValidation);
    }


    await $('#header').removeClass('hidden').fadeIn();
    await $('#desc').removeClass('hidden').fadeIn();
    await $('#cta_button').removeClass('hidden').fadeIn();
    var seconds_per_question = question_level_seconds_to_respond != undefined ? question_level_seconds_to_respond : document.seconds_per_question;
    var timer = seconds_per_question * 1000;

    while (timer > 0 && !document.submitted_answer) {
      await sleep(100);
      if (!document.pause) {
        timer -= 100;
      }
      $('#timer').removeClass('hidden').html(timer / 1000 + 's left');
      if (timer < 7500) {
        $('#timer').addClass('yellow');
      } else if (timer < 2000) {
        $('#timer').addClass('orange');
      } else {
        $('#timer').removeClass('orange').removeClass('yellow').removeClass('red');
      }
    }
    timer = 2 * 1000;

    while (timer > 0 && !document.submitted_answer) {
      await sleep(100);
      timer -= 100;

      $('#timer').addClass('red').html(0 + 's left');
    }
    $('#timer').removeClass('red').html('...');
  }
};


var advance_to_state = async function(new_state) {

  // setup
  if (document.state_transitioning) {
    return;
  }
  if (document.quiz_started) {
    document.submitted_answer = 1;
    return;
  }

  // confirm
  if (new_state == 4) {
    var sure = confirm('are you sure?  make sure you study up. if you fail the quest, you cannot try again until after the cooldown period (' + document.quest['cooldown_minutes'] + ' mins).');

    if (!sure) {
      await $('#cta_button').removeClass('hidden').fadeIn();
      return;
    }
  }

  document.state_transitioning = true;

  var old_state = document.quest_state;

  // generic pre-state transition hooks
  await $('#header').fadeOut();
  await sleep(500);
  await $('#cta_button').fadeOut();
  document.typewriter_txt = '';
  await $('#desc').fadeOut();
  await sleep(500);

  // custom pre-state transition hooks
  // 2 to 3
  if (old_state == 2) {
    start_music_midi('hero');
    await sleep(2000);
    await toggle_character_class($('#protagonist'), [ 'heal', '' ]);
  }

  // manage state transitoin
  console.log('state from', old_state, '/', document.quest_state, ' to', new_state);
  document.quest_state = new_state;
  for (var p = 0; p < 10; p += 1) {
    $('body').removeClass('stage_' + p);
  }
  $('body').addClass('stage_' + new_state);

  // force login
  if (!document.contxt['github_handle']) {
    document.location.href = document.location.href.replace('#', '') + '?login=1';
  }


  // -- individual transitions callbacks --

  // 0 to 1
  var new_html;

  if (old_state == 0 && new_state == 1) {
    await sleep(1000);
    await $('#header').html('Quest Intro');
    await $('#header').fadeIn();
    await sleep(1000);
    await $('#desc').html('');
    await $('#desc').removeClass('hidden').fadeIn();
    document.typewriter_id = 'desc';
    document.typewriter_i = 0;
    document.typewriter_txt = document.quest.game_schema.intro;
    document.typewriter_speed = 30;

    typeWriter();
    await wait_for_typewriter();

    var kudos_reward_html = " <BR><BR> If you're successful in this quest, you'll earn this limited edition <strong>" + document.kudos_reward['name'] + "</strong> Kudos: <BR> <BR> <img style='height: 250px;width: 220px;' src=" + document.kudos_reward['img'] + '>';

    new_html = $('#desc').html() + kudos_reward_html;

    $('#desc').html(new_html);

    await $('#desc').removeClass('hidden').fadeIn();
    await sleep(1000);
    await $('#cta_button a').html('Continue 🤟');
    await $('#cta_button').removeClass('hidden').fadeIn();
  }/* 1 to 2 */ else if (old_state == 1) {
    await sleep(1000);
    await $('#header').html('Quest Rules');
    await $('#header').fadeIn();
    show_prize();
    start_music_midi('boss');
    await sleep(1000);
    await $('#helpful_guide').fadeOut();
    await $('#desc').html('');
    await $('#desc').removeClass('hidden').fadeIn();
    document.typewriter_id = 'desc';
    document.typewriter_i = 0;
    document.typewriter_txt = document.quest.game_schema.rules;
    document.typewriter_speed = 50;
    typeWriter();
    await wait_for_typewriter();
    await sleep(500);
    await $('#enemy').removeClass('hidden');
    await toggle_character_class($('#enemy'), [ 'heal', 'harm' ]);
    await $('#cta_button a').html('Got It 🤙');
    await $('#cta_button').removeClass('hidden').fadeIn();
  }/* 2 to 3 */ else if (old_state == 2) {
    await sleep(1000);
    await $('#header').html('');
    await $('#desc').html('');
    await $('#header').html('Quest Prep');
    await $('#header').fadeIn();
    await sleep(1000);
    await $('#desc').html('');
    var text = 'You will be given the following links to prepare for your journey (est read time: ' + document.quest.game_schema.est_read_time_mins + ' mins ).*';
    var html = '';
    var iterate_me = document.quest.game_schema.prep_materials;

    for (var i = 0; i < iterate_me.length; i += 1) {
      var ele = iterate_me[i];

      html += '<li><a href=' + ele.url + ' target=new>' + ele.title + '</a></li>';
    }
    html += '<BR> Take a moment and read through them. You will have limited time to look things up when the quest starts.';

    document.typewriter_id = 'desc';
    document.typewriter_i = 0;
    document.typewriter_txt = text;
    document.typewriter_speed = 50;
    typeWriter();

    await $('#desc').removeClass('hidden').fadeIn();
    await wait_for_typewriter();
    new_html = $('#desc').html() + html;

    $('#desc').html(new_html);

    await sleep(100);
    await $('#cta_button a').html('Got It 🤙');
    await $('#cta_button').removeClass('hidden').fadeIn();
  }/* 3 to 4 */ else if (old_state == 3) {
    show_prize();
    await $('#helpful_guide').fadeOut();
    await sleep(500);
    $('.skip_intro').remove();
    await $('#enemy').removeClass('hidden');
    start_quiz();

  }

  // wrap up
  document.state_transitioning = false;
};

var death = async function() {
  orb_state('dead');
  $('body').addClass('death');
  $('#protagonist .ded').removeClass('hidden');
  await $('#header').fadeOut();
  await $('#cta_button').fadeOut();
  await $('#desc').fadeOut();
  start_music_midi('dead');
  await toggle_character_class($('#protagonist'), [ 'harm', '' ]);
  await sleep(500);
  await $('.prize').effect('explode');
  await sleep(1000);
  $('#protagonist').effect('explode');
  await sleep(200);
  await $('#header').addClass('fail').fadeIn().html('You Lose - Try again in ' + document.quest['cooldown_minutes'] + ' mins. ');
  await sleep(2500);
  await $('#header').fadeOut();
  await sleep(500);
  await $('#desc').html('<a class=button href=/quests>&lt;&lt; Quests</a><a class="button ml-2" href=/quests/new>Create Quest ^^</a> <a class=button href=/quests/next>Play Next &gt;&gt;</a>').removeClass('hidden').fadeIn();
  setInterval(function() {
    random_taunt_effect($('#enemy'));
  }, 2000);
};

var winner = async function(prize_url) {
  start_music_midi('hero');
  orb_state('final');
  $('body').addClass('winner');
  await sleep(500);
  $('#enemy .ded').removeClass('hidden');
  await $('#header').fadeOut();
  await $('#cta_button').fadeOut();
  await $('#desc').fadeOut();
  await sleep(500);
  $('#enemy').effect('explode');
  await sleep(500);
  await toggle_character_class($('#protagonist'), [ 'heal', '' ]);
  await sleep(500);
  await $('#header').addClass('success').fadeIn().html('You Win');
  var span = '<span style="display:block; font-weight: bold; font-size: 24px;">🏆Quest Prize🏅</span>';

  start_music_midi('secret-discovery');

  $('#desc').html(span + "<img style='height: 250px;width: 220px;' src=" + document.kudos_reward['img'] + '>');
  $('.prize').fadeOut();
  await sleep(500);
  $('#desc').removeClass('hidden');
  $('#desc').fadeIn();
  await sleep(1300);
  $('#desc').fadeOut();
  await sleep(1000);
  $('#cta_button a').attr('href', prize_url).html('Claim Prize 🏆').fadeIn();
  $('#cta_button').css('display', 'block');
  $('#cta_button p').css('display', 'none');
  $('#cta_button').removeClass('hidden');

  var a = $('#cta_button a').clone();

  a.attr('href', '/quests/next');
  a.html('Play Another ▶️');
  a.addClass('ml-3');
  $(a).insertAfter($('#cta_button a'));

  a = $('#cta_button a:first-child').clone();

  a.attr('href', '/quests/new');
  a.html('Create Quest 👨‍💻');
  a.addClass('ml-3');
  a.addClass('hide_on_mobile');
  $(a).insertAfter($('#cta_button a:first-child'));

  setInterval(function() {
    random_taunt_effect($('#protagonist'));
  }, 2000);
};

var start_quest = function() {
  $('#gameboard #header').html('<h3>💻 💾 CODE BATTLE 💾 💻</h3>' + document.quest['title']);
  $('#header').css('background-color', '#13145d');
  document.quest_state = 0;
};

$(document).ready(function() {
  // force the music to load
  setTimeout(function() {
    if (document.quest) {
      start_music_midi(document.music);
      pause_music_midi(document.music);
    }
  }, 100);

  if ($('#protagonist').length) {
    var preload_assets = async function() {
      var items = [ 'stage_4', 'question_number_1', 'question_number_2' ];

      for (var i = 0; i < 3; i += 1) {
        await sleep(10);
        await $('body').addClass(items[i]);
        console.log($('body').attr('class'));
      }
      for (var j = 0; j < 3; j += 1) {
        await sleep(10);
        await $('body').removeClass(items[j]);
      }
    };

    preload_assets();
  }

  $('#protagonist h3').html(trim_dots($('#protagonist h3').text(), 8));

  $(document).on('click', 'li.answer', function(e) {
    e.preventDefault();
    $(this).toggleClass('selected');
  });

  if (document.quest) {
    start_quest();
  }

});
