const openChat = () => {
  $('[data-openchat]').each(function(index, elem) {
    let chatWindow;
    $(elem).on('click', function() {
      let user = $(elem).data('openchat');
      let url = user ? `https://chat.gitcoin.co/gitcoin/messages/@${user}` : `https://chat.gitcoin.co/`;

      chatWindow = window.open(url, 'Loading', 'top=0,left=0,width=400,height=600,status=no,toolbar=no,location=no,menubar=no,titlebar=no');

    });
  })
}
openChat();
