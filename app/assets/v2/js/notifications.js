let notifications = [];
let page = 1;
let unreadNotifications = [];
let hasNext = false;
let numPages = '';
let numNotifications = '';

Vue.mixin({
  methods: {
    fetchNotifications: function(newPage) {
      var vm = this;

      if (newPage) {
        vm.page = newPage;
      }

      var getNotifications = fetchData (`/inbox/notifications/?page=${vm.page}`, 'GET');

      $.when(getNotifications).then(function(response) {
        newNotifications = newData(response.data, vm.notifications);
        newNotifications.forEach(function(item) {
          vm.notifications.push(item);
        });

        vm.numPages = response.num_pages;
        vm.hasNext = response.has_next;
        vm.numNotifications = response.count;

        vm.checkUnread();
        if (vm.hasNext) {
          vm.page = ++vm.page;

        } else {
          vm.page = 1;
        }
      });
    },
    markAll: function() {
      vm = this;

      vm.notifications.map((notify, index) => {
        notify.is_read = true;
      });
      var toRead = Array.from(vm.unreadNotifications, item => item.id);

      window.sessionStorage.setItem('notificationRead', toRead);
      vm.sendState();
    },
    markRead: function(item) {
      vm = this;
      window.sessionStorage.setItem('notificationRead', item);
    },
    checkUnread: function() {
      vm = this;
      vm.unreadNotifications = vm.notifications.filter(function(elem) {
        if (elem.is_read == false)
          return elem.id;
      });
    },
    sendState: function(toUnread) {
      vm = this;
      var putRead;
      // let toUnread;

      let notificationRead = sessionStorage.getItem('notificationRead');

      notificationRead && notificationRead.length ? notificationRead = notificationRead.split(',').map(String) : notificationRead;
      if (notificationRead) {

        if (toUnread) {
          const unread = Object();

          unread['unread'] = notificationRead;
          let data = JSON.stringify(unread);

          putRead = fetchData ('/inbox/notifications/unread/', 'PUT', data);
        } else {
          const read = Object();

          read['read'] = notificationRead;
          let data = JSON.stringify(read);

          putRead = fetchData ('/inbox/notifications/read/', 'PUT', data);
        }


        vm.notifications.map((notify, index) => {
          if (notificationRead.includes(notify.id))
            notify.is_read = !toUnread;
        });

        $.when(putRead).then(function(response) {
          sessionStorage.removeItem('notificationRead');
          vm.checkUnread();
        });
      }
      vm.checkUnread();

    },
    onScroll: function() {
      vm = this;
      let scrollContainer = event.target;

      if (scrollContainer.scrollTop + scrollContainer.clientHeight >= scrollContainer.scrollHeight) {
        if (vm.page <= vm.numPages) {
          this.fetchNotifications();
        }
      }
    }
  }

});

if (document.getElementById('gc-notifications')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-notifications',
    data: {
      page,
      notifications,
      unreadNotifications,
      hasNext,
      numPages,
      numNotifications
    },
    mounted() {
      this.fetchNotifications();
    },
    created() {
      this.sendState();
    }
  });
}

if (document.getElementById('gc-inbox')) {
  var appInbox = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-inbox',
    data() {
      return {
        page,
        notifications,
        unreadNotifications,
        hasNext,
        numPages,
        numNotifications,
        selectedNotifications: []
      };
    },
    computed: {
      selectAll: {
        get: function() {
          return this.notifications ? this.selectedNotifications.length == this.notifications.length : false;
        },
        set: function(value) {
          var selectedNotifications = [];

          if (value) {
            this.notifications.forEach(function(notification) {
              selectedNotifications.push(notification.id);
            });
          }

          this.selectedNotifications = selectedNotifications;
        }
      }
    },
    methods: {
      toggleRead(unread) {
        vm = this;

        vm.notifications.map((notify, index) => {
          if (vm.selectedNotifications.includes(notify.id))
            if (unread) {
              notify.is_read = false;
            } else {
              notify.is_read = true;
            }
        });
        window.sessionStorage.setItem('notificationRead', vm.selectedNotifications);
        if (unread) {
          vm.sendState(true);
        } else {
          vm.sendState();
        }
      },
      deleteNotification() {
        vm = this;
        const deleteObj = Object();

        deleteObj['delete'] = vm.selectedNotifications;
        let data = JSON.stringify(deleteObj);
        let deleteNotify = fetchData ('/inbox/notifications/delete/', 'DELETE', data);

        $.when(deleteNotify).then(function(response, status, statusText) {

          if (statusText.status === 204) {
            vm.notifications.map((notify, index) => {
              if (vm.selectedNotifications.includes(notify.id))
                vm.notifications.splice(notify[index], 1);
            });
            vm.selectedNotifications = [];
          }
        });
      },
      selectUnread() {
        vm = this;
        vm.selectedNotifications = [];
        vm.notifications.forEach(function(notification) {

          if (notification.is_read === false) {
            vm.selectedNotifications.push(notification.id);
          }
        });
      },
      selectRead() {
        vm = this;
        vm.selectedNotifications = [];
        vm.notifications.forEach(function(notification) {

          if (notification.is_read === true) {
            vm.selectedNotifications.push(notification.id);
          }
        });
      }
    },
    mounted() {
      this.fetchNotifications();
    },
    created() {
      this.sendState();
    }
  });
}

const newData = (newObj, oldObj) => {

  return newObj.filter(function(obj) {
    return !oldObj.some(function(obj2) {
      return obj.id == obj2.id;
    });
  });
};

Vue.filter('moment-fromnow', function(date) {
  moment.defineLocale('en-custom', {
    parentLocale: 'en',
    relativeTime: {
      future: 'in %s',
      past: '%s ',
      s: 'now',
      ss: '%ds',
      m: '1m',
      mm: '%d m',
      h: '1h',
      hh: '%dh',
      d: '1 day',
      dd: '%d days',
      M: '1 month',
      MM: '%d months',
      y: '1 year',
      yy: '%d years'
    }
  });
  return moment.utc(date).fromNow();
});

Vue.filter('moment', function(date) {
  moment.locale('en');
  return moment.utc(date).fromNow();
});
