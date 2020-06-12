(async function($) {
  // doc ready
  let teams = {};
  let lookupExpiry;

  try {
    lookupExpiry = localStorage['chatTeamsExpiry'] ? moment().isAfter(localStorage['chatTeamsExpiry']) : true;

    // teams = localStorage['chatTeams'] ? JSON.parse(localStorage['chatTeams']) : {};

  } catch (e) {
    teams = {};
    lookupExpiry = false;
  }


  // if (!teams.length || lookupExpiry) {
  if (document.contxt.chat_url && document.contxt.chat_access_token) {
    $.ajax({
      beforeSend: function(request) {
        request.setRequestHeader('Authorization', `Bearer ${document.contxt.chat_access_token}`);
      },
      url: `${document.contxt.chat_url}/api/v4/teams`,
      dataType: 'json',
      success: (response) => {
        if (!response) {
          console.log('ahh something failed');
        } else {

          for (let i in response) {
            if (!response[i]) {
              continue;
            }
            let key = response[i].id;

            teams[key] = response[i];
          }
          localStorage['chatTeamsExpiry'] = moment().add(1, 'days').format('MMMM Do YYYY, h:mm:ss');

          window.teams = teams;
        }
      },
      error: (error => {
        console.log(error);
      })
    });
  }
  // }


  document.domain = 'androolloyd.com'; // TODO: set this to be the proper value, as well as in the chat application
  window.testData = [];
  let loginWindow = null;
  let requestedNotificationPermission = false;

  const formatMessage = (channelData, postData) => {
    try {
      let title = '';

      switch (channelData.channel_type) {
        case 'D':
          title = 'Direct Message';
          break;
        default:
        case 'O':
        case 'P':
          title = channelData.channel_display_name;
          break;
      }
      let team = channelData.team_id ? teams[channelData.team_id] : {name: 'gitcoin'}; // TODO: move this to a default setting
      let channel = `/${team.name}/channels/${channelData.channel_name}`;
      let body = postData.message;
      let onClick = () => {
        window.chatSidebar.chatWindow(channel);
      };
      let requireInteraction = false;
      let silent = false;

      return {
        title,
        channel,
        body,
        onClick,
        requireInteraction,
        silent
      };
    } catch (e) {
      console.log(e);
    }
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
    // let icon = icon50;
    //
    // if (UserAgent.isEdge()) {
    //   icon = iconWS;
    // }


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
  };

  $(() => {
    window.chatSidebar = new Vue({
      delimiters: [ '[[', ']]' ],
      el: '#sidebar-chat-app',
      methods: {
        checkChatNotifications: function() {
          let vm = this;

          $.ajax({
            beforeSend: function(request) {
              request.setRequestHeader('Authorization', `Bearer ${document.contxt.chat_access_token}`);
            },
            url: `${document.contxt.chat_url}/api/v4/users/me/teams/unread`,
            dataType: 'json',
            success: (JSONUnread) => {
              let notified = false;
              let unread = 0;

              JSONUnread.forEach((team) => {
                vm.unreadCount += team.msg_count + team.mention_count;
              });
            },
            error: (error => {
              console.log(error);
            })
          });
        },
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
            newChannel = `${vm.chatURL}${channel}`;
          }
          vm.chatURLOverride = newChannel;
          vm.open();

        },
        open: function() {
          if (!this.isVisible) {
            this.$root.$emit('bv::toggle::collapse', 'sidebar-chat');
          }
        },
        showHandler: function(event) {
          this.isLoading = true;
        },
        changeHandler: function(visible) {
          this.isLoading = visible;
          this.isVisible = visible;
        },
        chatAppOnload: function(iframe) {
          let vm = this;

          $(iframe.contentDocument).ready(() => {
            if (vm.isLoggedIn) {
              setTimeout(() => {
                vm.isLoading = false;
              }, 500);
            }
          });

          vm.iframe = iframe;
        }
      },
      updated() {
        if (vm.isLoggedIn && vm.isVisible) {
          vm.isLoading = true;
        }
      },
      destroy() {
        vm.iframe = null;
      },
      created() {
        let vm = this;

        this.$nextTick(function() {
          vm.checkChatNotifications();
          vm.socket = new WebSocket(`wss://${vm.chatURL.replace(/(^\w+:|^)\/\//, '')}/api/v4/websocket`);

          vm.socket.onmessage = function(messageEvent) {
            if (document.activeElement !== vm.iframe) {
              if (vm.isLoggedIn && event.type && event.type === 'message') {
                try {
                  let msgData = JSON.parse(messageEvent.data);

                  if (msgData.event === 'posted') {
                    let channelData = msgData.data;
                    let postData = JSON.parse(channelData.post);

                    if (postData.user_id !== document.contxt.chat_id) {
                      let formattedNotification = formatMessage(channelData, postData);

                      showNotification(formattedNotification).then();
                    }

                  }
                } catch (e) {
                  console.log(e);
                }
              } else {
                vm.isLoading = false;
                vm.isLoggedIn = true;
              }
            }

          };
          vm.socket.onclose = function(event) {
            vm.socket.removeEventListener('close', vm.socket.onclose);
            if (event.code !== 1000 && !loginWindow && !vm.isLoggedIn) {
              loginWindow = window.open(vm.chatLoginURL, 'Loading', 'top=0,left=0,width=400,height=600,status=no,toolbar=no,location=no,menubar=no,titlebar=no');
            }
          };
        });
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
        const isMobile = (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i).test(navigator.userAgent);

        return {
          isMobile,
          unreadCount: 0,
          hasFocus: false,
          isVisible: false,
          iframe: null,
          renderKey: 'chat-iframe',
          socket: null,
          isLoading: true,
          isLoggedIn: false,
          chatURLOverride: null,
          mediaURL: window.media_url,
          chatURL: document.contxt.chat_url
        };
      }
    });
  });

})(jQuery);
