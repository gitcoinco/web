const sleep = (milliseconds) => {
  return new Promise(resolve => setTimeout(resolve, milliseconds));
};

var post_state = async (data) => {
  const location = document.location.href.replace('#','');
  const settings = {
      method: 'POST',
      headers: {
          Accept: 'application/json',
          'Content-Type': 'application/json',
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

}

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
  }
}

var get_midi = function(name) {
  return '/static/v2/audio/' + name + '.mid';
};

var start_music_midi = function(name) {
  // get_audio('bossmusic.mid').play();
  if (!document.music_enabled) {
    return;
  }
  MIDIjs.play(get_midi(name));
};
var resume_music_midi = function(name) {
  // get_audio('bossmusic.mid').play();
  MIDIjs.resume();
};
var pause_music_midi = function(name) {
  // get_audio('bossmusic.mid').play();
  MIDIjs.pause();
};

$(document).ready(function() {

  $('body').keyup(function(e) {
    // 1-10
    if (e.keyCode >= 49 && e.keyCode < 59 && document.quiz_started) {
      var selected = e.keyCode - 49;
      console.log(selected)
    }
    // space
    // enter
    if (e.keyCode == 32 || e.keyCode == 13) {
      if(document.quiz_started){
        return;
      } else {
        advance_to_state(document.quest_state + 1);
        e.preventDefault();
      }
    }
  });

  $('#cta_button a').on('click', function(e) {
    e.preventDefault();
    $('#cta_button').addClass('hidden');
    advance_to_state(document.quest_state + 1);

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
    while (document.state_transitioning) {
      await sleep(10);
    }
    document.quest_state = 3;
    advance_to_state(document.quest_state+1);
  });



  if (document.quest) {
    start_quest();
  }
});
