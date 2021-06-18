var appBounty;
let bounty = [];
let url = location.href;
const loadingState = {
  loading: 'loading',
  error: 'error',
  empty: 'empty',
  resolved: 'resolved'
};

document.result = bounty;

Vue.mixin({
  methods: {
    fetchBounty: function(newData) {
      let vm = this;
      let apiUrlBounty = `/actions/api/v0.1/bounty?github_url=${document.issueURL}`;
      const getBounty = fetchData(apiUrlBounty, 'GET');

      $.when(getBounty).then(function(response) {
        if (!response.length) {
          vm.loadingState = 'empty';
          return vm.syncBounty();
        }
        vm.bounty = response[0];
        vm.loadingState = 'resolved';
        vm.isOwner = vm.checkOwner(response[0].bounty_owner_github_username);
        vm.isOwnerAddress = vm.checkOwnerAddress(response[0].bounty_owner_address);
        document.result = response[0];
        if (newData) {
          delete sessionStorage['fulfillers'];
          delete sessionStorage['bountyId'];
          localStorage[document.issueURL] = '';
          document.title = `${response[0].title} | Gitcoin`;
          window.history.replaceState({}, `${response[0].title} | Gitcoin`, response[0].url);
        }
        if (vm.bounty.event && localStorage['pendingProject'] && (vm.bounty.standard_bounties_id == localStorage['pendingProject'])) {
          projectModal(vm.bounty.pk);
        }
        vm.staffOptions();
        vm.fetchIfPendingFulfillments();
        vm.initChain();
        vm.eventParams();
      }).catch(function(error) {
        vm.loadingState = 'error';
        _alert('Error fetching bounties. Please contact founders@gitcoin.co', 'danger');
      });
    },
    eventParams: function() {
      const searchParams = new URLSearchParams(window.location.search);

      if (searchParams.has('mutate_worker_action')) {
        const action = searchParams.get('mutate_worker_action');
        const product = document.result.event ? 'hackathons' : 'bounties';
        const productPersona = document.result.event ? 'hackathon' : 'bounty';
        const persona = this.isOwner ? 'funder' : 'hunter';
        const mtcPersona = `${productPersona}-${persona}`;
        let bountyEvent = {
          'alias': 'products',
          'data': [
            {
              'name': 'product',
              'attributes': {
                'product': product,
                'persona': mtcPersona,
                'action': action
              }
            }
          ]
        };

        if (document.result.event) {
          let stopHackathonEvent = {
            'alias': 'hackathon',
            'data': [
              {
                'name': action,
                'attributes': {
                  'hackathon-slug': document.result.event.slug,
                  'hackathon-action': action
                }
              }
            ]
          };

          bountyEvent = [ bountyEvent, stopHackathonEvent ];

        }

        MauticEvent.createEvent(bountyEvent);
        window.history.pushState({}, document.title, window.location.pathname);

      }


    },
    getTransactionURL: function(token_name, txn) {
      let url;

      switch (token_name) {
        case 'BTC':
          url = `https://blockstream.info/tx/${txn}`;
          break;

        case 'ETC':
          url = `https://blockscout.com/etc/mainnet/tx/${txn}`;
          break;

        case 'CELO':
        case 'cUSD':
          url = `https://explorer.celo.org/tx/${txn}`;
          break;

        case 'ZIL':
          url = `https://viewblock.io/zilliqa/tx/${txn}`;
          break;

        case 'DOT':
          url = `https://polkadot.subscan.io/extrinsic/${txn}`;
          break;

        case 'KSM':
          url = `https://kusama.subscan.io/extrinsic/${txn}`;
          break;

        case 'FIL':
          url = `https://filscan.io/#/tipset/message-detail?cid=${txn}`;
          break;

        case 'BNB':
        case 'BUSD':
          url = `https://bscscan.com/tx/${txn}`;
          break;

        case 'ONE':
          url = `https://explorer.harmony.one/#/tx/${txn}`;
          break;

        case 'RBTC':
        case 'RDOC':
        case 'DOC':
        case 'RIF':
        case 'SOV':
          url = `https://explorer.rsk.co/tx/${txn}`;
          break;

        case 'CKB':
          url = `https://explorer.nervos.org/transaction/${txn}`;
          break;

        case 'XDC':
          url = `https://explorer.xinfin.network/tx/${txn}`;
          break;

        case 'ALGO':
        case 'USDTa':
        case 'USDCa':
          url = `https://algoexplorer.io/tx/${txn}`;
          break;

        case 'SC':
          url = `https://siastats.info/navigator?search=${txn}`;
          break;

        case 'XTZ':
          url = `https://tzkt.io/${txn}`;
          break;

        default:
          url = `https://etherscan.io/tx/${txn}`;

      }
      return url;
    },
    getAddressURL: function(token_name, address) {
      let url;

      switch (token_name) {
        case 'BTC':
          url = `https://blockstream.info/address/${address}`;
          break;

        case 'ETC':
          url = `https://blockscout.com/etc/mainnet/address/${address}`;
          break;

        case 'CELO':
        case 'cUSD':
          url = `https://explorer.celo.org/address/${address}`;
          break;

        case 'ZIL':
          url = `https://viewblock.io/zilliqa/address/${address}`;
          break;

        case 'DOT':
          url = `https://polkadot.subscan.io/account/${address}`;
          break;

        case 'KSM':
          url = `https://kusama.subscan.io/account/${address}`;
          break;

        case 'FIL':
          url = `https://filscan.io/#/tipset/address-detail?address=${address}`;
          break;

        case 'BNB':
        case 'BUSD':
          url = `https://bscscan.com/address/${address}`;
          break;

        case 'ONE':
          url = `https://explorer.harmony.one/#/address/${address}`;
          break;

        case 'RBTC':
        case 'RDOC':
        case 'DOC':
        case 'RIF':
        case 'SOV':
          url = `https://explorer.rsk.co/address/${address}`;
          break;

        case 'CKB':
          url = `https://explorer.nervos.org/address/${address}`;
          break;

        case 'XDC':
          url = `https://explorer.xinfin.network/addr/${address}`;
          break;

        case 'ALGO':
        case 'USDTa':
        case 'USDCa':
          url = `https://algoexplorer.io/tx/${address}`;
          break;

        case 'SC':
          url = `https://siastats.info/navigator?search=${address}`;
          break;

        case 'XTZ':
          url = `https://tzkt.io/${address}/operations/`;
          break;

        default:
          url = `https://etherscan.io/address/${address}`;
      }
      return url;
    },
    getQRString: function(token_name, address, value) {
      value = value || 0;

      let qr_string;

      switch (token_name) {
        case 'BTC':
          qr_string = value ?
            `bitcoin:${address}?amount=${value}` :
            `bitcoin:${address}`;
          break;

        case 'ETC':
          qr_string = value ?
            `ethereum:${address}?value=${value}` :
            `ethereum:${address}`;
          break;

        case 'CELO':
        case 'cUSD':
          qr_string = value ?
            `celo://wallet/pay?address=${address}&amount=${value}&token=${token_name}` :
            `celo://wallet/pay?address=${address}&token=${token_name}`;
          break;

        case 'ZIL':
          qr_string = value ?
            `zilliqa://${address}?amount=${value}` :
            `zilliqa://${address}`;
          break;

        case 'FIL':
          qr_string = value ?
            `filecoin://${address}?amount=${value}` :
            `filecoin://${address}`;
          break;
      }

      return qr_string;
    },
    syncBounty: function() {
      let vm = this;

      if (!localStorage[document.issueURL]) {
        vm.loadingState = 'notfound';
        return;
      }

      let bountyMetadata = JSON.parse(localStorage[document.issueURL]);

      async function waitBlock(txid) {
        let receipt = promisify(cb => web3.eth.getTransactionReceipt(txid, cb));

        try {
          let result = await receipt;

          console.log(result);
          const data = {
            url: document.issueURL,
            txid: txid,
            network: document.web3network
          };
          let syncDb = fetchData('/sync/web3/', 'POST', data);

          $.when(syncDb).then(function(response) {
            console.log(response);

            vm.fetchBounty(true);
          }).catch(function(error) {
            setTimeout(vm.syncBounty(), 10000);
          });
        } catch (error) {
          return error;
        }
      }
      waitBlock(bountyMetadata.txid);

    },
    checkOwner: function(handle) {
      let vm = this;

      if (vm.contxt.github_handle) {
        return caseInsensitiveCompare(document.contxt['github_handle'], handle);
      }
      return false;

    },
    checkOwnerAddress: function(bountyOwnerAddress) {
      let vm = this;

      if (cb_address) {
        return caseInsensitiveCompare(cb_address, bountyOwnerAddress);
      }
      return false;

    },
    checkInterest: function() {
      let vm = this;

      if (!vm.contxt.github_handle) {
        return false;
      }
      let isInterested = !!(vm.bounty.interested || []).find(interest => caseInsensitiveCompare(interest.profile.handle, vm.contxt.github_handle));
      // console.log(isInterested)

      return isInterested;

    },
    checkApproved: function() {
      let vm = this;

      if (!vm.contxt.github_handle) {
        return false;
      }
      // pending=false
      let result = vm.bounty.interested.find(interest => caseInsensitiveCompare(interest.profile.handle, vm.contxt.github_handle));

      return result ? !result.pending : false;

    },
    checkFulfilled: function() {
      let vm = this;

      if (!vm.contxt.github_handle) {
        return false;
      }
      return !!(vm.bounty.fulfillments || []).find(fulfiller => caseInsensitiveCompare(fulfiller.fulfiller_github_username, vm.contxt.github_handle));
    },
    syncGhIssue: function() {
      let vm = this;
      let apiUrlIssueSync = `/sync/get_issue_details?url=${encodeURIComponent(vm.bounty.github_url)}&token=${currentProfile.githubToken}`;
      const getIssueSync = fetchData(apiUrlIssueSync, 'GET');

      $.when(getIssueSync).then(function(response) {
        vm.updateGhIssue(response);
      });
    },
    updateGhIssue: function(response) {
      let vm = this;
      const payload = JSON.stringify({
        issue_description: response.description,
        title: response.title
      });
      let apiUrlUpdateIssue = `/bounty/change/${vm.bounty.pk}`;
      const postUpdateIssue = fetchData(apiUrlUpdateIssue, 'POST', payload);

      $.when(postUpdateIssue).then(function(response) {
        vm.bounty.issue_description = response.description;
        vm.bounty.title = response.title;
        _alert({ message: response.msg }, 'success');
      }).catch(function(response) {
        _alert({ message: response.responseJSON.error }, 'danger');
      });
    },
    copyTextToClipboard: function(text) {
      if (!navigator.clipboard) {
        _alert('Could not copy text to clipboard', 'danger', 5000);
      } else {
        navigator.clipboard.writeText(text).then(function() {
          _alert('Text copied to clipboard', 'success', 5000);
        }, function(err) {
          _alert('Could not copy text to clipboard', 'danger', 5000);
        });
      }
    },
    getTenant: function(token_name, web3_type) {
      let tenant;
      let vm = this;

      if (web3_type == 'manual') {
        tenant = 'OTHERS';
        return tenant;
      }

      switch (token_name) {

        case 'ETC':
          tenant = 'ETC';
          break;

        case 'BTC':
          tenant = 'BTC';
          break;

        case 'CELO':
        case 'cUSD':
          tenant = 'CELO';
          break;

        case 'ZIL':
          tenant = 'ZIL';
          break;

        case 'DOT':
        case 'KSM':
          tenant = 'POLKADOT';
          break;

        case 'FIL':
          tenant = 'FILECOIN';
          break;

        case 'BNB':
        case 'BUSD':
          tenant = 'BINANCE';
          break;

        case 'ONE':
          tenant = 'HARMONY';
          break;

        case 'RBTC':
        case 'DOC':
        case 'RDOC':
        case 'RIF':
        case 'SOV':
          tenant = 'RSK';
          break;

        case 'CKB':
          tenant = 'NERVOS';
          vm.canChangeFunderAddress = true;
          break;

        case 'XDC':
          tenant = 'XINFIN';
          break;

        case 'ALGO':
        case 'USDTa':
        case 'USDCa':
          tenant = 'ALGORAND';
          break;

        case 'SC':
          tenant = 'SIA';
          vm.canChangeFunderAddress = true;
          break;

        case 'XTZ':
          tenant = 'TEZOS';
          break;

        default:
          tenant = 'ETH';
      }

      return tenant;
    },
    fulfillmentComplete: function(payout_type, fulfillment_id, event) {
      let vm = this;

      const token_name = vm.bounty.token_name;
      const decimals = tokenNameToDetails('mainnet', token_name).decimals;
      const amount = vm.fulfillment_context.amount;
      const payout_tx_id = vm.fulfillment_context.payout_tx_id ? vm.fulfillment_context.payout_tx_id : null;
      const funder_address = vm.bounty.bounty_owner_address;
      const tenant = vm.getTenant(token_name, vm.bounty.web3_type);

      const payload = {
        payout_type: payout_type,
        tenant: tenant,
        amount: amount * 10 ** decimals,
        token_name: token_name,
        funder_address: funder_address,
        payout_tx_id: payout_tx_id
      };

      const apiUrlBounty = `/api/v1/bounty/payout/${fulfillment_id}`;

      event.target.disabled = true;

      fetchData(apiUrlBounty, 'POST', payload).then(response => {
        event.target.disabled = false;
        if (200 <= response.status && response.status <= 204) {
          console.log('success', response);

          vm.fetchBounty();
          this.$refs['payout-modal' + fulfillment_id][0].closeModal();

          vm.fulfillment_context = {
            active_step: 'payout_amount'
          };

        } else {
          _alert('Unable to make payout bounty. Please try again later', 'danger');
          console.error(`error: bounty payment failed with status: ${response.status} and message: ${response.message}`);
        }
      }).catch(function(error) {
        event.target.disabled = false;
        _alert('Unable to make payout bounty. Please try again later', 'danger');
      });
    },
    nextStepAndLoadPYPLButton: function(fulfillment_id, fulfiller_identifier) {
      let vm = this;

      Promise.resolve(vm.goToStep('submit_transaction', 'payout_amount')).then(() => {
        const ele = '#payout-with-pypl';

        $(ele).html('');
        const modal = this.$refs['payout-modal' + fulfillment_id][0];

        payWithPYPL(fulfillment_id, fulfiller_identifier, ele, vm, modal);
      });
    },
    payWithExtension: function(fulfillment_id, fulfiller_address, payout_type) {
      let vm = this;
      const modal = this.$refs['payout-modal' + fulfillment_id][0];

      switch (payout_type) {
        case 'web3_modal':
          payWithWeb3(fulfillment_id, fulfiller_address, vm, modal);
          break;

        case 'polkadot_ext':
          payWithPolkadotExtension(fulfillment_id, fulfiller_address, vm, modal);
          break;

        case 'binance_ext':
          payWithBinanceExtension(fulfillment_id, fulfiller_address, vm, modal);
          break;

        case 'harmony_ext':
          payWithHarmonyExtension(fulfillment_id, fulfiller_address, vm, modal);
          break;

        case 'rsk_ext':
          payWithRSKExtension(fulfillment_id, fulfiller_address, vm, modal);
          break;

        case 'xinfin_ext':
          payWithXinfinExtension(fulfillment_id, fulfiller_address, vm, modal);
          break;

        case 'algorand_ext':
          payWithAlgorandExtension(fulfillment_id, fulfiller_address, vm, modal);
          break;

        case 'tezos_ext':
          payWithTezosExtension(fulfillment_id, fulfiller_address, vm, modal);
          break;
      }
    },
    closeBounty: function() {

      let vm = this;
      const bounty_id = vm.bounty.pk;

      const apiUrlBounty = `/api/v1/bounty/${bounty_id}/close`;

      fetchData(apiUrlBounty, 'POST').then(response => {
        if (200 <= response.status && response.status <= 204) {
          vm.bounty.status = 'done';
        } else {
          _alert('Unable to close. bounty. Please try again later', 'danger');
          console.error(`error: bounty closure failed with status: ${response.status} and message: ${response.message}`);
        }
      });
    },
    show_extend_deadline_modal: function() {
      show_extend_deadline_modal();
    },
    show_interest_modal: function() {
      show_interest_modal();
    },
    staffOptions: function() {
      let vm = this;

      if (!vm.bounty.pk) {
        return;
      }

      if (vm.contxt.is_staff && !vm.quickLinks.length) {
        vm.quickLinks.push({
          label: 'View in Admin',
          href: `/_administrationdashboard/bounty/${vm.bounty.pk}/change/`,
          title: 'View in Admin Tool'
        }, {
          label: 'Hide Bounty',
          href: `${vm.bounty.url}?admin_override_and_hide=1`,
          title: 'Hides Bounty from Active Bounties'
        }, {
          label: 'Toggle Remarket Ready',
          href: `${vm.bounty.url}?admin_toggle_as_remarket_ready=1`,
          title: 'Sets Remarket Ready if not already remarket ready.  Unsets it if already remarket ready.'
        }, {
          label: 'Suspend Auto Approval',
          href: `${vm.bounty.url}?suspend_auto_approval=1`,
          title: 'Suspend *Auto Approval* of Bounty Hunters Who Have Applied for This Bounty'
        });

        if (vm.bounty.needs_review) {
          vm.quickLinks.push({
            label: 'Mark as Reviewed',
            href: `${vm.bounty.url}?mark_reviewed=1`,
            title: 'Suspend *Auto Approval* of Bounty Hunters Who Have Applied for This Bounty'
          });
        }
      }
    },
    contactFunder: function() {
      let vm = this;
      let text = window.prompt('What would you like to say to the funder?', '');

      if (text === null) {
        return;
      }
      document.location.href = `${vm.bounty.url}?admin_contact_funder=${text}`;
    },
    snoozeeGitbot: function() {
      let vm = this;
      let text = window.prompt('How many days do you want to snooze?', '');

      if (text === null) {
        return;
      }
      document.location.href = `${vm.bounty.url}?snooze=${text}`;
    },
    hasAcceptedFulfillments: function() {
      let vm = this;

      if (!vm.bounty) {
        return [];
      }

      return vm.bounty.fulfillments.filter(fulfillment =>
        fulfillment.accepted &&
        fulfillment.payout_status == 'done'
      );

    },
    fetchIfPendingFulfillments: function() {
      let vm = this;

      const pendingFulfillments = vm.bounty.fulfillments.filter(fulfillment =>
        fulfillment.payout_status == 'pending'
      );

      if (pendingFulfillments.length > 0) {
        if (!vm.pollInterval) {
          vm.pollInterval = setInterval(vm.fetchBounty, 60000);
        }
      } else {
        clearInterval(vm.pollInterval);
        vm.pollInterval = null;
      }
      return;
    },
    stopWork: function(isOwner, handle) {
      let text = isOwner ?
        'Are you sure you would like to stop this user from working on this bounty ?' :
        'Are you sure you would like to stop working on this bounty ?';

      if (!confirm(text)) {
        return;
      }

      let vm = this;

      const headers = {
        'X-CSRFToken': csrftoken
      };

      const apiUrlBounty = `/actions/bounty/${vm.bounty.pk}/interest/remove/`;

      fetchData(apiUrlBounty, 'POST', { handle }, headers).then(response => {
        if (200 <= response.status && response.status <= 204) {
          this.fetchBounty();
          let text = isOwner ?
            "You\'ve stopped the user from working on this bounty ?" :
            "You\'ve stopped work on this bounty";

          let product = document.result.event ? 'hackathons' : 'bounties';
          let productPersona = document.result.event ? 'hackathon' : 'bounty';
          let persona = isOwner ? 'funder' : 'hunter';
          let mtcPersona = `${productPersona}-${persona}`;

          let stopEvent = {
            'alias': 'products',
            'data': [
              {
                'name': 'product',
                'attributes': {
                  'product': product,
                  'persona': mtcPersona,
                  'action': 'stop'
                }
              }
            ]
          };

          if (document.result.event) {
            let stopHackathonEvent = {
              'alias': 'hackathon',
              'data': [
                {
                  'name': 'stop',
                  'attributes': {
                    'hackathon-slug': document.result.event.slug,
                    'hackathon-action': 'stop'
                  }
                }
              ]
            };

            stopEvent = [ stopEvent, stopHackathonEvent ];

          }

          MauticEvent.createEvent(stopEvent);

          _alert(text, 'success');
        } else {
          _alert('Unable to stop work on bounty. Please try again later', 'danger');
          console.error(`error: stopping work on bounty failed due to : ${response}`);
        }
      });
    },
    canStopWork: function(handle) {
      let vm = this;

      if (!handle) {
        return false;
      }

      if (vm.bounty.fulfillments.filter(fulfillment =>
        fulfillment.fulfiller_github_username != handle).length
      ) {
        return true;
      }

      return false;
    },
    goToStep: function(nextStep, currentStep, flow) {
      let vm = this;

      if (flow) {
        vm.fulfillment_context.flow = flow;
      }
      vm.fulfillment_context.referrer = currentStep;
      vm.fulfillment_context.active_step = nextStep;
    },
    initFulfillmentContext: function(fulfillment) {
      let vm = this;

      switch (fulfillment.payout_type) {
        case 'qr':
        case 'manual':
        case 'nervos_ext':
        case 'sia_ext':
          vm.fulfillment_context.active_step = 'check_wallet_owner';
          vm.getTenant(vm.bounty.token_name, fulfillment.payout_type);
          break;

        case 'fiat':
        case 'web3_modal':
        case 'polkadot_ext':
        case 'rsk_ext':
        case 'xinfin_ext':
        case 'algorand_ext':
        case 'tezos_ext':
          vm.fulfillment_context.active_step = 'payout_amount';
          break;
      }
    },
    initChain: function() {

      let vm = this;
      const token = vm.bounty.token_name;

      switch (vm.bounty.web3_type) {
        case 'polkadot_ext': {
          let polkadot_endpoint;

          if (token == 'KSM') {
            polkadot_endpoint = KUSAMA_ENDPOINT;
          } else if (token == 'DOT') {
            polkadot_endpoint = POLKADOT_ENDPOINT;
          }

          polkadot_utils.connect(polkadot_endpoint).then(res => {
            console.log(res);
            polkadot_extension_dapp.web3Enable('gitcoin').then(() => {
              vm.fulfillment_context.active_step = 'payout_amount';
            }).catch(err => {
              _alert('Please ensure you\'ve connected your polkadot extension to Gitcoin', 'danger');
              console.log(err);
            });
          });
          break;
        }

        case 'binance_ext': {
          vm.fulfillment_context.active_step = 'payout_amount';
          break;
        }

        case 'harmony_ext':
          vm.fulfillment_context.active_step = 'payout_amount';
          break;
      }
    },
    validateFunderAddress: function(token_name) {
      let vm = this;
      let hasError = false;

      vm.errors = {};

      switch (token_name) {
        case 'CKB': {
          const ADDRESS_REGEX = new RegExp('^(ckb){1}[0-9a-zA-Z]{43,92}$');
          const isNervosValid = ADDRESS_REGEX.test(vm.bounty.bounty_owner_address);
    
          if (!isNervosValid && !vm.bounty.bounty_owner_address.toLowerCase().startsWith('0x')) {
            hasError = true;
          }
        }

        // include validation for other tokens here
      }

      if (hasError) {
        vm.$set(vm.errors, 'funderAddress', `Please enter a valid ${token_name} address`);
      }
    }
  },
  computed: {
    sortedActivity: function() {
      const token_details = tokenAddressToDetailsByNetwork(
        this.bounty.token_address, this.bounty.network
      );
      const decimals = token_details && token_details.decimals;

      this.decimals = decimals;

      let activities = this.bounty.activities.sort((a, b) => new Date(b.created) - new Date(a.created));

      if (decimals) {
        activities.forEach((activity, index) => {
          if (activity.metadata) {
            if (activity.metadata.token_name == 'USD' && activity.activity_type == 'worker_paid') {
              activity.metadata['token_value'] = activity.metadata.payout_amount;
            } else {
              activity.metadata['token_value'] = activity.metadata.value_in_token / 10 ** decimals;
            }
          }
        });
      }
      return activities;
    },
    isExpired: function() {
      return moment(document.result['expires_date']).isBefore();
    },
    expiresAfterAYear: function() {
      return moment().diff(document.result['expires_date'], 'years') < -1;
    }
  }
});

