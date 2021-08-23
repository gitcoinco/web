/* eslint-disable no-prototype-builtins */

let users = [];
let usersPage = 1;
let usersNumPages = '';
let usersHasNext = false;
let numUsers = '';
let hackathonId = document.hasOwnProperty('hackathon_id') ? document.hackathon_id : '';

const EventBus = new Vue();

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

      if (vm.hideFilterButton) {
        vm.params.persona = 'tribe';
      }

      if (vm.params.persona === 'tribe') {
        // remove filters which do not apply for tribes directory
        delete vm.params['rating'];
        delete vm.params['organisation'];
        delete vm.params['skills'];
      }

      if (vm.tribeFilter) {
        vm.params.tribe = vm.tribeFilter;
      }


      let searchParams = new URLSearchParams(vm.params);

      let apiUrlUsers = `/api/v0.1/users_fetch/?${searchParams.toString()}`;

      if (vm.hideFilterButton) {
        apiUrlUsers += '&type=explore_tribes';
      }

      var getUsers = fetchData(apiUrlUsers, 'GET');

      $.when(getUsers).then(function(response) {

        response.data.forEach(function(item) {
          vm.users.push(item);
        });

        vm.usersNumPages = response.num_pages;
        vm.usersHasNext = response.has_next;
        vm.numUsers = response.count;
        vm.showBanner = response.show_banner;
        vm.persona = response.persona;
        vm.rating = response.rating;
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
        {'usersId': [user], 'bountyId': bounty.id},
        {'X-CSRFToken': csrftoken}
      );

      $.when(postInvite).then((response) => {
        console.log(response);
        if (response.status === 500) {
          _alert(response.msg, 'danger');

        } else {
          vm.$refs['user-modal'].closeModal();
          _alert('The invitation has been sent', 'info');
        }
      });
    },
    sendInviteAll: function(bountyUrl) {
      let vm = this;
      const apiUrlInvite = '/api/v0.1/bulk_invite/';
      const postInvite = fetchData(
        apiUrlInvite,
        'POST',
        {'params': vm.params, 'bountyId': bountyUrl},
        {'X-CSRFToken': csrftoken}
      );

      $.when(postInvite).then((response) => {
        console.log(response);
        if (response.status !== 200) {
          _alert(response.msg, 'danger');

        } else {
          vm.$refs['user-modal'].closeModal();
          _alert('The invitation has been sent', 'info');
        }
      });

    },
    getIssueDetails: function(url) {
      let vm = this;
      const apiUrldetails = `/actions/api/v0.1/bounties/?github_url=${encodeURIComponent(url)}`;

      vm.errorIssueDetails = undefined;

      url = new URL(url);
      if (url.host == 'github.com') {
        vm.issueDetails = null;
        vm.errorIssueDetails = 'Please paste a github issue url';
        return;
      }
      vm.issueDetails = undefined;
      const getIssue = fetchData(apiUrldetails, 'GET');

      $.when(getIssue).then((response) => {
        if (response[0]) {
          vm.issueDetails = response[0];
          vm.errorIssueDetails = undefined;
        } else {
          vm.issueDetails = null;
          vm.errorIssueDetails = 'This issue wasn\'t bountied yet.';
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
        let getUsers = fetchData(api, 'GET');

        $.when(getUsers).then(function(response) {
          if (response && response.data.length) {
            vm.openBounties(response.data[0]);
            $('#userModal').bootstrapModal('show');
          } else {
            _alert('The user was not found. Please try using the search box.', 'danger');
          }
        });
      }
    },

    extractURLFilters: function(serverFilters) {
      let vm = this;
      let params = getAllUrlParams();
      let columns = serverFilters[vm.header.index]['mappings'][vm.header.type]['properties'];

      if (params.body && !vm.filtersLoaded) {
        let decodedBody = decodeURIComponent(params.body);


        let newBody = JSON.parse(decodedBody);

        this.setBody(newBody);
        this.fetch(this);

        if (Object.values(newBody).length > 0) {
          try {
            // eslint-disable-next-line guard-for-in
            let query = newBody['query'];
            let activeFilters = [];

            if (query.hasOwnProperty('bool') && query['bool'].hasOwnProperty('filter') && query['bool']['filter'].hasOwnProperty('bool') && query['bool']['filter']['bool'].hasOwnProperty('should')) {
              query = query['bool']['filter']['bool']['should'];
              for (let x in query) {
                if (!query[x])
                  continue;
                let terms = query[x]['term'];

                if (!terms) {
                  continue;
                }
                // eslint-disable-next-line guard-for-in
                for (let prop in terms) {
                  let term = terms[prop];

                  let meta = columns[prop];

                  if (!meta)
                    continue;
                  let propKey = prop.replace('_exact', '');

                  if (typeof activeFilters[propKey] !== 'object') {
                    activeFilters[propKey] = [];
                  }
                  activeFilters[propKey].push(term);
                  if (columns[propKey]['selected'] !== true) {
                    columns[propKey]['selected'] = true;
                    columns[propKey]['selectedValues'] = [];
                  }


                  let value = Object.values(activeFilters[propKey])[0];

                  if (!value)
                    continue;
                  columns[propKey]['selectedValues'].push(value);

                  let _instruction = {
                    fun: 'orFilter',
                    args: [ 'term', propKey, value ]
                  };

                  this.localInstructions.push(_instruction);
                  this.addInstruction(_instruction);
                }
              }
              vm.params = activeFilters;
            }


          } catch (e) {
            console.log(e);
          }
        }

      }
      vm.esColumns = columns;

      vm.filterLoaded = true;
    },
    joinTribe: function(user, event) {
      event.target.disabled = true;
      const url = `/tribe/${user.handle}/join/`;
      const sendJoin = fetchData(url, 'POST', {}, {'X-CSRFToken': csrftoken});

      $.when(sendJoin).then(function(response) {
        event.target.disabled = false;

        if (response.is_member) {
          ++user.follower_count;
          user.is_following = true;
        } else {
          --user.follower_count;
          user.is_following = false;
        }

        event.target.classList.toggle('btn-outline-secondary');
        event.target.classList.toggle('btn-primary');
      }).fail(function(error) {
        event.target.disabled = false;
      });
    }
  }
});
Vue = Vue.extend({
  delimiters: [ '[[', ']]' ]
});


