let users = [];
let usersPage = 1;
let usersNumPages = '';
let usersHasNext = false;
let numUsers = '';
// let funderBounties = [];

Vue.mixin({
  methods: {
    fetchUsers: function(newPage) {
      let vm = this;

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
      let vm = this;

      vm.users = [];

      vm.fetchUsers(1);

    },
    bottomVisible: function() {
      let vm = this;

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
      let vm = this;
      
      // fetch bounties
      let apiUrlBounties = '/api/v0.1/user_bounties/';

      let getBounties = fetchData(apiUrlBounties, 'GET');

      $.when(getBounties).then((response) => {
        // response.data.forEach(function(item) {
        //   console.log(item)
        // });
        vm.funderBounties = response.data;
        console.log(vm.funderBounties);
      });

    },
    openBounties: function(user) {
      let vm = this;

      console.log(user);
      vm.userSelected = user;
      vm.showModal = true;

    },
    sendInvite: function(bounty, user) {
      let vm = this;

      console.log(vm.bountySelected, bounty, user, csrftoken);
      vm.showModal = false;
      let apiUrlInvite = '/api/v0.1/social_contribution_email/';
      let postInvite = fetchData(
        apiUrlInvite,
        'POST',
        { 'url': bounty.github_url, 'usersId': [user], 'bountyId': bounty.id, 'msg': 'check this'},
        {'X-CSRFToken': csrftoken}
      );
      
      $.when(postInvite).then((response) => {
        console.log(response);
        if (response.status === 500) {
          _alert(response.msg, 'error');
          
        } else {
          _alert('The invitation has been sent', 'info');
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
      numUsers,
      media_url,
      searchTerm: null,
      bottom: false,
      params: {},
      funderBounties: [],
      showModal: false,
      bountySelected: null
    },
    mounted() {
      this.fetchUsers();
    },
    created() {
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
