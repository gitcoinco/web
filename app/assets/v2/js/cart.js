/**
 * @notice Vue component for managing cart and checkout process
 * @dev If you need to interact with the Rinkeby Dai contract (e.g. to reset allowances for
 * testing), use this one click dapp: https://oneclickdapp.com/drink-leopard/
 */
const BN = Web3.utils.BN;
const { parseUnits, parseEther, formatEther } = ethers.utils;
const { Zero: ZERO } = ethers.constants;
const { BigNumber } = ethers;
let appCart;

document.addEventListener('dataWalletReady', async function(e) {
  appCart.$refs['cart'].network = networkName;
  appCart.$refs['cart'].networkId = String(Number(web3.eth.currentProvider.chainId));
}, false);

// needWalletConnection();

// Constants
const MATIC_ADDRESS = '0x0000000000000000000000000000000000001010';
const ETH_ADDRESS = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE';
const gitcoinAddress = '0xde21F729137C5Af1b01d73aF1dC21eFfa2B8a0d6'; // Gitcoin donation address for mainnet and rinkeby
const gitcoinAddressPolygon = '0x366adF5B96Ee15AfF5d66B0Fa44a56330b55E97B'; // Gitcoin donation address for polygon mainnet and mumbai
const POLYGON_TESTNET_NETWORK_ID = '80001';
const POLYGON_MAINNET_NETWORK_ID = '137';

// Contract parameters and constants
const bulkCheckoutAbi = [{ 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'token', 'type': 'address' }, { 'indexed': true, 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }, { 'indexed': false, 'internalType': 'address', 'name': 'dest', 'type': 'address' }, { 'indexed': true, 'internalType': 'address', 'name': 'donor', 'type': 'address' }], 'name': 'DonationSent', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'previousOwner', 'type': 'address' }, { 'indexed': true, 'internalType': 'address', 'name': 'newOwner', 'type': 'address' }], 'name': 'OwnershipTransferred', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': false, 'internalType': 'address', 'name': 'account', 'type': 'address' }], 'name': 'Paused', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'token', 'type': 'address' }, { 'indexed': true, 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }, { 'indexed': true, 'internalType': 'address', 'name': 'dest', 'type': 'address' }], 'name': 'TokenWithdrawn', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': false, 'internalType': 'address', 'name': 'account', 'type': 'address' }], 'name': 'Unpaused', 'type': 'event' }, { 'inputs': [{ 'components': [{ 'internalType': 'address', 'name': 'token', 'type': 'address' }, { 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }, { 'internalType': 'address payable', 'name': 'dest', 'type': 'address' }], 'internalType': 'struct BulkCheckout.Donation[]', 'name': '_donations', 'type': 'tuple[]' }], 'name': 'donate', 'outputs': [], 'stateMutability': 'payable', 'type': 'function' }, { 'inputs': [], 'name': 'owner', 'outputs': [{ 'internalType': 'address', 'name': '', 'type': 'address' }], 'stateMutability': 'view', 'type': 'function' }, { 'inputs': [], 'name': 'pause', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [], 'name': 'paused', 'outputs': [{ 'internalType': 'bool', 'name': '', 'type': 'bool' }], 'stateMutability': 'view', 'type': 'function' }, { 'inputs': [], 'name': 'renounceOwnership', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': 'newOwner', 'type': 'address' }], 'name': 'transferOwnership', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [], 'name': 'unpause', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address payable', 'name': '_dest', 'type': 'address' }], 'name': 'withdrawEther', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': '_tokenAddress', 'type': 'address' }, { 'internalType': 'address', 'name': '_dest', 'type': 'address' }], 'name': 'withdrawToken', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }];
const bulkCheckoutAddress = '0x7d655c57f71464B6f83811C55D84009Cd9f5221C';
const gnosisSafeAbi = [{'constant': true, 'inputs': [], 'name': 'VERSION', 'outputs': [{'internalType': 'string', 'name': '', 'type': 'string'}], 'payable': false, 'stateMutability': 'view', 'type': 'function'}];

// Grant data
let grantData = []; // data for grants in cart, initialized in mounted hook

Vue.component('eth-checkout-button', {
  delimiters: [ '[[', ']]' ],
  template: '#eth-checkout-template',
  props: [ 'maxCartItems', 'network', 'isZkSyncDown', 'donationInputs', 'onPolygonUpdate', 'currentTokens', 'grantsByTenant',
    'grantsUnderMinimalContribution', 'isCheckoutOngoing', 'standardCheckout', 'isPolygonDown', 'onZkSyncUpdate' ]
});


