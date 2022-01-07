Vue.mixin({
  methods: {
    tabChange: function(input) {
      window.location = `${this.grant.details_url}?tab=${input}`;
    },
    enableTab: function() {
      let vm = this;
      let urlParams = new URLSearchParams(window.location.search);

      vm.targetGrant = urlParams.get('grant');

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
    async fetchGrants() {
      let vm = this;

      this.loading = true;

      // fetch owned grants with clr matches
      const url = '/grants/v1/api/clr-matches/';

      try {
        let result = await (await fetch(url)).json();

        // update claim status + format date fields
        result.map(async grant => {
          grant.clr_matches.map(async m => {
            m.grant_payout.funding_withdrawal_date = m.grant_payout.funding_withdrawal_date
              ? moment(m.grant_payout.funding_withdrawal_date).format('MMM D, Y')
              : null;
  
            m.grant_payout.grant_clrs.map(e => {
              e.claim_start_date = e.claim_start_date ? moment(e.claim_start_date).format('MMM D') : null;
              e.claim_end_date = e.claim_end_date ? moment(e.claim_end_date).format('MMM D, Y') : null;
            });
  
            const claimData = await vm.checkClaimStatus(m, grant.admin_address);
  
            m.status = claimData.status;
            m.claim_date = claimData.timestamp ? moment.unix(claimData.timestamp).format('MMM D, Y') : null;
          });
        });

        this.grants = result.sort((a, b) => b.clr_matches.length - a.clr_matches.length);

        this.loading = false;

      } catch (e) {
        console.error(e);
        _alert('Something went wrong. Please try again later', 'danger');
      }
    },
    async checkClaimStatus(match, admin_address) {
      const recipientAddress = admin_address;
      const contractAddress = match.grant_payout.contract_address;
      const txHash = match.claim_tx;

      let status = 'not-found';
      let timestamp = null;

      if (!txHash) {
        return { status, timestamp };
      }

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
    async claimMatch(match, admin_address) {
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
        _alert('Please connect Ethereum wallet', 'danger');
        return;
      }

      let chainId = Number(web3.eth.currentProvider.chainId);

      if (chainId < 1 || chainId > 5) {
        waitingState(false);
        _alert('Please connect to a valid Ethereum network', 'danger');
        return;
      }

      const user = (await web3.eth.getAccounts())[0];

      // Get contract instance
      const matchPayouts = await new web3.eth.Contract(
        JSON.parse(document.contxt.match_payouts_abi),
        match.grant_payout.contract_address
      );

      // Claim payout
      matchPayouts.methods.claimMatchPayout(admin_address)
        .send({from: user})
        .on('transactionHash', async function(txHash) {
          await vm.postToDatabase(match.pk, txHash);
          await vm.fetchGrants();
          vm.$forceUpdate();
          vm.tabSelected = 1;
          waitingState(false);
          _alert('Your matching funds claim is being processed', 'success');
        })
        .on('error', function(error) {
          waitingState(false);
          _alert(error, 'danger');
        });
    },
    async postToDatabase(matchPk, claimTx) {
      const url = '/grants/v1/api/clr-matches/';
      const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      try {
        let result = await fetch(url, {
          method: 'POST',
          headers: {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfmiddlewaretoken
          },
          body: JSON.stringify({pk: matchPk, claim_tx: claimTx})
        });

        if (result.status >= 400) {
          throw await result.json();
        }
      } catch (err) {
        // TODO: Something went wrong, manual ingestion?
        console.error(err);
        _alert(err, 'danger');
        // console.log('Standard claim ingestion failed, falling back to manual ingestion');
      }
    },
    stringifyClrs(clrs) {
      let c = clrs.map(a => a.display_text);
      let g = [];

      c.forEach(elem => {
        g.push(elem);
        if (g.join(', ').length > 24) {
          g.splice(-1);
          g.push(`+${c.length - g.length} more`);
        }
      });

      return g.slice(0, -1).join(', ') + ' ' + g.slice(-1);
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
        grants: [],
        tabSelected: 1,
        tab: null,
        targetGrant: null
      };
    },
    mounted: async function() {
      this.enableTab();

      // fetch user's owned grants with CLR match history
      await this.fetchGrants();

      // scroll to specific grant if url specified a target grant
      if (this.targetGrant) {
        $('html, body').animate({
          scrollTop: $('#grant-' + this.targetGrant).offset().top
        }, 'slow');
      }
    }
  });
}