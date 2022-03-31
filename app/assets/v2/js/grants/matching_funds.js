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

      vm.loading = true;

      // fetch owned grants with clr matches
      const url = '/grants/v1/api/clr-matches?expand=token';

      try {
        let grants = await (await fetch(url)).json();

        // fetch only ETH grants
        grants = grants.filter(grant => grant.admin_address != '0x0')
        // update claim status + format date fields
        await Promise.all(grants.map(async grant => {
          await Promise.all(grant.clr_matches.map(async m => {
            if (m.grant_payout) {
              m.grant_payout.funding_withdrawal_date = m.grant_payout.funding_withdrawal_date
                ? moment(m.grant_payout.funding_withdrawal_date).format('MMM D, Y')
                : null;

              m.grant_payout.grant_clrs.map(e => {
                e.claim_start_date = e.claim_start_date ? moment(e.claim_start_date).format('MMM D') : null;
                e.claim_end_date = e.claim_end_date ? moment(e.claim_end_date).format('MMM D, Y') : null;
              });

              const claimData = await vm.checkClaimStatus(m);

              m.status = claimData.status;

              // check to ensure we don't allow users to claim if balance is 0
              if (!m.claim_tx && m.status == 'no-balance-to-claim') {
                m.claim_tx = 'NA';
              }

              m.claim_date = claimData.timestamp ? moment.unix(claimData.timestamp).format('MMM D, Y') : null;
            } else {
              Promise.resolve();
            }
          }));
        }));

        vm.grants = grants;
        vm.loading = false;

      } catch (e) {
        console.error(e);
        _alert('Something went wrong. Please try again later', 'danger');
      }
    },

    async checkClaimStatus(match, adminAddress) {
      const contractAddress = match.grant_payout.contract_address;
      const txHash = match.claim_tx;

      let status = 'not-found';
      let timestamp = null;

      web3 = new Web3(`wss://rinkeby.infura.io/ws/v3/${document.contxt.INFURA_V3_PROJECT_ID}`);

      const payoutContract = await new web3.eth.Contract(
        JSON.parse(document.contxt.match_payouts_abi),
        contractAddress
      );

      const hexAmount = match.merkle_claim?.amount || '0x00';
      const index = match.merkle_claim?.index;
      const amount = web3.utils.toBN(hexAmount);

      if (index === undefined || amount.toString() === '0') {
        return {
          status: 'no-balance-to-claim',
          timestamp
        };
      }

      if (!txHash) {
        return { status, timestamp };
      }

      const claimed = await payoutContract.methods.hasClaimed(index).call();

      if (claimed) {
        return {
          status: 'claimed',
          timestamp
        };
      }

      return {
        status: 'pending',
        timestamp
      };
    },

    async claimMatch(match, adminAddress) {
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

      const chainId = Number(web3.eth.currentProvider.chainId);

      if (chainId < 1 || chainId > 5) {
        waitingState(false);
        _alert('Please connect to a valid Ethereum network', 'danger');
        return;
      }

      const networkName = getDataChains(String(chainId), 'chainId')[0] && getDataChains(String(chainId), 'chainId')[0].network;

      if (match.grant_payout.network != networkName) {
        waitingState(false);
        _alert(`Please connect to Ethereum ${match.grant_payout.network} network`, 'danger');
        return;
      }

      const user = (await web3.eth.getAccounts())[0];

      // Get contract instance
      const matchPayouts = await new web3.eth.Contract(
        JSON.parse(document.contxt.match_payouts_abi),
        match.grant_payout.contract_address
      );

      const hexAmount = match.merkle_claim?.amount || '0x0';
      const index = match.merkle_claim?.index;
      const merkleProof = match.merkle_claim?.merkleProof || [];

      // Claim payout
      const claimArgs = {
        index: index,
        claimee: adminAddress,
        amount: hexAmount,
        merkleProof: merkleProof,
      };

      matchPayouts.methods.claim(claimArgs)
        .send({from: user})
        .on('transactionHash', async txHash => {
          await this.postToDatabase(match.pk, txHash);
          await this.fetchGrants();
          this.$forceUpdate();
          this.tabSelected = 1;
          waitingState(false);
          _alert('Your matching funds claim is being processed', 'success');
        })
        .on('error', function(error) {
          waitingState(false);
          _alert(error, 'danger');
        });
    },
    async postToDatabase(matchPk, claimTx) {
      const url = '/grants/v1/api/clr-matches/?expand=token';
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
    sortGrants() {
      // reset scroll to top grant
      if (this.targetGrant === undefined) {
        this.scrollToElement('grant-' + this.grants[0].id);
        this.targetGrant = null;
      }

      this.$nextTick(() => {
        switch (this.tabSelected) {
          case 0:
            this.grants.sort((a, b) => b.clr_matches.filter(a => !a.claim_tx).length - a.clr_matches.filter(a => !a.claim_tx).length);
            break;
          case 1:
            this.grants.sort((a, b) => b.clr_matches.filter(a => a.claim_tx).length - a.clr_matches.filter(a => a.claim_tx).length);
            break;
        }
      });
    },
    stringifyClrs(clrs) {
      let c = clrs.map(a => a.display_text);
      let g = [];

      c.every(elem => {
        g.push(elem);
        if (g.join(', ').length > 24) {
          g.splice(-1);
          g.push(`+${c.length - g.length} more`);
          return false;
        }
        return true;
      });

      return g.slice(0, -1).join(', ') + ' ' + g.slice(-1);
    },
    scrollToElement(element) {
      const container = this.$refs[element][this.tabSelected];

      container.scrollIntoView(true);
    },
    hasHistoricalMatches(grant) {
      return grant.clr_matches.length && grant.clr_matches.filter(a => a.claim_tx).length;
    },
    canClaimMatch(grant) {
      return grant.clr_matches.length && grant.clr_matches.filter(
        a => a.claim_tx === null &&
        a.grant_payout).length;
    },
    filterMatchingPayout(matches) {
      return matches.filter(match => match.grant_payout);
    }
  }
});

if (document.getElementById('gc-matching-funds')) {
  props: ['grant'],
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

      if (this.targetGrant) {
        // scroll to specific grant if url specified a target grant
        this.scrollToElement('grant-' + this.targetGrant);
        this.targetGrant = undefined;
      } else {
        // sort grants - it happens in the else block cause sort messes up with scrollToElement
        this.sortGrants();
      }
    }
  });
}
