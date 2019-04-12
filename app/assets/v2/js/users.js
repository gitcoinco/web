Vue.component('select2', {
  props: [ 'options', 'value' ],
  template: '#select2-template',
  mounted: function() {
    var vm = this;

    $(this.$el).select2({ data: this.options })
      .val(this.value)
      .trigger('change')
      .on('change', function() {
        vm.$emit('input', this.value);
      });
  },
  watch: {
    value: function(value) {
      // update value
      $(this.$el).val(value).trigger('change');
    },
    options: function(options) {
      // update options
      $(this.$el).empty().select2({ data: options });
    }
  },
  destroyed: function() {
    $(this.$el).off().select2('destroy');
  }
});

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
      vm.params.page = vm.usersPage;

      if (vm.searchTerm) {
        vm.params.search = vm.searchTerm;
      } else {
        delete vm.params['search'];
      }

      if (vm.selectedSkills) {
        vm.params.keywords = vm.selectedSkills;
      } else {
        delete vm.params['keywords'];
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
    searchFilters: function() {
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
      skills: document.keywords,
      selectedSkills: [],
      bottom: false,
      params: {}
    },
    mounted() {
      this.fetchUsers();
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


// $('#skills').select2({
//   placeholder: 'Select skills',
//   tags: 'true',
//   allowClear: true,
//   data: document.keywords
// });


