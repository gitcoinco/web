(function ($) {
  // doc ready
  $(() => {
    window.chatSidebar = new Vue({
      delimiters:['[[', ']]'],
      el: '#sidebar-chat-app',
      data: function() {
        return {
          chatURL: document.contxt.chat_url || 'https://chat.gitcoin.co'
        };
      }
    });
  });

})(jQuery);
