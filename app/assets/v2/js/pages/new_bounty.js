let appFormBounty;

window.addEventListener('dataWalletReady', function(e) {
  appFormBounty.network = networkName;
  appFormBounty.form.funderAddress = selectedAccount;
}, false);

const helpText = {
  '#new-bounty-acceptace-criteria': 'Check out great examples of acceptance criteria from some of our past successful bounties!'
};

const bountyTypes = [
  'Bug',
  'Project',
  'Feature',
  'Security',
  'Improvement',
  'Design',
  'Docs',
  'Code review',
  'Other'
];

Vue.use(VueQuillEditor);
Vue.component('v-select', VueSelect.VueSelect);

Vue.component('quill-editor-ext', {
  props: [ 'initial', 'options' ],
  template: '#quill-editor-ext',
  data() {
    return {
    };
  },
  methods: {
    onUpdate: function(event) {
      this.$emit('change', {
        text: event.text,
        delta: event.quill.getContents()
      });
    }
  },
  mounted() {
    this.$refs.quillEditor.quill.setContents(this.initial);
  }
});

Vue.mixin({
  data() {
    return {
      step: 1,
      bountyTypes: bountyTypes,
      tagOptions: [
        'JavaScript',
        'TypeScript',
        'HTML',
        'Solidity',
        'CSS',
        'Python',
        'React',
        'Ethereum',
        'Blockchain',
        'DeFi',
        'Shell',
        'web3',
        'Design',
        'NFT',
        'Rust',
        'Dockerfile',
        'Go',
        'Community',
        'dApp',
        'API',
        'Documentation',
        'DAO',
        'Smart contract',
        'UI/UX',
        'POAP'
      ],
      contactDetailsType: [
        'Discord',
        'Telegram',
        'Email'
      ],
      contactDetailsPlaceholderMap: {
        '': 'mydiscord#1234',
        'Discord': 'mydiscord#1234',
        'Telegram': 'mytelegramusername',
        'Email': 'my@email.com'
      },
      networkOptions: [
        {
          'id': '1',
          'logo': static_url + 'v2/images/chains/ethereum.svg',
          'label': 'ETH'
        },
        {
          'id': '0',
          'logo': static_url + 'v2/images/chains/bitcoin.svg',
          'label': 'BTC'
        },
        {
          'id': '666',
          'logo': static_url + 'v2/images/chains/paypal.svg',
          'label': 'PayPal'
        },
        {
          'id': '56',
          'logo': static_url + 'v2/images/chains/binance.svg',
          'label': 'Binance'
        },
        {
          'id': '1000',
          'logo': static_url + 'v2/images/chains/harmony.svg',
          'label': 'Harmony'
        },
        {
          'id': '58',
          'logo': static_url + 'v2/images/chains/polkadot.svg',
          'label': 'Polkadot'
        },
        {
          'id': '59',
          'logo': static_url + 'v2/images/chains/kusama.svg',
          'label': 'Kusama'
        },
        {
          'id': '61',
          'logo': static_url + 'v2/images/chains/ethereum-classic.svg',
          'label': 'ETC'
        },
        {
          'id': '102',
          'logo': static_url + 'v2/images/chains/zilliqa.svg',
          'label': 'Zilliqa'
        },
        {
          'id': '600',
          'logo': static_url + 'v2/images/chains/filecoin.svg',
          'label': 'Filecoin'
        },
        {
          'id': '42220',
          'logo': static_url + 'v2/images/chains/celo.svg',
          'label': 'Celo'
        },
        {
          'id': '30',
          'logo': static_url + 'v2/images/chains/rsk.svg',
          'label': 'RSK'
        },
        {
          'id': '50',
          'logo': static_url + 'v2/images/chains/xinfin.svg',
          'label': 'Xinfin'
        },
        {
          'id': '1001',
          'logo': static_url + 'v2/images/chains/algorand.svg',
          'label': 'Algorand'
        },
        {
          'id': '1935',
          'logo': static_url + 'v2/images/chains/sia.svg',
          'label': 'Sia'
        },
        {
          'id': '1995',
          'logo': static_url + 'v2/images/chains/nervos.svg',
          'label': 'Nervos'
        },
        {
          'id': '50797',
          'logo': static_url + 'v2/images/chains/tezos.svg',
          'label': 'Tezos'
        },
        {
          'id': '270895',
          'logo': static_url + 'v2/images/chains/casper.svg',
          'label': 'Casper'
        },
        {
          'id': '717171',
          'logo': null,
          'label': 'Other'
        }
      ]
    };
  },
  methods: {
    getContactDetailsPlaceholder: function(val) {
      return this.contactDetailsPlaceholderMap[val] || this.contactDetailsPlaceholderMap[''];
    },
    estHoursValidator: function() {
      this.form.hours = parseFloat(this.form.hours || 0);
      this.form.hours = Math.ceil(this.form.hours);
      this.calcValues('token');
    },
    getIssueDetails: function(url) {
      let vm = this;

      if (!url) {
        vm.$set(vm.errors, 'issueDetails', undefined);
        vm.form.issueDetails = null;
        return vm.form.issueDetails;
      }

      let ghIssueUrl;

      try {
        ghIssueUrl = new URL(url);
      } catch (e) {
        vm.form.issueDetails = undefined;
        vm.$set(vm.errors, 'issueDetails', 'Please paste a github issue url');
        return;
      }

      if (ghIssueUrl.host != 'github.com') {
        vm.form.issueDetails = undefined;
        vm.$set(vm.errors, 'issueDetails', 'Please paste a github issue url');
        return;
      }

      if (ghIssueUrl.pathname.includes('/pull/')) {
        vm.$set(vm.errors, 'issueDetails', 'Please paste a github issue url and not a PR');
        return;
      }


      vm.orgSelected = ghIssueUrl.pathname.split('/')[1].toLowerCase();

      if (vm.checkBlocked(vm.orgSelected)) {
        vm.$set(vm.errors, 'issueDetails', 'This repo is not bountyable at the request of the maintainer.');
        vm.form.issueDetails = undefined;
        return;
      }
      vm.$delete(vm.errors, 'issueDetails');

      let apiUrldetails = `/sync/get_issue_details?url=${encodeURIComponent(url.trim())}&duplicates=true&network=${vm.network}`;

      if (vm.hackathon_slug) {
        apiUrldetails += `&hackathon_slug=${encodeURIComponent(vm.hackathon_slug)}`;
      }

      vm.form.issueDetails = undefined;
      const getIssue = fetchData(apiUrldetails, 'GET');

      $.when(getIssue).then((response) => {
        if (!Object.keys(response).length) {
          return vm.$set(vm.errors, 'issueDetails', 'Nothing found. Please check the issue URL.');
        }

        vm.form.issueDetails = response;

        let md = window.markdownit();

        vm.form.richDescription = md.render(vm.form.issueDetails.description);
        vm.form.title = vm.form.issueDetails.title;

        vm.$set(vm.errors, 'issueDetails', undefined);
      }).catch((err) => {
        console.log(err);
        vm.form.issueDetails = undefined;
        vm.$set(vm.errors, 'issueDetails', err.responseJSON.message);
      });

    },
    validateOrgUrl: function(url) {
      let vm = this;

      if (!url) {
        vm.$set(vm.errors, 'orgDetails', undefined);
        return;
      }

      let ghIssueUrl;

      try {
        ghIssueUrl = new URL(url);
      } catch (e) {
        vm.$set(vm.errors, 'orgDetails', 'Please paste a github org url');
        return;
      }

      if (ghIssueUrl.host != 'github.com') {
        vm.$set(vm.errors, 'orgDetails', 'Please paste a github org url');
        return;
      }

      let apiUrldetails = `/sync/validate_org_url?url=${encodeURIComponent(url.trim())}`;

      if (vm.hackathon_slug) {
        apiUrldetails += `&hackathon_slug=${encodeURIComponent(vm.hackathon_slug)}`;
      }

      vm.form.orgDetails = undefined;
      const getIssue = fetchData(apiUrldetails, 'GET');

      $.when(getIssue).then((response) => {
        vm.$set(vm.errors, 'orgDetails', undefined);
      }).catch((err) => {
        console.log(err);
        vm.form.issueDetails = undefined;
        vm.$set(vm.errors, 'orgDetails', err.responseJSON.message);
      });
    },
    getTokens: function() {
      let vm = this;
      const apiUrlTokens = '/api/v1/tokens/';
      const getTokensData = fetchData(apiUrlTokens, 'GET');

      $.when(getTokensData).then((response) => {
        vm.tokens = response;
        // vm.form.token = vm.filterByChainId[0];
        vm.getAmount(vm.form.token.symbol);

      }).catch((err) => {
        console.log(err);
      });

    },
    getBinanceSelectedAccount: async function() {
      let vm = this;

      try {
        vm.form.funderAddress = await binance_utils.getSelectedAccount();
      } catch (error) {
        vm.funderAddressFallback = true;
      }
    },
    onChainInput: function() {
      this.form.token = null;
      this.form.amount = 0;
      this.form.amountusd = 0;
    },
    getAmount: function(token) {
      let vm = this;

      if (!token) {
        return;
      }
      const apiUrlAmount = `/sync/get_amount?amount=1&denomination=${token}`;
      const getAmountData = fetchData(apiUrlAmount, 'GET');

      $.when(getAmountData).then(tokens => {
        vm.coinValue = tokens[0].usdt;
        // vm.calcValues('usd');
      }).catch((err) => {
        console.log(err);
      });
    },
    calcValues: function(direction) {
      let vm = this;

      if (direction == 'usd') {
        let usdValue = vm.form.amount * vm.coinValue;

        vm.form.amountusd = Number(usdValue.toFixed(2));
      } else {
        vm.form.amount = Number(vm.form.amountusd * 1 / vm.coinValue).toFixed(4);
      }

    },
    addKeyword: function(item) {
      let vm = this;

      vm.form.keywords.push(item);
    },
    validateFunderAddress: function() {
      let vm = this;

      return validateWalletAddress(vm.chainId, vm.form.funderAddress);
    },
    checkFormStep1: function() {
      let vm = this;

      ret = {};

      if (vm.step1Submitted) {
        if (!vm.form.experience_level) {
          ret['experience_level'] = 'Please select the experience level';
        }
        if (!vm.form.project_length) {
          ret['project_length'] = 'Please select the project length';
        }

        if (!vm.form.bounty_type) {
          ret['bounty_type'] = 'Please select the bounty type';
        } else if (vm.form.bounty_type === 'Other') {
          if (!vm.form.bounty_type_other) {
            ret['bounty_type_other'] = 'Please describe your bounty type';
          }
        }
        
        if (vm.form.keywords.length < 1) {
          ret['keywords'] = 'Select at least one category';
        }
      }

      return ret;
    },

    checkFormStep2: function() {
      let vm = this;

      ret = {};

      if (vm.step2Submitted) {
        if (!vm.form.bountyInformationSource) {
          ret['bountyInformationSource'] = 'Select the bounty information source';
        } else if (vm.form.bountyInformationSource === 'github') {
          
          if (!vm.form.issueUrl) {
            ret['issueDetails'] = 'Please input a GitHub issue';
          } else if (vm.errors.issueDetails) {
            if (vm.errors.issueDetails) {
              ret['issueDetails'] = vm.errors.issueDetails;
            }
          }

        } else {
          if (!vm.form.title) {
            ret['title'] = 'Please input bounty title';
          }

          if (!vm.form.richDescriptionText.trim()) {
            ret['description'] = 'Please input bounty description';
          }

          if (vm.isHackathonBounty) {
            if (!vm.form.organisationUrl) {
              ret['organisationUrl'] = 'Please input a GitHub organization URL';
            } else if (vm.errors.orgDetails) {
              if (vm.errors.orgDetails) {
                ret['organisationUrl'] = vm.errors.orgDetails;
              }
            }
          }

        }
      }

      return ret;
    },

    checkFormStep3: function() {
      let vm = this;

      ret = {};

      if (vm.step3Submitted) {
        if (!vm.chainId) {
          ret['chainId'] = 'Please select a chain';
        }

        if (!vm.form.token) {
          ret['token'] = 'Please select a token';
        }

        if (vm.form.peg_to_usd) {
          let amountusd = Number.parseFloat(vm.form.amountusd);

          if (!amountusd > 0) {
            ret['amountusd'] = 'Please enter a valid anount';
          }
        } else {
          let amount = Number.parseFloat(vm.form.amount);

          if (!amount > 0) {
            ret['amount'] = 'Please enter a valid anount';
          }
        }
      }

      return ret;
    },

    checkFormStep4: function() {
      let vm = this;

      ret = {};

      if (vm.step4Submitted) {
        if (!vm.form.project_type) {
          ret['project_type'] = 'Select the project type';
        }
        if (!vm.form.permission_type) {
          ret['permission_type'] = 'Select the permission type';
        }
      }

      return ret;
    },

    checkForm: async function() {
      return true;
    },
    web3Type() {
      let vm = this;
      let type;

      switch (vm.chainId) {
        case '1':
          // ethereum
          type = 'web3_modal';
          break;
        case '30':
          // rsk
          type = 'rsk_ext';
          break;
        case '50':
          // xinfin
          type = 'xinfin_ext';
          break;
        case '59':
        case '58':
          // 58 - polkadot, 59 - kusama
          type = 'polkadot_ext';
          break;
        case '56':
          // binance
          type = 'binance_ext';
          break;
        case '1000':
          // harmony
          type = 'harmony_ext';
          break;
        case '1995':
          // nervos
          type = 'nervos_ext';
          break;
        case '1001':
          // algorand
          type = 'algorand_ext';
          break;
        case '1935':
          // sia
          type = 'sia_ext';
          break;
        case '50797':
          // tezos
          type = 'tezos_ext';
          break;
        case '270895':
          // casper
          type = 'casper_ext';
          break;
        case '1155':
          // cosmos
          type = 'cosmos_ext';
          break;
        case '666':
          // paypal
          type = 'fiat';
          break;
        case '0': // bitcoin
        case '61': // ethereum classic
        case '102': // zilliqa
        case '600': // filecoin
        case '42220': // celo mainnet
        case '44786': // celo alfajores tesnet
        case '717171': // other
          type = 'qr';
          break;
        default:
          type = 'web3_modal';
      }

      vm.form.web3_type = type;
      return type;
    },
    getParams: async function() {
      let vm = this;

      let params = new URLSearchParams(window.location.search);

      if (params.has('invite')) {
        vm.expandedGroup.reserve = [1];
      }

      if (params.has('reserved')) {
        vm.expandedGroup.reserve = [1];
        await vm.getUser(null, params.get('reserved'), true);
      }

      let url;

      if (params.has('url')) {
        url = params.get('url');
        vm.form.issueUrl = url;
        vm.getIssueDetails(url);
      }

      if (params.has('source')) {
        url = params.get('source');
        vm.form.issueUrl = url;
        vm.getIssueDetails(url);
      }
    },
    showQuickStart: function(force) {
      let quickstartDontshow = localStorage['quickstart_dontshow'] ? JSON.parse(localStorage['quickstart_dontshow']) : false;

      if (quickstartDontshow !== true || force) {
        fetch('/bounty/quickstart')
          .then(function(response) {
            return response.text();
          }).then(function(html) {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const guide = doc.querySelector('.btn-closeguide');

            doc.querySelector('.show_video').href = 'https://www.youtube.com/watch?v=m1X0bDpVcf4';
            doc.querySelector('.show_video').target = '_blank';

            guide.dataset.dismiss = 'modal';

            const docArticle = doc.querySelector('.content').innerHTML;
            const content = $.parseHTML(
              `<div id="gitcoin_updates" class="modal fade" tabindex="-1" role="dialog" aria-hidden="true">
                <div class="modal-dialog modal-xl" style="max-width:95%">
                  <div class="modal-content px-4 py-3">
                    <div class="col-12">
                      <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                        <span aria-hidden="true">&times;</span>
                      </button>
                    </div>
                    ${docArticle}
                    <div class="col-12 my-4 d-flex justify-content-around">
                      <button type="button" class="btn btn-primary" data-dismiss="modal" aria-label="Close">Close</button>
                    </div>
                  </div>
                </div>
              </div>`);

            $(content).appendTo('body');
            document.getElementById('dontshow').checked = quickstartDontshow;
            $('#gitcoin_updates').bootstrapModal('show');

            $(document).on('change', '#dontshow', function(e) {
              if ($(this)[0].checked) {
                localStorage['quickstart_dontshow'] = true;
              } else {
                localStorage['quickstart_dontshow'] = false;
              }
            });
          });

        $(document, '#gitcoin_updates').on('hidden.bs.modal', function(e) {
          $('#gitcoin_updates').remove();
          $('#gitcoin_updates').bootstrapModal('dispose');
        });
      }
    },
    isExpanded(key, type) {
      return this.expandedGroup[type].indexOf(key) !== -1;
    },
    toggleCollapse(key, type) {
      if (this.isExpanded(key, type)) {
        this.expandedGroup[type].splice(this.expandedGroup[type].indexOf(key), 1);
      } else {
        this.expandedGroup[type].push(key);
      }
    },
    updateDate(date) {
      // date is expected to be a momentjs object
      let vm = this;

      vm.form.expirationTimeDelta = date;
    },
    updatePayoutDate(date) {
      // date is expected to be a momentjs object
      let vm = this;

      vm.form.payoutDate = date;
    },
    userSearch(search, loading) {
      let vm = this;

      if (search.length < 3) {
        return;
      }
      loading(true);
      vm.getUser(loading, search);
    },
    getUser: async function(loading, search, selected) {
      let vm = this;
      let myHeaders = new Headers();
      let url = `/api/v0.1/users_search/?token=${currentProfile.githubToken}&term=${escape(search)}`;

      myHeaders.append('X-Requested-With', 'XMLHttpRequest');
      return new Promise(resolve => {

        fetch(url, {
          credentials: 'include',
          headers: myHeaders
        }).then(res => {
          res.json().then(json => {
            vm.usersOptions = json;
            if (selected) {
              vm.$set(vm.form, 'reservedFor', vm.usersOptions[0].text);
            }
            resolve();
          });
          if (loading) {
            loading(false);
          }
        });
      });
    },
    checkBlocked(org) {
      let vm = this;
      let blocked = vm.blockedUrls.toLocaleString().toLowerCase().split(',');

      return blocked.indexOf(org.toLowerCase()) > -1;
    },
    featuredValue() {
      let vm = this;
      const apiUrlAmount = `/sync/get_amount?amount=${vm.usdFeaturedPrice}&denomination=USDT`;
      const getAmountData = fetchData(apiUrlAmount, 'GET');

      $.when(getAmountData).then(value => {
        vm.ethFeaturedPrice = value[0].eth.toFixed(4);

      }).catch((err) => {
        console.log(err);
      });
    },
    payFeaturedBounty: async function() {
      let vm = this;

      if (!provider) {
        onConnect();
        return false;
      }
      return new Promise(resolve =>
        web3.eth.sendTransaction({
          to: '0x88c62f1695DD073B43dB16Df1559Fda841de38c6',
          from: selectedAccount,
          value: web3.utils.toWei(String(vm.ethFeaturedPrice), 'ether'),
          gas: web3.utils.toHex(318730),
          gasLimit: web3.utils.toHex(318730)
        }, function(error, result) {
          if (error) {
            _alert({ message: gettext('Unable to upgrade to featured bounty. Please try again.') }, 'danger');
            console.log(error);
          } else {
            saveAttestationData(
              result,
              vm.ethFeaturedPrice,
              '0x88c62f1695DD073B43dB16Df1559Fda841de38c6',
              'featuredbounty'
            );
            resolve();
          }
        })
      );
    },
    payFees: async function() {
      let vm = this;
      const toAddress = '0x88c62f1695DD073B43dB16Df1559Fda841de38c6';

      if (!provider) {
        onConnect();
        return false;
      }
      return new Promise(resolve => {

        if (vm.form.token.symbol === 'ETH') {
          web3.eth.sendTransaction({
            to: toAddress,
            from: selectedAccount,
            // the toFixed(0) at the end is for the rare cases where due to limitations in the number representation
            // the result still contains decimal places
            value: BigInt((vm.totalAmount.totalFee.toFixed(18) * Math.pow(10, 18)).toFixed(0)).toString()
          }).once('transactionHash', (txnHash, errors) => {

            console.log(txnHash, errors);

            if (errors) {
              _alert({ message: gettext('Unable to pay bounty fee. Please try again.') }, 'danger');
            } else {
              vm.form.feeTxId = txnHash;
              saveAttestationData(
                txnHash,
                vm.totalAmount.totalFee,
                '0x88c62f1695DD073B43dB16Df1559Fda841de38c6',
                'bountyfee'
              );
              resolve();
            }
          });
        } else if (vm.form.token.chainId === 1) {
          const amountInWei = vm.totalAmount.totalFee * 1.0 * Math.pow(10, vm.form.token.decimals);
          const amountAsString = new web3.utils.BN(BigInt(amountInWei)).toString();
          const token_contract = new web3.eth.Contract(token_abi, vm.form.token.address);

          token_contract.methods.transfer(toAddress, web3.utils.toHex(amountAsString)).send({ from: selectedAccount },
            function(error, txnId) {
              if (error) {
                _alert({ message: gettext('Unable to pay bounty fee. Please try again.') }, 'danger');
              } else {
                resolve();
              }
            }
          );

        }
      });
    },
    /**
     * Filters tokens by vm.networkId
     * @param {*} tokens
     * @returns {*} tokens
     */
    filterByNetworkId: function(tokens) {
      let vm = this;

      if (vm.networkId) {
        tokens = tokens.filter((token) => {
          return String(token.networkId) === vm.networkId;
        });
      }
      return tokens;
    },
    submitForm: async function() {
      let vm = this;

      if (!document.isHackathonBounty) {
        if (!provider && vm.chainId === '1') {
          onConnect();
          return false;
        }

        if (vm.bountyFee > 0 && !vm.subscriptionActive) {
          await vm.payFees();
        }

        if (vm.form.featuredBounty && !vm.subscriptionActive) {
          await vm.payFeaturedBounty();
        }
      }
      
      if (vm.form.organisationUrl) {
        try {
          let url = new URL(vm.form.organisationUrl);
          let pathSegments = url.pathname.split('/');
          let orgName = pathSegments[pathSegments.length - 1] || pathSegments[pathSegments.length - 2];

          vm.form.fundingOrganisation = orgName;
        } catch (error) {
          vm.form.fundingOrganisation = vm.form.organisationUrl;
        }
      }

      const metadata = {
        issueTitle: vm.form.title,
        issueDescription: vm.form.bountyInformationSource == 'github' ? vm.form.issueDetails.description : vm.form.description,
        issueKeywords: vm.form.keywords.join(),
        githubUsername: vm.form.githubUsername,
        notificationEmail: vm.form.notificationEmail,
        fullName: vm.form.fullName,
        experienceLevel: vm.form.experience_level,
        projectLength: vm.form.project_length,
        bountyType: vm.form.bounty_type,
        estimatedHours: vm.form.hours,
        fundingOrganisation: vm.form.fundingOrganisation,
        eventTag: vm.form.eventTag,
        is_featured: vm.form.featuredBounty ? '1' : undefined,
        repo_type: 'public',
        featuring_date: vm.form.featuredBounty && ((new Date().getTime() / 1000) | 0) || 0,
        reservedFor: '',
        releaseAfter: '',
        tokenName: vm.form.token.symbol,
        invite: [],
        bounty_categories: vm.form.bounty_categories.join(),
        activity: '',
        chain_id: vm.chainId
      };

      const params = {
        'title': metadata.issueTitle,
        'amount': vm.form.amount,
        'value_in_token': vm.form.amount * 10 ** vm.form.token.decimals,
        'token_name': metadata.tokenName,
        'token_address': vm.form.token.address,
        'bounty_type': metadata.bountyType !== 'Other' ? metadata.bountyType : vm.form.bounty_type_other,
        'project_length': metadata.projectLength,
        'estimated_hours': metadata.estimatedHours,
        'experience_level': metadata.experienceLevel,
        'github_url': vm.form.issueUrl,
        'bounty_owner_email': metadata.notificationEmail,
        'bounty_owner_github_username': metadata.githubUsername,
        'bounty_owner_name': metadata.fullName, // ETC-TODO REMOVE ?
        'bounty_reserved_for': metadata.reservedFor,
        'release_to_public': metadata.releaseAfter,
        'never_expires': vm.form.never_expires,
        'expires_date': vm.form.never_expires ? 9999999999 : moment(vm.form.expirationTimeDelta).utc().unix(),
        'payout_date': vm.form.never_expires ? 9999999999 : moment(vm.form.payoutDate).utc().unix(),
        'metadata': JSON.stringify(metadata),
        'raw_data': {}, // ETC-TODO REMOVE ?
        'network': vm.network,
        'issue_description': metadata.issueDescription,
        'custom_issue_description': JSON.stringify(vm.form.richDescriptionContent),
        'funding_organisation': metadata.fundingOrganisation,
        'balance': vm.form.amount * 10 ** vm.form.token.decimals, // ETC-TODO REMOVE ?
        'project_type': vm.form.project_type,
        'permission_type': vm.form.permission_type,
        'bounty_categories': metadata.bounty_categories,
        'repo_type': metadata.repo_type,
        'is_featured': metadata.is_featured,
        'featuring_date': metadata.featuring_date,
        'fee_amount': vm.totalAmount.totalFee,
        'fee_tx_id': vm.form.feeTxId,
        'coupon_code': vm.form.couponCode,
        'privacy_preferences': JSON.stringify({
          show_email_publicly: vm.form.showEmailPublicly
        }),
        'attached_job_description': vm.form.jobDescription,
        'eventTag': metadata.eventTag,
        'auto_approve_workers': vm.form.auto_approve_workers,
        'web3_type': vm.web3Type(),
        'activity': metadata.activity,
        'bounty_owner_address': vm.form.funderAddress,
        'acceptance_criteria': JSON.stringify(vm.form.richAcceptanceCriteria),
        'resources': JSON.stringify(vm.form.richResources),
        'contact_details': JSON.stringify(vm.nonEmptyContactDetails),
        'bounty_source': vm.form.bountyInformationSource,
        'peg_to_usd': vm.form.peg_to_usd,
        'amount_usd': vm.form.amountusd,
        'owners': JSON.stringify(vm.form.bounty_owners.map(owner => owner.id))
      };

      vm.sendBounty(params);

    },
    sendBounty(data) {
      let vm = this;

      if (typeof ga !== 'undefined') {
        ga('send', 'event', 'Create Bounty', 'click', 'Bounty Funder');
      }

      const apiUrlBounty = '/api/v1/bounty/create';
      const postBountyData = fetchData(apiUrlBounty, 'POST', data);
  
      $.when(postBountyData).then((response) => {
        if (200 <= response.status && response.status <= 204) {
          console.log('success', response);
          removeEventListener('beforeunload', beforeUnloadListener, {capture: true});
          window.location.href = response.bounty_url;
        } else if (response.status == 304) {
          _alert('Bounty already exists for this github issue.', 'danger');
          console.error(`error: bounty creation failed with status: ${response.status} and message: ${response.message}`);
        } else {
          _alert(`Unable to create a bounty. ${response.message}`, 'danger');
          console.error(`error: bounty creation failed with status: ${response.status} and message: ${response.message}`);
        }

      }).catch((err) => {
        console.log(err);
        _alert('Unable to create a bounty. Please try again later', 'danger');
      });

    },
    updateNav: function(direction) {
      if (direction === 1) {
        // Forward navigation
        let errors = {};

        switch (this.step) {
          case 1:
            this.step1Submitted = true;
            errors = this.checkFormStep1();
            break;
          case 2:
            this.step2Submitted = true;
            errors = this.checkFormStep2();
            break;
          case 3:
            this.step3Submitted = true;
            errors = this.checkFormStep3();
            break;
          case 4:
            this.step4Submitted = true;
            errors = this.checkFormStep4();
            break;
          default:
            this.submitForm();
            return;
        }
        if (Object.keys(errors).length == 0) {
          this.step += 1;
        }
      } else if (this.step > 1) {
        // Backward navigation
        this.step -= 1;
      }
    },

    removeContactDetails(idx) {
      this.form.contactDetails.splice(idx, 1);
    },

    addContactDetails() {
      this.form.contactDetails.push({
        type: '',
        value: ''
      });
    },

    updateCustomDescription({text, delta}) {
      this.form.richDescriptionText = text;
      this.form.richDescriptionContent = delta;
    },

    updateAcceptanceCriteria({ text, delta }) {
      this.form.richAcceptanceCriteria = delta;
      this.form.richAcceptanceCriteriaText = text;
    },

    updateResources({ text, delta }) {
      this.form.richResources = delta;
      this.form.richResourcesText = text;
    },

    popover(elementId) {
      $(elementId).popover({
        placement: 'right',
        content: helpText[elementId]
      }).popover('show');
    }
  },
  computed: {
    bountyFee: function() {
      let vm = this;

      if (vm.chainId === '1' && !vm.subscriptionActive) {
        return Number(document.FEE_PERCENTAGE);
      }
      return 0;
      
    },
    totalAmount: function() {
      let vm = this;
      let fee = vm.bountyFee / 100.0;

      let totalFee = Number(vm.form.amount) * fee;
      let total = Number(vm.form.amount) + totalFee;

      return { 'totalFee': totalFee, 'total': total };
    },
    totalTx: function() {
      let vm = this;
      let numberTx = 0;

      if (vm.chainId === '1' && !vm.subscriptionActive) {
        numberTx += vm.bountyFee > 0 ? 1 : 0;
      } else {
        numberTx = 0;
      }

      if (!vm.subscriptionActive) {
        numberTx += vm.form.featuredBounty ? 1 : 0;
      }

      return numberTx;

    },
    filterOrgSelected: function() {
      if (!this.orgSelected) {
        return;
      }
      return `/dynamic/avatar/${this.orgSelected}`;
    },
    successRate: function() {
      let rate;

      if (!this.form.amountusd) {
        return;
      }

      rate = ((this.form.amountusd / this.form.hours) * 100 / 120).toFixed(0);
      if (rate > 100) {
        rate = 100;
      }
      return rate;

    },
    sortByPriority: function() {
      return this.tokens.sort(function(a, b) {
        return b.priority - a.priority;
      });
    },
    filterByNetwork: function() {
      const vm = this;

      if (vm.network == '') {
        return vm.sortByPriority;
      }
      return vm.sortByPriority.filter((item) => {

        return item.network.toLowerCase().indexOf(vm.network.toLowerCase()) >= 0;
      });
    },
    filterByChainId: function() {
      const vm = this;
      let result;

      if (vm.chainId == '') {
        result = vm.filterByNetwork;
      } else {
        result = vm.filterByNetwork.filter((item) => {
          return String(item.chainId) === vm.chainId;
        });

        if (vm.chainId == '1') {
          // allow only mainnet tokens in ETH chain
          vm.networkId = '1';
          result = vm.filterByNetworkId(result);
        }
      }
      return result;
    },
    currentSteps: function() {
      const steps = [
        {
          text_long: 'Bounty Type',
          text_short: 'Bounty Type',
          active: false
        },
        {
          text_long: 'Bounty Details',
          text_short: 'Bounty Details',
          active: false
        },
        {
          text_long: 'Payment Information',
          text_short: 'Payment Info',
          active: false
        },
        {
          text_long: 'Additional Information',
          text_short: 'Additional Info',
          active: false
        },
        {
          text_long: 'Review Bounty',
          text_short: 'Review Bounty',
          active: false
        }
      ];

      steps[this.step - 1].active = true;
      return steps;
    },
    chainId: function() {
      if (this.chain) {
        return this.chain.id;
      }
      return '';
    },
    isExpired: function() {
      return moment(this.form.expirationTimeDelta).isBefore();
    },
    expiresAfterAYear: function() {
      if (this.form.never_expires) {
        return true;
      }
      return moment().diff(this.form.expirationTimeDelta, 'years') < -1;
    },
    isPayoutDateExpired: function() {
      return moment(this.form.payoutDate).isBefore();
    },
    payoutDateExpiresAfterAYear: function() {
      if (this.form.never_expires) {
        return true;
      }
      return moment().diff(this.form.payoutDate, 'years') < -1;
    },
    step1Errors: function() {
      return this.checkFormStep1();
    },
    isStep1Valid: function() {
      let ret = Object.keys(this.step1Errors).length == 0;

      return ret;
    },
    step2Errors: function() {
      return this.checkFormStep2();
    },
    isStep2Valid: function() {
      let ret = Object.keys(this.step2Errors).length == 0;

      return ret;
    },
    step3Errors: function() {
      return this.checkFormStep3();
    },
    isStep3Valid: function() {
      let ret = Object.keys(this.step3Errors).length == 0;

      return ret;
    },
    step4Errors: function() {
      return this.checkFormStep4();
    },
    isStep4Valid: function() {
      let ret = Object.keys(this.step4Errors).length == 0;

      return ret;
    },
    nonEmptyContactDetails: function() {
      if (this.form.contactDetails) {
        return this.form.contactDetails.filter(function(c) {
          return !!c.value;
        });
      }
      return [];
      
    }
  },
  watch: {
    form: {
      deep: true,
      handler(newVal, oldVal) {
        this.dirty = true;
      }
    },
    chain: async function(val) {

      if (val) {
        // if (!provider && val.id === '1') {
        //   await onConnect();
        // }

        // if (val.id === '56') {
        //   this.getBinanceSelectedAccount();
        // }

        this.getTokens();
      }
    }
  }
});

