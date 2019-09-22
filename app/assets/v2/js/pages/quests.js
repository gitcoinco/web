$(document).ready(function() {

  var get_audio = function(name){
    return new Audio('/static/v2/audio/'+name+'.wav');
  }

  var start_quest = function(){
    $("#gameboard #header").html(document.quest['title']);

    get_audio('secret-discovery-sound').play();


  };

  if(document.quest){
    start_quest();
  }
});
