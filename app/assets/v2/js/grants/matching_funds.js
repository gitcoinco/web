Vue.mixin({
  methods: {
    tabChange: function(input) {
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
      let vm = this;

      this.loading = true;

      // fetch clr match entries of owned grants
      const url = '/grants/v1/api/clr-matches/';

      try {
        let result = await (await fetch(url)).json();

        // update claim status + format date fields
        result.map(async m => {
          m.grant_payout.funding_withdrawal_date = m.grant_payout.funding_withdrawal_date
            ? moment(m.grant_payout.funding_withdrawal_date).format('MMM D, Y')
            : null;

          const claimData = await vm.checkClaimStatus(m);

          m.status = claimData.status;
          m.claim_date = claimData.timestamp ? moment.unix(claimData.timestamp).format('MMM D, Y') : null;
        });

        // group clr matches by grant title
        result = await this.groupByGrant(result);

        // assign property for if grants have any claim or not
        Object.keys(result).forEach(grantTitle => {
          if (result[grantTitle].filter(a => a.has_claimed).length === 0) {
            result[grantTitle].hasNoClaim = true;
          } else {
            result[grantTitle].hasNoClaim = false;
          }
        });

        this.clrMatches = result;

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
    async checkClaimStatus(match) {
      const recipientAddress = match.grant.admin_address;
      const contractAddress = match.grant_payout.contract_address;
      const txHash = match.payout_tx;

      let status = 'not-found';
      let timestamp = null;

      web3 = new Web3(`wss://mainnet.infura.io/ws/v3/${document.contxt.INFURA_V3_PROJECT_ID}`);

      let tx = await web3.eth.getTransaction(txHash);

      if (tx && tx.to == contractAddress) {
        status = 'pending'; // claim transaction is pending

        addressWithout0x = recipientAddress.replace('0x', '').toLowerCase();

        // check if user attempted to claim match payout
        // 0x8658b34 is the method id of the claimMatchPayout(address _recipient) function
        userClaimedMatchPayout = tx.input.startsWith('0x8658b34') && tx.input.endsWith(addressWithout0x);
        
        if (userClaimedMatchPayout) {
          let receipt = await web3.eth.getTransactionReceipt(txHash);

          if (receipt && receipt.status) {
            status = 'claimed';
            timestamp = (await web3.eth.getBlock(receipt.blockNumber)).timestamp; // fetch claim date
          }
        }
      }

      return { status, timestamp };
    },
    async claimMatch(match) {
      const vm = this;

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
          await this.fetchCLRMatches();
          vm.$forceUpdate();
          this.tabSelected = 1;
          waitingState(false);
          _alert("Match payout claimed! Funds will be sent to your grant's address", 'success');
        })
        .on('error', function(error) {
          waitingState(false);
          _alert(error, 'danger');
        });
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
        clrMatches: null,
        tabSelected: 1,
        tab: null
      };
    },
    mounted: async function() {
      this.enableTab();

      // fetch CLR match history of the user's owned grants
      await this.fetchCLRMatches();
    }
  });
}