let users = [];
let usersPage = 1;
let usersNumPages = '';
let usersHasNext = false;
let numUsers = '';
let funderBounties = [];

Vue.mixin({
  methods: {
    fetchUsers: function(newPage) {
      var vm = this;

      if (newPage) {
        vm.usersPage = newPage;
      }
      vm.params.page = vm.usersPage;

      if (vm.searchTerm) {
        vm.params.search = vm.searchTerm;
      } else {
        delete vm.params['search'];
      }
      let searchParams = new URLSearchParams(vm.params);
      
      let apiUrlUsers = `/api/v0.1/users_fetch/?${searchParams.toString()}`;

      var getUsers = fetchData (apiUrlUsers, 'GET');

      $.when(getUsers).then(function(response) {
      
        response.data.forEach(function(item) {
          vm.users.push(item);
        });

        vm.usersNumPages = response.num_pages;
        vm.usersHasNext = response.has_next;
        vm.numUsers = response.count;

        if (vm.usersHasNext) {
          vm.usersPage = ++vm.usersPage;

        } else {
          vm.usersPage = 1;
        }
      });
    },
    searchUsers: function() {
      vm = this;
      vm.users = [];

      vm.fetchUsers(1);

    },
    bottomVisible: function() {
      vm = this;

      const scrollY = window.scrollY;
      const visible = document.documentElement.clientHeight;
      const pageHeight = document.documentElement.scrollHeight - 500;
      const bottomOfPage = visible + scrollY >= pageHeight;

      if (bottomOfPage || pageHeight < visible) {
        if (vm.usersHasNext) {
          vm.fetchUsers();
          vm.usersHasNext = false;
        }
      }
    },
    fetchBounties: function() {
      vm = this;
      
      // fetch bounties
      vm.funderBounties = [];
      console.log(vm.funderBounties);
    },
    openBounties: function(userIds) {
      vm = this;
      console.log(userIds);
      vm.showModal = true;

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
      numUsers,
      media_url,
      searchTerm: null,
      bottom: false,
      params: {},
      funderBounties,
      showModal: false
    },
    mounted() {
      this.fetchUsers();
      this.fetchBounties();
    },
    beforeMount() {
      window.addEventListener('scroll', () => {
        this.bottom = this.bottomVisible();
      }, false);
    },
    beforeDestroy() {
      window.removeEventListener('scroll', () => {
        this.bottom = this.bottomVisible();
      });
    }
  });
}

Vue.component('modal', {
  template: '#modal-template'
});
