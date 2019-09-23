$(document).ready(function() {

  const sleep = (milliseconds) => {
    return new Promise(resolve => setTimeout(resolve, milliseconds))
  };

  function typeWriter() {
    if(document.typewriter_i==0){
      document.typewriter_offset = 0;
    }
    if (document.typewriter_offset + document.typewriter_i < document.typewriter_txt.length) {
      var char = document.typewriter_txt.charAt(document.typewriter_i);
      if (char=="*"){
        char="<BR>"; 
        document.typewriter_offset += 3;
      }
      document.getElementById(document.typewriter_id).innerHTML += char;
      document.typewriter_i++;
      setTimeout(typeWriter, document.typewriter_speed);
    }
  }

  var advance_to_state = async function(new_state){

    // setup
    if(document.state_transitioning){
      return;
    }
    
    // confirm
    if(new_state == 4){
      var sure = confirm('are you sure?  make sure you study up. if you fail the quest, you cannot try again until after the cooldown period (4 hours).')
      if(!sure){
        return;
      }
    }

    document.state_transitioning = true;

    var old_state = document.quest_state;

    // generic pre-state transition hooks
    await $('#header').fadeOut();
    await sleep(500);
    await $('#cta_button').fadeOut();
    document.typewriter_txt = ""
    await $('#desc').fadeOut();
    await sleep(500);

    // custom pre-state transition hooks
    // 2 to 3
    if(old_state == 2){
        start_music_midi('hero');
        await sleep(2000);
        await $('#protagonist').removeClass('hidden');
        for(var i = 0; i<5; i+=1){
          await sleep(200);
          $("#protagonist").addClass('heal');
          await sleep(200);
          $("#protagonist").removeClass('heal');
      }
        await sleep(500);
    }


    // manage state transitoin
    var old_state = document.quest_state;
    console.log("state from to", old_state, new_state);
    document.quest_state = new_state
    $('body').addClass("stage_" + new_state);
    $('body').removeClass("stage_" + old_state);


    // -- individual transitions callbacks --

    // 0 to 1
    if(old_state == 0 && new_state == 1){
      await sleep(1000);
      if(!document.contxt['github_handle']){
        document.location.href = document.location.href.replace("#",'') + "?login=1"
      }
      await $('#header').html("Quest Intro");
      await $('#header').fadeIn();
      await sleep(1000);
      await $('#desc').html("");
      await $('#desc').removeClass('hidden').fadeIn();
      document.typewriter_id = "desc";
      document.typewriter_i = 0;
      document.typewriter_txt = document.quest.game_schema.intro; 
      document.typewriter_speed = 50;
      typeWriter();

      await $('#desc').removeClass('hidden').fadeIn();
      await sleep(1000);
      await $('#cta_button a').html("Continue 🤟");
      await $('#cta_button').fadeIn();
    }// 1 to 2
    else if(old_state == 1){
      await sleep(1000);
      await $('#header').html("Quest Rules");
      await $('#header').fadeIn();
      start_music_midi('boss');
      await sleep(1000);
      await $('#desc').html("");
      await $('#desc').removeClass('hidden').fadeIn();
      document.typewriter_id = "desc";
      document.typewriter_i = 0;
      document.typewriter_txt = document.quest.game_schema.rules; 
      document.typewriter_speed = 50;
      typeWriter();
      await sleep(1500);
      await $('#enemy').removeClass('hidden');
      for(var i = 0; i<5; i+=1){
        await sleep(200);
        $("#enemy").addClass('heal').removeClass('harm');
        await sleep(200);
        $("#enemy").addClass('harm').removeClass('heal');
    }
      await sleep(500);
      await $("#enemy").removeClass('harm');
      await $('#cta_button a').html("Got It 🤙");
      await $('#cta_button').fadeIn();
    }// 2 to 3
    else if(old_state == 2){
      await sleep(1000);
      await $('#header').html("");
      await $('#desc').html("");
      await $('#header').html("Quest Prep");
      await $('#header').fadeIn();
      await sleep(1000);
      await $('#desc').html('');
      var text = "You will be given the following links to prepare for your journey.*"
      var html = '';
      var iterate_me = document.quest.game_schema.prep_materials;
      for(var i=0; i<iterate_me.length; i+=1){
        var ele = iterate_me[i];
        html += "<li><a href="+ele.url+" target=new>"+ele.title+"</a></li>";
      }
      setTimeout(function(){
        var new_html = $('#desc').html() + html;
        $('#desc').html(new_html);
      },4000);
      document.typewriter_id = "desc";
      document.typewriter_i = 0;
      document.typewriter_txt = text; 
      document.typewriter_speed = 50;
      typeWriter();
      await $('#desc').removeClass('hidden').fadeIn();
      await sleep(1000);
      await $('#cta_button a').html("Got It 🤙");
      await $('#cta_button').fadeIn();
    }// 3 to 4
    else if(old_state == 3){
      await $('#enemy').removeClass('hidden');
      start_music_midi('bossmusic');
    }

    // wrap up
    document.state_transitioning = false;

  };

  $('body').keyup(function(e){
   // space
   // enter
   if(e.keyCode == 32 || e.keyCode == 13){
      advance_to_state(document.quest_state+1);
      e.preventDefault();
   }
});

  $('#cta_button').on('click', function(e){
    e.preventDefault()

    advance_to_state(document.quest_state+1)

  })

  $('.music_toggle').on('click', function(e){
    e.preventDefault()
    document.music_enabled = !document.music_enabled;
    if(document.music_enabled){
      $(this).html('Sound On 🎵');
      $(this).addClass('on');
      resume_music_midi();
    } else {
      $(this).html('Sound Off 🔕');
      $(this).addClass('off');
      pause_music_midi();
    }
  })

  $('.skip_intro').on('click', async function(e){
    e.preventDefault();
    $(this).remove();
    while(document.state_transitioning){
      await sleep(10);
    }
    document.quest_state = 2;
    advance_to_state(document.quest_state++);
  })

  var start_quest = function(){
    $("#gameboard #header").html(document.quest['title']);
    document.quest_state = 0;

  };

  var dustbin = function(){
};

  var get_midi = function(name){
    return '/static/v2/audio/'+name+'.mid';
  }

  var start_music_midi = function(name){
    //get_audio('bossmusic.mid').play();
    if(!document.music_enabled){return}
    MIDIjs.play(get_midi(name));
  };
  var resume_music_midi = function(name){
    //get_audio('bossmusic.mid').play();
    MIDIjs.resume();
  };
  var pause_music_midi = function(name){
    //get_audio('bossmusic.mid').play();
    MIDIjs.pause();
  };

  if(document.quest){
    start_quest();
  }
});
