(function($) {
  // doc ready
  $(() => {
    window.chatSidebar = new Vue({
      delimiters:['[[', ']]'],
      el: '#sidebar-chat-app',
      methods: {
        chatWindow: function(channel) {
          let vm = this;
          const dm = channel ? channel.indexOf('@') >= 0 : false;

          channel = channel || 'town-square';
          const hackathonTeamSlug = 'hackathons';
          const gitcoinTeamSlug = 'gitcoin';
          const isHackathon = (document.hackathon_id !== null);

          vm.chatURLOverride = `${vm.chatURL}/${isHackathon ? hackathonTeamSlug : gitcoinTeamSlug}/${dm ? 'messages' : 'channels'}/${channel}`;
          vm.open();
        },
        showHandler: function(visible) {
          let vm = this;

          vm.isLoading = visible;
        },
        open: function() {
          this.$root.$emit('bv::toggle::collapse', 'sidebar-chat');
        },
        chatSocketTest: function(iframe) {
          console.log('hello')
          let vm = this;
          let socket = new WebSocket(`wss://${vm.chatURL.replace(/(^\w+:|^)\/\//, '')}/api/v4/websocket`);

          socket.onmessage = function(event) {
            this.removeEventListener('close', socket.onclose);
            this.removeEventListener('message', socket.onmessage);
            socket.close(1000);
            vm.isLoading = false;
            vm.isLoggedIn = true;
          };

          socket.onclose = function(event) {
            if (event.code !== 1000) {
              this.removeEventListener('close', socket.onclose);
              vm.isLoading = false;
              vm.isLoggedIn = false;
            }
          };
        }
      },
      computed: {
        chatLoginURL: function() {
          return `${this.chatURL}/oauth/gitcoin/login?redirect_to=${window.location}`;
        },
        loadURL: function() {
          return (this.chatURLOverride !== null) ? this.chatURLOverride : this.chatURL;
        }
      },
      data: function() {
        return {
          openChat: false,
          isLoading: true,
          isLoggedIn: false,
          chatURLOverride: null,
          mediaURL: window.media_url,
          chatURL: document.contxt.chat_url || 'https://chat.gitcoin.co'
        };
      }
    });
  });

})(jQuery);
