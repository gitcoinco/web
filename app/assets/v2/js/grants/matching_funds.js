Vue.mixin({
  methods: {
    paginate: function(array, page_size, page_number) {
      return array.slice(page_number * page_size, page_number * page_size + page_size);
    },
    tabChange: function(input) {

      console.log(input);
      window.location = `${this.grant.details_url}?tab=${input}`;
    },
    enableTab: function() {
      let vm = this;
      let urlParams = new URLSearchParams(window.location.search);

      vm.tab = urlParams.get('tab');

      switch (vm.tab) {
        case 'ready_to_claim':
          vm.tabSelected = 1;
          break;
        case 'claim_history':
          vm.tabSelected = 2;
          break;
        default:
          vm.tabSelected = 0;
      }
      window.history.replaceState({}, document.title, `${window.location.pathname}`);
    },
    fetchCLRMatches: function() {
      // fetch clr match entries of owned grants
      const vm = this;

      vm.loadingRelated = true;

      const url = '/grants/v1/api/clr_matches';

      fetch(url).then(function(res) {
        return res.json();
      }).then(function(json) {
        // some computation
        vm.loadingRelated = false;
      }).catch(console.error);
    },
    async hasClaimed(address, txHash) {
      web3 = new Web3(`wss://mainnet.infura.io/ws/v3/${document.contxt.INFURA_V3_PROJECT_ID}`);
      // const CONTRACT_ADDRESS = '0x0EbD2E2130b73107d0C45fF2E16c93E7e2e10e3a';
      // const CONTRACT_ABI = [{"inputs":[{"internalType":"address","name":"_owner","type":"address"},{"internalType":"address","name":"_funder","type":"address"},{"internalType":"contract IERC20","name":"_dai","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[],"name":"Finalized","type":"event"},{"anonymous":false,"inputs":[],"name":"Funded","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"contract IERC20","name":"token","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"FundingWithdrawn","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"recipient","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"PayoutAdded","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"recipient","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"PayoutClaimed","type":"event"},{"inputs":[{"internalType":"address","name":"_recipient","type":"address"}],"name":"claimMatchPayout","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"dai","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"enablePayouts","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"finalize","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"funder","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"payouts","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"components":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"internalType":"struct MatchPayouts.PayoutFields[]","name":"_payouts","type":"tuple[]"}],"name":"setPayouts","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"state","outputs":[{"internalType":"enum MatchPayouts.State","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"}],"name":"withdrawFunding","outputs":[],"stateMutability":"nonpayable","type":"function"}]

      // const matchingContract = new web3.eth.Contract(CONTRACT_ABI, CONTRACT_ADDRESS);
      // matchingContract.getPastEvents('PayoutClaimed', {
      //   filter: {
      //     recipient: '0x1208a26FAa0F4AC65B42098419EB4dAA5e580AC6'
      //   },
      //   fromBlock: 11479195,
      //   toBlock: 'latest'
      // })
      // .then(function(events){
      //   console.log(events);
      // })
      // .catch(function(e) {
      //   console.log("Failed to fetch claim status.");
      // });
      let tx = await web3.eth.getTransaction(txHash);
      
      addressWithout0x = address.replace('0x', '').toLowerCase();

      // check if user attempted to claim match payout
      // 0x8658b34 is the method id of the claimMatchPayout(address _recipient) function
      console.log(tx);
      userClaimedMatchPayout = tx.input.startsWith('0x8658b34') && tx.input.endsWith(addressWithout0x);
      
      if (userClaimedMatchPayout) {
        let receipt = await web3.eth.getTransactionReceipt(txHash);

        if (receipt)
          return true;
      }

      return false;
    },
    backNavigation: function() {
      const vm = this;
      const lgt = localStorage.getItem('last_grants_title') || 'Grants';
      const lgi = document.referrer.indexOf(location.host) != -1 ? 'javascript:history.back()' : '/grants/explorer';

      if (lgi && lgt) {
        vm.$set(vm.backLink, 'url', lgi);
        vm.$set(vm.backLink, 'title', lgt);
      }
    },
    scrollToElement(element) {
      const container = this.$refs[element];

      container.scrollIntoViewIfNeeded({behavior: 'smooth', block: 'start'});
    }
  }
});

if (document.getElementById('gc-matching-funds')) {
  appGrantDetails = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-matching-funds',
    data() {
      return {
        loading: false,
        loadingTx: false,
        clrMatchHistory: {},
        tabSelected: 1,
        tab: null,
        backLink: {
          url: '/grants',
          title: 'Grants'
        }
      };
    },
    mounted: function() {
      this.enableTab();
      this.backNavigation();
      this.hasClaimed(
        '0xdbb16c68aa373229db9f37d85087264361691ab9',
        '0x43ee7def85a5b4b5ecf7c551bbf99014220e779046d6faccc43e790e2b7e7ab8'
      ).then(console.log);
    }
  });
}