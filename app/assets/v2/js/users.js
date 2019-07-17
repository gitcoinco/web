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

      vm.isLoading = true;
      vm.noResults = false;

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

        if (vm.users.length) {
          vm.noResults = false;
        } else {
          vm.noResults = true;
        }
        vm.isLoading = false;
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
        vm.isFunder = response.is_funder;
        vm.funderBounties = response.data;
      });

    },
    openBounties: function(user) {
      let vm = this;

      vm.userSelected = user;
    },
    sendInvite: function(bounty, user) {
      let vm = this;

      console.log(vm.bountySelected, bounty, user, csrftoken);
      let apiUrlInvite = '/api/v0.1/social_contribution_email/';
      let postInvite = fetchData(
        apiUrlInvite,
        'POST',
        { 'usersId': [user], 'bountyId': bounty.id},
        {'X-CSRFToken': csrftoken}
      );

      $.when(postInvite).then((response) => {
        console.log(response);
        if (response.status === 500) {
          _alert(response.msg, 'error');

        } else {
          vm.$refs['user-modal'].closeModal();
          _alert('The invitation has been sent', 'info');
        }
      });

    },
    closeModal() {
      this.$refs['user-modal'].closeModal();
    },
    inviteOnMount: function() {
      let vm = this;

      vm.contributorInvite = getURLParams('invite');
      vm.currentBounty = getURLParams('current-bounty');

      if (vm.contributorInvite) {
        let api = `/api/v0.1/users_fetch/?search=${vm.contributorInvite}`;
        let getUsers = fetchData (api, 'GET');

        $.when(getUsers).then(function(response) {
          if (response && response.data) {
            vm.openBounties(response.data[0]);
            $('#userModal').bootstrapModal('show');
          }
        });
      }
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
      currentBounty: undefined,
      contributorInvite: undefined,
      isFunder: false,
      bountySelected: null,
      userSelected: [],
      showModal: false,
      showFilters: true,
      skills: document.keywords,
      selectedSkills: [],
      noResults: false,
      isLoading: true
    },
    mounted() {
      this.fetchUsers();
      this.$watch('params', function(newVal, oldVal) {
        this.searchUsers();
      }, {
        deep: true
      });
    },
    created() {
      this.fetchBounties();
      this.inviteOnMount();
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
