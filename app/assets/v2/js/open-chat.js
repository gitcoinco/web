const openChat = () => {
  $('[data-openchat]').each(function(index, elem) {

    $(elem).on('click', function() {
      const user = $(elem).data('openchat'); 
    });
  });
  $('[data-sponser-openchat').each(function(index, elem) {

    $(elem).on('click', function() {
      const sponserChannel = $(elem).data('openchat');
    });
  });
};

openChat();
