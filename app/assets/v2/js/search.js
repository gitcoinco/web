if (document.getElementById('gc-search')) {
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-search',
    data: {
      term: '',
      results: [],
      isLoading: false,
      isDirty: false,
      currentTab: 0,
      source_types: [
        'All',
        'Profile',
        'Bounty',
        'Grant',
        'Kudos',
        'Quest',
        'Page'
      ],
      labels: {
        'All': 'All',
        'Profile': 'Profiles',
        'Bounty': 'Bounties',
        'Grant': 'Grants',
        'Kudos': 'Kudos',
        'Quest': 'Quests',
        'Page': 'Pages'
      }
    },
    mounted() {
      this.search();
    },
    created() {
      this.search();
    },
    methods: {
      init: function() {
        setTimeout(() => {
          $('.has-search input[type=text]').focus();
        }, 100);
      },
      dirty: async function(e) {
        this.isDirty = true;
      },
      search: async function(e) {
        let vm = this;
        let thisDate = new Date();

        vm.isDirty = false;
        // prevent 2x search at once
        if (vm.isLoading) {
          return;
        }

        if (vm.term.length >= 4) {
          vm.isLoading = true;
          document.current_search = thisDate;

          const response = await fetchData(
            `/api/v0.1/search/?term=${vm.term}`,
            'GET'
          );
          // let response = [{"title": "bounty event test cooperative", "description": "https://github.com/danlipert/gitcoin-test/issues/38https://github.com/danlipert/gitcoin-test/issues/38https://github.com/danlipert/gitcoin-test/issues/38https://github.com/danlipert/gitcoin-test/issues/38https://github.com/danlipert/gitcoin-test/issues/38", "full_search": "bounty event test cooperativehttps://github.com/danlipert/gitcoin-test/issues/38https://github.com/danlipert/gitcoin-test/issues/38https://github.com/danlipert/gitcoin-test/issues/38https://github.com/danlipert/gitcoin-test/issues/38https://github.com/danlipert/gitcoin-test/issues/38Bounty", "url": "https://gitcoin.co/issue/danlipert/gitcoin-test/39/2533", "pk": 15138, "img_url": "https://gitcoin.co/dynamic/avatar/danlipert/1", "timestamp": "2020-04-11T10:26:33.327518+00:00", "source_type": "Bounty"}, {"title": "Gitcoin Ambassador", "description": "This Kudos can be awarded only by Gitcoin team, and signifies that one was a Gitcoin ambassador during Fall 2018 and beyond.", "full_search": "Gitcoin AmbassadorThis Kudos can be awarded only by Gitcoin team, and signifies that one was a Gitcoin ambassador during Fall 2018 and beyond.Kudos", "url": "https://gitcoin.co/kudos/486/gitcoin_ambassador", "pk": 94898, "img_url": "https://gitcoin.co/dynamic/kudos/486/gitcoin_ambassador", "timestamp": "2020-04-11T11:32:06.394147+00:00", "source_type": "Kudos"}, {"title": "Gitcoin Genesis", "description": "The Gitcoin Genesis Badge is the rarest of the Gitcoin team badges.  Owners of this badge contributed to Gitcoin in a meaningful way in the way-back-when.", "full_search": "Gitcoin GenesisThe Gitcoin Genesis Badge is the rarest of the Gitcoin team badges.  Owners of this badge contributed to Gitcoin in a meaningful way in the way-back-when.Kudos", "url": "https://gitcoin.co/kudos/3/gitcoin_genesis", "pk": 94470, "img_url": "https://gitcoin.co/dynamic/kudos/3/gitcoin_genesis", "timestamp": "2020-04-10T17:03:20.171063+00:00", "source_type": "Kudos"}, {"title": "Gitcoin Torchbearer", "description": "For the Gitcoin Grants TorchBearers", "full_search": "Gitcoin TorchbearerFor the Gitcoin Grants TorchBearersKudos", "url": "https://gitcoin.co/kudos/1904/gitcoin_torchbearer", "pk": 94775, "img_url": "https://gitcoin.co/dynamic/kudos/1904/gitcoin_torchbearer", "timestamp": "2020-04-11T11:26:46.881200+00:00", "source_type": "Kudos"}, {"title": "Gitcoin Genesis", "description": "The Gitcoin Genesis Badge is the rarest of the Gitcoin team badges.  Owners of this badge contributed to Gitcoin in a meaningful way in the way-back-when.", "full_search": "Gitcoin GenesisThe Gitcoin Genesis Badge is the rarest of the Gitcoin team badges.  Owners of this badge contributed to Gitcoin in a meaningful way in the way-back-when.Kudos", "url": "https://gitcoin.co/kudos/53/gitcoin_genesis", "pk": 94915, "img_url": "https://gitcoin.co/dynamic/kudos/53/gitcoin_genesis", "timestamp": "2020-04-11T10:26:48.271323+00:00", "source_type": "Kudos"}, {"title": "Gitcoin Quests 101", "description": "This Quest is an intro to Gitcoin Quests (how meta!)", "full_search": "Gitcoin Quests 101This Quest is an intro to Gitcoin Quests (how meta!)Quest", "url": "https://gitcoin.co/quests/43/gitcoin-quests-101", "pk": 17139, "img_url": "https://gitcoin.co/dynamic/kudos/4550/grants_round_3_contributor_-_futurism_bot", "timestamp": "2020-04-11T15:25:54.813955+00:00", "source_type": "Quest"}, {"title": "gitcoin mock issue", "description": "####gitcoin mock issue\r\n<!---\r\nThis\r\n -->", "full_search": "gitcoin mock issue####gitcoin mock issue\r\n<!---\r\nThis\r\n -->Bounty", "url": "https://gitcoin.co/issue/Korridzy/range/1/566", "pk": 12982, "img_url": "https://gitcoin.co/dynamic/avatar/Korridzy/1", "timestamp": "2020-04-11T02:26:36.194393+00:00", "source_type": "Bounty"}, {"title": "Gitcoin Testing", "description": "Testing Gitcoin Functionality with this issue.", "full_search": "Gitcoin TestingTesting Gitcoin Functionality with this issue.Bounty", "url": "https://gitcoin.co/issue/UniBitProject/wallet/18/1476", "pk": 14619, "img_url": "https://gitcoin.co/dynamic/avatar/UniBitProject/1", "timestamp": "2020-04-10T19:26:57.564235+00:00", "source_type": "Bounty"}, {"title": "Gitcoin and StandardBounties 101", "description": "Whats the difference between Gitcoin and StandardBounties?", "full_search": "Gitcoin and StandardBounties 101Whats the difference between Gitcoin and StandardBounties?Quest", "url": "https://gitcoin.co/quests/32/gitcoin-and-standardbounties-101", "pk": 17140, "img_url": "https://gitcoin.co/dynamic/kudos/105/bee_of_all_trades", "timestamp": "2020-04-11T15:25:54.483253+00:00", "source_type": "Quest"}, {"title": "Gitcoin Robot Friend", "description": "This kudos for those who wanna see a gitcoin robot friend", "full_search": "Gitcoin Robot FriendThis kudos for those who wanna see a gitcoin robot friendKudos", "url": "https://gitcoin.co/kudos/12477/gitcoin_robot_friend", "pk": 191834, "img_url": "https://gitcoin.co/dynamic/kudos/12477/gitcoin_robot_friend", "timestamp": "2020-04-08T18:24:39.350902+00:00", "source_type": "Kudos"}];

          if (document.current_search == thisDate) {
            vm.results = groupBySource(response);
          }
          vm.isLoading = false;
        } else {
          vm.results = {};
          vm.isLoading = false;
        }
      }
    }
  });
}
document.current_search = new Date();

const groupBySource = results => {
  let grouped_result = {};

  results.map(result => {
    const source_type = result.source_type;

    grouped_result['All'] ? grouped_result['All'].push(result) : grouped_result['All'] = [result];
    grouped_result[source_type] ? grouped_result[source_type].push(result) : grouped_result[source_type] = [result];
  });
  return grouped_result;
};

$(document).on('click', '.gc-search .dropdown-menu', function(event) {
  event.stopPropagation();
});
