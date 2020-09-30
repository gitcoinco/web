/**
 * @notice Vue component for managing cart and checkout process
 * @dev If you need to interact with the Rinkeby Dai contract (e.g. to reset allowances for
 * testing), use this one click dapp: https://oneclickdapp.com/drink-leopard/
 */
const BN = Web3.utils.BN;

needWalletConnection();

// Constants
const ETH_ADDRESS = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE';
const gitcoinAddress = '0x00De4B13153673BCAE2616b67bf822500d325Fc3'; // Gitcoin donation address for mainnet and rinkeby

// Contract parameters and constants
const bulkCheckoutAbi = [{ 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'token', 'type': 'address' }, { 'indexed': true, 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }, { 'indexed': false, 'internalType': 'address', 'name': 'dest', 'type': 'address' }, { 'indexed': true, 'internalType': 'address', 'name': 'donor', 'type': 'address' }], 'name': 'DonationSent', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'previousOwner', 'type': 'address' }, { 'indexed': true, 'internalType': 'address', 'name': 'newOwner', 'type': 'address' }], 'name': 'OwnershipTransferred', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': false, 'internalType': 'address', 'name': 'account', 'type': 'address' }], 'name': 'Paused', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': true, 'internalType': 'address', 'name': 'token', 'type': 'address' }, { 'indexed': true, 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }, { 'indexed': true, 'internalType': 'address', 'name': 'dest', 'type': 'address' }], 'name': 'TokenWithdrawn', 'type': 'event' }, { 'anonymous': false, 'inputs': [{ 'indexed': false, 'internalType': 'address', 'name': 'account', 'type': 'address' }], 'name': 'Unpaused', 'type': 'event' }, { 'inputs': [{ 'components': [{ 'internalType': 'address', 'name': 'token', 'type': 'address' }, { 'internalType': 'uint256', 'name': 'amount', 'type': 'uint256' }, { 'internalType': 'address payable', 'name': 'dest', 'type': 'address' }], 'internalType': 'struct BulkCheckout.Donation[]', 'name': '_donations', 'type': 'tuple[]' }], 'name': 'donate', 'outputs': [], 'stateMutability': 'payable', 'type': 'function' }, { 'inputs': [], 'name': 'owner', 'outputs': [{ 'internalType': 'address', 'name': '', 'type': 'address' }], 'stateMutability': 'view', 'type': 'function' }, { 'inputs': [], 'name': 'pause', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [], 'name': 'paused', 'outputs': [{ 'internalType': 'bool', 'name': '', 'type': 'bool' }], 'stateMutability': 'view', 'type': 'function' }, { 'inputs': [], 'name': 'renounceOwnership', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': 'newOwner', 'type': 'address' }], 'name': 'transferOwnership', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [], 'name': 'unpause', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address payable', 'name': '_dest', 'type': 'address' }], 'name': 'withdrawEther', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }, { 'inputs': [{ 'internalType': 'address', 'name': '_tokenAddress', 'type': 'address' }, { 'internalType': 'address', 'name': '_dest', 'type': 'address' }], 'name': 'withdrawToken', 'outputs': [], 'stateMutability': 'nonpayable', 'type': 'function' }];
const bulkCheckoutAddress = '0x7d655c57f71464B6f83811C55D84009Cd9f5221C';
const batchZkSyncDepositContractAddress = '0x9D37F793E5eD4EbD66d62D505684CD9f756504F6';
const batchZkSyncDepositContractAbi = '[{"inputs":[{"internalType":"address","name":"_zkSync","type":"address"},{"internalType":"contract IERC20[]","name":"_tokens","type":"address[]"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"contract IERC20","name":"token","type":"address"},{"indexed":false,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"AllowanceSet","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"contract IERC20","name":"token","type":"address"},{"indexed":true,"internalType":"uint104","name":"amount","type":"uint104"},{"indexed":true,"internalType":"address","name":"user","type":"address"}],"name":"DepositMade","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"inputs":[],"name":"ETH_TOKEN_PLACHOLDER","outputs":[{"internalType":"contract IERC20","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_recipient","type":"address"},{"components":[{"internalType":"contract IERC20","name":"token","type":"address"},{"internalType":"uint104","name":"amount","type":"uint104"}],"internalType":"struct BatchZkSyncDeposit.Deposit[]","name":"_deposits","type":"tuple[]"}],"name":"deposit","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"setAllowance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"zkSync","outputs":[{"internalType":"contract IZkSync","name":"","type":"address"}],"stateMutability":"view","type":"function"}]';
const zkSyncContractAbi = '[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"blockNumber","type":"uint32"}],"name":"BlockCommit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"blockNumber","type":"uint32"}],"name":"BlockVerification","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"totalBlocksVerified","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"totalBlocksCommitted","type":"uint32"}],"name":"BlocksRevert","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"zkSyncBlockId","type":"uint32"},{"indexed":true,"internalType":"uint32","name":"accountId","type":"uint32"},{"indexed":false,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint16","name":"tokenId","type":"uint16"},{"indexed":false,"internalType":"uint128","name":"amount","type":"uint128"}],"name":"DepositCommit","type":"event"},{"anonymous":false,"inputs":[],"name":"ExodusMode","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint32","name":"nonce","type":"uint32"},{"indexed":false,"internalType":"bytes","name":"fact","type":"bytes"}],"name":"FactAuth","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"zkSyncBlockId","type":"uint32"},{"indexed":true,"internalType":"uint32","name":"accountId","type":"uint32"},{"indexed":false,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint16","name":"tokenId","type":"uint16"},{"indexed":false,"internalType":"uint128","name":"amount","type":"uint128"}],"name":"FullExitCommit","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint64","name":"serialId","type":"uint64"},{"indexed":false,"internalType":"enum Operations.OpType","name":"opType","type":"uint8"},{"indexed":false,"internalType":"bytes","name":"pubData","type":"bytes"},{"indexed":false,"internalType":"uint256","name":"expirationBlock","type":"uint256"}],"name":"NewPriorityRequest","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":true,"internalType":"uint16","name":"tokenId","type":"uint16"},{"indexed":false,"internalType":"uint128","name":"amount","type":"uint128"},{"indexed":true,"internalType":"address","name":"owner","type":"address"}],"name":"OnchainDeposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint16","name":"tokenId","type":"uint16"},{"indexed":false,"internalType":"uint128","name":"amount","type":"uint128"}],"name":"OnchainWithdrawal","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"queueStartIndex","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"queueEndIndex","type":"uint32"}],"name":"PendingWithdrawalsAdd","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"queueStartIndex","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"queueEndIndex","type":"uint32"}],"name":"PendingWithdrawalsComplete","type":"event"},{"constant":true,"inputs":[],"name":"EMPTY_STRING_KECCAK","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint32","name":"","type":"uint32"}],"name":"authFacts","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes22","name":"","type":"bytes22"}],"name":"balancesToWithdraw","outputs":[{"internalType":"uint128","name":"balanceToWithdraw","type":"uint128"},{"internalType":"uint8","name":"gasReserveValue","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint32","name":"","type":"uint32"}],"name":"blocks","outputs":[{"internalType":"uint32","name":"committedAtBlock","type":"uint32"},{"internalType":"uint64","name":"priorityOperations","type":"uint64"},{"internalType":"uint32","name":"chunks","type":"uint32"},{"internalType":"bytes32","name":"withdrawalsDataHash","type":"bytes32"},{"internalType":"bytes32","name":"commitment","type":"bytes32"},{"internalType":"bytes32","name":"stateRoot","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint64","name":"_n","type":"uint64"}],"name":"cancelOutstandingDepositsForExodusMode","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_blockNumber","type":"uint32"},{"internalType":"uint32","name":"_feeAccount","type":"uint32"},{"internalType":"bytes32[]","name":"_newBlockInfo","type":"bytes32[]"},{"internalType":"bytes","name":"_publicData","type":"bytes"},{"internalType":"bytes","name":"_ethWitness","type":"bytes"},{"internalType":"uint32[]","name":"_ethWitnessSizes","type":"uint32[]"}],"name":"commitBlock","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_n","type":"uint32"}],"name":"completeWithdrawals","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"uint104","name":"_amount","type":"uint104"},{"internalType":"address","name":"_franklinAddr","type":"address"}],"name":"depositERC20","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_franklinAddr","type":"address"}],"name":"depositETH","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_accountId","type":"uint32"},{"internalType":"uint16","name":"_tokenId","type":"uint16"},{"internalType":"uint128","name":"_amount","type":"uint128"},{"internalType":"uint256[]","name":"_proof","type":"uint256[]"}],"name":"exit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"uint32","name":"","type":"uint32"},{"internalType":"uint16","name":"","type":"uint16"}],"name":"exited","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"exodusMode","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"firstPendingWithdrawalIndex","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"firstPriorityRequestId","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_accountId","type":"uint32"},{"internalType":"address","name":"_token","type":"address"}],"name":"fullExit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"_address","type":"address"},{"internalType":"uint16","name":"_tokenId","type":"uint16"}],"name":"getBalanceToWithdraw","outputs":[{"internalType":"uint128","name":"","type":"uint128"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"getNoticePeriod","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes","name":"initializationParameters","type":"bytes"}],"name":"initialize","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"isReadyForUpgrade","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"numberOfPendingWithdrawals","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint32","name":"","type":"uint32"}],"name":"pendingWithdrawals","outputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint16","name":"tokenId","type":"uint16"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint64","name":"","type":"uint64"}],"name":"priorityRequests","outputs":[{"internalType":"enum Operations.OpType","name":"opType","type":"uint8"},{"internalType":"bytes","name":"pubData","type":"bytes"},{"internalType":"uint256","name":"expirationBlock","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_maxBlocksToRevert","type":"uint32"}],"name":"revertBlocks","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes","name":"_pubkey_hash","type":"bytes"},{"internalType":"uint32","name":"_nonce","type":"uint32"}],"name":"setAuthPubkeyHash","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalBlocksCommitted","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalBlocksVerified","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalCommittedPriorityRequests","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalOpenPriorityRequests","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"triggerExodusIfNeeded","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes","name":"upgradeParameters","type":"bytes"}],"name":"upgrade","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"upgradeCanceled","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"upgradeFinishes","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"upgradeNoticePeriodStarted","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"upgradePreparationActivationTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"upgradePreparationActive","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"upgradePreparationStarted","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_blockNumber","type":"uint32"},{"internalType":"uint256[]","name":"_proof","type":"uint256[]"},{"internalType":"bytes","name":"_withdrawalsData","type":"bytes"}],"name":"verifyBlock","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"uint128","name":"_amount","type":"uint128"}],"name":"withdrawERC20","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint128","name":"_amount","type":"uint128"},{"internalType":"uint128","name":"_maxAmount","type":"uint128"}],"name":"withdrawERC20Guarded","outputs":[{"internalType":"uint128","name":"withdrawnAmount","type":"uint128"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint128","name":"_amount","type":"uint128"}],"name":"withdrawETH","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]';
const zkSyncContractAddressMainnet = '0xaBEA9132b05A70803a4E85094fD0e1800777fBEF';
const zkSyncContractAddressRinkeby = '0x82F67958A5474e40E1485742d648C0b0686b6e5D';

// Grant data
let grantHeaders = [ 'Grant', 'Amount', 'Total CLR Match Amount' ]; // cart column headers
let grantData = []; // data for grants in cart, initialized in mounted hook

Vue.use(VueTelInput);

