(async function ($) {
  // doc ready

  document.domain = 'androolloyd.com';
  const lookups = {

  };
  const showNotification = async function(
    {
      title,
      channel,
      body,
      requireInteraction,
      onClick,
      silent
    }
  ) {
    let vm = this;
    // let icon = icon50;
    //
    // if (UserAgent.isEdge()) {
    //   icon = iconWS;
    // }

    let icon = '';

    if (!('Notification' in window)) {
      throw new Error('Notification not supported');
    }

    if (typeof Notification.requestPermission !== 'function') {
      throw new Error('Notification.requestPermission not supported');
    }

    if (Notification.permission !== 'granted' && requestedNotificationPermission) {
      throw new Error('Notifications already requested but not granted');
    }

    requestedNotificationPermission = true;

    let permission = await Notification.requestPermission();

    if (typeof permission === 'undefined') {
      // Handle browsers that don't support the promise-based syntax.
      permission = await new Promise((resolve) => {
        Notification.requestPermission(resolve);
      });
    }

    if (permission !== 'granted') {
      throw new Error('Notifications not granted');
    }

    const notification = new Notification(title, {
      body,
      tag: body,
      icon: 'https://s.gitcoin.co/static/v2/images/helmet.png',
      requireInteraction,
      silent
    });

    if (onClick) {
      notification.onclick = onClick;
    }

    notification.onerror = () => {
      throw new Error('Notification failed to show.');
    };

    // Mac desktop app notification dismissal is handled by the OS
    setTimeout(() => {
      notification.close();
    }, 5000);

    return () => {
      notification.close();
    };
  }

  Notification.requestPermission((response) => {
    console.log(response);
  });
  window.addEventListener('message', async (event) => {
    if (event.data.type === 'iframe-chat-notification' && event.origin === window.chatSidebar.chatURL) {
      let notification = event.data.message;
      console.log(event.data);
      notification.onClick = () => {
        window.chatSidebar.chatWindow(notification.channelLink);
      };
      await showNotification(event.data.message);
    }
  });

  $(() => {
    window.chatSidebar = new Vue({
      delimiters: [ '[[', ']]' ],
      el: '#sidebar-chat-app',
      methods: {

        chatWindow: function(channel) {
          let vm = this;
          const isExactChannel = channel.indexOf('channel');
          const dm = channel ? channel.indexOf('@') >= 0 : false;

          channel = channel || 'town-square';
          const hackathonTeamSlug = 'hackathons';
          const gitcoinTeamSlug = 'gitcoin';
          const isHackathon = (document.hackathon_id !== null);

          let newChannel = '';

          if (!isExactChannel) {
            newChannel = `${vm.chatURL}/${isHackathon ? hackathonTeamSlug : gitcoinTeamSlug}/${dm ? 'messages' : 'channels'}/${channel}`;
          } else {
            newChannel = channel;
          }
          vm.iframe.contentWindow.window.browserHistory.push(newChannel);
          vm.open();

        },
        open: function () {
          if (!this.isVisible) {
            this.$root.$emit('bv::toggle::collapse', 'sidebar-chat');
          }
        },
        changeHandler: function (event) {
          this.isVisible = event;
        },
        chatSocketTest: function (iframe) {
          let vm = this;
          let loginWindow = null;

          vm.iframe = iframe;
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
            if (event.code !== 1000 && !loginWindow && !vm.isLoggedIn) {
              loginWindow = window.open(vm.chatLoginURL, 'Loading', 'top=0,left=0,width=400,height=600,status=no,toolbar=no,location=no,menubar=no,titlebar=no');
            }
          };
        }
      },
      computed: {
        chatLoginURL: function () {
          return `${this.chatURL}/oauth/gitcoin/login?redirect_to=${window.location.protocol}//${window.location.host}/chat/login/`;
        },
        loadURL: function () {
          return (this.chatURLOverride !== null) ? this.chatURLOverride : this.chatURL;
        }
      },
      data: function () {
        return {
          hasFocus: false,
          isVisible: false,
          iframe: null,
          renderKey: 'chat-iframe',
          socket: null,
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