Vue.component('grants-cart', {
  delimiters: [ '[[', ']]' ],

  data: function() {
    return {
      // Checkout, shared
      selectedZcashPayment: 'taddress',
      optionsZcashPayment: [
        { text: 'Wallet t-address', value: 'taddress' },
        { text: 'Transaction Hash', value: 'txid' }
      ],
      selectedQRPayment: 'address',
      optionsQRPayment: [
        { text: 'Wallet address', value: 'address' },
        { text: 'Transaction Hash', value: 'txid' }
      ],
      selectedETHCartToken: 'DAI',
      chainId: '',
      networkId: '',
      network: 'mainnet',
      tabSelected: 'ETH',
      tabIndex: null,
      currentTokens: [], // list of all available tokens
      adjustGitcoinFactor: false, // if true, show section for user to adjust Gitcoin's percentage
      tokenList: undefined, // array of all tokens for selected network
      isLoading: undefined,
      gitcoinFactorRaw: 5, // By default, 5% of donation amount goes to Gitcoin
      grantData,
      hideWalletAddress: true,
      AnonymizeGrantsContribution: false,
      include_for_clr: false,
      windowWidth: window.innerWidth,
      userAddress: undefined,
      isCheckoutOngoing: false, // true once user clicks "Standard checkout" button
      activeCheckout: undefined, // standard / polygon / zksync
      maxCartItems: 50, // Max supported items in cart at once
      UsdMinimalContribution: 1,
      // Checkout, zkSync
      zkSyncSupportedTokens: [], // Used to inform user which tokens in their cart are on zkSync
      zkSyncEstimatedGasCost: undefined, // Used to tell user which checkout method is cheaper
      polygonSupportedTokens: [], // Used to inform user which tokens in their cart are on Polygon
      polygonEstimatedGasCost: undefined, // Used to tell user which checkout method is cheaper
      isZkSyncDown: document.disableZksync, // disable zkSync when true
      isPolygonDown: document.disablePolygon, // disable polygon when true
      isPolkadotExtInstalled: false,
      showConfirmationModal: false, // Used to display interim transaction confirmation modal
      chainScripts: {
        'POLKADOT': [
          `${static_url}v2/js/lib/polkadot/core.min.js`,
          `${static_url}v2/js/lib/polkadot/extension.min.js`,
          `${static_url}v2/js/lib/polkadot/utils.js`,
          `${static_url}v2/js/grants/cart/polkadot_extension.js`
        ],
        'BINANCE': [
          `${static_url}v2/js/lib/binance/utils.js`,
          `${static_url}v2/js/grants/cart/binance_extension.js`
        ],
        'HARMONY': [
          `${static_url}v2/js/lib/harmony/HarmonyUtils.browser.js`,
          `${static_url}v2/js/lib/harmony/HarmonyJs.browser.js`,
          `${static_url}v2/js/lib/harmony/HarmonyAccount.browser.js`,
          `${static_url}v2/js/lib/harmony/HarmonyCrypto.browser.js`,
          `${static_url}v2/js/lib/harmony/HarmonyNetwork.browser.js`,
          `${static_url}v2/js/lib/harmony/utils.js`,
          `${static_url}v2/js/grants/cart/harmony_extension.js`
        ],
        'RSK': [
          `${static_url}v2/js/grants/cart/rsk_extension.js`
        ],
        'ALGORAND': [
          `${static_url}v2/js/tokens.js`,
          `${static_url}v2/js/grants/cart/algorand_extension.js`
        ]
      }
    };
  },

  computed: {
    grantsByTenant() {
      let vm = this;
      let result;

      result = vm.grantData.filter((item)=>{
        return item.tenants.includes(vm.tabSelected);
      });

      return result;

    },
    grantsUnderMinimalContribution() {
      let vm = this;
      let result;

      result = vm.grantData.filter((item)=>{
        return item.grant_donation_amount_usd < vm.UsdMinimalContribution;
      });

      return result;

    },
    grantsTenants() {
      let vm = this;
      var grantsTenants = vm.grantData.reduce(function(result, grant) {

        return result.concat(grant.tenants);
      }, []);

      return grantsTenants;
    },
    grantsCountByTenant() {
      let vm = this;

      var grantsTentantsCount = vm.grantData.reduce(function(result, grant) {
        var currentCount = result[grant.tenants] || 0;

        result[grant.tenants] = currentCount + 1;
        return result;
      }, {});

      return grantsTentantsCount;
    },
    sortByPriority: function() {
      return this.currentTokens.sort(function(a, b) {
        return b.priority - a.priority;
      });
    },
    filterByNetwork: function() {
      const vm = this;

      if (vm.network == '') {
        return vm.sortByPriority;
      }
      return vm.sortByPriority.filter((item)=>{
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
      }
      return result;
    },
    filterByNetworkId: function() {
      const vm = this;
      let result;

      if (vm.networkId == '') {
        result = vm.filterByChainId;
      } else {
        result = vm.filterByChainId.filter((item) => {
          return String(item.networkId) === vm.networkId;
        });
      }
      return result;
    },
    fetchTokens() {
      // removes duplicates from the tokens array of objects
      let vm = this;
      let uniq = {};

      return vm.filterByChainId.filter(
        obj => !uniq[obj['name']] && (uniq[obj['name']] = true)
      );
    },
    // Returns true if user is logged in with GitHub, false otherwise
    isLoggedIn() {
      return document.contxt.github_handle;
    },

    // Percentage of donation that goes to Gitcoin
    gitcoinFactor() {
      return Number(this.gitcoinFactorRaw) / 100;
    },

    // Amounts being donated to grants
    donationsToGrants() {
      return this.donationSummaryTotals(1);
    },

    // Amounts being donated to Gitcoin
    donationsToGitcoin() {
      return this.donationSummaryTotals(this.gitcoinFactor);
    },

    // Total amounts being donated
    donationsTotal() {
      return this.donationSummaryTotals(1 + this.gitcoinFactor);
    },

    // String describing user's donations to grants
    donationsToGrantsString() {
      return this.donationSummaryString('donationsToGrants', 2);
    },

    // String describing user's donations to Gitcoin
    donationsToGitcoinString() {
      return this.donationSummaryString('donationsToGitcoin', 4);
    },

    // String describing user's total donations
    donationsTotalString() {
      return this.donationSummaryString('donationsTotal', 2);
    },

    predictionTotal() {
      let totalEstimatedMatch = 0;
      let donationToken;

      this.grantData.map(grant => {
        const match = Number(grant['grant_donation_clr_match']);

        if (!isNaN(match)) {
          totalEstimatedMatch += match;
        }
        donationToken = grant['grant_donation_currency'];
      });

      return {
        'token': donationToken,
        'total': totalEstimatedMatch.toFixed(2),
        'total_str': totalEstimatedMatch.toFixed(2).toString() + ' DAI'
      };
    },

    predictionTotalString() {
      return this.predictionTotal['total_str'];
    },

    totalString() {
      const token = Object.keys(this['donationsTotal'])[0];
      let total = Number(this['donationsTotal'][token]);
      const match = Number(this.predictionTotal['total']);
  
      if (match && token === 'DAI') {
        total += match;
  
        return total.toFixed(2).toString() + ' ' + token;
      } else if (match) {
        
        const match_str = this.predictionTotal['total_str'];
        const donation_total_str = total.toFixed(2).toString() + ' ' + token;
        
        return donation_total_str + ' + ' + match_str;
      }
  
      return total.toFixed(2).toString() + ' ' + token;
    },

    // Array of objects containing all donations and associated data
    donationInputs() {
      return this.computeDonationInputs(gitcoinAddress);
    },

    donationInputsPolygon() {
      return this.computeDonationInputs(gitcoinAddressPolygon);
    },

    // Total amount of native currency that needs to be sent along with the transaction
    donationInputsNativeAmount() {
      // Get the total native currency we need to send
      const initialValue = new BN('0');
      let nativeCurrencyAddress = this.nativeCurrency === 'MATIC' ? MATIC_ADDRESS : ETH_ADDRESS;
      const nativeCurrencyAmountBN = this.donationInputs.reduce((accumulator, currentValue) => {
        return currentValue.token === nativeCurrencyAddress
          ? accumulator.add(new BN(currentValue.amount)) // native currency donation
          : accumulator.add(new BN('0')); // token donation
      }, initialValue);

      return nativeCurrencyAmountBN.toString(10);
    },

    nativeCurrency() {
      let isPolygon = this.networkId === POLYGON_TESTNET_NETWORK_ID || this.networkId === POLYGON_MAINNET_NETWORK_ID;

      return isPolygon ? 'MATIC' : 'ETH';
    },

    // Estimated gas limit for the transaction
    donationInputsGasLimitL1() {
      // The below heuristics are used instead of `estimateGas()` so we can send the donation
      // transaction before the approval txs are confirmed, because if the approval txs
      // are not confirmed then estimateGas will fail.
      if (this.chainId !== '1') {
        return;
      }

      // If we have a cart where all donations are in Dai, we use a linear regression to
      // estimate gas costs based on real checkout transaction data, and add a 50% margin
      const donationCurrencies = this.donationInputs.map(donation => donation.token);
      const daiAddress = this.getTokenByName('DAI')?.addr;
      const isAllDai = donationCurrencies.every((addr) => addr === daiAddress);

      if (isAllDai) {
        if (donationCurrencies.length === 1) {
          // Special case since we overestimate here otherwise
          return 100000;
        }
        // Below curve found by running script at the repo below around 9AM PT on 2020-Jun-19
        // then generating a conservative best-fit line
        // https://github.com/mds1/Gitcoin-Checkout-Gas-Analysis
        return 27500 * donationCurrencies.length + 125000;
      }

      // Otherwise, based on contract tests, we use the more conservative heuristic below to get
      // a gas estimate. The estimates used here are based on testing the cost of a single
      // donation (i.e. one item in the cart). Because gas prices go down with batched
      // transactions, whereas this assumes they're constant, this gives us a conservative estimate
      const gasLimit = this.donationInputs.reduce((accumulator, currentValue) => {
        const tokenAddr = currentValue.token?.toLowerCase();

        if (currentValue.token === ETH_ADDRESS) {
          return accumulator + 70000; // ETH donation gas estimate

        } else if (tokenAddr === '0x960b236A07cf122663c4303350609A66A7B288C0'.toLowerCase()) {
          return accumulator + 170000; // ANT donation gas estimate

        } else if (tokenAddr === '0xfC1E690f61EFd961294b3e1Ce3313fBD8aa4f85d'.toLowerCase()) {
          return accumulator + 500000; // aDAI donation gas estimate

        } else if (tokenAddr === '0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643'.toLowerCase()) {
          return accumulator + 450000; // cDAI donation gas estimate

        } else if (tokenAddr === '0x3472A5A71965499acd81997a54BBA8D852C6E53d'.toLowerCase()) {
          return accumulator + 200000; // BADGER donation gas estimate. See https://github.com/gitcoinco/web/issues/8112

        }

        return accumulator + 100000; // generic token donation gas estimate
      }, 0);

      return gasLimit;
    },

    // Make a recommendation to the user about which checkout to use
    checkoutRecommendation() {
      const estimateL1 = Number(this.donationInputsGasLimitL1); // L1 gas cost estimate
      const estimateZkSync = Number(this.zkSyncEstimatedGasCost); // zkSync gas cost estimate
      const estimatePolygon = Number(this.polygonEstimatedGasCost); // polygon gas cost estimate

      const compareWithL2 = (estimateL2, name) => {
        if (estimateL1 < estimateL2) {
          const savingsInGas = estimateL2 - estimateL1;
          const savingsInPercent = Math.round(savingsInGas / estimateL2 * 100);

          return { name: 'Standard checkout', savingsInGas, savingsInPercent };
        }

        const savingsInGas = estimateL1 - estimateL2;
        const percentSavings = savingsInGas / estimateL1 * 100;
        const savingsInPercent = percentSavings > 99 ? 99 : Math.round(percentSavings); // max value of 99%

        return { name, savingsInGas, savingsInPercent };
      };

      zkSyncComparisonResult = compareWithL2(estimateZkSync, 'zkSync');
      polygonComparisonResult = compareWithL2(estimatePolygon, 'Polygon');
      zkSyncSavings = zkSyncComparisonResult.name === 'zkSync' ? zkSyncComparisonResult.savingsInPercent : 0;
      polygonSavings = polygonComparisonResult.name === 'Polygon' ? polygonComparisonResult.savingsInPercent : 0;

      if (zkSyncSavings > polygonSavings) {
        return zkSyncComparisonResult;
      } else if (zkSyncSavings < polygonSavings) {
        return polygonComparisonResult;
      }

      return zkSyncComparisonResult; // recommendation will be standard checkout
    },

    isHarmonyExtInstalled() {
      return window.onewallet && window.onewallet.isOneWallet;
    },

    isBinanceExtInstalled() {
      return window.BinanceChain || false;
    },

    isAlgorandExtInstalled() {
      return window.AlgoSigner || false;
    },

    isRskExtInstalled() {
      const rskHost = 'https://public-node.rsk.co';
      const rskClient = new Web3();

      rskClient.setProvider(
        new rskClient.providers.HttpProvider(rskHost)
      );

      if (!provider) {
        try {
          return ethereum.isNiftyWallet;
        } catch (e) {
          return false;
        }
      }
    }
  },

  methods: {
    // Array of objects containing all donations and associated data
    computeDonationInputs(destGitcoinAddress) {
      let isPolygon = destGitcoinAddress == gitcoinAddressPolygon;

      if (!this.grantsByTenant || this.tabSelected !== 'ETH') {
        return undefined;
      }

      // Generate array of objects containing donation info from cart
      const donations = this.grantsByTenant.map((grant) => {
        const tokenDetails = this.getTokenByName(grant.grant_donation_currency, isPolygon);
        let amount;

        try {
          amount = parseUnits(String(Number(grant.grant_donation_amount) || 0), tokenDetails?.decimals);
        } catch {
          amount = parseUnits(String(0), tokenDetails?.decimals);
        }

        return {
          token: tokenDetails?.addr,
          amount: amount.toString(),
          dest: grant.grant_admin_address,
          name: grant.grant_donation_currency, // token abbreviation, e.g. DAI
          grant, // all grant data from localStorage
          tokenApprovalTxHash: '' // tx hash of token approval required for this donation
        };
      });

      // Append the Gitcoin donations (these already account for gitcoinFactor)
      Object.keys(this.donationsToGitcoin).forEach((token) => {
        const tokenDetails = this.getTokenByName(token, isPolygon);
        const amount = parseUnits(String(this.donationsToGitcoin[token]), tokenDetails?.decimals);

        const gitcoinGrantInfo = {
          // Manually fill this in so we can access it for the POST requests.
          // We use empty strings for fields that are not needed here
          grant_admin_address: destGitcoinAddress,
          grant_contract_address: '0xeb00a9c1Aa8C8f4b20C5d3dDA2bbC64Aa39AF752',
          grant_contract_version: '1',
          grant_donation_amount: this.donationsToGitcoin[token],
          grant_donation_clr_match: '',
          grant_donation_currency: token,
          grant_donation_num_rounds: 1,
          grant_id: '12',
          grant_image_css: '',
          grant_logo: '',
          grant_slug: 'gitcoin-grants-official-matching-pool-fund',
          grant_title: 'Gitcoin Grants Official Matching Pool Fund',
          grant_token_address: '0x0000000000000000000000000000000000000000',
          grant_token_symbol: '',
          isAutomatic: true // we add this field to help properly format the POST requests,
        };

        // Only add to donation inputs array if donation amount is greater than 0
        if (amount.gt(ZERO)) {
          donations.push({
            amount: amount.toString(),
            token: tokenDetails?.addr,
            dest: destGitcoinAddress,
            name: token, // token abbreviation, e.g. DAI
            grant: gitcoinGrantInfo, // equivalent to grant data from localStorage
            tokenApprovalTxHash: '' // tx hash of token approval required for this donation
          });
        }

      });
      return donations;
    },

    checkForGnosisSafes: async function() {
      // collate grants which represent contracts which cannot be interacted with
      const withCode = [];
      const unsafeGrants = [];

      // make these checks on mainnet
      const mainnetProvider = new Web3('https://mainnet.infura.io/v3/1e0a90928efe4bb78bb1eeceb8aacc27');

      // check each of the grants for an address starting with 0x
      const grants = this.grantsByTenant.filter(grant => !!grant.grant_admin_address && grant.grant_admin_address.length === 42 && grant.grant_admin_address.startsWith('0x'));

      // check each of the grants in the cart to see if it points to a contract
      await Promise.all(grants.map((grant) => new Promise((resolve) => {
        // check for contract on Polygon
        mainnetProvider.eth.getCode(grant.grant_admin_address).then((code) => {
          // if the address points to a contract, we want to stop any contributions from being sent here
          if (code !== '0x') {
            // (this could be a gnosis safe created via a relayer and until we can check for that, we want to block all contribs from hitting this address on polygon)
            unsafeGrants.push(grant);
          }
          // resolve the discovered code
          resolve(code);
        });
      })));

      // return any grants which cannot be contributed to
      return unsafeGrants;
    },
    setChainScripts: function() {
      let vm = this;

      vm.grantsTenants.forEach(function(tenant) {
        tenant = tenant === 'KUSAMA' ? 'POLKADOT' : tenant;
        let cb = tenant === 'POLKADOT' ? vm.isPolkadotLoaded : null;

        if (vm.chainScripts[tenant]) {
          vm.loadDynamicScripts(cb, vm.chainScripts[tenant], `${tenant}-script`);
        }
      });
    },
    /* Set supported tokens for L2s */
    loadSupportedTokens() {
      // zkSync
      // Mainnet list: https://api.zksync.io/api/v0.1/tokens
      // Rinkeby list: https://rinkeby-api.zksync.io/api/v0.1/tokens
      this.zkSyncSupportedTokens = this.network === 'rinkeby'
        ? [ 'ETH', 'USDT', 'USDC', 'LINK', 'TUSD', 'HT', 'OMG', 'TRB', 'ZRX', 'BAT', 'REP', 'STORJ', 'NEXO', 'MCO', 'KNC', 'LAMB', 'GNT', 'MLTT', 'XEM', 'DAI', 'PHNX' ]
        : [ 'ETH', 'DAI', 'USDC', 'TUSD', 'USDT', 'SUSD', 'BUSD', 'LEND', 'BAT', 'KNC', 'LINK', 'MANA', 'MKR', 'REP', 'SNX', 'WBTC', 'ZRX', 'MLTT', 'LRC', 'HEX', 'PAN', 'SNT', 'YFI', 'UNI', 'STORJ', 'TBTC', 'EURS', 'GUSD', 'RENBTC', 'RNDR', 'DARK', 'CEL', 'AUSDC', 'CVP', 'BZRX', 'REN', 'RAI' ];

      // Polygon
      // We hardcode the list from Gitcoin's historical data based on the top ten tokens
      // on ethereum chain and also Polygon network used by users to checkout.
      // Confirm the token exists on Polygon's list of supported tokens: https://mapper.matic.today/
      this.polygonSupportedTokens = this.network === 'mainnet'
        ? [ 'DAI', 'ETH', 'USDT', 'USDC', 'PAN', 'BNB', 'UNI', 'CELO', 'MASK', 'MATIC' ]
        : [ 'DAI', 'ETH', 'USDT', 'USDC', 'UNI', 'MATIC' ];
    },
    async isPolkadotLoaded() {
      let vm = this;

      const asyncFunction = (t) => new Promise(resolve => setTimeout(resolve, t));

      return (async() => {

        while (!Object.prototype.hasOwnProperty.call(window, 'polkadot_extension_dapp'))
          await asyncFunction(3000);
        return await polkadot_extension_dapp.isWeb3Injected;
      })().then(result => {
        vm.isPolkadotExtInstalled = result;
        return vm.isPolkadotExtInstalled;
      });
    },
    // When the cart-ethereum-zksync component is updated, it emits an event with new data as the
    // payload. This component listens for that event and uses the data to show the user details
    // and suggestions about their checkout (gas cost estimates and why zkSync may not be
    // supported for their current cart)
    onZkSyncUpdate: function(data) {
      this.zkSyncEstimatedGasCost = data.zkSyncEstimatedGasCost;
    },

    onPolygonUpdate: function(data) {
      this.polygonEstimatedGasCost = data.polygonEstimatedGasCost;
    },

    tabChange: async function(input, promptModal = true) {
      let vm = this;

      vm.tabSelected = vm.$refs.tabs.tabs[input].id;
      if (!vm.grantsCountByTenant[vm.tabSelected]) {
        vm.tabIndex += 1;
        return;
      }

      switch (vm.tabSelected) {
        default:
        case 'ETH':
          vm.chainId = '1';
          if (promptModal) {
            if (!web3Modal) {
              needWalletConnection();
            } else if (!provider) {
              await onConnect();
            }
          }
          break;
        case 'ZCASH':
          vm.chainId = '123123';
          break;
        case 'CELO':
          vm.chainId = '42220';
          break;
        case 'ZIL':
          vm.chainId = '102';
          break;
        case 'HARMONY':
          vm.chainId = '1000';
          break;
        case 'BINANCE':
          vm.chainId = '56';
          break;
        case 'KUSAMA':
          vm.chainId = '59';
          break;
        case 'POLKADOT':
          vm.chainId = '58';
          break;
        case 'RSK':
          vm.chainId = '30';
          break;
        case 'ALGORAND':
          vm.chainId = '1001';
          break;
      }
    },
    confirmQRPayment: function(e, grant) {
      let vm = this;

      e.preventDefault();

      // this.$refs.form.reportValidity()
      if (!e.target.reportValidity()) {
        return;
      }

      let data = {'contributions': [{

        'grant_id': grant.grant_id,
        'contributor_address': grant.contributor_address,
        'tx_id': grant.payoutTxId,
        'token_symbol': grant.grant_donation_currency,
        'tenant': this.tabSelected,
        'amount_per_period': grant.grant_donation_amount

      }]};

      vm.$set(grant, 'loading', true);
      vm.$set(grant, 'error', null);
      const postContribution = fetchData('v1/api/contribute', 'POST', JSON.stringify(data));

      vm.errorMessage = '';

      $.when(postContribution).then(response => {
        // set the cooldown time to one minute
        if (response.success_contributions && response.success_contributions.length) {
          if (grant.grant_id === response.success_contributions[0].grant_id) {
            // grant.error= response.invalid_contributions[0].message;
            MauticEvent.createEvent({
              'alias': 'products',
              'data': [
                {
                  'name': 'product',
                  'attributes': {
                    'product': 'grants',
                    'persona': 'grants-contributor',
                    'action': 'contribute'
                  }
                }
              ]
            });
            vm.$set(grant, 'success', response.success_contributions[0].message);
          }
        }
        if (response.invalid_contributions && response.invalid_contributions.length) {
          if (grant.grant_id === response.invalid_contributions[0].grant_id) {
            // grant.error= response.invalid_contributions[0].message;
            vm.$set(grant, 'loading', false);
            vm.$set(grant, 'error', response.invalid_contributions[0].message);
          }

          // vm.grantData.filter((item)=>{
          //   if(item.grant_id.includes(e.invalid_contributions[0].grant_id)) {
          //     // return item.error = e.invalid_contributions[0].message
          //     return
          //   }
          // });

        }
      }).catch((e) => {
        vm.$set(grant, 'error', 'error submitting data, try again later');
        vm.$set(grant, 'loading', false);
      });
    },
    contributeWithExtension: function(grant, tenant, data) {
      let vm = this;

      switch (tenant) {
        case 'ALGORAND':
          if (data) {
            contributeWithAlgorandExtension(grant, vm, data);
          } else {
            initAlgorandConnection(grant, vm);
          }
          break;
        case 'RSK':
          contributeWithRskExtension(grant, vm);
          break;
        case 'HARMONY':
          contributeWithHarmonyExtension(grant, vm);
          break;
        case 'BINANCE':
          contributeWithBinanceExtension(grant, vm);
          break;
        case 'POLKADOT':
        case 'KUSAMA':
          if (data) {
            contributeWithPolkadotExtension(grant, vm, data);
          } else {
            initPolkadotConnection(grant, vm);
          }
          break;
      }
    },
    loginWithGitHub() {
      window.location.href = `${window.location.origin}/login/github/?next=/grants/cart`;
    },
    confirmClearCart() {
      this.clearCart();
      this.isLoading = false;
    },
    clearCart() {
      CartData.clearCart();
      this.grantData = [];
      update_cart_title();
    },

    shareCart() {
      _alert('Cart URL copied to clipboard', 'success', 1000);
      copyToClipboard(CartData.share_url());
    },

    updateDonationCurrency(chain) {

      if (chain == 'ETH') {
        this.grantData.map(grant => {
          grant.grant_donation_currency = this.selectedETHCartToken;
        });
      }
      CartData.setCart(this.grantData);
    },

    twitterShareLink() {
      const url = `https://twitter.com/intent/tweet?text=${CartData.share_url()}`;

      window.open(url, '_blank');
    },

    updateCartData(e) {
      this.grantData = (e && e.detail && e.detail.list && e.detail.list) || [];
      update_cart_title();
    },

    removeGrantFromCart(id) {
      CartData.removeIdFromCart(id);
      this.grantData = CartData.loadCart();
      update_cart_title();
      this.tabChange(this.tabIndex, promptModal = false);
    },

    updatePaymentStatus(grant_id, step = 'waiting', txnid, additionalAttributes) {
      let vm = this;
      let grantData = vm.grantData;

      grantData.forEach((grant, index) => {
        if (grant.grant_id == grant_id) {
          vm.grantData[index].payment_status = step;
          if (txnid) {
            vm.grantData[index].txnid = txnid;
          }
          if (additionalAttributes) {
            vm.grantData[index].additionalAttributes = additionalAttributes;
          }
        }
      });

      vm.$forceUpdate();
    },

    /**
     * @notice Wrapper around web3's estimateGas so it can be used with await
     * @param tx Transaction to estimate gas for
     */
    async estimateGas(tx) {
      return new Promise(function(resolve, reject) {
        tx.estimateGas((err, res) => {
          if (err) {
            return reject(err);
          }
          resolve(res);
        });
      });
    },

    /**
     * @notice Generates an object where keys are token names and value are the total amount
     * being donated in that token. Scale factor scales the amounts used by a constant
     * @dev The addition here is based on human-readable numbers so BN is not needed
     */
    donationSummaryTotals(scaleFactor = 1) {
      const totals = {};

      this.grantsByTenant.forEach(grant => {
        // Scale up number by 1e18 to use BigNumber, multiply by scaleFactor

        let totalDonationAmount;

        try {
          totalDonationAmount = parseEther(String(grant.grant_donation_amount) || 0)
            .mul(String(Math.round(scaleFactor * 10000)))
            .div('10000');
        } catch {
          totalDonationAmount = parseEther(String(0))
            .mul(String(Math.round(scaleFactor * 10000)))
            .div('10000');
        }

        // Add the number to the totals object
        // First time seeing this token, set the field and initial value
        if (!totals[grant.grant_donation_currency]) {
          totals[grant.grant_donation_currency] = totalDonationAmount;
        } else {
          // We've seen this token, so just update the total
          totals[grant.grant_donation_currency] = totals[grant.grant_donation_currency].add(totalDonationAmount);
        }
      });

      // Convert from BigNumber back to regular numbers
      Object.keys(totals).map((key) => {
        totals[key] = formatEther(totals[key]);
      });
      return totals;
    },

    /**
     * @notice Returns a string of the form "3 DAI + 0.5 ETH + 10 USDC" which describe the
     * user's donations for a given property
     */
    donationSummaryString(propertyName, maximumFractionDigits = 2) {
      if (!this[propertyName]) {
        return undefined;
      }

      let string = '';

      Object.keys(this[propertyName]).forEach(key => {
        // key is our token symbol, so for now let's skip this if key is ZEC
        if (key === 'ZEC')
          return;

        // Round to 2 digits
        const amount = this[propertyName][key];
        const formattedAmount = amount.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits
        });

        if (string === '') {
          string += `${formattedAmount} ${key}`;
        } else {
          string += ` + ${formattedAmount} ${key}`;
        }
      });
      return string;
    },

    handleError(err) {
      console.error(err); // eslint-disable-line no-console
      let message = 'There was an error';

      if (err.message)
        message = err.message;
      else if (err.msg)
        message = err.msg;
      else if (typeof err === 'string')
        message = err;

      _alert(message, 'danger');
      this.activeCheckout = undefined;
      this.showConfirmationModal = false;
      indicateMetamaskPopup(true);
    },

    /**
     * @notice Get token address and decimals using data fetched from the API endpoint in the
     * mounted hook
     * @dev We use this instead of tokenNameToDetails in tokens.js because we use a different
     * address to represent ETH. We also add additional fields that are not included in the
     * response to facilitate backward compatibility
     * @param {String} name Token name, e.g. ETH or DAI
     */
    getTokenByName(name, isPolygon = false) {
      if (name === 'ETH' && !isPolygon) {
        return {
          addr: ETH_ADDRESS,
          address: ETH_ADDRESS,
          name: 'ETH',
          symbol: 'ETH',
          decimals: 18,
          priority: 1
        };
      }

      return this.filterByChainId.filter(token => token.name === name && token.networkId == this.networkId)[0];
    },

    async applyAmountToAllGrants(grant) {
      const preferredAmount = grant.grant_donation_amount;
      const preferredTokenName = grant.grant_donation_currency;
      const fallbackAmount = await this.valueToEth(preferredAmount, preferredTokenName);
      const tenant = grant.tenants[0];

      this.grantData.forEach((grant, index) => {
        // Assume all tokens available on this chain are accepted by this grant. This gives us
        // an array of token symbols to compare against
        const acceptedCurrencies = this.filterByChainId.map((token) => token.symbol);

        // Skip this loop if this grant is not the same tenant as the clicked grant
        if (this.grantData[index].tenants[0] !== tenant)
          return;

        // Update the values
        if (!acceptedCurrencies.includes(preferredTokenName)) {
          // If the selected token is not available, fallback to ETH
          this.grantData[index].grant_donation_amount = fallbackAmount;
          this.grantData[index].grant_donation_currency = 'ETH';
        } else {
          // Otherwise use the user selected option
          this.grantData[index].grant_donation_amount = preferredAmount;
          this.grantData[index].grant_donation_currency = preferredTokenName;
        }
      });
    },

    // Must be called at the beginning of the standard L1 bulk checkout flow
    async initializeStandardCheckout() {
      // Prompt web3 login if not connected
      if (!provider) {
        return await onConnect();
      }

      let networkId = String(Number(web3.eth.currentProvider.chainId));
      let networkName = getDataChains(networkId, 'chainId')[0] && getDataChains(networkId, 'chainId')[0].network;

      if (networkName == 'mainnet' && networkId !== '1') {
        // User MetaMask must be connected to Ethereum mainnet
        try {
          await ethereum.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: '0x1' }]
          });
        } catch (switchError) {
          if (switchError.code === 4001) {
            throw new Error('Please connect MetaMask to Ethereum network.');
          } else if (switchError.code === -32002) {
            throw new Error('Please respond to a pending MetaMask request.');
          } else {
            console.error(switchError);
          }
        }
      }

      if (typeof ga !== 'undefined') {
        ga('send', 'event', 'Grant Checkout', 'click', 'Person');
      }

      // Throw if invalid Gitcoin contribution percentage
      if (Number(this.gitcoinFactorRaw) < 0 || Number(this.gitcoinFactorRaw) > 99) {
        throw new Error('Gitcoin contribution amount must be between 0% and 99%');
      }

      // Throw if there's negative values in the cart
      this.donationInputs.forEach(donation => {
        if (Number(donation.amount) < 0) {
          throw new Error('Cannot have negative donation amounts');
        }
      });

      // Initialization complete, return address of current user
      return (await web3.eth.getAccounts())[0];
    },

    /**
     * @notice For each token, checks if an approval is needed against the specified contract, and
     * returns the data
     * @param userAddress User's web3 address
     * @param targetContract Address of the contract to check allowance against. Currently this
     * should only be the bulkCheckout contract address
     */
    async getAllowanceData(userAddress, targetContract, isPolygon = false) {
      // Get list of tokens user is donating with
      const selectedTokens = Object.keys(this.donationsToGrants);

      // Initialize return variable
      let allowanceData = [];

      // Define function that calculates the total required allowance for the specified token
      const calcTotalAllowance = (tokenDetails) => {
        const initialValue = new BN('0');

        return this.donationInputs.reduce((accumulator, currentValue) => {
          return currentValue.token === tokenDetails.addr
            ? accumulator.add(new BN(currentValue.amount)) // token donation
            : accumulator.add(new BN('0')); // native currency donation
        }, initialValue);
      };

      // Loop over each token in the cart and check allowance
      for (let i = 0; i < selectedTokens.length; i += 1) {
        const tokenName = selectedTokens[i];
        const tokenDetails = this.getTokenByName(tokenName, isPolygon);

        // If native currency donation no approval is necessary, just check balance
        if (tokenDetails.name === this.nativeCurrency) {
          const userEthBalance = await web3.eth.getBalance(userAddress);

          if (new BN(userEthBalance, 10).lt(new BN(this.donationInputsNativeAmount, 10))) {
            // User ETH balance is too small compared to selected donation amounts
            throw new Error(`Insufficient ${tokenDetails.name} balance to complete checkout`);
          }
          // ETH balance is sufficient, continue to next iteration since no approval check
          continue;
        }

        // Get current allowance
        const tokenContract = new web3.eth.Contract(token_abi, tokenDetails.addr);
        const allowance = new BN(await getAllowance(targetContract, tokenDetails.addr), 10);

        // Get required allowance based on donation amounts
        // We use reduce instead of this.donationsTotal because this.donationsTotal will
        // not have floating point errors, but the actual amounts used will
        const requiredAllowance = calcTotalAllowance(tokenDetails);

        // Check user token balance against requiredAllowance
        const userTokenBalance = await tokenContract.methods
          .balanceOf(userAddress)
          .call({ from: userAddress });

        if (new BN(userTokenBalance, 10).lt(requiredAllowance)) {
          // Balance is too small, exit checkout flow
          throw new Error(`Insufficient ${tokenName} balance to complete checkout`, 'error');
        }

        // If no allowance is needed, continue to next token
        if (allowance.gte(new BN(requiredAllowance))) {
          continue;
        }

        // If we do need to set the allowance, save off the required info to request it later
        allowanceData.push({
          allowance: requiredAllowance.toString(),
          contract: tokenContract,
          tokenName
        });
      } // end checking approval requirements for each token being used for donations

      return allowanceData;
    },

    /**
     * @notice Requests all allowances and executes checkout once all allowance transactions
     * have been sent
     * @param allowanceData Output from getAllowanceData() function
     * @param targetContract Address of the contract to check allowance against. Currently this
     * should only be the bulkCheckout contract address
     * @param callback Function to after allowance approval transactions are sent
     * @param callbackParams Array of input arguments to pass to the callback function
     */
    async requestAllowanceApprovalsThenExecuteCallback(
      allowanceData,
      userAddress,
      targetContract,
      callback = undefined,
      callbackParams = []
    ) {
      console.log('Requesting token approvals...');

      if (allowanceData.length === 0) {
        console.log('✅ No approvals needed');
        if (callback)
          await callback(...callbackParams);
        return;
      }

      indicateMetamaskPopup();
      for (let i = 0; i < allowanceData.length; i += 1) {
        // Add 20% margin to ensure enough is approved
        // TODO make this more precise
        const allowance = ethers.BigNumber.from(allowanceData[i].allowance.toString()).mul('120').div('100').toString();
        const contract = allowanceData[i].contract;
        const tokenName = allowanceData[i].tokenName;
        const approvalTx = contract.methods.approve(targetContract, allowance);

        // We split this into two very similar branches, because on the last approval
        // we execute the callback (the main donation flow) after we get the transaction hash
        if (i !== allowanceData.length - 1) {
          approvalTx
            .send({ from: userAddress })
            .on('transactionHash', (txHash) => {
              this.setApprovalTxHash(tokenName, txHash);
            })
            .on('error', (error, receipt) => {
              // If the transaction was rejected by the network with a receipt, the second parameter will be the receipt.
              this.handleError(error);
            });
        } else {
          approvalTx
            .send({ from: userAddress })
            .on('transactionHash', async(txHash) => { // eslint-disable-line no-loop-func
              indicateMetamaskPopup(true);
              this.setApprovalTxHash(tokenName, txHash);
              console.log('✅ Received all token approvals');
              if (callback) {
                await callback(...callbackParams);
              }
            })
            .on('error', (error, receipt) => {
              // If the transaction was rejected by the network with a receipt, the second parameter will be the receipt.
              this.handleError(error);
            });
        }
      }
    },

    resetNetwork() {
      if (this.nativeCurrency == 'MATIC') {
        this.network = this.network == 'testnet' ? 'rinkeby' : 'mainnet';
        this.networkId = this.networkId == '80001' ? '4' : '1';
      }
    },

    // Standard L1 checkout flow
    async standardCheckout() {
      try {
        // Setup -----------------------------------------------------------------------------------
        this.activeCheckout = 'standard';
        this.resetNetwork();
        const userAddress = await this.initializeStandardCheckout();
        
        // Token approvals and balance checks (just checks data, does not execute approavals)
        const allowanceData = await this.getAllowanceData(userAddress, bulkCheckoutAddress);

        // Send donation if no approvals -----------------------------------------------------------
        if (allowanceData.length === 0) {
          // Send transaction and exit function
          this.sendDonationTx(userAddress);
          return;
        }

        // Request approvals then send donations ---------------------------------------------------
        await this.requestAllowanceApprovalsThenExecuteCallback(
          allowanceData,
          userAddress,
          bulkCheckoutAddress,
          this.sendDonationTx,
          [userAddress]
        );
      } catch (err) {
        this.handleError(err);
      }
    },

    /**
     * @notice Saves off the transaction hash of the approval transaction to include with the POST
     * payload to be stored in Gitcoin's DB
     */
    setApprovalTxHash(tokenName, txHash) {
      this.donationInputs.forEach((donation, index) => {
        if (donation.name === tokenName) {
          this.donationInputs[index].tokenApprovalTxHash = txHash;
        }
      });
    },

    // Returns donation inputs for a transaction, filtered to remove unused data
    getDonationInputs() {
      return this.getFilteredDonationInputs(this.donationInputs);
    },

    // Returns donation inputs for a transaction, filtered to remove unused data
    getFilteredDonationInputs(donationInputsToFilter) {
      // We use parse and stringify to avoid mutating this.donationInputs since we use it later
      const donationInputs = JSON.parse(JSON.stringify(donationInputsToFilter)).map(donation => {
        delete donation.name;
        delete donation.grant;
        delete donation.tokenApprovalTxHash;
        return donation;
      });

      // Remove donations of zero value
      const donationInputsFiltered = donationInputs.filter(donation => {
        return Number(donation.amount) !== 0;
      });

      return donationInputsFiltered;
    },
    
    async sendDonationTx(userAddress) {
      // Get our donation inputs
      const bulkTransaction = new web3.eth.Contract(bulkCheckoutAbi, bulkCheckoutAddress);
      const donationInputsFiltered = this.getDonationInputs();

      // Send transaction
      indicateMetamaskPopup();
      bulkTransaction.methods
        .donate(donationInputsFiltered)
        .send({ from: userAddress, gas: this.donationInputsGasLimitL1, value: this.donationInputsNativeAmount })
        .on('transactionHash', async(txHash) => {
          console.log('Donation transaction hash: ', txHash);
          indicateMetamaskPopup(true);
          await this.postToDatabase([txHash], bulkCheckoutAddress, userAddress); // Save contributions to database
          await this.finalizeCheckout(); // Update UI and redirect
        })
        .on('error', (error, receipt) => {
          // If the transaction was rejected by the network with a receipt, the second parameter will be the receipt.
          this.handleError(error);
        });
    },

    // POSTs donation data to database. Wrapped in a try/catch, and if it fails, we fallback to the manual ingestion script
    async postToDatabase(txHash, contractAddress, userAddress, checkout_type = 'eth_std') {
      try {
        // this.grantsByTenant is the array used for donations, and this.donationInputs is computed from it
        // We loop through each donation to configure the payload then POST the required data
        const donations = this.donationInputs;
        const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // If standard checkout, stretch it so there's one hash for each donation (required for `for` loop below)
        const txHashes = checkout_type === 'eth_zksync' ? txHash : new Array(donations.length).fill(txHash[0]);

        // Configure template payload
        const saveSubscriptionPayload = {
          // Values that are constant for all donations
          checkout_type,
          contributor_address: userAddress,
          csrfmiddlewaretoken,
          frequency_count: 1,
          frequency_unit: 'rounds',
          gas_price: 0,
          gitcoin_donation_address: gitcoinAddress,
          hide_wallet_address: this.hideWalletAddress,
          anonymize_gitcoin_grants_contributions: false,
          include_for_clr: this.include_for_clr,
          match_direction: '+',
          network: document.web3network,
          num_periods: 1,
          real_period_seconds: 0,
          recurring_or_not: 'once',
          signature: 'onetime',
          splitter_contract_address: contractAddress,
          subscription_hash: 'onetime',
          visitorId: document.visitorId,
          // Values that vary by donation
          'gitcoin-grant-input-amount': [],
          admin_address: [],
          amount_per_period: [],
          confirmed: [],
          contract_address: [],
          contract_version: [],
          denomination: [],
          grant_id: [],
          split_tx_id: [], // Bulk donation hash for L1, or specific hash for L2
          sub_new_approve_tx_id: [],
          token_address: [],
          token_symbol: []
        };

        for (let i = 0; i < donations.length; i += 1) {
          // Get donation information
          const donation = donations[i];
          const grantId = donation.grant.grant_id;

          // Get token information
          const tokenName = donation.grant.grant_donation_currency;
          const tokenDetails = this.getTokenByName(tokenName);

          // Gitcoin uses special addresses to represent native chain currencies, but the contract does not.
          // Therefore we get the value of denomination and token_address using the below logic instead of
          // using tokenDetails.addr
          switch (tokenName) {
            case 'ETH' && checkout_type !== 'eth_polygon':
              tokenAddress = '0x0000000000000000000000000000000000000000';
              break;
            case 'MATIC' && checkout_type === 'eth_polygon':
              tokenAddress = '0x0000000000000000000000000000000000001010';
              break;
            default:
              tokenAddress = tokenDetails.addr;
          }

          // For automatic contributions to Gitcoin, set 'gitcoin-grant-input-amount' to 100.
          // Why 100? Because likely no one will ever use 100% or a normal grant, so using
          // 100 makes it easier to search the DB to find which Gitcoin donations were automatic
          const isAutomatic = donation.grant.isAutomatic;
          const gitcoinGrantInputAmt = isAutomatic ? 100 : Number(this.gitcoinFactorRaw);

          // Add the donation parameters
          saveSubscriptionPayload.admin_address.push(donation.grant.grant_admin_address);
          saveSubscriptionPayload.amount_per_period.push(Number(donation.grant.grant_donation_amount));
          saveSubscriptionPayload.confirmed.push(false);
          saveSubscriptionPayload.contract_address.push(donation.grant.grant_contract_address);
          saveSubscriptionPayload.contract_version.push(donation.grant.grant_contract_version);
          saveSubscriptionPayload.denomination.push(tokenAddress);
          saveSubscriptionPayload['gitcoin-grant-input-amount'].push(gitcoinGrantInputAmt);
          saveSubscriptionPayload.grant_id.push(grantId);
          saveSubscriptionPayload.split_tx_id.push(txHashes[i]);
          saveSubscriptionPayload.sub_new_approve_tx_id.push(donation.tokenApprovalTxHash);
          saveSubscriptionPayload.token_address.push(tokenAddress);
          saveSubscriptionPayload.token_symbol.push(tokenName);
        } // end for each donation

        // Configure request parameters
        const url = '/grants/bulk-fund';
        const headers = {
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        };
        const saveSubscriptionParams = {
          method: 'POST',
          headers,
          body: new URLSearchParams(saveSubscriptionPayload)
        };

        // Send saveSubscription request
        const res = await fetch(url, saveSubscriptionParams);
        const json = await res.json();

        MauticEvent.createEvent({
          'alias': 'products',
          'data': [
            {
              'name': 'product',
              'attributes': {
                'product': 'grants',
                'persona': 'grants-contributor',
                'action': 'contribute'
              }
            }
          ]
        });

      } catch (err) {
        // Something went wrong, so we use the manual ingestion process instead
        console.error(err);
        console.log('Standard contribution ingestion failed, falling back to manual ingestion');
        await this.postToDatabaseManualIngestion(txHash, userAddress, checkout_type);
      }
    },

    // Alternative to postToDatabase that uses the manual ingestion process
    async postToDatabaseManualIngestion(txHash, userAddress, checkout_type = 'eth_std') {
      // Determine if this was a zkSync checkout or standard L1 checkout. For this endpoint, we pass a txHash
      // to ingest L1 contributions or an address to pass L2 contributions

      txHash = checkout_type === 'eth_std' || checkout_type === 'eth_polygon' ? txHash[0] : ''; // txHash is always an array of hashes from checkout
      userAddress = checkout_type === 'eth_zksync' ? userAddress : '';

      // Get user's signature to prevent ingesting arbitrary transactions under your own username, then ingest
      const { signature, message } = await this.signMessage(userAddress);
      const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      const url = '/grants/ingest';
      const headers = { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' };
      const network = document.web3network || 'mainnet';
      const payload = { csrfmiddlewaretoken, txHash, userAddress, signature, message, network };
      const postParams = { method: 'POST', headers, body: new URLSearchParams(payload) };
      let json; // response

      // Send saveSubscription request
      try {
        _alert('Please be patient, as manual ingestion may take 1-2 minutes', 'info', '3000');
        const res = await fetch(url, postParams);

        json = await res.json();
        console.log('ingestion response: ', json);
        if (!json.success) {
          console.log('ingestion failed');
          _alert(`Your transactions could not be processed. Please visit ${window.location.host}/grants/add-missing-contributions to ensure your contributions are counted`, 'danger');
          throw new Error(`Your transactions could not be processed. Please visit ${window.location.host}/grants/add-missing-contributions to ensure your contributions are counted`);
        }
      } catch (err) {
        console.error(err);
        const message = `Your contribution was successful, but was not recognized by our database. Please visit ${window.location.host}/grants/add-missing-contributions to ensure your contributions are counted`;

        _alert(message, 'danger');
        throw new Error(message);
      }
    },

    // Asks user to sign a message as verification they own the provided address
    async signMessage(userAddress) {
      const baseMessage = 'Something went wrong, but we want to ensure your contributions are counted!\n\nSign this message as verification that you control the provided wallet address so we can process your contributions'; // base message that will be signed
      const ethersProvider = new ethers.providers.Web3Provider(provider); // ethers provider instance
      const signer = ethersProvider.getSigner(); // ethers signers
      const { chainId } = await ethersProvider.getNetwork(); // append chain ID if not mainnet to mitigate replay attack
      const message = chainId === 1 || chainId === 137 ? baseMessage : `${baseMessage}\n\nChain ID: ${chainId}`;

      // Get signature from user
      const isValidSignature = (sig) => ethers.utils.isHexString(sig) && sig.length === 132; // used to verify signature
      let signature = await signer.signMessage(message); // prompt to user is here, uses eth_sign

      // Fallback to personal_sign if eth_sign isn't supported (e.g. for Status and other wallets)
      if (!isValidSignature(signature)) {
        signature = await ethersProvider.send(
          'personal_sign',
          [ ethers.utils.hexlify(ethers.utils.toUtf8Bytes(message)), userAddress.toLowerCase() ]
        );
      }

      // Verify signature
      if (!isValidSignature(signature)) {
        console.error('Invalid signature', signature);
        throw new Error('Invalid signature. Please try again.');
      }

      return { signature, message };
    },

    /**
     * @notice POSTs donation data to database, updates local storage, redirects page, shows
     * success alert
     */
    async finalizeCheckout() {
      // Number of items decides the timeout time
      const timeout_amount = 1500 + (this.grantsByTenant.length * 500);

      // Clear cart, redirect back to grants page, and show success alert

      CartData.setCheckedOut(this.grantsByTenant);

      // Remove each grant from the cart which has just been checkout
      this.grantsByTenant.forEach((grant) => {
        CartData.removeIdFromCart(grant.grant_id);
      });

      setTimeout(function() {
        setTimeout(function() {
          this.activeCheckout = undefined;
          window.location.href = `${window.location.origin}/grants/explorer`;
        }, 500);
      }, timeout_amount);
    },

    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    },

    onResize() {
      this.windowWidth = window.innerWidth;
    },

    lerp(x_lower, x_upper, y_lower, y_upper, x) {
      return y_lower + (((y_upper - y_lower) * (x - x_lower)) / (x_upper - x_lower));
    },

    // Converts `amount` of `tokenSymbol` to equivalent value in DAI, based on data in `tokenPrices`
    valueToDai(amount, tokenSymbol, tokenPrices) {
      const tokenIndex = tokenPrices.findIndex(item => item.token === tokenSymbol);
      const amountOfOne = tokenPrices[tokenIndex].usdt; // value of 1 tokenSymbol in USDT (we treat USDT as equal to DAI)

      return Number(amount) * Number(amountOfOne); // convert based on quantity and return
    },

    // Converts `amount` of `tokenSymbol` to equivalent value in ETH
    async valueToEth(amount, tokenSymbol) {
      const url = `${window.location.origin}/sync/get_amount?amount=${amount}&denomination=${tokenSymbol}`;
      const response = await fetch(url);
      const newAmount = await response.json();

      return newAmount[0].eth;
    },

    async predictCLRMatch(grant, amount) {
      const clr_prediction_curve_2d = grant.grant_clr_prediction_curve;
      const clr_prediction_curve = clr_prediction_curve_2d.map(row => row[2]);

      if (amount > 10000) {
        amount = 10000;
      }

      const contributions_axis = [ 0, 1, 10, 100, 1000, 10000 ];
      let predicted_clr = 0;
      let index = 0;

      if (isNaN(amount)) {
        predicted_clr = clr_prediction_curve[index];
      } else if (contributions_axis.indexOf(amount) >= 0) {
        index = contributions_axis.indexOf(amount);
        predicted_clr = clr_prediction_curve[index];
      } else {
        let x_lower = 0;
        let x_upper = 0;
        let y_lower = 0;
        let y_upper = 0;

        if (0 < amount && amount < 1) {
          x_lower = 0;
          x_upper = 1;
          y_lower = clr_prediction_curve[0];
          y_upper = clr_prediction_curve[1];
        } else if (1 < amount && amount < 10) {
          x_lower = 1;
          x_upper = 10;
          y_lower = clr_prediction_curve[1];
          y_upper = clr_prediction_curve[2];
        } else if (10 < amount && amount < 100) {
          x_lower = 10;
          x_upper = 100;
          y_lower = clr_prediction_curve[2];
          y_upper = clr_prediction_curve[3];
        } else if (100 < amount && amount < 1000) {
          x_lower = 100;
          x_upper = 1000;
          y_lower = clr_prediction_curve[3];
          y_upper = clr_prediction_curve[4];
        } else {
          x_lower = 1000;
          x_upper = 10000;
          y_lower = clr_prediction_curve[4];
          y_upper = clr_prediction_curve[5];
        }

        predicted_clr = this.lerp(x_lower, x_upper, y_lower, y_upper, amount);
      }
      return predicted_clr;
    },

    // ===================================== Helper functions ======================================

    // Returns Ethereum cart data if found in the JSON store for `userAddress`, and false otherw
    async getEthereumCartJSONStore(userAddress) {
      const url = `get-ethereum-cart-data?user_address=${userAddress}`;
      const res = await fetch(url, { method: 'GET' });
      const json = await res.json();
      const cartData = json.ethereum_cart_data;

      if (cartData && cartData.length > 0) {
        return cartData;
      }
      return false;
    },
    loadDynamicScripts: function(callback, urlObj, id) {
      urlObj.forEach(function(source, index) {
        let existingScript = document.getElementById(id + index);

        if (!existingScript) {
          const script = document.createElement('script');

          script.src = urlObj[index];
          script.id = id + index;
          document.body.appendChild(script);

          script.onload = () => {
            if (callback)
              callback();
          };
        }
        if (existingScript && callback)
          callback();
      });
    }
  },

  watch: {
    chainId: async function(val) {
      // if (!provider && val === '1') {
      //   await onConnect();
      // }
    },
    // Use watcher to keep local storage in sync with Vue state
    grantData: {
      async handler() {
        CartData.setCart(this.grantData);
        const tokenNames = Array.from(new Set(this.grantData.map(grant => grant.grant_donation_currency)));

        const priceUrl = `${window.location.origin}/sync/get_amount?denomination=${tokenNames}`;
        const priceResponse = await fetch(priceUrl);
        const tokenPrices = (await priceResponse.json());

        // Update CLR match
        for (let i = 0; i < this.grantData.length; i += 1) {
          const verification_required_to_get_match = false;

          if (this.grantData[i].is_clr_eligible === 'true' || this.grantData[i].is_clr_eligible === 'True') {
            this.$set(this.grantData[i], 'is_clr_eligible', true);
          }
          if (
            (!document.verified && verification_required_to_get_match) ||
            grantData.is_clr_eligible == 'False'
          ) {
            this.grantData[i].grant_donation_clr_match = 0;
          } else {
            const grant = this.grantData[i];
            // Convert amount to DAI
            const rawAmount = Number(grant.grant_donation_amount);
            const STABLE_COINS = [ 'DAI', 'SAI', 'USDT', 'TUSD', 'aDAI', 'USDC' ];
            // All stable coins are handled with USDT (see app/app/settings.py for list)
            const tokenName = STABLE_COINS.includes(grant.grant_donation_currency)
              ? 'USDT'
              : grant.grant_donation_currency;

            const amount = this.valueToDai(rawAmount, tokenName, tokenPrices);

            this.$set(this.grantData[i], 'grant_donation_amount_usd', amount);

            const matchAmount = await this.predictCLRMatch(grant, amount);
            const clr_curve = grant.grant_clr_prediction_curve;
            const has_reached_cap = clr_curve && (clr_curve[0][1] !== 0 && clr_curve[1][2] == 0 && clr_curve[2][2] == 0 && clr_curve[3][2] == 0 && clr_curve[4][2] == 0 && clr_curve[5][2] == 0);

            this.$set(this.grantData[i], 'grant_donation_clr_match', matchAmount ? matchAmount.toFixed(2) : 0);
            this.$set(this.grantData[i], 'has_reached_cap', has_reached_cap);
          }
        }
      },
      deep: true
    },

    // We watch this variable to update the robot image
    gitcoinFactorRaw: {
      handler() {
        $('.bot-heart').hide();
        if (Number(this.gitcoinFactorRaw) <= 0) {
          $('#bot-heartbroken').show();
        } else if (Number(this.gitcoinFactorRaw) >= 20) {
          $('#bot-heart-20').show();
        } else if (Number(this.gitcoinFactorRaw) >= 15) {
          $('#bot-heart-15').show();
        } else if (Number(this.gitcoinFactorRaw) >= 10) {
          $('#bot-heart-10').show();
        } else if (Number(this.gitcoinFactorRaw) > 0) {
          $('#bot-heart-5').show();
        }
      }
    }
  },

  async mounted() {
    // Show loading dialog
    this.isLoading = true;

    // Load list of all tokens
    const tokensResponse = await fetch('/api/v1/tokens');
    const allTokens = await tokensResponse.json();

    // Only keep the ones for the current network
    this.currentTokens = allTokens.filter((token) => token.network === document.web3network || 'mainnet');
    this.currentTokens.forEach((token) => {
      // Add addr and name fields for backwards compatibility with existing code in this file
      token.addr = token.address;
      token.name = token.symbol;
    });

    // Set supported tokens for L2s
    this.loadSupportedTokens();

    // Read array of grants in cart from localStorage
    let grantData = CartData.loadCart();

    this.selectedETHCartToken = grantData.length > 0 && grantData[0].grant_donation_currency;

    const grantIds = grantData.map(grant => grant.grant_id);

    // Fetch updated Grants data for all cart grants
    const url = `${window.location.origin}/grants/v1/api/grants?pks=${grantIds.join(',')}&slim=true`;
    const response = await fetch(url);
    const updatedGrant = (await response.json()).grants;

    grantData.forEach(async(grant, index) => {

      const grantIndex = updatedGrant.findIndex(item => {
        return Number(item.grant_id) === Number(grant.grant_id);
      });

      // Make sure none have empty currencies, and if they do default to 5 DAI. This is done
      // to prevent the cart from getting stuck loading if a currency is empty
      updatedGrant[grantIndex]['grant_donation_currency'] = this.selectedETHCartToken;
      updatedGrant[grantIndex]['grant_donation_amount'] = grant.grant_donation_amount ? grant.grant_donation_amount : '5';
    });

    if (updatedGrant) {
      CartData.setCart(updatedGrant);
      this.grantData = updatedGrant;
    } else {
      this.grantData = [];
    }

    // Load needed scripts based on tenants
    this.setChainScripts();

    // Support responsive design
    window.addEventListener('resize', this.onResize);

    // watch for cartUpdates
    window.addEventListener('cartDataUpdated', this.updateCartData);

    // Show user cart now
    this.isLoading = false;
  },

  beforeDestroy() {
    // unwatch cartUpdates
    window.removeEventListener('cartDataUpdated', this.updateCartData);
    window.removeEventListener('resize', this.onResize);
  }
});

var update_cart_title = function() {
  const grants_cart = localStorage.getItem('grants_cart');
  const num_grants = grants_cart ? JSON.parse(grants_cart).length : 0;
  const new_title = 'Grants Cart (' + num_grants + ') | Gitcoin';

  $('title').text(new_title);
};

$(document).ready(function() {
  update_cart_title();
});

if (document.getElementById('gc-grants-cart')) {

  appCart = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-grants-cart',
    data: {
    }
  });
}