Vue.component('grants-cart', {
  delimiters: [ '[[', ']]' ],

  data: function() {
    return {
      // Checkout, shared
      currentTokens: [], // list of all available tokens
      adjustGitcoinFactor: false, // if true, show section for user to adjust Gitcoin's percentage
      tokenList: undefined, // array of all tokens for selected network
      isLoading: undefined,
      gitcoinFactorRaw: 5, // By default, 5% of donation amount goes to Gitcoin
      grantHeaders,
      grantData,
      comments: undefined,
      hideWalletAddress: true,
      windowWidth: window.innerWidth,
      userAddress: undefined,
      // Checkout, zkSync
      zkSyncContractAddress: undefined,
      depositContractToUse: undefined, // what address to deposit through, batch contract or regular zkSync contract
      ethersProvider: undefined,
      signer: undefined, // signer from regular web3 wallet
      syncProvider: undefined,
      gitcoinSyncWallet: undefined, // wallet from zkSync wallet using Gitcoin-specific signature
      nominalSyncWallet: undefined, // default wallet from zkSync using their SDK
      showZkSyncModal: false,
      zkSyncAllowanceData: undefined,
      zkSyncDepositTxHash: undefined,
      zkSyncCheckoutStep1Status: 'not-started', // valid values: not-started, pending, complete
      zkSyncCheckoutStep2Status: 'not-started', // valid values: not-started, pending, complete, not-applicable
      zkSyncCheckoutStep3Status: 'not-started', // valid values: not-started, pending, complete
      numberOfConfirmationsNeeded: undefined, // number of confirmations user must wait for deposit tx
      currentConfirmationNumber: 0, // current number of confirmations received  for deposit tx
      zkSyncCheckoutFlowStep: 0, // used for UI updates during the final step
      currentTxNumber: 0, // used as part of the UI updates during the final step
      zkSyncWasInterrupted: undefined, // read from local storage, true if user closes window before deposit is complete
      showAdvancedSettings: false, // advanced settings let user deposit extra funds into zkSync
      zkSyncAdditionalDeposits: [], // array of objects of: { amount: ABC, tokenSymbol: 'XYZ' }
      zkSyncDonationInputsEthAmount: undefined, // version of donationInputsEthAmount, but used to account for additional deposit amount
      hasSufficientZkSyncBalance: true, // starts as true, is true if user already has enough funds in their zkSync account for checkout
      maxPossibleSignatures: 4, // for Flow A, start by assuming 4 -- two logins, set signing key, one transfer
      isZkSyncModalLoading: false, // modal requires async actions before loading, so show loading spinner to improve UX
      zkSyncWalletState: undefined, // state of user's nominal zkSync wallet
      selectedNetwork: undefined, // used to force computed properties to update when document.web3network changes
      zkSyncFeeTotals: {}, // used to dispaly a string showing the total zkSync fees when checking out with Flow B
      zkSyncFeesString: undefined, // string generated from the above property
      isZkSyncDown: false, // true if zkSync is having issues with their servers
      // SMS validation
      csrf: $("input[name='csrfmiddlewaretoken']").val(),
      validationStep: 'intro',
      showValidation: false,
      phone: '',
      validNumber: false,
      errorMessage: '',
      verified: document.verified,
      code: '',
      timePassed: 0,
      timeInterval: 0,
      display_email_option: false,
      countDownActive: false,
      // BrightID
      isBrightIDVerified: false,
      // Collection
      showCreateCollection: false,
      collectionTitle: '',
      collectionDescription: '',
      collections: [],
      selectedCollection: null
    };
  },

  computed: {
    // Returns true if user is logged in with GitHub, false otherwise
    isLoggedIn() {
      return document.contxt.github_handle;
    },

    // Determine when activate the save collection button
    isValidCollection() {
      if (this.selectedCollection !== null) {
        return true;
      } else if (this.collectionTitle.length > 3 && this.collectionDescription.length < 140) {
        return true;
      }

      return false;
    },

    // Returns true of screen size is smaller than 576 pixels (Bootstrap's small size)
    isMobileDevice() {
      return this.windowWidth < 576;
    },

    // Array of arrays, item i lists supported tokens for donating to grant given by grantData[i]
    currencies() {
      if (!this.grantData || !this.tokenList)
        return undefined;

      // Get supported tokens for each grant
      const currencies = this.grantData.map(grant => {
        // Return full list if grant accepts all tokens
        if (grant.grant_token_address === '0x0000000000000000000000000000000000000000') {
          return this.tokenList.map(token => token.name);
        }

        // Return ETH + selected token otherwise
        let allowedTokens = ['ETH'];

        this.tokenList.forEach(tokenData => {
          if (tokenData.addr === grant.grant_token_address)
            allowedTokens.push(tokenData.name);
        });
        return allowedTokens;
      });

      return currencies;
    },

    // Percentage of donation that goes to Gitcoin
    gitcoinFactor() {
      return Number(this.gitcoinFactorRaw) / 100;
    },

    // Amounts being donated to grants
    donationsToGrants() {
      return this.donationSummaryTotals(1 - this.gitcoinFactor);
    },

    // Amounts being donated to Gitcoin
    donationsToGitcoin() {
      return this.donationSummaryTotals(this.gitcoinFactor);
    },

    // Total amounts being donated
    donationsTotal() {
      return this.donationSummaryTotals(1);
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

    // Array of objects containing all donations and associated data
    donationInputs() {
      if (!this.grantData)
        return undefined;

      // Generate array of objects containing donation info from cart
      let gitcoinFactor = 100 * this.gitcoinFactor;
      const donations = this.grantData.map((grant, index) => {
        const tokenDetails = this.getTokenByName(grant.grant_donation_currency);
        const amount = this.toWeiString(
          Number(grant.grant_donation_amount),
          tokenDetails.decimals,
          100 - gitcoinFactor
        );

        return {
          token: tokenDetails.addr,
          amount,
          dest: grant.grant_admin_address,
          name: grant.grant_donation_currency, // token abbreviation, e.g. DAI
          grant, // all grant data from localStorage
          comment: this.comments[index], // comment left by donor to grant owner
          tokenApprovalTxHash: '' // tx hash of token approval required for this donation
        };
      });

      // Append the Gitcoin donations (these already account for gitcoinFactor)
      Object.keys(this.donationsToGitcoin).forEach((token) => {
        const tokenDetails = this.getTokenByName(token);
        const amount = this.toWeiString(this.donationsToGitcoin[token], tokenDetails.decimals);

        const gitcoinGrantInfo = {
          // Manually fill this in so we can access it for the POST requests.
          // We use empty strings for fields that are not needed here
          grant_admin_address: gitcoinAddress,
          grant_contract_address: '0xeb00a9c1Aa8C8f4b20C5d3dDA2bbC64Aa39AF752',
          grant_contract_version: '1',
          grant_donation_amount: this.donationsToGitcoin[token],
          grant_donation_clr_match: '',
          grant_donation_currency: token,
          grant_donation_num_rounds: 1,
          grant_id: '86',
          grant_image_css: '',
          grant_logo: '',
          grant_slug: 'gitcoin-sustainability-fund',
          grant_title: 'Gitcoin Grants Round 7+ Development Fund',
          grant_token_address: '0x0000000000000000000000000000000000000000',
          grant_token_symbol: '',
          isAutomatic: true // we add this field to help properly format the POST requests
        };

        // Only add to donation inputs array if donation amount is greater than 0
        if ((new BN(amount)).gt(new BN('0'))) {
          donations.push({
            amount,
            token: tokenDetails.addr,
            dest: gitcoinAddress,
            name: token, // token abbreviation, e.g. DAI
            grant: gitcoinGrantInfo, // equivalent to grant data from localStorage
            comment: '', // comment left by donor to grant owner
            tokenApprovalTxHash: '' // tx hash of token approval required for this donation
          });
        }

      });
      return donations;
    },

    // Total amount of ETH that needs to be sent along with the transaction
    donationInputsEthAmount() {
      // Get the total ETH we need to send
      const initialValue = new BN('0');
      const ethAmountBN = this.donationInputs.reduce((accumulator, currentValue) => {
        return currentValue.token === ETH_ADDRESS
          ? accumulator.add(new BN(currentValue.amount)) // ETH donation
          : accumulator.add(new BN('0')); // token donation
      }, initialValue);

      return ethAmountBN.toString(10);
    },

    // Estimated gas limit for the transaction
    donationInputsGasLimitL1() {
      // The below heuristics are used instead of `estimateGas()` so we can send the donation
      // transaction before the approval txs are confirmed, because if the approval txs
      // are not confirmed then estimateGas will fail.

      // If we have a cart where all donations are in Dai, we use a linear regression to
      // estimate gas costs based on real checkout transaction data, and add a 50% margin
      const donationCurrencies = this.donationInputs.map(donation => donation.token);
      const daiAddress = this.getTokenByName('DAI').addr;
      const isAllDai = donationCurrencies.every((addr) => addr === daiAddress);

      if (isAllDai) {
        if (donationCurrencies.length === 1) {
          // Special case since we overestimate here otherwise
          return 80000;
        }
        // Below curve found by running script at the repo below around 9AM PT on 2020-Jun-19
        // then generating a conservative best-fit line
        // https://github.com/mds1/Gitcoin-Checkout-Gas-Analysis
        return 25000 * donationCurrencies.length + 125000;
      }

      // Otherwise, based on contract tests, we use the more conservative heuristic below to get
      // a gas estimate. The estimates used here are based on testing the cost of a single
      // donation (i.e. one item in the cart). Because gas prices go down with batched
      // transactions, whereas this assumes they're constant, this gives us a conservative estimate
      const gasLimit = this.donationInputs.reduce((accumulator, currentValue) => {
        const tokenAddr = currentValue.token.toLowerCase();

        if (currentValue.token === ETH_ADDRESS) {
          return accumulator + 50000; // ETH donation gas estimate

        } else if (tokenAddr === '0x960b236A07cf122663c4303350609A66A7B288C0'.toLowerCase()) {
          return accumulator + 170000; // ANT donation gas estimate

        } else if (tokenAddr === '0xfC1E690f61EFd961294b3e1Ce3313fBD8aa4f85d'.toLowerCase()) {
          return accumulator + 500000; // aDAI donation gas estimate

        } else if (tokenAddr === '0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643'.toLowerCase()) {
          return accumulator + 450000; // cDAI donation gas estimate

        }
        return accumulator + 100000; // generic token donation gas estimate
      }, 0);

      return gasLimit;
    },

    maxPossibleTransactions() {
      if (!this.donationsTotal) {
        return '-';
      }

      let number = 1;

      Object.keys(this.donationsTotal).forEach((token) => {
        if (token !== 'ETH') {
          number += 1;
        }
      });
      return number;
    },

    // =============================================================================================
    // ============================= START ZKSYNC COMPUTED PROPERTIES ==============================
    // =============================================================================================

    // Link to L2 account (Flow A) or L1 deposit transaction (Flow B) on block explorer. For L2
    // we link to an account instead of a transfer because there are multiple transfers if multiple
    // tokens are being used
    zkSyncBlockExplorerUrl() {
      // Flow A, zkScan link
      if (this.hasSufficientZkSyncBalance) {
        if (this.selectedNetwork === 'rinkeby')
          return `https://${this.selectedNetwork}.zkscan.io/explorer/accounts/${this.userAddress}`;
        return `https://zkscan.io/explorer/accounts/${this.userAddress}`;
      }

      // Flow B, etherscan link
      if (!this.zkSyncDepositTxHash)
        return undefined;
      if (this.selectedNetwork === 'rinkeby')
        return `https://${this.selectedNetwork}.etherscan.io/tx/${this.zkSyncDepositTxHash}`;
      return `https://etherscan.io/tx/${this.zkSyncDepositTxHash}`;
    },

    // Array of supported tokens
    zkSyncSupportedTokens() {
      const mainnetTokens = [ 'ETH', 'DAI', 'USDC', 'USDT', 'LINK', 'WBTC', 'PAN', 'SNT' ];

      if (!this.selectedNetwork)
        return mainnetTokens;
      if (this.selectedNetwork === 'rinkeby')
        return [ 'ETH', 'USDT', 'LINK' ];
      return mainnetTokens;
    },

    // Estimated gas limit for zkSync checkout
    zkSyncDonationInputsGasLimit() {
      // The below heuristics are used instead of `estimateGas()` so we can send the donation
      // transaction before the approval txs are confirmed, because if the approval txs
      // are not confirmed then estimateGas will fail.

      // zkSync transfer costs from their docs
      const gasPerTransfer = 2000;

      // Deposit into zkSync costs
      const depositGasCost = {
        'ETH': 200000,
        'DAI': 250000,
        'USDC': 250000,
        'USDT': 250000,
        'LINK': 250000,
        'WBTC': 250000,
        'PAN': 250000
      };

      // Make sure all tokens in cart are supported
      const donationCurrencies = this.donationInputs.map(donation => donation.name);

      for (let i = 0; i < donationCurrencies.length; i += 1) {
        if (!this.zkSyncSupportedTokens.includes(donationCurrencies[i])) {
          // Include that token is not supported
          return '10000000';
        }
      }

      // If user has enough funds in their zkSync wallet, estimation is straightforward
      if (this.hasSufficientZkSyncBalance) {
        return String(this.donationInputs.length * gasPerTransfer);
      }

      // Otherwise, if they only have one token in cart, use those estimates
      const numberOfTokens = Array.from(new Set(donationCurrencies)).length;

      switch (numberOfTokens) {
        case 1:
          tokenName = donationCurrencies[0];
          return String(depositGasCost[tokenName]);
        case 2:
          return String(250000 * 2);
        case 3:
          return String(250000 * 3);
        case 4:
          return String(250000 * 4);
        case 5:
          return String(250000 * 5);
        case 6:
          return String(250000 * 6);
        case 7:
          return String(250000 * 7);
        default:
          // Too many tokens, zkSync does not support them all
          return '10000000';
      }
    },

    /**
     * @notice Returns a list of tokens in the users cart that do not support zkSync
     */
    zkSyncUnsupportedTokens() {
      let unsupported = [];
      const donationCurrencies = this.donationInputs.map(donation => donation.name);

      for (let i = 0; i < donationCurrencies.length; i += 1) {
        if (!this.zkSyncSupportedTokens.includes(donationCurrencies[i])) {
          // Include that token is not supported
          unsupported.push(donationCurrencies[i]);
        }
      }
      return Array.from(new Set(unsupported));
    },

    /**
     * @notice Make a recommendation to the user about which checkout to use
     */
    checkoutRecommendation() {
      const estimateL1 = Number(this.donationInputsGasLimitL1);
      const estimateZkSync = Number(this.zkSyncDonationInputsGasLimit);

      if (estimateL1 < estimateZkSync) {
        const savingsInGas = estimateZkSync - estimateL1;
        const savingsInPercent = Math.round(savingsInGas / estimateZkSync * 100);

        return {
          name: 'Standard checkout',
          savingsInGas,
          savingsInPercent
        };
      }

      const savingsInGas = estimateL1 - estimateZkSync;
      const savingsInPercent = Math.round(savingsInGas / estimateL1 * 100);

      return {
        name: 'zkSync',
        savingsInGas,
        savingsInPercent
      };
    }

    // =============================================================================================
    // ============================== END ZKSYNC COMPUTED PROPERTIES ===============================
    // =============================================================================================
  },

  methods: {
    // TODO: SMS related methos and state should be removed and refactored into the component that
    // should be shared between the cart and the Trust Bonus tab
    dismissVerification() {
      localStorage.setItem('dismiss-sms-validation', true);
      this.showValidation = false;
    },
    showSMSValidationModal() {
      if (!this.verified) {
        this.showValidation = true;
      } else {
        _alert('You have been verified previously');
      }
    },
    // VALIDATE
    validateCode() {
      const vm = this;

      if (vm.code) {
        const verificationRequest = fetchData('/sms/validate/', 'POST', {
          code: vm.code,
          phone: vm.phone
        }, {'X-CSRFToken': vm.csrf});

        $.when(verificationRequest).then(response => {
          vm.verificationEnabled = false;
          vm.verified = true;
          vm.validationStep = 'verifyNumber';
          vm.showValidation = false;
          _alert('You have been verified', 'success');
        }).catch((e) => {
          vm.errorMessage = e.responseJSON.msg;
        });
      }
    },
    startVerification() {
      this.phone = '';
      this.validationStep = 'requestVerification';
      this.validNumber = false;
      this.errorMessage = '';
      this.code = '';
      this.timePassed = 0;
      this.timeInterval = 0;
      this.display_email_option = false;
    },
    countdown() {
      const vm = this;

      if (!vm.countDownActive) {
        vm.countDownActive = true;

        setInterval(() => {
          vm.timePassed += 1;
        }, 1000);
      }
    },
    resendCode(delivery_method) {
      const e164 = this.phone.replace(/\s/g, '');
      const vm = this;

      vm.errorMessage = '';

      if (vm.validNumber) {
        const verificationRequest = fetchData('/sms/request', 'POST', {
          phone: e164,
          delivery_method: delivery_method || 'sms'
        }, {'X-CSRFToken': vm.csrf});

        vm.errorMessage = '';

        $.when(verificationRequest).then(response => {
          // set the cooldown time to one minute
          this.timePassed = 0;
          this.timeInterval = 60;
          this.countdown();
          this.display_email_option = response.allow_email;
        }).catch((e) => {
          vm.errorMessage = e.responseJSON.msg;
        });
      }
    },
    // REQUEST VERIFICATION
    requestVerification(event) {
      const e164 = this.phone.replace(/\s/g, '');
      const vm = this;

      if (vm.validNumber) {
        const verificationRequest = fetchData('/sms/request', 'POST', {
          phone: e164
        }, {'X-CSRFToken': vm.csrf});

        vm.errorMessage = '';

        $.when(verificationRequest).then(response => {
          vm.validationStep = 'verifyNumber';
          this.timePassed = 0;
          this.timeInterval = 60;
          this.countdown();
          this.display_email_option = response.allow_email;
        }).catch((e) => {
          vm.errorMessage = e.responseJSON.msg;
        });
      }
    },
    isValidNumber(validation) {
      console.log(validation);
      this.validNumber = validation.isValid;
    },
    loginWithGitHub() {
      window.location.href = `${window.location.origin}/login/github/?next=/grants/cart`;
    },
    // BRIGHTID
    async fetchBrightIDStatus() {
      if (!document.brightid_uuid) {
        return;
      }

      const url = `https://app.brightid.org/node/v5/verifications/Gitcoin/${document.brightid_uuid}`;
      const response = await fetch(url);

      this.isBrightIDVerified = (response.status === 200);
    },
    confirmClearCart() {
      if (confirm('are you sure')) {
        this.clearCart();
      }
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

    removeGrantFromCart(id) {
      CartData.removeIdFromCart(id);
      this.grantData = CartData.loadCart();
      update_cart_title();
    },

    addComment(id, text) {
      // Set comment at this index to an empty string to show textarea
      this.grantData[id].grant_comments = text ? text : '';
      CartData.setCart(this.grantData);
      this.$forceUpdate();

      $('input[type=textarea]').focus();
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

      this.grantData.forEach(grant => {
        if (!totals[grant.grant_donation_currency]) {
          // First time seeing this token, set the field and initial value
          totals[grant.grant_donation_currency] = Number(grant.grant_donation_amount) * scaleFactor;
        } else {
          // We've seen this token, so just update the total
          totals[grant.grant_donation_currency] += (Number(grant.grant_donation_amount) * scaleFactor);
        }
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
        // Round to 2 digits
        const amount = this[propertyName][key];
        const formattedAmount = amount.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits
        });

        if (string === '') {
          string += `${formattedAmount} ${key}`;
        } else {
          string += `+ ${formattedAmount} ${key}`;
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

      _alert(message, 'error');
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
    getTokenByName(name) {
      if (name === 'ETH') {
        return {
          addr: ETH_ADDRESS,
          address: ETH_ADDRESS,
          name: 'ETH',
          symbol: 'ETH',
          decimals: 18,
          priority: 1
        };
      }
      return this.currentTokens.filter(token => token.name === name)[0];
    },

    /**
     * @notice Returns a string of the human-readable value, in "Wei", where by wei we refer
     * to the proper integer value based on the number of token decimals
     * @param {Number} number Human-readable number to convert, e.g. 0.1 or 3
     * @param {Number} decimals Number of decimals for conversion to Wei
     * @param {Number} scaleFactor Factor to multiply number by, as percent*100, e.g. value of 100
     * means multiply by scale factor of 1
     */
    toWeiString(number, decimals, scaleFactor = 100) {
      let wei;

      try {
        wei = Web3.utils.toWei(String(number));
      } catch (e) {
        // When numbers are too small toWei fails because there's too many decimal places
        wei = Math.round(number * 10 ** 18);
      }

      const base = new BN(10, 10);
      const factor = base.pow(new BN(18 - decimals, 10));
      const scale = new BN(scaleFactor, 10);
      const amount = (new BN(wei)).mul(scale).div(new BN(100, 10));

      return amount.div(factor).toString(10);
    },

    async applyAmountToAllGrants(grant) {
      const preferredAmount = grant.grant_donation_amount;
      const preferredTokenName = grant.grant_donation_currency;
      const fallbackAmount = await this.valueToEth(preferredAmount, preferredTokenName);

      this.grantData.forEach((grant, index) => {
        const acceptedCurrencies = this.currencies[index]; // tokens accepted by this grant

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

    /**
     * @notice Must be called at the beginning of each checkout flow (L1, zkSync, etc.)
     */
    async initializeCheckout() {
      // Prompt web3 login if not connected
      if (!provider) {
        return await onConnect();
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
      const userAddress = (await web3.eth.getAccounts())[0];

      return userAddress;
    },

    /**
     * @notice For each token, checks if an approval is needed against the specified contract, and
     * returns the data
     * @param userAddress User's web3 address
     * @param targetContract Address of the contract to check allowance against (e.g. the
     * regular BulkCheckout contract, the zkSync contract, etc.)
     */
    async getAllowanceData(userAddress, targetContract) {
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
            : accumulator.add(new BN('0')); // ETH donation
        }, initialValue);
      };

      // Loop over each token in the cart and check allowance
      for (let i = 0; i < selectedTokens.length; i += 1) {
        const tokenName = selectedTokens[i];
        const tokenDetails = this.getTokenByName(tokenName);

        // If ETH donation no approval is necessary, just check balance
        if (tokenDetails.name === 'ETH') {
          const userEthBalance = await web3.eth.getBalance(userAddress);

          if (new BN(userEthBalance, 10).lt(new BN(this.donationInputsEthAmount, 10))) {
            // User ETH balance is too small compared to selected donation amounts
            this.zkSyncCheckoutStep1Status = 'not-started';
            this.zkSyncCheckoutStep2Status = 'not-started';
            this.showZkSyncModal = false;
            throw new Error('Insufficient ETH balance to complete checkout');
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
          this.zkSyncCheckoutStep1Status = 'not-started';
          this.zkSyncCheckoutStep2Status = 'not-started';
          this.showZkSyncModal = false;
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
     * @param targetContract Address of the contract to check allowance against (e.g. the
     * regular BulkCheckout contract, the zkSync contract, etc.)
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

    /**
     * @notice Checkout flow
     */
    async checkout() {
      try {
        // Setup -----------------------------------------------------------------------------------
        const userAddress = await this.initializeCheckout();

        // Token approvals and balance checks (just checks data, does not execute approavals)
        const allowanceData = await this.getAllowanceData(
          userAddress,
          bulkCheckoutAddress
        );

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

    /**
     * Returns donation inputs for a transaction, filtered to remove unused data
     */
    getDonationInputs() {
      // We use parse and stringify to avoid mutating this.donationInputs since we use it later
      const donationInputs = JSON.parse(JSON.stringify(this.donationInputs)).map(donation => {
        delete donation.name;
        delete donation.grant;
        delete donation.comment;
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

      indicateMetamaskPopup();
      bulkTransaction.methods
        .donate(donationInputsFiltered)
        .send({ from: userAddress, gas: this.donationInputsGasLimitL1, value: this.donationInputsEthAmount })
        .on('transactionHash', async(txHash) => {
          console.log('Donation transaction hash: ', txHash);
          indicateMetamaskPopup(true);
          _alert('Saving contributions. Please do not leave this page.', 'success', 2000);
          await this.postToDatabase(txHash, bulkCheckoutAddress, userAddress); // Save contributions to database
          await this.finalizeCheckout(); // Update UI and redirect
        })
        .on('error', (error, receipt) => {
          // If the transaction was rejected by the network with a receipt, the second parameter will be the receipt.
          this.handleError(error);
        });
    },

    /**
     * @notice POSTs donation data to database. Intended to be called from finalizeCheckout()
     */
    async postToDatabase(txHash, contractAddress, userAddress) {
      // this.donationInputs is the array used for bulk donations
      // We loop through each donation and POST the required data
      const donations = this.donationInputs;
      const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

      // Configure template payload
      const saveSubscriptionPayload = {
        // Values that are constant for all donations
        contributor_address: userAddress,
        csrfmiddlewaretoken,
        frequency_count: 1,
        frequency_unit: 'rounds',
        gas_price: 0,
        gitcoin_donation_address: gitcoinAddress,
        hide_wallet_address: this.hideWalletAddress,
        match_direction: '+',
        network: document.web3network,
        num_periods: 1,
        real_period_seconds: 0,
        recurring_or_not: 'once',
        signature: 'onetime',
        split_tx_id: txHash, // this txhash is our bulk donation hash
        splitter_contract_address: contractAddress,
        subscription_hash: 'onetime',
        // Values that vary by donation
        'gitcoin-grant-input-amount': [],
        admin_address: [],
        amount_per_period: [],
        comment: [],
        confirmed: [],
        contract_address: [],
        contract_version: [],
        denomination: [],
        grant_id: [],
        sub_new_approve_tx_id: [],
        token_address: [],
        token_symbol: []
      };

      for (let i = 0; i < donations.length; i += 1) {
        // Get URL to POST to
        const donation = donations[i];
        const grantId = donation.grant.grant_id;

        // Get token information
        const tokenName = donation.grant.grant_donation_currency;
        const tokenDetails = this.getTokenByName(tokenName);

        // Gitcoin uses the zero address to represent ETH, but the contract does not. Therefore we
        // get the value of denomination and token_address using the below logic instead of
        // using tokenDetails.addr
        const isEth = tokenName === 'ETH';
        const tokenAddress = isEth ? '0x0000000000000000000000000000000000000000' : tokenDetails.addr;

        // Replace undefined comments with empty strings
        const comment = donation.grant.grant_comments === undefined ? '' : donation.grant.grant_comments;

        // For automatic contributions to Gitcoin, set 'gitcoin-grant-input-amount' to 100.
        // Why 100? Because likely no one will ever use 100% or a normal grant, so using
        // 100 makes it easier to search the DB to find which Gitcoin donations were automatic
        const isAutomatic = donation.grant.isAutomatic;
        const gitcoinGrantInputAmt = isAutomatic ? 100 : Number(this.gitcoinFactorRaw);

        // Add the donation parameters
        saveSubscriptionPayload.admin_address.push(donation.grant.grant_admin_address);
        saveSubscriptionPayload.amount_per_period.push(Number(donation.grant.grant_donation_amount));
        saveSubscriptionPayload.comment.push(comment);
        saveSubscriptionPayload.confirmed.push(false);
        saveSubscriptionPayload.contract_address.push(donation.grant.grant_contract_address);
        saveSubscriptionPayload.contract_version.push(donation.grant.grant_contract_version);
        saveSubscriptionPayload.denomination.push(tokenAddress);
        saveSubscriptionPayload['gitcoin-grant-input-amount'].push(gitcoinGrantInputAmt);
        saveSubscriptionPayload.grant_id.push(grantId);
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
    },

    /**
     * @notice POSTs donation data to database, updates local storage, redirects page, shows
     * success alert
     */
    async finalizeCheckout() {
      // Clear cart, redirect back to grants page, and show success alert
      localStorage.setItem('contributions_were_successful', 'true');
      localStorage.setItem('contributions_count', String(this.grantData.length));
      var network = document.web3network;
      let timeout_amount = 1500 + (CartData.loadCart().length * 500);

      setTimeout(function() {
        _alert('Contributions saved', 'success', 1000);
        setTimeout(function() {
          if (network === 'rinkeby') {
            window.location.href = `${window.location.origin}/grants/?network=rinkeby&category=`;
          } else {
            window.location.href = `${window.location.origin}/grants`;
          }
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

    valueToDai(amount, tokenSymbol, tokenPrices) {
      const tokenIndex = tokenPrices.findIndex(item => item.token === tokenSymbol);
      const amountOfOne = tokenPrices[tokenIndex].usdt; // value of 1 tokenSymbol

      return Number(amount) * Number(amountOfOne); // convert based on quantity and return
    },

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

    // =============================================================================================
    // =================================== START ZKSYNC METHODS ====================================
    // =============================================================================================

    // ===================================== Helper functions ======================================

    /**
     * @notice Set flag in database to true if user was interrupted before completing zkSync
     * checkout
     * @param {Boolean} deposit_tx_hash Tx hash of the corresponding deposit that was interrupted,
     * undefined otherwise
     * @param {String} userAddress Address of user to check status for
     */
    async setInterruptStatus(deposit_tx_hash, userAddress) {
      const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      const url = 'zksync-set-interrupt-status';
      const headers = { 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8' };
      const payload = {
        method: 'POST',
        headers,
        body: new URLSearchParams({ deposit_tx_hash, user_address: userAddress, csrfmiddlewaretoken })
      };

      // Send request
      const res = await fetch(url, payload);
      const json = await res.json();

      return json;
    },

    /**
     * @notice Check interrupt status for the logged in user
     * @param {String} userAddress Address of user to check status for
     */
    async getInterruptStatus(userAddress) {
      const url = `zksync-get-interrupt-status?user_address=${userAddress}`;
      const res = await fetch(url, { method: 'GET' });
      const json = await res.json();
      const txHash = json.deposit_tx_hash;

      if (txHash.length === 66 && txHash.startsWith('0x')) {
        // Valid transaction hash. Check if tx failed
        const receipt = await this.ethersProvider.getTransactionReceipt(txHash);

        if (receipt.status === 0) {
          // Transaction failed, user must start over so mark them as not interrupted
          await this.setInterruptStatus(null, this.userAddress);
          return false;
        }

        // Transaction was mined, user must complete checkout
        return txHash;
      }

      // User was not interrupted
      return false;
    },

    /**
     * @notice Checks the interrupt status for a user, and prompts them to complete their
     * checkout if they have been interrupted
     */
    async checkInterruptStatus() {
      try {
        // We manually fetch the address so we can try checking independently of whether the
        // this.userAddress parameter has been set. This is also why we need a try/catch -- the
        // user may not have connected their wallet.
        const userAddress = (await web3.eth.getAccounts())[0];
        const result = await this.getInterruptStatus(userAddress);

        this.zkSyncWasInterrupted = Boolean(result);
        if (this.zkSyncWasInterrupted) {
          this.zkSyncDepositTxHash = result;
        }
      } catch (e) {
        this.handleError(e);
      }
    },

    /**
     * @notice For the given transaction hash, looks to see if it's been replaced
     * @param txHash String, transaction hash to check
     * @returns New transaction hash if found, original othrwise
     */
    async getReplacedTx(txHash) {
      const url = `get-replaced-tx?tx_hash=${txHash}`;
      const res = await fetch(url, { method: 'GET' });
      const json = await res.json();
      const newTxHash = json.tx_hash;

      return newTxHash;
    },

    /**
     * @notice For each token, returns the total amount donated in that token. Used instead of
     * this.donationsTotal to ensure there's no floating point errors. This is very similar to
     * getAllowanceData()
     */
    zkSyncSummaryData() {
      const selectedTokens = Object.keys(this.donationsToGrants); // list of tokens being used
      let summaryData = [];

      // Define function that calculates the total amount for the specified token
      const calcTotalAllowance = (tokenDetails) => {
        const initialValue = new BN('0');

        return this.donationInputs.reduce((accumulator, currentValue) => {
          return currentValue.token === tokenDetails.addr
            ? accumulator.add(new BN(currentValue.amount)) // token donation
            : accumulator.add(new BN('0')); // ETH donation
        }, initialValue);
      };

      // Loop over each token in the cart and get required allowance (i.e. total donation amount in
      // that token)
      for (let i = 0; i < selectedTokens.length; i += 1) {
        const tokenName = selectedTokens[i];
        const tokenDetails = this.getTokenByName(tokenName);
        const tokenContract = new web3.eth.Contract(token_abi, tokenDetails.addr);
        const requiredAllowance = calcTotalAllowance(tokenDetails);

        // If ETH donation we can skip
        if (tokenDetails.name === 'ETH') {
          continue;
        }

        // If we do need to set the allowance, save off the required info to request it later
        summaryData.push({
          allowance: requiredAllowance.toString(),
          contract: tokenContract,
          tokenName
        });
      }

      return summaryData;
    },

    /**
     * @notice Login to zkSync account associated with user's web3 wallet
     */
    async zkSyncLoginNominal() {
      console.log('Waiting for user to sign the prompt to log in to zkSync directly...');
      const nominalSyncWallet = await zksync.Wallet.fromEthSigner(this.signer, this.syncProvider);

      console.log('✅ Login complete. Nominal sync wallet generated from web3 account. View wallet:', nominalSyncWallet);
      return nominalSyncWallet;
    },

    /**
     * @notice Generate a Gitcoin-specific private key to use and login to zkSync with it
     * @returns User's gitcoinSyncWallet instance
     */
    async zkSyncLoginGitcoin() {
      // Prompt for user's signature to generate deterministic private key. This enables us
      // to determinstically generate the same, Gitcoin-specific zkSync wallet on each visit
      const message = 'Access Gitcoin zkSync account.\n\nOnly sign this message for a trusted client!';

      indicateMetamaskPopup();
      let signature;

      signature = await this.signer.signMessage(message); // web3 prompt to user is here
      if (!signature) {
        // Fallback to personal_sign if eth_sign isn't supported (for Status and other wallets)
        signature = await this.ethersProvider.send(
          'personal_sign',
          [ ethers.utils.hexlify(ethers.utils.toUtf8Bytes(message)), this.userAddress.toLowerCase() ]
        );
      }

      indicateMetamaskPopup(true);
      const privateKey = ethers.utils.sha256(signature);
      const wallet = new ethers.Wallet(privateKey);

      // Login to zkSync
      console.log('Waiting for user to sign the prompt to log in to zkSync via Gitcoin...');
      const gitcoinSyncWallet = await zksync.Wallet.fromEthSigner(wallet, this.syncProvider);

      console.log('✅ Login complete. Gitcoin sync wallet generated from web3 account. View wallet:', gitcoinSyncWallet);
      return gitcoinSyncWallet;
    },

    /**
     * @notice Initialize UI updates for tracking confirmation counter
     */
    updateConfirmationsInUI() {
      // Track number of confirmations live in UI
      this.currentConfirmationNumber = 1;
      if (this.currentConfirmationNumber === this.numberOfConfirmationsNeeded) {
        // We only need one confirmation, so we're done -- this is for Rinkeby
        this.zkSyncCheckoutFlowStep += 1;
      } else {
        // Watch for blocks so update number of confirmations received in UI
        this.ethersProvider.on('block', () => {
          this.currentConfirmationNumber += 1;
          if (this.currentConfirmationNumber === this.numberOfConfirmationsNeeded) {
            // Remove listener and update state once we get all required confirmations
            this.zkSyncCheckoutFlowStep += 1;
            this.ethersProvider.removeAllListeners('block');
          }
        });
      }
    },

    /**
     * @notice Gets the serial ID from zkSync deposit transaction by parsing event logs
     * @param receipt Transaction receipt from ethers.js
     */
    getDepositSerialId(receipt) {
      // Parse logs in receipt so we can get priority request IDs from the events
      console.log('Parsing transaction receipt for NewPriorityRequest events...');
      const zkSyncInterface = new ethers.utils.Interface(zkSyncContractAbi);
      const logs = receipt.logs
        .map((log) => {
          // Only parse logs from the zkSync contract, not our batch deposit contract
          if (log.address === this.zkSyncContractAddress)
            return zkSyncInterface.parseLog(log);
        })
        .filter((log) => log && log.name === 'NewPriorityRequest') // only keep these events
        .map((event) => event.args.serialId.toNumber()); // we only need the serialId

      console.log(`Found ${logs.length} serial IDs in the event logs. Will track the last one`, logs);

      // Take the last ID and track that one to know when deposit is committed. Since all
      // deposits were in the same tx, it shouldn't matter which ID we use. We do not wait
      // for it to be verified, as this takes much longer and it's safe enough to wait only
      // for commitment. Some relevant notes are below.
      //
      // There are two types of states on the zkSync network: (1) Commited, and (2) Verified
      //   (1) Committed: last state known to the zkSync network, can be ahead of verified state
      //   (2) Verified: state that is proved with ZKP on the Ethereum network.
      //
      // There are also two types of operations: (1) Priority operations, and (2) Transactions
      //   (1) Priority operations: Initiated directly on the Ethereum mainnet, e.g. deposits.
      //       These are identified with a numerical ID or the hash of the Ethereum transaction
      //   (2) Transactions: Submitted through the zkSync operator using the API. These are
      //       identified by the has of their serialized representation
      //
      // Note: If we do not wait for this receipt, the unlock step below will fail with
      // "Error: Failed to Set Signing Key: Account does not exist in the zkSync network"
      const serialId = logs[logs.length - 1];

      return serialId;
    },

    /**
     * @notice For the specified serial ID, check if it's been committed, and if not, wait for it
     * to be committed and recognized by the zkSync network
     * @param serialId ID to track
     */
    async waitForSerialIdCommitment(serialId) {
      console.log(`Waiting for confirmation that priority operation with ID ${serialId} is committed...`);

      // Check status. It almost certainly has not been committed yet, but good practice to check
      const depositStatus = await this.syncProvider.getPriorityOpStatus(serialId);

      console.log('Current deposit status: ', depositStatus);

      // If deposit has not yet been committed, wait for that
      if (!depositStatus.block || !depositStatus.block.committed) {
        console.log('Deposit not yet committed, waiting for it...');
        const depositReceipt = await this.syncProvider.notifyPriorityOp(serialId, 'COMMIT');

        console.log('✅ Deposit received', depositReceipt);
      } else {
        console.log('✅ Deposit received', depositStatus);
      }
      this.zkSyncCheckoutFlowStep += 1; // next we register deterministic wallet and sign transactions
      return;
    },

    /**
     * @notice For the given syncWallet, see if the public key needs to be registered, and if so,
     * register it
     */
    async checkAndRegisterSigningKey(syncWallet) {
      // To control assets in zkSync network, an account must register a separate public key
      // once. This can only be done once they have interacted with the network in some way, such
      // as receiving a deposit, so we do that now since the deposit is complete. It cannot be
      // done earlier because otherwise the account won't exist in the zkSync accounts Merkle tree
      console.log('Registering public key to unlock deterministic wallet on zkSync...');
      if (!(await syncWallet.isSigningKeySet())) {
        if ((await syncWallet.getAccountId()) == undefined) {
          // This means the account has never interacted with the network
          throw new Error('Unknown account');
        }

        // Determine how to set key based on wallet type
        let changePubkey;

        if (syncWallet.ethSignerType.verificationMethod === 'ECDSA') {
          console.log('  Using ECDSA to set signing key');
          changePubkey = await syncWallet.setSigningKey();
        } else {
          console.log('  Using ERC-1271 to set signing key. This requires an on-chain transaction');
          const signingKeyTx = await syncWallet.onchainAuthSigningKey();

          changePubkey = await syncWallet.setSigningKey('committed', true);
        }

        // Wait until the tx is committed
        await changePubkey.awaitReceipt();
        console.log('✅ specified sync wallet is ready to use on zkSync');
      } else {
        console.log('✅ specified sync wallet was already initialized');
      }
      return;
    },

    /**
     * @notice Returns next expected nonce for the user's Gitcoin sync wallet
     */
    async getGitcoinSyncWalletNonce() {
      console.log('Getting state and nonce of Gitcoin sync wallet...');
      const syncWalletState = await this.gitcoinSyncWallet.getAccountState();
      const nonce = syncWalletState.committed.nonce;

      console.log('✅ State of Gitcoin sync wallet retrieved', syncWalletState);
      return nonce;
    },

    /**
     * @notice Generates the zkSync transfer signature
     * @param {Number} nonce Initial nonce that should be used for first signature
     * @returns Array of signatures that can be sent on zkSync
     */
    async generateTransferSignatures(nonce) {
      const donationInputs = this.donationInputs; // just for convenience

      console.log('Generating signatures for transfers...');
      console.log('  Array of donations to be made is', donationInputs);

      const donationSignatures = []; // signatures for grant contribution transfers

      // Get signatures for donation transfers
      for (let i = 0; i < donationInputs.length; i += 1) {
        this.currentTxNumber += 1;
        console.log(`  Generating signature ${i + 1} of ${donationInputs.length}...`);
        const donationInput = donationInputs[i];
        const { fee, amount } = await this.getZkSyncFeeAndAmount(donationInput);

        // Now we can generate the signature for this transfer
        const signedTransfer = await this.gitcoinSyncWallet.signSyncTransfer({
          to: donationInput.dest,
          token: donationInput.name,
          amount,
          fee,
          nonce
        });

        donationSignatures.push(signedTransfer);

        // Increment nonce to prepare for next signature
        nonce += 1;
      }
      this.currentTxNumber = 0;
      console.log('✅ All signatures have been generated', donationSignatures);
      return donationSignatures;
    },

    /**
     * @notices Accepts signed transfers and dispatches those transfers
     * @param donationSignatures Array of signatures each output from signSyncTransfer
     */
    async dispatchSignedTransfers(donationSignatures) {
      console.log('Sending transfers to the network...');
      this.zkSyncCheckoutFlowStep += 1; // sending transactions

      // Dispatch donations ------------------------------------------------------------------------
      for (let i = 0; i < donationSignatures.length; i += 1) {
        this.currentTxNumber += 1;
        console.log(`  Sending transfer ${i + 1} of ${donationSignatures.length}...`);
        const transfer = await zksync.wallet.submitSignedTransaction(donationSignatures[i], this.syncProvider);

        console.log(`  Transfer ${i + 1} sent`, transfer);
        const receipt = await transfer.awaitReceipt();

        console.log(`  ✅ Got transfer ${i + 1} receipt`, receipt);
      }

      // Transfer any remaining tokens to user's main wallet ---------------------------------------
      this.zkSyncCheckoutFlowStep += 1; // Done!
      const gitcoinZkSyncState = await this.syncProvider.getState(this.gitcoinSyncWallet.cachedAddress);
      const balances = gitcoinZkSyncState.committed.balances;
      const tokens = Object.keys(balances);

      // Loop through each token the user has
      for (let i = 0; i < tokens.length; i += 1) {
        try {
          const tokenSymbol = tokens[i];
          const transferInfo = {
            dest: this.userAddress,
            name: tokenSymbol,
            amount: balances[tokenSymbol]
          };

          console.log(`Sending remaining ${tokenSymbol} to user's main zkSync wallet...`);

          // The amount returned is the packable version of the amount input. Note that closest
          // packable amount is strictly less than or equal to the input amount
          const { fee, amount } = await this.getZkSyncFeeAndAmount(transferInfo);

          // This fee and amount cannot be used directly, because the amount is the full balance.
          // We now need to subtract the fee from this amount, and must ensure there is
          // actually enough balance left to send this transfer. Otherwise we do not have enough
          // balance to cover the transfer fee

          if (amount.gt(fee)) {
            // Packed account balance is greater than fee, so we can proceed with transfer
            const transferAmount = zksync.utils.closestPackableTransactionAmount(amount.sub(fee));

            // Send transfer
            const tx = await this.gitcoinSyncWallet.syncTransfer({
              to: transferInfo.dest,
              token: transferInfo.name,
              amount: transferAmount,
              fee
            });

            console.log('  Transfer sent', tx);

            // Wait for it to be committed
            const receipt = await tx.awaitReceipt();

            console.log('  ✅ Got transfer receipt', receipt);

          } else {
            console.log('  ❗ Remaining balance is less than the fee, skipping this transfer');
            continue;
          }

        } catch (e) {
          if (e.message === 'zkSync transaction failed: Not enough balance') {
            // Only dust is left for this token, so skip it
            console.log('  ❗ Only dust left, skipping this transfer');
            continue;
          }
          // Everything worked successfully, so let's not throw an error here because the user's
          // donations did succeed. Instead, there is just small excess funds left in the account
          console.error(e);
        }
      }

      // Done!
      this.zkSyncCheckoutStep3Status = 'complete';
      this.zkSyncCheckoutFlowStep += 1; // Done!
      console.log('✅ All transfers have been successfully sent');
      return;
    },

    /**
     * @notice For a given donation in this.donationInputs, returns the packed fee and amount
     * @param donation Object, one element from the this.donationInputs array
     */
    async getZkSyncFeeAndAmount(donation) {
      // Fees must be packable to 2-byte long floating-point representations. Here we find an
      // acceptable transaction fee by querying the server, and this will already be packable
      const fee = await this.syncProvider.getTransactionFee(
        'Transfer', // transaction type
        donation.dest, // recipient address
        donation.name // token name
      );

      // Transfer amounts must be packable to 5-byte long floating-point representations. So
      // here we find the closest packable amount
      const amountBN = ethers.BigNumber.from(donation.amount);
      const amount = zksync.utils.closestPackableTransactionAmount(amountBN);

      return { fee: fee.totalFee, amount };
    },

    /**
     * @notice Setup parameters needed for zkSync checkout
     */
    async setupZkSync() {
      // Configure ethers and zkSync
      const network = document.web3network || 'mainnet';

      this.ethersProvider = new ethers.providers.Web3Provider(provider);
      this.signer = this.ethersProvider.getSigner();
      this.syncProvider = await zksync.getDefaultProvider(network, 'HTTP');
      this.numberOfConfirmationsNeeded = await this.syncProvider.getConfirmationsForEthOpAmount();
      this.zkSyncDonationInputsEthAmount = this.donationInputsEthAmount;
      this.zkSyncWalletState = await this.syncProvider.getState(this.userAddress);

      // Set zkSync contract address based on network
      this.zkSyncContractAddress = network === 'mainnet'
        ? zkSyncContractAddressMainnet // mainnet
        : zkSyncContractAddressRinkeby; // rinkeby
    },

    /**
     * @notice Checks if user has sufficient balance to check out with out a deposit transaciton
     */
    async checkZkSyncBalances() {
      try {
        // Assume true until proven otherwise
        this.hasSufficientZkSyncBalance = true;
        const selectedTokens = Object.keys(this.donationsToGrants);

        for (let i = 0; i < selectedTokens.length; i += 1) {
          const tokenSymbol = selectedTokens[i];
          const decimals = this.getTokenByName(tokenSymbol).decimals;
          const balance = this.zkSyncWalletState.committed.balances[tokenSymbol];

          // Total amount user needs to transfer, including a conservative fee estimate
          const requiredAmount = ethers.utils.parseUnits(String(this.donationsTotal[tokenSymbol]), decimals);
          const totalRequiredAmount = await this.getTotalAmountToTransfer(tokenSymbol, requiredAmount);

          // Get worst case fee amount
          this.zkSyncFeeTotals[tokenSymbol] = await this.getMaxFee(tokenSymbol);
          this.setZkSyncFeesString();

          // Note: Don't `break` out of the if statements if insufficient balance, because we
          // also use this function to set the fee string shown to the user on the checkout modal

          // Balance will be undefined if the user does not have that token, so we can break
          if (!balance) {
            this.hasSufficientZkSyncBalance = false;
          }

          // Otherwise, we compare their balance against the required amount
          if (ethers.BigNumber.from(balance).lt(totalRequiredAmount)) {
            this.hasSufficientZkSyncBalance = false;
          }
        }
      } catch (e) {
        // Fallback to false if we couldn't get balance
        console.error(e);
        this.hasSufficientZkSyncBalance = false;
      }
    },

    /**
     * @notice For a given token and amount, determines how many total transfers are needed
     * and the corresponding total amount, after fees, that is needed to cover them.
     */
    async getTotalAmountToTransfer(tokenSymbol, initialAmount) {
      // Number of transfers that will take place is:
      //   number of donations + 1 initial transfer + 1 final transfer + 1 for margin
      //
      // We are intentionally conservative here because we'd rather a user deposit too much
      // and be successful than too little and fail. The downside to being conservative is that
      // users are required to have enough margin in their accound balance to accomodate this, but
      //  that is ok because it's similar to be required to have enough ETH for excess L1 gas limit
      const numberOfFees = 3 + this.donationInputs.filter((x) => x.name === tokenSymbol).length;

      // Transfers to an address that has never used zkSync are more expensive, which is why we
      // use a random address as the recipient -- this gives us a conservative estimate. We also
      // do this to avoid hitting the zkSync servers with dozens of rapid fee requests when users
      // have a large number of items in their cart
      const { fee, amount } = await this.getZkSyncFeeAndAmount({
        dest: ethers.Wallet.createRandom().address, // gives an address that has never been used on zkSync
        name: tokenSymbol,
        amount: initialAmount
      });

      return amount.add(fee.mul(String(numberOfFees)));
    },

    /**
     * @notice Calculates the maximum possible fees for a specific token
     */
    async getMaxFee(tokenSymbol) {
      const numberOfFees = 3 + this.donationInputs.filter((x) => x.name === tokenSymbol).length;
      const fee = await this.syncProvider.getTransactionFee(
        'Transfer', // transaction type
        ethers.Wallet.createRandom().address, // recipient address
        tokenSymbol // token name
      );

      return fee.totalFee.mul(String(numberOfFees));
    },

    /**
     * @notice String describing the user's zkSync fees, used for Flow A
     */
    setZkSyncFeesString() {
      // If no fees, default to empty string
      if (Object.keys(this.zkSyncFeeTotals).length === 0)
        return '';


      // Conver token amounts to human-readable values (from wei)
      const tokens = Object.keys(this.zkSyncFeeTotals);
      const feeTotals = {};

      for (let i = 0; i < tokens.length; i += 1) {
        const tokenName = tokens[i];
        const decimals = this.getTokenByName(tokenName).decimals;
        const amount = ethers.utils.formatUnits(this.zkSyncFeeTotals[tokenName].toString(), decimals);

        feeTotals[tokenName] = amount;
      }

      // Generate the string
      let string = '';

      tokens.forEach(tokenName => {
        // Round to 2 digits
        const amount = feeTotals[tokenName];
        const formattedAmount = amount.toLocaleString(undefined, {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        });

        if (string === '') {
          string += `${formattedAmount} ${tokenName}`;
        } else {
          string += `+ ${formattedAmount} ${tokenName}`;
        }
      });

      // Set value
      this.zkSyncFeesString = string;
    },

    // ==================================== Main functionality =====================================

    /**
     * @notice Triggers appropriate modal when user begins checkout. If user has an interrupted
     * cart, they must finish checking out with that before doing another checkout
     */
    async startZkSyncCheckoutProcess() {
      try {
        // With zkSync we limit checkout to 100 total donations due to current tx validator
        // limitations. See update_tx_status() app/grants/models.py for more info
        if (this.donationInputs.length > 100) {
          throw new Error(`Checkout with zkSync is currently limited to 100 contributions, but you have ${this.donationInputs.length} contributions. Please remove items from your cart and try again.`);
        }

        // Show zkSync checkout modal
        this.isZkSyncModalLoading = true;
        this.showZkSyncModal = true;

        // Make sure user is connected to web3 and setup zkSync
        this.userAddress = await this.initializeCheckout();
        await this.setupZkSync();

        // See if user was previously interrupted during checkout
        await this.checkInterruptStatus();

        // Set current ETH amount
        this.zkSyncDonationInputsEthAmount = this.donationInputsEthAmount;

        // Make sure selected tokens are valid on zkSync
        const selectedTokens = Object.keys(this.donationsToGrants);

        selectedTokens.forEach((token) => {
          if (!this.zkSyncSupportedTokens.includes(token)) {
            throw new Error(`${token} is not supported with zkSync checkout. Supported currencies are: ${this.zkSyncSupportedTokens.join(', ')}`);
          }
        });

        // Make sure amounts are packable
        for (let i = 0; i < this.donationInputs.length; i += 1) {
          const donation = this.donationInputs[i];
          let fee;
          let amount;

          try {
            // This will throw if amounts are not ok
            ({ fee, amount } = await this.getZkSyncFeeAndAmount(donation));

            // Verify returned values are big numbers above zero
            if (!fee.gt(ethers.constants.Zero))
              throw new Error('Something went wrong with fee amount');
            if (!amount.gt(ethers.constants.Zero))
              throw new Error('Something went wrong with fee amount');

          } catch (e) {
            this.showZkSyncModal = false;
            console.error(e);
            console.log('Corresponding donation:', donation);
            console.log('Corresponding fee:', fee);
            console.log('Corresponding amount:', amount);
            throw e;
          }
        }

        // Populate field for holding additional deposits
        this.zkSyncAdditionalDeposits = []; // clear existing data
        selectedTokens.forEach((tokenSymbol) => this.zkSyncAdditionalDeposits.push({amount: 0, tokenSymbol }));

        // Re-check that user has sufficient funds in the zkSync account (Flow A), or if they will
        // need deposit into the Gitcoin zkSync account (Flow B)
        await this.checkZkSyncBalances();

        // If user has sufficient balance, count how many signatures they need (Flow A)
        if (this.hasSufficientZkSyncBalance) {
          // 4 minimum —- login via Gitcoin, login directly, one token transfer, assume
          // signing key is set

          // +1 for each additional token in their cart
          selectedTokens.forEach((token, index) => {
            if (index !== 0) {
              // SKip first one since we already expect at least one token transfer
              this.maxPossibleSignatures += 1;
            }
          });
        }

        this.isZkSyncModalLoading = false;
      } catch (e) {
        this.showZkSyncModal = false;
        this.handleError(e);
      }
    },

    /**
     * @notice Step 1: Initialize app state and login to zkSync via Gitcoin. This applies to
     * Flow A and Flow B
     */
    async zkSyncLoginGitcoinFlow() {
      try {
        this.zkSyncCheckoutStep1Status = 'pending';

        // Set contract to deposit through based on number of tokens used. We do this to save
        // gas costs by avoiding the overhead of the batch deposit contract if the user is only
        // donating one token
        const numberOfCurrencies = Object.keys(this.donationsToGrants).length;

        this.depositContractToUse = numberOfCurrencies === 1
          ? this.depositContractToUse = this.zkSyncContractAddress
          : this.depositContractToUse = batchZkSyncDepositContractAddress;

        // Prompt for user's signature to login to zkSync
        this.gitcoinSyncWallet = await this.zkSyncLoginGitcoin();

        // Skip next step if only donating ETH, but check that user has enough balance
        const selectedTokens = Object.keys(this.donationsToGrants);

        if (selectedTokens.length === 1 && selectedTokens[0] === 'ETH' && !this.hasSufficientZkSyncBalance) {
          this.zkSyncAllowanceData = await this.getAllowanceData(this.userAddress, this.depositContractToUse);
          this.zkSyncCheckoutStep2Status = 'not-applicable';
        }
        this.zkSyncCheckoutStep1Status = 'complete';
      } catch (e) {
        this.zkSyncCheckoutStep1Status = 'not-started';
        this.handleError(e);
      }
    },

    /**
     * @notice Step 2: Sign in to zkSync directly (Flow A) OR get ERC20 approvals (Flow B)
     */
    async zkSyncBeginStep2() {
      try {
        this.zkSyncCheckoutStep2Status = 'pending';
        // Flow A
        if (this.hasSufficientZkSyncBalance) {
          this.zkSyncCheckoutFlowStep = -1; // dummy value to prevent "Confirmations received" from showing
          this.nominalSyncWallet = await this.zkSyncLoginNominal();

          const isSigningKeySet = this.nominalSyncWallet.isSigningKeySet();

          if (isSigningKeySet)
            this.maxPossibleSignatures -= 1;
          this.zkSyncCheckoutStep2Status = 'complete';
          return;
        }
        // Flow B
        await this.zkSyncApprovals(); // callback is used here so step 2 status is updated elsewhere
      } catch (e) {
        this.zkSyncCheckoutStep2Status = 'not-started';
        this.handleError(e);
      }
    },

    /**
     * @notice Step 2 of Flow B: Checks balances and gets ERC20 approvals
     */
    async zkSyncApprovals() {
      try {
        // If user was interrupted and already sent their deposit transaction, we do not need
        // any token approvals
        if (this.zkSyncDepositTxHash && this.zkSyncWasInterrupted) {
          this.zkSyncCheckoutStep2Status = 'not-applicable';
          return;
        }

        // Otherwise, get required allowance amounts and proceed as normal
        this.zkSyncAllowanceData = await this.getAllowanceData(this.userAddress, this.depositContractToUse);
        const BigNumber = ethers.ethers.BigNumber;

        // Add token allowances for any additional deposits that user has specified
        for (let i = 0; i < this.zkSyncAllowanceData.length; i += 1) {
          const allowanceDetails = this.zkSyncAllowanceData[i];
          const tokenSymbol = allowanceDetails.tokenName;
          const decimals = this.getTokenByName(tokenSymbol).decimals;
          const currentAmount = BigNumber.from(allowanceDetails.allowance);
          const extra = this.zkSyncAdditionalDeposits.filter((x) => x.tokenSymbol === tokenSymbol)[0];

          if (!extra)
            continue;

          const additionalAmount = ethers.utils.parseUnits(String(extra.amount), decimals);
          const newAmount = currentAmount.add(additionalAmount).toString();
          const totalRequiredAmount = await this.getTotalAmountToTransfer(tokenSymbol, newAmount);

          this.zkSyncAllowanceData[i].allowance = totalRequiredAmount;

          // Make sure user has enough funds
          const userTokenBalance = await allowanceDetails.contract.methods
            .balanceOf(this.userAddress)
            .call({from: this.userAddress});

          if (BigNumber.from(userTokenBalance).lt(BigNumber.from(totalRequiredAmount))) {
            this.zkSyncCheckoutStep1Status = 'not-started';
            this.zkSyncCheckoutStep2Status = 'not-started';
            this.showZkSyncModal = false;
            throw new Error(`Insufficient ${tokenSymbol} balance to complete checkout`, 'error');
          }
        }

        // Add ETH additional deposit and ensure user has enough for donation + gas (use lte not lt)
        const selectedTokens = Object.keys(this.donationsToGrants);

        if (selectedTokens.includes('ETH') && this.zkSyncAdditionalDeposits.length > 0) {
          const initialAmount = BigNumber.from(this.zkSyncDonationInputsEthAmount);
          const newAmount = ethers.utils.parseEther(
            String(this.zkSyncAdditionalDeposits.filter((x) => x.tokenSymbol === 'ETH')[0].amount)
          );
          const totalRequiredAmount = await this.getTotalAmountToTransfer('ETH', newAmount);

          this.zkSyncDonationInputsEthAmount = initialAmount.add(totalRequiredAmount).toString();
          const userEthBalance = await web3.eth.getBalance(this.userAddress);

          if (BigNumber.from(userEthBalance).lte(BigNumber.from(this.zkSyncDonationInputsEthAmount))) {
            this.zkSyncCheckoutStep1Status = 'not-started';
            this.zkSyncCheckoutStep2Status = 'not-started';
            this.showZkSyncModal = false;
            throw new Error('Insufficient ETH balance to complete checkout');
          }
        }

        // Otherwise, request approvals. As mentioned above, we check against userAddress
        // (the main web3 wallet) because this is where funds will be transferred from
        await this.requestAllowanceApprovalsThenExecuteCallback(
          this.zkSyncAllowanceData,
          this.userAddress,
          this.depositContractToUse,
          () => {
            this.zkSyncCheckoutStep2Status = 'complete';
          }
        );
      } catch (e) {
        this.zkSyncCheckoutStep2Status = 'not-started';
        this.handleError(e);
      }
    },

    /**
     * @notice Step 3: Main function for executing zkSync checkout
     */
    async zkSyncBeginStep3() {
      this.zkSyncCheckoutStep3Status = 'pending';
      // Flow A
      if (this.hasSufficientZkSyncBalance) {
        await this.sendZkSyncDonationFlowA();
        return;
      }
      // Flow B
      await this.sendZkSyncDonationFlowB();
    },

    /**
     * @notice Step 3 of Flow A. User already has funds in L2, so we transfer from there to their
     * Gitcoin sync wallet, and from the sync wallet we dispatch all transfers without needing to
     * prompt the user
     */
    async sendZkSyncDonationFlowA() {
      // Set signing key for nominal zkSync account if necessary
      await this.checkAndRegisterSigningKey(this.nominalSyncWallet);

      // Do the transfers to gitcoin sync wallet
      const selectedTokens = Object.keys(this.donationsToGrants);

      for (let i = 0; i < selectedTokens.length; i += 1) {
        tokenSymbol = selectedTokens[i];
        console.log(`Transferring all required ${tokenSymbol} to Gitcoin sync wallet...`);
        const decimals = this.getTokenByName(tokenSymbol).decimals;
        const totalAmount = ethers.utils.parseUnits(String(this.donationsTotal[tokenSymbol]), decimals);

        // Get total amount that needs to be transferred with all fees
        const totalRequiredAmount = await this.getTotalAmountToTransfer(tokenSymbol, totalAmount);
        const transferInfo = {
          dest: this.gitcoinSyncWallet.cachedAddress,
          name: tokenSymbol,
          amount: totalRequiredAmount
        };

        // Get cost of fee for that transfer, and send transfer
        const { fee, amount } = await this.getZkSyncFeeAndAmount(transferInfo);
        const tx = await this.nominalSyncWallet.syncTransfer({
          to: transferInfo.dest,
          token: transferInfo.name,
          // totalRequiredAmount amount includes fee of this transfer, so subtract that now because
          // otherwise we'd be transferring one additional fee
          amount: zksync.utils.closestPackableTransactionAmount(amount.sub(fee)),
          fee
        });

        console.log('  Transfer sent', tx);

        // Wait for it to be committed
        const receipt = await tx.awaitReceipt();

        console.log('  ✅ Got transfer receipt', receipt);
      }

      // Final steps

      this.zkSyncCheckoutFlowStep = 2; // Steps 0 and 1 are skipped here

      // Save contributions to database once transfers to gitcoinSyncWallet are complete
      await this.postToDatabase(this.gitcoinSyncWallet.cachedAddress, '', this.userAddress);

      await this.finishZkSyncTransfersAllFlows();
    },

    /**
     * @notice Step 3 of Flow B. User has no funds in L2, so we deposit directly to their Gitcoin
     * sync wallet, and from the sync wallet we dispatch all transfers without needing to prompt
     * the user. Any excess funds are transferred to the user's ordinary L1 account
     */
    async sendZkSyncDonationFlowB() {
      try {
      // Setup -------------------------------------------------------------------------------------
        const ethAmount = this.zkSyncDonationInputsEthAmount; // amount of ETH being donated
        const depositRecipient = this.gitcoinSyncWallet.address(); // address of deposit recipient
        const BigNumber = ethers.BigNumber;

        // Deposit funds ---------------------------------------------------------------------------
        // Setup overrides
        let overrides = {
          gasLimit: BigNumber.from(String(this.zkSyncDonationInputsGasLimit)),
          value: ethers.constants.Zero
        };

        if (BigNumber.from(ethAmount).gt('0')) {
          // Specify how much ETH to send with transaction
          const ethToDonate = await this.getTotalAmountToTransfer('ETH', ethAmount);
          const extra = this.zkSyncAdditionalDeposits.filter((x) => x.tokenSymbol === 'ETH')[0];

          if (!extra) {
            overrides.value = ethToDonate;
          } else {
            const additionalAmount = ethers.utils.parseUnits(String(extra.amount), 18);

            overrides.value = ethToDonate.add(additionalAmount);
          }
        }

        const selectedTokens = Object.keys(this.donationsToGrants);
        let depositTx;

        if (this.depositContractToUse === batchZkSyncDepositContractAddress) {
          // If batch deposit ---------------------------------------------------------
          // Deposit mix of tokens
          console.log('Generating deposit payload...');
          const deposits = []; // array of arrays, passed into batckZkSyncDepositContract.deposit(...)

          // Handle ETH
          if (BigNumber.from(ethAmount).gt('0'))
            deposits.push([ ETH_ADDRESS, overrides.value ]);

          // Handle tokens
          const summaryData = this.zkSyncSummaryData();

          if (summaryData.length > 0) {
            for (let i = 0; i < summaryData.length; i += 1) {
              const tokenDonation = summaryData[i];
              const tokenAddress = tokenDonation.contract._address;
              const tokenName = tokenDonation.tokenName;
              const tokenAmount = await this.getTotalAmountToTransfer(tokenName, tokenDonation.allowance);
              const extra = this.zkSyncAdditionalDeposits.filter((x) => x.tokenSymbol === tokenName)[0];
              let totalAmount;

              if (!extra) {
                totalAmount = tokenAmount;
              } else {
                const decimals = this.getTokenByName(tokenName).decimals;
                const additionalAmount = ethers.utils.parseUnits(String(extra.amount), decimals);

                totalAmount = tokenAmount.add(additionalAmount);
              }

              deposits.push([ tokenAddress, totalAmount ]);
            }
          }

          if (deposits.length === 0) {
            throw new Error('There are no deposits to be made');
          }
          console.log('✅ Deposit payload ready');
          console.log('    _deposits array', deposits);
          console.log('    overrides', overrides);

          // Get contract instance
          const batckZkSyncDepositContract = new ethers.Contract(
            batchZkSyncDepositContractAddress,
            batchZkSyncDepositContractAbi,
            this.signer
          );

          // Verify user has sufficient balances now that we account for transaction fees
          // Check tokens
          for (let i = 0; i < deposits.length; i += 1) {
            const tokenAddress = deposits[i][0];

            if (tokenAddress === ETH_ADDRESS) {
              // Skip ETH because we check it later
              continue;
            }

            const tokenContract = new web3.eth.Contract(token_abi, tokenAddress);
            const requiredAmount = deposits[i][1];
            const userTokenBalance = await tokenContract.methods.balanceOf(this.userAddress).call({from: this.userAddress});

            if (BigNumber.from(userTokenBalance).lt(BigNumber.from(requiredAmount))) {
              this.zkSyncCheckoutStep1Status = 'not-started';
              this.zkSyncCheckoutStep2Status = 'not-started';
              this.zkSyncCheckoutStep3Status = 'not-started';
              this.showZkSyncModal = false;
              throw new Error(`Insufficient ${tokenSymbol} balance to complete checkout`, 'error');
            }
          }

          // Check ETH
          const userEthBalance = await web3.eth.getBalance(this.userAddress);

          if (BigNumber.from(userEthBalance).lt(BigNumber.from(overrides.value))) {
            this.zkSyncCheckoutStep1Status = 'not-started';
            this.zkSyncCheckoutStep2Status = 'not-started';
            this.zkSyncCheckoutStep3Status = 'not-started';
            this.showZkSyncModal = false;
            throw new Error('Insufficient ETH balance to complete checkout');
          }


          // Send transaction
          console.log('Waiting for user to send deposit transaction...');
          indicateMetamaskPopup();
          depositTx = await batckZkSyncDepositContract.deposit(depositRecipient, deposits, overrides);

        } else if (selectedTokens.length === 1 && selectedTokens[0] === 'ETH') {
          // If only ETH deposit ---------------------------------------------------
          // Check ETH balance
          const userEthBalance = await web3.eth.getBalance(this.userAddress);

          if (BigNumber.from(userEthBalance).lt(BigNumber.from(overrides.value))) {
            this.zkSyncCheckoutStep1Status = 'not-started';
            this.zkSyncCheckoutStep2Status = 'not-started';
            this.zkSyncCheckoutStep3Status = 'not-started';
            this.showZkSyncModal = false;
            throw new Error('Insufficient ETH balance to complete checkout');
          }

          // Deposit ETH
          const zkSyncContract = new ethers.Contract(this.depositContractToUse, zkSyncContractAbi, this.signer);

          console.log('Waiting for user to send deposit transaction...');
          indicateMetamaskPopup();
          depositTx = await zkSyncContract.depositETH(depositRecipient, overrides);

        } else if (selectedTokens.length === 1 && selectedTokens[0] !== 'ETH') {
          // If only token deposit ---------------------------------------------------
          // Deposit tokens
          const zkSyncContract = new ethers.Contract(this.depositContractToUse, zkSyncContractAbi, this.signer);
          const tokenDonation = this.zkSyncSummaryData()[0];
          const tokenAmount = await this.getTotalAmountToTransfer(tokenDonation.tokenName, tokenDonation.allowance);

          const tokenContract = new web3.eth.Contract(token_abi, tokenDonation.contract._address);
          const userTokenBalance = await tokenContract.methods.balanceOf(this.userAddress).call({from: this.userAddress});

          const extra = this.zkSyncAdditionalDeposits.filter((x) => x.tokenSymbol === tokenDonation.tokenName)[0];
          let totalAmount;

          if (!extra) {
            totalAmount = tokenAmount;
          } else {
            const decimals = this.getTokenByName(tokenDonation.tokenName).decimals;
            const additionalAmount = ethers.utils.parseUnits(String(extra.amount), decimals);

            totalAmount = tokenAmount.add(additionalAmount);
          }

          if (BigNumber.from(userTokenBalance).lt(BigNumber.from(totalAmount))) {
            this.zkSyncCheckoutStep1Status = 'not-started';
            this.zkSyncCheckoutStep2Status = 'not-started';
            this.zkSyncCheckoutStep3Status = 'not-started';
            this.showZkSyncModal = false;
            throw new Error(`Insufficient ${tokenDonation.tokenName} balance to complete checkout`, 'error');
          }

          console.log('Waiting for user to send deposit transaction...');
          indicateMetamaskPopup();
          depositTx = await zkSyncContract.depositERC20(tokenDonation.contract._address, totalAmount, depositRecipient, overrides);

        } else {
          throw new Error('Something went wrong');
        }

        indicateMetamaskPopup(true);
        this.zkSyncDepositTxHash = depositTx.hash;
        // Save contributions to database
        await this.postToDatabase(this.zkSyncDepositTxHash, this.depositContractToUse, this.userAddress);
        // Assume checkout will not be completed
        await this.setInterruptStatus(this.zkSyncDepositTxHash, this.userAddress);
        console.log('✅ Deposit transaction sent', depositTx);
        console.log('Waiting for deposit transaction to be mined...');

        // Wait for first confirmation
        const receipt = await depositTx.wait();

        // Final steps
        console.log('✅ Deposit transaction mined', receipt);
        await this.finishZkSyncStep3(receipt);
      } catch (e) {
        this.handleError(e);
      }
    },

    /**
     * @notice Step 3, alternate: Used if zkSync checkout is interrupted
     */
    async resumeZkSyncDonation() {
      // By this point, the deposit transaction hash will be known
      this.zkSyncCheckoutStep3Status = 'pending';

      // Check for updated transaction hash
      this.zkSyncDepositTxHash = await this.getReplacedTx(this.zkSyncDepositTxHash);

      // Get transaction receipt
      let receipt = await this.ethersProvider.getTransactionReceipt(this.zkSyncDepositTxHash);

      if (!receipt) {
        //  Transaction is pending, wait for it and resume normal flow afterwards
        receipt = await this.ethersProvider.waitForTransaction(this.zkSyncDepositTxHash);
        console.log('✅ Deposit transaction mined', receipt);
      }

      await this.finishZkSyncStep3(receipt);
    },

    /**
     * @notice Executes final shared Flow B steps between standard flow and interrupt flow
     * @param receipt receipt from the deposit transaction
     */
    async finishZkSyncStep3(receipt) {
      // Track number of confirmations live in UI
      this.updateConfirmationsInUI();

      // Wait for deposit to be committed
      // Parse logs in receipt so we can get priority request IDs from the events
      const serialId = this.getDepositSerialId(receipt);

      // Wait for that ID to be acknowledged by the zkSync network
      await this.waitForSerialIdCommitment(serialId);

      // Final steps
      await this.finishZkSyncTransfersAllFlows();
    },

    /**
     * @notice Final shared steps between Flow A and Flow B
     */
    async finishZkSyncTransfersAllFlows() {
      // Unlock deterministic wallet's zkSync account
      await this.checkAndRegisterSigningKey(this.gitcoinSyncWallet);

      // Fetch the expected nonce from the network. We cannot assume it's zero because this may
      // not be the user's first checkout
      let nonce = await this.getGitcoinSyncWalletNonce();


      // Generate signatures
      const donationSignatures = await this.generateTransferSignatures(nonce);

      // Dispatch the transfers
      await this.dispatchSignedTransfers(donationSignatures);
      console.log('✅✅✅ Checkout complete!');

      // Final processing
      await this.setInterruptStatus(null, this.userAddress);
      await this.finalizeCheckout();
    },


    // =============================================================================================
    // ==================================== END ZKSYNC METHODS =====================================
    // =============================================================================================

    // ================== Start collection logic ==================
    createCollection: async function() {
      const csrfmiddlewaretoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
      const cart = CartData.loadCart();
      const grantIds = cart.map(grant => grant.grant_id);
      let response;

      const body = {
        collectionTitle: this.collectionTitle,
        collectionDescription: this.collectionDescription,
        grants: grantIds
      };

      if (this.selectedCollection) {
        body['collection'] = this.selectedCollection;
      }

      try {

        response = await fetchData('/grants/v1/api/collections/new', 'POST', body, {'X-CSRFToken': csrfmiddlewaretoken});
        const redirect = `/grants/collections?collection_id=${response.collection.id}`;

        _alert('Congratulations, your new collection was created successfully!', 'success');
        this.cleanCollectionModal();
        this.showCreateCollection = false;

        window.location = redirect;

      } catch (e) {
        _alert(e.msg, 'error');
      }
    },
    cleanCollectionModal: function() {
      this.collectionTitle = '';
      this.collectionDescription = '';
    }
    // ================== End collection logic ==================
  },

  watch: {
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
            const matchAmount = await this.predictCLRMatch(grant, amount);

            this.grantData[i].grant_donation_clr_match = matchAmount ? matchAmount.toFixed(2) : 0;
          }
        }

        // Update suggested checkout option
        if (this.zkSyncWalletState) {
          await this.checkZkSyncBalances();
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
    this.fetchBrightIDStatus();
    const urlParams = new URLSearchParams(window.location.search);

    if (urlParams.has('verify') && urlParams.get('verify').toLowerCase() === 'true') {
      this.showSMSValidationModal();
    }

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

    // Read array of grants in cart from localStorage
    this.grantData = CartData.loadCart();
    // Initialize array of empty comments
    this.comments = this.grantData.map(grant => undefined);

    // Get list of all grant IDs and unique tokens in the cart
    const grantIds = this.grantData.map(grant => grant.grant_id);

    // Fetch updated CLR curves for all grants
    const url = `${window.location.origin}/grants/v1/api/clr?pks=${grantIds.join(',')}`;
    const response = await fetch(url);
    const clrCurves = (await response.json()).grants;

    // Update CLR curves
    this.grantData.forEach((grant, index) => {
      // Find the clrCurves entry with the same grant ID as this grant
      const clrIndex = clrCurves.findIndex(item => {
        return Number(item.pk) === Number(grant.grant_id);
      });

      // Replace the CLR prediction curve
      this.grantData[index].grant_clr_prediction_curve = clrCurves[clrIndex].clr_prediction_curve;
    });

    // Wait until we can load token list
    let elapsedTime = 0;
    let delay = 50; // 50 ms debounce

    while (!this.tokenList) {
      try {
        // Default to mainnet if nothing found after 5s
        var network = elapsedTime >= 5000 ? 'mainnet' : document.web3network;

        if (typeof network != 'undefined') {
          this.tokenList = tokens(network);
        }
      } catch (err) {}
      elapsedTime += delay;
      await this.sleep(delay);
    }
    // Support responsive design
    window.addEventListener('resize', this.onResize);

    // If user started deposit tx (final step of zkSync checkout), warn them before closing or
    // reloading page. We do not save the signatures here -- we do that immediately after they
    // are generated -- to increase reliability. This is because the beforeunload may sometimes
    // be ignored by browsers, e.g. if users have not interacted with the page
    window.addEventListener('beforeunload', (e) => {
      if (
        this.zkSyncCheckoutStep3Status === 'pending' &&
        this.zkSyncCheckoutStep3Status !== 'complete'
      ) {
        // This shows a generic message staying "Leave site? Changes you made may not be saved". This
        // cannot be changed, as "the ability to do this was removed in Chrome 51. It is widely
        // considered a security issue, and most vendors have removed support."
        // source: https://stackoverflow.com/questions/40570164/how-to-customize-the-message-changes-you-made-may-not-be-saved-for-window-onb
        e.preventDefault();
        e.returnValue = '';
      }
    });

    // Assume insufficient zkSync balance to start
    this.hasSufficientZkSyncBalance = false;

    // Show user cart

    // Check zkSync balance. Used to find which checkout option is cheaper
    this.isLoading = false;
    window.addEventListener('dataWalletReady', async(e) => {
      try {
        await needWalletConnection();

        // Force re-render so computed properties are updated (some are dependent on
        // document.web3network, and Vue cannot watch document.web3network for an update)
        this.selectedNetwork = document.web3network;

        // Setup zkSync and check balances
        this.userAddress = (await web3.eth.getAccounts())[0];
        await this.setupZkSync();
        await this.checkZkSyncBalances();

        // See if user was previously interrupted during checkout
        await this.checkInterruptStatus();
        if (this.zkSyncWasInterrupted) {
          this.showZkSyncModal = true;
        }
      } catch (e) {
        console.error(e);
      }

    }, false);

    const collections_response = await fetchData('/grants/v1/api/collections');

    this.collections = collections_response.collections;
    // Cart is now ready
    // this.isLoading = false;
  },

  beforeDestroy() {
    window.removeEventListener('resize', this.onResize);
  }
});

var update_cart_title = function() {
  var num_grants = JSON.parse(localStorage.getItem('grants_cart')).length;
  let new_title = 'Grants Cart (' + num_grants + ') | Gitcoin';

  $('title').text(new_title);
};

$(document).ready(function() {
  $(document).on('keyup', 'input[name=telephone]', function(e) {
    var number = $(this).val();

    if (number[0] != '+') {
      number = '+' + number;
      $(this).val(number);
    }
  });


  $(document).on('click', '#verify_offline', function(e) {
    $(this).remove();
    $('#verify_offline_target').css('display', 'block');
  });

  update_cart_title();
});

if (document.getElementById('gc-grants-cart')) {

  const app = new Vue({
    delimiters: [ '[[', ']]' ],
    el: '#gc-grants-cart',
    data: {
      grantHeaders,
      grantData
    }
  });

  if (document.contxt.github_handle && !document.verified && localStorage.getItem('dismiss-sms-validation') !== 'true') {
    app.$refs.cart.showSMSValidationModal();
  }
}
