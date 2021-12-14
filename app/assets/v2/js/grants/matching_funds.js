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
    async fetchCLRMatches() {
      // partition function to split result array based on condition
      function partition(array, isValid) {
        return array.reduce(([ pass, fail ], elem) => {
          return isValid(elem) ? [ [ ...pass, elem ], fail ] : [ pass, [ ...fail, elem ] ];
        }, [ [], [] ]);
      }

      let vm = this;

      // fetch clr match entries of owned grants
      const url = '/grants/v1/api/clr-matches';

      try {
        let result = await (await fetch(url)).json();

        // update claim status + format date fields
        result.map(async m => {
          m.grant_payout.funding_withdrawal_date = m.grant_payout.funding_withdrawal_date
            ? moment(m.grant_payout.funding_withdrawal_date).format('MMM D, Y')
            : null;

          const claimData = await vm.hasClaimed(
            m.grant.admin_address,
            m.grant_payout.contract_address,
            m.payout_tx
          );

          m.has_claimed = claimData.status;
          m.claim_date = claimData.timestamp ? moment.unix(claimData.timestamp).format('MMM D, Y') : null;
        });


        // split result into clr matches that are ready to claim and those for history
        const [ pass, fail ] = partition(result, a => !a.hasClaimed && !a.grant_payout.funding_withdrawn);
        
        // group clr matches by grant title
        this.readyToClaim = await this.groupByGrant(pass);
        this.clrMatchHistory = await this.groupByGrant(fail);

        this.loading = false;

      } catch (e) {
        console.error(e);
        _alert('Something went wrong. Please try again later', 'danger');
      }
    },
    async groupByGrant(clrMatches) {
      // group clr matches by grant title

      result = await clrMatches.reduce(async function(r, a) {
        r[a.grant.title] = r[a.grant.title] || [];
        r[a.grant.title].push(a);
        return r;
      }, Object.create(null));

      return result;
    },
    async hasClaimed(recipientAddress, contractAddress, txHash) {
      let status = false;
      let timestamp = null;

      web3 = new Web3(`wss://mainnet.infura.io/ws/v3/${document.contxt.INFURA_V3_PROJECT_ID}`);

      let tx = await web3.eth.getTransaction(txHash);

      if (tx && tx.to == contractAddress) {
        addressWithout0x = recipientAddress.replace('0x', '').toLowerCase();

        // check if user attempted to claim match payout
        // 0x8658b34 is the method id of the claimMatchPayout(address _recipient) function
        userClaimedMatchPayout = tx.input.startsWith('0x8658b34') && tx.input.endsWith(addressWithout0x);
        
        if (userClaimedMatchPayout) {
          let receipt = await web3.eth.getTransactionReceipt(txHash);

          console.log(receipt);

          if (receipt) {
            status = true;
            timestamp = (await web3.eth.getBlock(receipt.blockNumber)).timestamp; // fetch claim date
          }
        }
      }

      return { status, timestamp };
    },
    async claimMatch(match) {
      console.log(match);

      // Helper method to manage state
      const waitingState = (state) => {
        if (state === true) {
          document.getElementById('claim-match').classList.add('disabled');
        } else {
          document.getElementById('claim-match').classList.remove('disabled');
        }
        indicateMetamaskPopup(!state);
      };
      
      waitingState(true);

      // Connect wallet
      if (!provider) {
        await onConnect();
      }

      // Confirm wallet was connected (user may have closed wallet connection prompt)
      if (!provider) {
        return;
      }
      const user = (await web3.eth.getAccounts())[0];

      // Get contract instance
      const matchPayouts = await new web3.eth.Contract(
        JSON.parse(document.contxt.match_payouts_abi),
        match.grant_payout.contract_address
      );

      // Claim payout
      matchPayouts.methods.claimMatchPayout(match.grant.admin_address)
        .send({from: user})
        .on('transactionHash', async function(txHash) {
          waitingState(false);
          _alert("Match payout claimed! Funds will be sent to your grant's address", 'success');
        })
        .on('error', function(error) {
          waitingState(false);
          _alert(error, 'danger');
        });
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
        loading: true,
        clrMatchHistory: null,
        readyToClaim: null,
        tabSelected: 1,
        tab: null,
        backLink: {
          url: '/grants',
          title: 'Grants'
        }
      };
    },
    mounted: async function() {
      this.enableTab();
      this.backNavigation();

      // fetch CLR match history of the user's owned grants
      await this.fetchCLRMatches();

      console.log(this.clrMatchHistory);
      console.log(this.readyToClaim);

      // this.hasClaimed(
      //   '0xdbb16c68aa373229db9f37d85087264361691ab9',
      //   '0x0EbD2E2130b73107d0C45fF2E16c93E7e2e10e3a',
      //   '0x43ee7def85a5b4b5ecf7c551bbf99014220e779046d6faccc43e790e2b7e7ab8'
      // ).then(console.log);
    }
  });
}