if (document.getElementById('gc-bounty-detail')) {
  appBounty = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-bounty-detail',
    data() {
      return {
        errors: {},
        loadingState: loadingState['loading'],
        bounty: bounty,
        url: url,
        cb_address: cb_address,
        isOwner: false,
        isOwnerAddress: false,
        fulfillment_context: {
          active_step: 'check_wallet_owner',
          include_amount_in_qr: true,
          amount: 0
        },
        decimals: 18,
        inputBountyOwnerAddress: bounty.bounty_owner_address,
        contxt: document.contxt,
        quickLinks: [],
        pollInterval: null,
        canChangeFunderAddress: false
      };
    },
    mounted() {
      this.fetchBounty();
    }
  });
}


var show_extend_deadline_modal = function() {
  let modals = $('#modalExtend');
  let modalBody = $('#modalExtend .modal-content');
  const url = '/modal/extend_issue_deadline?pk=' + document.result['pk'];

  moment.locale('en');
  modals.on('show.bs.modal', function() {
    modalBody.load(url, () => {
      const currentExpires = moment.utc(document.result['expires_date']);

      $('#modalExtend input[name="expirationTimeDelta"]').daterangepicker({
        parentEl: '#extend_deadline',
        singleDatePicker: true,
        startDate: moment(currentExpires).add(1, 'month'),
        minDate: moment().add(1, 'day'),
        ranges: {
          '1 week': [ moment(currentExpires).add(7, 'days'), moment(currentExpires).add(7, 'days') ],
          '2 weeks': [ moment(currentExpires).add(14, 'days'), moment(currentExpires).add(14, 'days') ],
          '1 month': [ moment(currentExpires).add(1, 'month'), moment(currentExpires).add(1, 'month') ],
          '3 months': [ moment(currentExpires).add(3, 'month'), moment(currentExpires).add(3, 'month') ],
          '1 year': [ moment(currentExpires).add(1, 'year'), moment(currentExpires).add(1, 'year') ]
        },
        'locale': {
          'customRangeLabel': 'Custom'
        }
      }, function(start, end, label) {
        set_extended_time_html(end);
      });

      set_extended_time_html($('#modalExtend input[name="expirationTimeDelta"]').data('daterangepicker').endDate);

      $('#neverExpires').on('click', () => {
        if ($('#neverExpires').is(':checked')) {
          $('#expirationTimeDelta').attr('disabled', true);
          $('#extended-expiration-date #extended-days').html('Never');
          $('#extended-expiration-date #extended-date').html('-');
        } else {
          $('#expirationTimeDelta').attr('disabled', false);
          set_extended_time_html($('#modalExtend input[name="expirationTimeDelta"]').data('daterangepicker').endDate);
        }
      });

      modals.on('submit', function(event) {
        event.preventDefault();

        var extended_time = $('input[name=updatedExpires]').val();

        extend_expiration(document.result['pk'], {
          deadline: extended_time
        });
      });
    });
  });
  modals.bootstrapModal('show');
  $(document, modals).on('hidden.bs.modal', function(e) {
    $('#extend_deadline').remove();
    $('.daterangepicker').remove();
  });
};