if (document.getElementById('gc-users-elastic')) {

  Vue.component('directory-card', {
    name: 'DirectoryCard',
    delimiters: [ '[[', ']]' ],
    props: [ 'user', 'funderBounties' ]
  });

  Vue.use(innerSearch.default);
  Vue.component('autocomplete', {
    props: [ 'options', 'value' ],
    template: '#select2-template',
    data: function() {
      return {
        selectedFilters: []
      };
    },
    methods: {
      reset: function() {
        $(this.$el).select2().val(null).trigger('change');
      },
      formatMapping: function(item) {
        console.log(item);
        return item.name;
      },
      formatMappingSelection: function(filter) {
        return '';
      }
    },
    created() {
      EventBus.$on('reset', () => {
        this.s2.val([]).trigger('change');
      });
    },
    mounted() {
      let count = 0;
      let vm = this;
      let mappedFilters = {};
      let data = $.map(this.options, function(obj, key) {

        if (key.indexOf('_exact') === -1)
          return;
        let newKey = key.replace('_exact', '');

        if (mappedFilters[newKey])
          return;
        obj.id = count++;
        obj.text = newKey;
        obj.key = key;

        if (obj.selected && obj.key !== 'keywords') {
          console.log(`${obj.text} is selected`);
          vm.selectedFilters.push(obj.id);
        }

        mappedFilters[newKey] = true;
        mappedFilters[key] = true;
        return obj;
      });

      vm.s2 = $(vm.$el)
        .select2({
          data: data,
          multiple: true,
          allowClear: true,
          placeholder: 'Search for another filter to add',
          minimumInputLength: 1,
          escapeMarkup: function(markup) {
            return markup;
          }
        })
        .on('change', function() {
          let val = $(vm.$el).val();
          let changeData = $.map(val, function(filter) {
            return data[filter];
          });

          vm.$emit('input', changeData);
          EventBus.$emit('query:changed');
        });

      vm.s2.val(vm.selectedFilters).trigger('change');
      // fix for wrong position on select open
      var select2Instance = $(vm.$el).data('select2');

      select2Instance.on('results:message', function(params) {
        this.dropdown._resizeDropdown();
        this.dropdown._positionDropdown();
      });
    },
    destroyed: function() {
      $(this.$el).off().select2('destroy');
      this.$emit('destroyed');
    }
  });
  window.UserDirectory = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-users-elastic',
    data: {
      localInstructions: [],
      csrf: document.csrf,
      esColumns: [],
      filterLoaded: false,
      users,
      usersPage,
      usersNumPages,
      usersHasNext,
      numUsers,
      media_url,
      searchTerm: null,
      bottom: false,
      params: {},
      filters: [],
      funderBounties: [],
      currentBounty: undefined,
      contributorInvite: undefined,
      isFunder: false,
      bountySelected: null,
      userSelected: [],
      showModal: false,
      showFilters: !document.getElementById('explore_tribes'),
      skills: document.keywords,
      selectedSkills: [],
      noResults: false,
      isLoading: true,
      gitcoinIssueUrl: '',
      issueDetails: undefined,
      errorIssueDetails: undefined,
      showBanner: undefined,
      persona: undefined,
      hideFilterButton: !!document.getElementById('explore_tribes')
    },
    methods: {
      filterSorter: function(results) {
        return results;
      },
      select2InputEventListener(cb, args) {
        cb(args);
        this.serializeBodytoShare();
      },
      resetCallback: function() {
        this.checkedItems = [];
      },
      autoCompleteDestroyed: function() {
        this.filters = [];
      },
      autoCompleteChange: function(filters) {
        this.filters = filters;
      },
      serializeBodytoShare: function() {
        const currBody = this.body;

        const jsonBody = JSON.stringify(currBody);

        const params = `body=${encodeURIComponent(jsonBody)}`;
        const shareURL = `${window.location.origin}${window.location.pathname}?${params}`;

        window.history.pushState('', '', shareURL);

        console.log(shareURL);
      },
      outputToCSV: function() {

        let url = '/api/v0.1/users_csv/';

        const csvRequest = fetchData(url, 'POST', JSON.stringify(this.body), {'X-CSRFToken': vm.csrf, 'Content-Type': 'application/json;'});

        $.when(csvRequest).then(json => {
          _alert(json.message);
        }).catch(() => _alert('There was an issue processing your request'));
      },

      fetchMappings: function() {
        let vm = this;

        $.when(vm.header.client.indices.getMapping())
          .then(response => {
            this.extractURLFilters(response);
            this.fetch(this);
          });
      }
    },
    updated() {
      this.serializeBodytoShare();
    },
    mounted() {
      this.fetchMappings();
    },
    created() {
      this.setHost(document.contxt.search_url);
      this.setIndex('haystack');
      this.setType('modelresult');

      this.bus.$on('reset', () => {
        EventBus.$emit('reset');
        this.removeInstructions();
        this.fetch(this);
      });
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
