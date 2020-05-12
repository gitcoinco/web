const hackathon_slug = document.hackathon_slug
const sponsors = document.sponsors
Vue.component('v-select', VueSelect.VueSelect);
Vue.mixin({
  methods: {
    getIssueDetails: function(url) {
      let vm = this;

      if (!url) {
        vm.errorIssueDetails = undefined;
        return vm.issueDetails = null;
      }

      if (url.indexOf('github.com/') < 0) {
        vm.issueDetails = null;
        vm.errorIssueDetails = 'Please paste a github issue url';
        return;
      }

      let ghIssueUrl = new URL(url);

      vm.orgSelected = '';

      const apiUrldetails = `/sync/get_issue_details?url=${encodeURIComponent(url)}&hackathon_slug=${vm.hackathon_slug}`;

      vm.errorIssueDetails = undefined;
      vm.issueDetails = undefined;
      const getIssue = fetchData(apiUrldetails, 'GET');

      $.when(getIssue).then((response) => {
        vm.orgSelected = ghIssueUrl.pathname.split('/')[1];

        vm.issueDetails = response;
        vm.errorIssueDetails = undefined;
        // if (response[0]) {
        // } else {
        //   vm.issueDetails = null;
        //   vm.errorIssueDetails = 'This issue wasn\'t bountied yet.';
        // }
      }).catch((err) => {
        console.log(err)
        vm.errorIssueDetails = err.responseJSON.message;
      });

    },
    getTokens: function(){
      let vm = this;
      const apiUrlTokens = '/api/v1/tokens/';
      const getTokensData = fetchData(apiUrlTokens, 'GET');
      $.when(getTokensData).then((response) => {
        vm.tokens = response;
        vm.form.token = vm.filterByNetwork[0]
        vm.getAmount(vm.form.token.symbol)

      }).catch((err) => {
        console.log(err)
        // vm.errorIssueDetails = err.responseJSON.message;
      });

    },
    getAmount: function(token) {
      let vm = this;

      if (!token) {
        return;
      }
      const apiUrlAmount = `/sync/get_amount?amount=1&denomination=${token}`;
      const getAmountData = fetchData(apiUrlAmount, 'GET');
      $.when(getAmountData).then((response) => {
        vm.coinValue = response.usdt;
        vm.calcValues('usd')

      }).catch((err) => {
        console.log(err)
        // vm.errorIssueDetails = err.responseJSON.message;
      });
    },
    calcValues: function(direction) {
      let vm = this;
      if (direction == 'usd') {
        let usdValue = vm.form.amount * vm.coinValue
        vm.form.amountusd = Number(usdValue.toFixed(2));
        console.log(vm.form.amountusd)
      } else {
        vm.form.amount = Number(vm.form.amountusd * 1 / vm.coinValue).toFixed(4);
        console.log(vm.form.amount)
      }

    },
    addKeyword: function(item) {
      let vm = this;

      vm.form.keywords.push(item)
    },
    checkForm: function(e) {
      let vm = this;
      if (vm.form.bounty_categories.length < 1) {
        vm.errors.push('Select at least one category')
        e.preventDefault();
      } else {
        return;
      }
    },
    submitForm: function() {
      let vm = this;

      if (network === 'mainnnet') {
        // vm.blockchainSend(form)
        // vm.sendData(form)

      } else if (network === 'custom') {
        // vm.sendData(form)

      }


    },
    sendData: function() {
      // api post method

    },
    blockchainSend: function() {

    }
  },
  computed: {
    sortByPriority: function() {
      // console.log(elem)
      return this.tokens.sort(function(a, b) {
        return b.priority - a.priority
      })
    },
    filterByNetwork: function() {
      const vm = this;
      if( vm.network == ''){
        return vm.tokens;
      }
      return vm.sortByPriority.filter((item)=>{

        return item.network.toLowerCase().indexOf(vm.network.toLowerCase()) >= 0;
      })
    }
  }
})

if (document.getElementById('gc-hackathon-new-bounty')) {
  // var vueSelect = import('vue-select');
  var app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-hackathon-new-bounty',
    components: {
      'vue-select': 'vue-select'
    },
    data() {
      return {
        tokens: [],
        network: 'mainnet',
        hackathon_slug: hackathon_slug,
        issueDetails: undefined,
        errorIssueDetails: undefined,
        errors: [],
        sponsors: sponsors,
        orgSelected: '',
        selected: null,
        coinValue: null,
        form: {
          gitcoinIssueUrl: '',
          bounty_categories:[],
          project_type:'',
          permission_type:'',
          keywords: [],
          amount: 0.001,
          amountusd: null,
          token: {},
        },
      }
    },
    mounted() {
      this.getTokens();
    }
  });
}