if (document.getElementById('gc-hackathon-new-bounty')) {
  let expirationTimeDelta = moment().add(1, 'month');
  let payoutDate = expirationTimeDelta;

  appFormBounty = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-hackathon-new-bounty',
    components: {
      'vue-select': 'vue-select'
    },
    data() {
      return {
        status: 'OPEN',
        tokens: [],
        network: 'mainnet',
        chain: null,
        funderAddressFallback: false,
        checkboxes: { 'terms': false, 'termsPrivacy': false, 'hiringRightNow': false },
        expandedGroup: { 'reserve': [], 'featuredBounty': [] },
        errors: {},
        usersOptions: [],
        orgSelected: '',
        subscriptions: document.subscriptions,
        subscriptionActive: (document.subscriptions ? document.subscriptions.length : false) || document.contxt.is_pro,
        coinValue: null,
        usdFeaturedPrice: 12,
        ethFeaturedPrice: null,
        blockedUrls: document.blocked_urls,
        dirty: false,
        submitted: true,
        step1Submitted: false,
        step2Submitted: false,
        step3Submitted: false,
        step4Submitted: false,
        reserveBounty: null,
        sponsors: document.sponsors, // USed only for hackathon
        isHackathonBounty: document.isHackathonBounty,
        hackathon_slug: document.hackathon ? document.hackathon.slug : null,
        isNew: true,
        form: {
          eventTag: document.hackathon ? document.hackathon.name : '',
          expirationTimeDelta: expirationTimeDelta,
          payoutDate: payoutDate,
          featuredBounty: false,
          fundingOrganisation: '',
          issueDetails: undefined,
          issueUrl: '',
          githubUsername: document.contxt.github_handle,
          notificationEmail: document.contxt.email,
          showEmailPublicly: '1',
          auto_approve_workers: false,
          fullName: document.contxt.name,
          hours: '1',
          bounty_categories: [],
          project_type: document.isHackathonBounty ? 'multiple' : null,
          permission_type: '',
          keywords: [],
          amount: 0.0,
          amountusd: null,
          peg_to_usd: true,
          token: null,
          terms: false,
          termsPrivacy: false,
          feeTxId: null,
          couponCode: document.coupon_code,
          tags: [],
          bounty_type: null,
          bountyInformationSource: null,
          contactDetails: [{
            type: 'Discord',
            value: ''
          }],
          richResources: '',
          richResourcesText: '',
          richAcceptanceCriteria: '',
          richAcceptanceCriteriaText: '',
          organisationUrl: '',
          title: '',
          description: '',
          richDescription: '',
          bounty_owners: [],
          never_expires: false,
          richDescriptionContent: null,
          richDescriptionText: ''
        },
        editorOptionPrio: {
          modules: {
            toolbar: [
              [ 'bold', 'italic', 'underline' ],
              [{ 'align': [] }],
              [{ 'list': 'ordered' }, { 'list': 'bullet' }],
              [ 'link', 'code-block' ],
              ['clean']
            ]
          },
          theme: 'snow',
          placeholder: 'Describe what your bounty is about',
          readOnly: true
        }
      };
    },
    mounted() {
      this.getParams();
      if (!document.isHackathonBounty) {
        this.showQuickStart();
      }
      this.getTokens();
      this.featuredValue();
    }
  });
}
