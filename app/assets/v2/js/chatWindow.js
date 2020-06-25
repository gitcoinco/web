let lookupExpiry;

(async function($) {

  const MAX_WEBSOCKET_FAILS = 7;
  const MIN_WEBSOCKET_RETRY_TIME = 3000; // 3 sec
  const MAX_WEBSOCKET_RETRY_TIME = 300000; // 5 mins

  class WebSocketClient {
    // Copyright (c) 2015-present Mattermost, Inc. All Rights Reserved.
    constructor() {
      this.conn = null;
      this.connectionUrl = null;
      this.sequence = 1;
      this.eventSequence = 0;
      this.connectFailCount = 0;
      this.eventCallback = null;
      this.responseCallbacks = {};
      this.firstConnectCallback = null;
      this.reconnectCallback = null;
      this.missedEventCallback = null;
      this.errorCallback = null;
      this.closeCallback = null;
    }

    initialize(connectionUrl = this.connectionUrl, token) {
      if (this.conn) {
        return;
      }

      if (connectionUrl == null) {
        console.log('websocket must have connection url'); // eslint-disable-line no-console
        return;
      }

      if (this.connectFailCount === 0) {
        console.log('websocket connecting to ' + connectionUrl); // eslint-disable-line no-console
      }

      this.conn = new WebSocket(connectionUrl);
      this.connectionUrl = connectionUrl;

      this.conn.onopen = () => {
        this.eventSequence = 0;

        if (token) {
          this.sendMessage('authentication_challenge', {token});
        }

        if (this.connectFailCount > 0) {
          console.log('websocket re-established connection'); // eslint-disable-line no-console
          if (this.reconnectCallback) {
            this.reconnectCallback();
          }
        } else if (this.firstConnectCallback) {
          this.firstConnectCallback();
        }

        this.connectFailCount = 0;
      };

      this.conn.onclose = () => {
        this.conn = null;
        this.sequence = 1;

        if (this.connectFailCount === 0) {
          console.log('websocket closed'); // eslint-disable-line no-console
        }

        this.connectFailCount++;

        if (this.closeCallback) {
          this.closeCallback(this.connectFailCount);
        }

        let retryTime = MIN_WEBSOCKET_RETRY_TIME;

        // If we've failed a bunch of connections then start backing off
        if (this.connectFailCount > MAX_WEBSOCKET_FAILS) {
          retryTime = MIN_WEBSOCKET_RETRY_TIME * this.connectFailCount * this.connectFailCount;
          if (retryTime > MAX_WEBSOCKET_RETRY_TIME) {
            retryTime = MAX_WEBSOCKET_RETRY_TIME;
          }
        }

        setTimeout(
          () => {
            this.initialize(connectionUrl, token);
          },
          retryTime
        );
      };

      this.conn.onerror = (evt) => {
        if (this.connectFailCount <= 1) {
          console.log('websocket error'); // eslint-disable-line no-console
          console.log(evt); // eslint-disable-line no-console
        }

        if (this.errorCallback) {
          this.errorCallback(evt);
        }
      };

      this.conn.onmessage = (evt) => {
        const msg = JSON.parse(evt.data);

        if (msg.seq_reply) {
          if (msg.error) {
            console.log(msg); // eslint-disable-line no-console
          }

          if (this.responseCallbacks[msg.seq_reply]) {
            this.responseCallbacks[msg.seq_reply](msg);
            Reflect.deleteProperty(this.responseCallbacks, msg.seq_reply);
          }
        } else if (this.eventCallback) {
          if (msg.seq !== this.eventSequence && this.missedEventCallback) {
            console.log('missed websocket event, act_seq=' + msg.seq + ' exp_seq=' + this.eventSequence); // eslint-disable-line no-console
            this.missedEventCallback();
          }
          this.eventSequence = msg.seq + 1;
          this.eventCallback(msg);
        }
      };
    }

    setEventCallback(callback) {
      this.eventCallback = callback;
    }

    setFirstConnectCallback(callback) {
      this.firstConnectCallback = callback;
    }

    setReconnectCallback(callback) {
      this.reconnectCallback = callback;
    }

    setMissedEventCallback(callback) {
      this.missedEventCallback = callback;
    }

    setErrorCallback(callback) {
      this.errorCallback = callback;
    }

    setCloseCallback(callback) {
      this.closeCallback = callback;
    }

    close() {
      this.connectFailCount = 0;
      this.sequence = 1;
      if (this.conn && this.conn.readyState === WebSocket.OPEN) {
        this.conn.onclose = () => {}; // eslint-disable-line no-empty-function
        this.conn.close();
        this.conn = null;
        console.log('websocket closed'); // eslint-disable-line no-console
      }
    }

    sendMessage(action, data, responseCallback) {
      const msg = {
        action,
        seq: this.sequence++,
        data
      };

      if (responseCallback) {
        this.responseCallbacks[msg.seq] = responseCallback;
      }

      if (this.conn && this.conn.readyState === WebSocket.OPEN) {
        this.conn.send(JSON.stringify(msg));
      } else if (!this.conn || this.conn.readyState === WebSocket.CLOSED) {
        this.conn = null;
        this.initialize();
      }
    }

    userTyping(channelId, parentId, callback) {
      const data = {};

      data.channel_id = channelId;
      data.parent_id = parentId;

      this.sendMessage('user_typing', data, callback);
    }

    userUpdateActiveStatus(userIsActive, manual, callback) {
      const data = {
        user_is_active: userIsActive,
        manual
      };

      this.sendMessage('user_update_active_status', data, callback);
    }

    getStatuses(callback) {
      this.sendMessage('get_statuses', null, callback);
    }

    getStatusesByIds(userIds, callback) {
      const data = {};

      data.user_ids = userIds;
      this.sendMessage('get_statuses_by_ids', data, callback);
    }
  }

  const fetchTeams = async() => {
    let teams = {};

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
            localStorage['chatTeams'] = JSON.stringify(teams);
            return teams;
          }
        },
        error: (error => {
          console.log(error);
        })
      });
    }
  };
  let teams = {};

  try {
    // lookupExpiry = localStorage['chatTeamsExpiry'] ? moment().isAfter(localStorage['chatTeamsExpiry']) : true;
    teams = await fetchTeams();
  } catch (e) {
    lookupExpiry = true;
    teams = await fetchTeams();
  }


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
      let body = `${channelData.sender_name}: ${postData.message}`.substr(0, 50);
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

    setTimeout(() => {
      window.chatSidebar.unreadCount++;
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

          if (document.contxt.chat_access_token && document.contxt.chat_url) {
            $.ajax({
              beforeSend: function(request) {
                request.setRequestHeader('Authorization', `Bearer ${document.contxt.chat_access_token}`);
              },
              url: `${document.contxt.chat_url}/api/v4/users/me/teams/unread`,
              dataType: 'json',
              success: (JSONUnread) => {
                let unread = 0;

                JSONUnread.forEach((team) => {
                  unread += team.msg_count + team.mention_count;
                });
                vm.unreadCount = unread;
              },
              error: (error => {
                console.log(error);
              })
            });
          }
        },
        chatWindow: function(channel) {
          let vm = this;
          const isExactChannel = channel.indexOf('channel');
          const dm = channel ? channel.indexOf('@') >= 0 : false;

          channel = channel || 'town-square';
          const hackathonTeamSlug = 'hackathons';
          const gitcoinTeamSlug = 'gitcoin';
          const isHackathon = (document.hackathon_id !== null);

          if (isExactChannel === -1) {
            channel = `/${isHackathon ? hackathonTeamSlug : gitcoinTeamSlug}/${dm ? 'messages' : 'channels'}/${channel}`;
          }

          let openFrame = vm.getOpenFrame();

          if (openFrame.frameWindow && openFrame.frameWindow.isActive) {
            if (openFrame.frameWindow.browserHistory) {
              openFrame.frameWindow.browserHistory.push(channel);
            } else {
              openFrame.frameWindow.location.go(channel);
            }
          } else {
            vm.chatURLOverride = `${vm.chatURL}${channel}`;
            vm.open();
          }

        },
        open: function() {
          if (!this.isVisible) {
            this.$root.$emit('bv::toggle::collapse', 'sidebar-chat');
          }
        },
        socketSessionLoginTest: function() {
          let vm = this;

          let client = new WebSocketClient();

          client.setFirstConnectCallback(() => {
            vm.isLoggedInFrame = true;
            vm.frameLoginAttempting = false;
            vm.isLoading = false;
          });
          client.setCloseCallback((closeMsg) => {
            vm.isLoggedInFrame = false;
            vm.frameLoginAttempting = true;
            vm.isLoading = true;
            vm.chatLogin();
          });

          client.initialize(vm.chatSocketURL);
        },
        chatLogin: function() {
          let vm = this;

          if (!vm.loginWindow) {
            vm.loginWindow = window.open(vm.chatLoginURL, 'Loading', 'top=0,left=0,width=400,height=600,status=no,toolbar=no,location=no,menubar=no,titlebar=no');
          }
        },
        getOpenFrame: function() {

          let $frameElement = $(vm.iframe);
          let frameElement = $frameElement[0];
          let frameContents = $frameElement.contents();
          let frameWindow = (frameElement && frameElement.contentWindow && frameElement.contentWindow.window) ? frameElement.contentWindow.window : null;

          return {
            frameElement,
            frameWindow,
            frameContents
          };
        },
        showHandler: function(event) {
          this.isLoading = true;
        },
        hideHandler: function(event) {
          this.isLoggedInFrame = false;
          this.iframe = null;
        },
        changeHandler: function(visible) {
          this.isLoading = visible;
          this.isVisible = visible;
        },
        iframeOnFocus: function() {
          vm.iframeHasFocus = true;
        },
        chatAppOnLoad: function(iframe) {
          let vm = this;

          vm.iframe = iframe;

          vm.$watch('isLoggedInFrame', function(newVal) {
            if (newVal && vm.validSessionInterval) {
              clearInterval(vm.validSessionInterval);
            }
          });
          let count = 0;

          $(iframe)
            .contents().find('head')
            .append($('<style type="text/css">.scrollbar--view {overflow:auto !important;}</style>')
            );
          $(iframe).contents().ready(() => {

            vm.validSessionInterval = setInterval(() => {

              try {
                if (!vm.isLoggedInFrame) {

                  if (!vm.frameLoginAttempting) {

                    if (vm.iframe) {

                      let openFrame = vm.getOpenFrame();

                      if (openFrame.frameWindow.location.pathname === '/login' || count >= 5) {
                        count = 0;
                        vm.frameLoginAttempting = true;
                        vm.chatLogin();

                      } else if (openFrame.frameWindow.location.pathname === '/select_team' || openFrame.frameContents.find('#sidebarSwitcherButton').length > 0) {
                        vm.isLoggedInFrame = true;
                        vm.frameLoginAttempting = false;
                        vm.isLoading = false;
                        clearInterval(vm.validSessionInterval);
                      } else {
                        count++;
                      }
                    } else {
                      vm.socketSessionLoginTest();
                    }
                  } else {
                    clearInterval(vm.validSessionInterval);
                  }
                } else {
                  clearInterval(vm.validSessionInterval);
                }
              } catch (e) {
                clearInterval(vm.validSessionInterval);
                vm.socketSessionLoginTest();
              }
            }, 1000);

          });

        }
      },
      destroy() {
        vm.iframe = null;
        clearInterval(vm.validSessionInterval);
      },
      created() {
        let vm = this;

        setInterval(() => {
          vm.checkChatNotifications();
        }, 15000);
        let client = new WebSocketClient();

        client.setEventCallback((msgData) => {

          if (vm.isLoggedInClient && msgData.event === 'posted') {
            try {

              let openFrame = vm.getOpenFrame();

              if (!(vm.iframe && openFrame.frameWindow && openFrame.frameWindow.isActive)) {
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
          }
        });
        client.setFirstConnectCallback(() => {
          vm.isLoggedInClient = true;
        });
        client.setCloseCallback((closeMsg) => {
          vm.isLoggedInClient = false;
        });
        client.setReconnectCallback((msg) => {
          vm.isLoggedInClient = true;
        });
        client.initialize(vm.chatSocketURL, document.contxt.chat_access_token);

        vm.socket = client;
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
          validSessionInterval: false,
          frameHasFocus: false,
          frameLoginAttempting: false,
          chatSocketURL: `wss://${document.contxt.chat_url.replace(/(^\w+:|^)\/\//, '')}/api/v4/websocket`,
          unreadCount: 0,
          hasFocus: false,
          isVisible: false,
          iframe: null,
          renderKey: 'chat-iframe',
          socket: null,
          isLoading: true,
          isLoggedInClient: false,
          isLoggedInFrame: false,
          chatURLOverride: document.chat_url_override || null,
          mediaURL: window.media_url,
          chatURL: document.contxt.chat_url
        };
      }
    });
  });

})(jQuery);
