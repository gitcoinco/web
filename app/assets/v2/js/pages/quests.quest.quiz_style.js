
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

    for (var d = 0; d < $('.answer.selected').length; d += 1) {
      answers[d] = $('.answer.selected a')[d].innerHTML;
    }
    var response = await post_state({
      'question_number': question_number,
      'answers': answers
    });

    // manage state transition
    console.log('question from', question_number, ' to', question_number + 1);
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
    var $safe_html = $('<ul />');

    for (var i = 0; i < possible_answers.length; i += 1) {
      var ele = possible_answers[i]['answer'];
      var $a = $('<a />').attr('href', '#').text(ele);
      var $li = $('<li />').attr('class', 'answer').append($a);

      $safe_html.append($li);
    }
    $('#enemy .attack').removeClass('hidden');
    setTimeout(function() {
      $('#enemy .attack').addClass('hidden');
    }, 2000);
    $('#enemy').effect('bounce');
    await $('#cta_button a').text('Submit Response 📨');
    await $('#header').text(question);
    await $('#desc').html($safe_html.html());
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

    var safe_reward = $('<div />');

    safe_reward.append(" <BR><BR> If you're successful in this quest, you'll earn this limited edition ");

    safe_reward.append($('<strong>').text(document.kudos_reward['name']));
    safe_reward.append(' Kudos: <BR> <BR> ');
    safe_reward.append($('<img>").attr("style", "height: 250px;width: 220px;').attr('src', document.kudos_reward['img']));
    
    if (document.reward_tip['token']) {
      safe_reward.append(" <BR><BR> If you're successful in this quest, you'll earn ");
      safe_reward.append($('<strong />').text(document.reward_tip['token_amount'] + ' ' + document.reward_tip['token']));
    }

    $('#desc').html($('#desc').html() + safe_reward.html());

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
    var $safe_html = $('<ul />');
    var iterate_me = document.quest.game_schema.prep_materials;

    for (var i = 0; i < iterate_me.length; i += 1) {
      var ele = iterate_me[i];
      var $a = $('<a></a>').text(ele.title).attr('href', ele.url);
      var $li = $('<li></li>').append($a);

      $safe_html.append($li);
    }

    var safe_html = $safe_html.html();

    safe_html += '<BR> Take a moment and read through them. You will have limited time to look things up when the quest starts.';

    document.typewriter_id = 'desc';
    document.typewriter_i = 0;
    document.typewriter_txt = text;
    document.typewriter_speed = 50;
    typeWriter();
    await $('#desc').removeClass('hidden').fadeIn();
    await wait_for_typewriter();
    $('#desc').html($('#desc').html() + safe_html);
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
  if (document.reward_tip['token_amount']) {
    $('#desc').html($('<strong />').text(document.reward_tip['token_amount'] + ' ' + document.reward_tip['token']));
  } else {
    $('#desc').append(span);
    $('#desc').append(
      $('<img>').attr('style', 'height: 250px;width: 220px;').attr('src', document.kudos_reward['img'])
    );
  }

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
  $('#gameboard #header').text(document.quest['title']);
  document.quest_state = 0;
};

$(document).ready(function() {
  var size_background = function() {
    var buffer = 50;

    $('.video-background').css('height', ($(window).height() + buffer) + 'px');
    $('.video-background').css('width', ($(window).width() + buffer) + 'px');
  };

  $(window).resize(size_background);
  size_background();
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

  $(document).on('click', '.answer', function(e) {
    e.preventDefault();
    $(this).toggleClass('selected');
  });

  if (document.quest) {
    start_quest();
  }

});
