let users = [];
let usersPage = 1;
let usersNumPages = '';
let usersHasNext = false;
let numUsers = '';

Vue.mixin({
  methods: {
    fetchUsers: function(newPage) {
      var vm = this;

      if (newPage) {
        vm.usersPage = newPage;
      }
      vm.params.page = vm.usersPage

      console.log(vm.searchTerm)
      if(vm.searchTerm) {
        vm.params.search = vm.searchTerm
      } else {
        delete vm.params['search']
      }
      let searchParams = new URLSearchParams(vm.params);
      
      let apiUrlUsers = `/api/v0.1/users_fetch/?${searchParams.toString()}`

      var getUsers = fetchData (apiUrlUsers, 'GET');

      $.when(getUsers).then(function(response) {
        console.log(response.data)
        // vm.users = response.data;
        // vm.users.push(response.data);
      
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
      // vm.usersPage = 1
      // vm.params.page = 1

      vm.fetchUsers(1)

    },
    bottomVisible: function() {
      vm = this;

      const scrollY = window.scrollY
      const visible = document.documentElement.clientHeight
      const pageHeight = document.documentElement.scrollHeight - 500
      const bottomOfPage = visible + scrollY >= pageHeight
      if( bottomOfPage || pageHeight < visible) {
        if (vm.usersHasNext) {
          vm.fetchUsers();
          vm.usersHasNext = false
        }
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
      params: {}
    },
    mounted() {
      this.fetchUsers();
    },
    beforeMount() {
      // window.addEventListener('scroll', this.onScroll);
      
      window.addEventListener('scroll', () => {
        this.bottom = this.bottomVisible()
      }, false)
      // this.onScroll()
      // this.sendState();
    },
    beforeDestroy () {
      window.removeEventListener('scroll', () => {
        this.bottom = this.bottomVisible()
      });
    }
  });
}


// const createQueryParams = params => 
//       Object.keys(params)
//             .map(k => `${k}=${encodeURI(params[k])}`)
//             .join('&');


// const data2 = {
//   var1: 'value1',
//   var2: 'value2'
// };

// const searchParams = new URLSearchParams(data);

// searchParams.toString()