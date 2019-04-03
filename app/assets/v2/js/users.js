let users = [];
let usersPage = 1;
let usersNumPages = '';
let usersHasNext = false;

Vue.mixin({
  methods: {
    fetchUsers: function(newPage) {
      var vm = this;

      if (newPage) {
        vm.usersPage = newPage;
      }

      var getNotifications = fetchData (`/api/v0.1/users_fetch/?page=${vm.usersPage}`, 'GET');

      $.when(getNotifications).then(function(response) {
        console.log(response.data)
        vm.users = response.data;
        
        // newNotifications = newData(response.data, vm.notifications);
        // newNotifications.forEach(function(item) {
          // vm.notifications.push(item);
        // });

        vm.usersNumPages = response.num_pages;
        vm.usersHasNext = response.has_next;
        vm.numNotifications = response.count;

        if (vm.usersHasNext) {
          vm.usersPage = ++vm.usersPage;

        } else {
          vm.usersPage = 1;
        }
      });
    }

  }

});

if (document.getElementById('gc-users-directory')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-users-directory',
    data: {
      users,
      usersPage,
      usersNumPages,
      usersHasNext,
      media_url
    },
    mounted() {
      this.fetchUsers();
    },
    created() {
      // this.sendState();
    }
  });
}
