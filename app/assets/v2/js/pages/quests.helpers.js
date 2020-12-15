const sleep = (milliseconds) => {
  return new Promise(resolve => setTimeout(resolve, milliseconds));
};

var trim_dots = function(_str, _chars) {
  if (_str.length > _chars) {
    _str = _str.substring(0, _chars) + '....';
  }
  return _str;
};

var show_prize = function() {
  var prize_info = '';

  if (document.reward_tip['token_amount']) {
    prize_info = '<strong>' + document.reward_tip['token_amount'] + ' ' + document.reward_tip['token'] + '</strong>';
  } else {
    prize_info = '<img src=' + document.kudos_reward['img'] + '>';
  }

  var kudos_html = "<div class='tl prize'><span>🏆Quest Prize🏅</span>" + prize_info + '</div>';

  $('#gameboard').append(kudos_html);
};

var random_taunt_effect = function(ele) {
  if (ele.data('effect')) {
    return;
  }
  ele.data('effect', 1);
  var r = Math.random();

  if (r < 0.3) {
    ele.effect('shake');
  } else if (r < 0.6) {
    ele.effect('pulsate');
  } else if (r < 0.8) {
    ele.effect('bounce');
  } else {
    ele.effect('highlight');
  }
  setTimeout(function() {
    ele.data('effect', 0);
  }, 1000);
};

var post_state = async(data) => {
  const location = document.location.href.replace('#', '') + '?answers=' + JSON.stringify(data);
  const settings = {
    method: 'POST',
    cache: 'no-cache',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  };

  try {
    const fetchResponse = await fetch(location, settings);
    const data = await fetchResponse.json();

    return data;
  } catch (e) {
    return e;
  }

};

var toggle_character_class = async function(sel, classes) {
  for (var k = 0; k < 5; k += 1) {
    await sleep(200);
    sel.addClass(classes[0]).removeClass(classes[1]);
    await sleep(200);
    sel.addClass(classes[1]).removeClass(classes[0]);
  }
  await sleep(500);
  await sel.removeClass(classes[0]);
  await sel.removeClass(classes[1]);
};

function typeWriter() {
  if (document.typewriter_i == 0) {
    document.typewriter_offset = 0;
    document.is_typewriter = true;
  }
  if (document.typewriter_offset + document.typewriter_i < document.typewriter_txt.length) {
    var char = document.typewriter_txt.charAt(document.typewriter_i);

    if (char == '*') {
      char = '<BR>';
      document.typewriter_offset += 3;
    }
    document.getElementById(document.typewriter_id).innerHTML += char;
    document.typewriter_i++;
    setTimeout(typeWriter, document.typewriter_speed);
  } else {
    document.is_typewriter = false;
  }
}

var wait_for_typewriter = async function() {
  while (document.is_typewriter) {
    await sleep(100);
  }
};

var get_midi = function(name) {
  return '/static/v2/audio/' + name + '.mid';
};

var start_music_midi = function(name) {
  // get_audio('bossmusic.mid').play();
  if (!document.music_enabled) {
    return;
  }
  if (typeof MIDIjs == 'undefined') {
    return;
  }
  try {
    MIDIjs.play(get_midi(name));
  } catch (e) {
    console.error(e);
  }
};
var resume_music_midi = function(name) {
  // get_audio('bossmusic.mid').play();
  if (typeof MIDIjs == 'undefined') {
    return;
  }
  MIDIjs.resume();
};
var pause_music_midi = function(name) {
  // get_audio('bossmusic.mid').play();
  if (typeof MIDIjs == 'undefined') {
    return;
  }
  MIDIjs.pause();
};
var orb_state = function(state) {
  var src = '/static/v2/images/quests/orb-' + state + '.svg';

  $('img.orb').attr('src', src);
};

$(document).ready(function() {

  $('body').keyup(function(e) {
    // 1-10
    if (e.keyCode >= 49 && e.keyCode < 59 && document.quiz_started) {
      var selected = e.keyCode - 48;

      $('#desc .answer:nth-child(' + selected + ')').toggleClass('selected');

    }
    // space
    // enter
    if (e.keyCode == 32 || e.keyCode == 13) {
      if (!document.quiz_started) {
        advance_to_state(document.quest_state + 1);
      } else {
        $('#cta_button a').click();
      }
      document.typewriter_speed = 40;
      e.preventDefault();
      
    }
  });
  $('body').keydown(function(e) {
    // space
    // enter
    if (e.keyCode == 32 || e.keyCode == 13) {
      document.typewriter_speed = 5;
      e.preventDefault();
      
    }
  });

  $('#cta_button a').on('click', function(e) {
    var target = $(this).attr('href');

    if (target == '#') {
      e.preventDefault();
      $('#cta_button').addClass('hidden');
      advance_to_state(document.quest_state + 1);
    }
  });

  $('.music_toggle').on('click', function(e) {
    e.preventDefault();
    document.music_enabled = !document.music_enabled;
    if (document.music_enabled) {
      $(this).html('Sound On 🎵');
      $(this).addClass('on');
      resume_music_midi();
    } else {
      $(this).html('Sound Off 🔕');
      $(this).addClass('off');
      pause_music_midi();
    }
  });

  $('.skip_intro').on('click', async function(e) {
    e.preventDefault();
    $(this).remove();
    document.typewriter_speed = 5;
    while (document.state_transitioning) {
      await sleep(10);
    }
    document.quest_state = 3;
    advance_to_state(document.quest_state + 1);
  });


  $('.give_feedback').on('click', async function(e) {
    e.preventDefault();
    var feedback = prompt('Any comments for the quest author? (optional)', '');
    var polarity = $(this).data('direction');
    
    var params = {
      'polarity': polarity,
      'feedback': feedback
    };
    var url = document.quest_feedback_url;

    $.post(url, params, function(response) {
      _alert('Thank you for your feedback on this quest.', 'success');
      $('#vote_container').remove();
    });
  });


  if (document.quest) {
    start_quest();
  }
});