var set_extended_time_html = function(extendedDuration) {
  extendedDuration = extendedDuration.set({ hour: 0, minute: 0, second: 0, millisecond: 0 });
  $('input[name=updatedExpires]').val(extendedDuration.utc().unix());
  $('#extended-expiration-date #extended-date').html(extendedDuration.format('MM-DD-YYYY hh:mm A'));
  $('#extended-expiration-date #extended-days').html(moment.utc(extendedDuration).fromNow());
};

var extend_expiration = function(bounty_pk, data) {
  var request_url = '/actions/bounty/' + bounty_pk + '/extend_expiration/';

  $.post(request_url, data, function(result) {

    if (result.success) {
      _alert({ message: result.msg }, 'success');
      appBounty.bounty.expires_date = moment.unix(data.deadline).utc().format();
      return appBounty.bounty.expires_date;
    }
    return false;
  }).fail(function(result) {
    _alert({ message: gettext('got an error. please try again, or contact support@gitcoin.co') }, 'danger');
  });
};

const submitInterest = (bounty, msg, self, onSuccess) => {
  add_interest(bounty, {
    issue_message: msg
  }).then(success => {
    if (success) {
      $(self).attr('href', '/uninterested');
      $(self).find('span').text(gettext('Stop Work'));
      $(self).parent().attr('title', '<div class="tooltip-info tooltip-sm">' + gettext('Notify the funder that you will not be working on this project') + '</div>');


      if (onSuccess) {
        onSuccess();
      }
    }
  }).catch((error) => {
    if (error.responseJSON.error === 'You may only work on max of 3 issues at once.')
      return;
    throw error;
  });
};

