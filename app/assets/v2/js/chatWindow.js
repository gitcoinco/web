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
          let vm = this;
          let loginWindow = null;

          vm.socket = new WebSocket(`wss://${vm.chatURL.replace(/(^\w+:|^)\/\//, '')}/api/v4/websocket`);

          vm.socket.onmessage = function(event) {
            vm.socket.removeEventListener('close', vm.socket.onclose);
            vm.socket.removeEventListener('message', vm.socket.onmessage);
            vm.socket.close(1000);
            vm.isLoading = false;
            vm.isLoggedIn = true;
          };

          vm.socket.onclose = function(event) {
            vm.socket.removeEventListener('close', vm.socket.onclose);
            vm.socket.removeEventListener('message', vm.socket.onmessage);
            if (event.code !== 1000 && !loginWindow) {
              loginWindow = window.open(vm.chatLoginURL, 'Loading', 'top=0,left=0,width=400,height=600,status=no,toolbar=no,location=no,menubar=no,titlebar=no');
            }
          };
        }
      },
      computed: {
        chatLoginURL: function() {
          return `${this.chatURL}/oauth/gitcoin/login?redirect_to=${window.location.protocol}//${window.location.host}/chat/login/`;
        },
        loadURL: function() {
          return (this.chatURLOverride !== null) ? this.chatURLOverride : this.chatURL;
        }
      },
      data: function() {
        return {
          renderKey: 'chat-iframe',
          socket: null,
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