var show_interest_modal = function() {
  var modals = $('#modalInterest');
  let modalBody = $('#modalInterest .modal-content');
  let modalUrl = `/interest/modal?redirect=${window.location.pathname}&pk=${document.result['pk']}`;

  modals.on('show.bs.modal', function() {
    modalBody.load(modalUrl, () => {
      let actionPlanForm = $('#action_plan');
      let issueMessage = $('#issue_message');
      let data = $('.team-users').data('initial') ? $('.team-users').data('initial').split(', ') : [];
      let projectForm = $('#projectForm');

      userSearch('.team-users', false, '', data, true, false);
      $('#looking-members').on('click', function() {
        $('.looking-members').toggle();
      });
      issueMessage.attr('placeholder', gettext('What steps will you take to complete this task? (min 30 chars)'));
      if (document.result.event) {
        $(document).on('change', '#project_logo', function() {
          previewFile($(this));
        });
        projectForm.on('submit', function(e) {
          e.preventDefault();
          const elements = $(this)[0];
          const logo = elements['logo'].files[0];
          const summary = elements['summary'].value;
          const data = $(this).serializeArray();

          submitInterest(document.result['pk'], summary, self, () => {
            appBounty.fetchBounty();

            submitProject(logo, data);
            modals.bootstrapModal('hide');
          });

          MauticEvent.createEvent({
            'alias': 'hackathon',
            'data': [
              {
                'name': 'interest',
                'attributes': {
                  'hackathon-slug': document.result.event.slug,
                  'hackathon-action': 'interest'
                }
              }
            ]
          },
          {
            'alias': 'products',
            'data': [
              {
                'name': 'product',
                'attributes': {
                  'product': 'hackathon',
                  'persona': 'hackathon-hunter',
                  'action': 'interest'
                }
              }
            ]
          });

        });

        return;
      }

      actionPlanForm.on('submit', function(event) {
        event.preventDefault();

        let msg = issueMessage.val().trim();

        if (!msg || msg.length < 30) {
          _alert({ message: gettext('Please provide an action plan for this ticket. (min 30 chars)') }, 'danger');
          return false;
        }

        add_interest(document.result['pk'], {
          issue_message: msg
        }).then(success => {
          if (success) {
            appBounty.fetchBounty();
            MauticEvent.createEvent({
              'alias': 'products',
              'data': [
                {
                  'name': 'product',
                  'attributes': {
                    'product': 'bounties',
                    'persona': 'bounty-hunter',
                    'action': 'interest'
                  }
                }
              ]
            });
            modals.bootstrapModal('hide');

            if (document.result.event) {
              projectModal(document.result.pk);
            }
          }
        }).catch((error) => {
          if (error.responseJSON.error === 'You may only work on max of 3 issues at once.')
            return;
          throw error;
        });

      });

    });
  });
  modals.bootstrapModal('show');
};

// $('body').on('click', '.issue_description img', function() {
//   var content = $.parseHTML(
//     '<div><div class="row"><div class="col-12 closebtn">' +
//       '<a id="" rel="modal:close" href="javascript:void" class="close" aria-label="Close dialog">' +
//         '<span aria-hidden="true">&times;</span>' +
//       '</a>' +
//     '</div>' +
//     '<div class="col-12 pt-2 pb-2"><img class="magnify" src="' + $(this).attr('src') + '"/></div></div></div>');

//   $(content).appendTo('body').modal({
//     modalClass: 'modal magnify'
//   });
// });

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

const promisify = (inner) =>
  new Promise((resolve, reject) =>
    inner((err, res) => {
      if (err) {
        reject(err);
      } else {
        resolve(res);
      }
    })
  );
