// TODO: add these assets somewhere
/*
<script
  src="https://cdn.jsdelivr.net/npm/algosdk@1.13.0/dist/browser/algosdk.min.js"
  integrity="sha384-3IaxTgktbWGiqPkr5oZQMM4H99ziYzoEUb6sznk03coGR2Cdf1r0I1GWPUL37iu8"
  crossorigin="anonymous"
></script>
<script src="https://temptemp3.github.io/dist/all.js" integrity="sha384-sOpwfoIDOqHhOe9+9CULn5hJ/bTRMXJyBxfgYeMwe45Mg5eLXqMqrKiH2yQkb/RM" crossorigin="anonymous"></script>
*/
const initAlgorandConnectionAlgoSigner = async(grant, vm) => {
  // 1. check if AlgoSigner is available
  if (!AlgoSigner) {
    _alert({ message: 'Please download or enable AlgoSigner extension' }, 'danger');
    return;
  }

  const NETWORK = 'TestNet';
  //const NETWORK = 'MainNet';

  // step2: get connected accounts
  AlgoSigner.connect().then(async() => {
    const addresses = await AlgoSigner.accounts({ ledger: NETWORK });
    console.log({addresses});
    if (addresses.length == 0) {
      _alert({ message: 'No wallet addresses detected on AlgoSigner extension' }, 'danger');
      return;
    }
    vm.updatePaymentStatus(grant.grant_id, 'waiting-on-user-input', null, {addresses});
  });
	
}
const initAlgorandConnectionMyAlgo = async(grant, vm) => {
  // 1. check if wallet is available
  if(!MyAlgoConnect) {
    _alert({ message: 'Please download or enable AlgoSigner extension' }, 'danger');
    return
  }
  // 1. get connected accounts
  const myAlgoConnect = new MyAlgoConnect();
  const accountsSharedByUser = await myAlgoConnect.connect();
  const addresses = accountsSharedByUser.map(el => el.address)
  console.log(accountsSharedByUser)
  console.log(addresses)
  vm.updatePaymentStatus(grant.grant_id, 'waiting-on-user-input', null, {addresses});
}
const initAlgorandConnectionWalletConnect = async(grant, vm) => {
  // 1. check if wallet is available
  if(!WalletConnect) {
    _alert({ message: 'Please download or enable AlgoSigner extension' }, 'danger');
    return
  }
  // 1. get connected accounts
  const connector = new WalletConnect.default({
    bridge: "https://bridge.walletconnect.org",
    qrcodeModal:  WalletConnectQRCodeModal.default
  });
  // Check if connection is already established
  if (!connector.connected) {
    // create new session
    connector.createSession();
  }

  // Subscribe to connection events
  connector.on("connect", (error, payload) => {
    if (error) {
      throw error;
    }
    // Get provided accounts and chainId
    const { accounts, chainId } = payload.params[0];
    vm.updatePaymentStatus(grant.grant_id, 'waiting-on-user-input', null, {addresses});
  });

  connector.on("session_update", (error, payload) => {
    if (error) {
      throw error;
    }

    // Get updated accounts and chainId
    const { accounts, chainId } = payload.params[0];
    vm.updatePaymentStatus(grant.grant_id, 'waiting-on-user-input', null, {addresses});
  });

  connector.on("disconnect", (error, payload) => {
    if (error) {
      throw error;
    }
    // Delete connector
  });
  /*
  const addresses = accountsSharedByUser.map(el => el.address)
  console.log(accountsSharedByUser)
  console.log(addresses)
  vm.updatePaymentStatus(grant.grant_id, 'waiting-on-user-input', null, {addresses});
  */
}

/*
 * initAlgorandConnection
 * returns connect wallet addresses to update payment status
 * for grant through vm
 */
const initAlgorandConnection = async(grant, vm) => {
  switch(localStorage.getItem("algowallet") || "AlgoSigner") {
    default:
    case 'AlgoSigner':
      initAlgorandConnectionAlgoSigner(grant, vm)
      break
    case 'MyAlgoConnect':
      initAlgorandConnectionMyAlgo(grant, vm);
      break
    case 'WalletConnect':
      initAlgorandConnectionWalletConnect(grant, vm);
      break
  }
};
const contributeWithAlgorandExtensionAlgoSigner = async(grant, vm, from_address) => {
  const token_name = grant.grant_donation_currency;
  const amount = grant.grant_donation_amount;
  const to_address = grant.algorand_payout_address;
  const token = vm.getTokenByName(token_name);

  const NETWORK = 'TestNet';
  //const NETWORK = 'MainNet';

  try {
    AlgoSigner.connect().then(async() => {
      
      // step3: check if enough balance is present
      const balance = await AlgoSigner.algod({
        ledger: NETWORK,
        path: `/v2/accounts/${from_address}`
      });
      console.log(balance)

      if (token_name == 'ALGO') {
        // ALGO token
        if (Number(balance.amount) <= amount * 10 ** token.decimals) {
          _alert({ message: `Insufficent balance in address ${from_address}` }, 'danger');
          return;
        }
      } else {
        // ALGO assets
        let is_asset_present = false;

        if (balance.assets && balance.assets.length > 0) {
          balance.assets.map(asset => {
            if (asset['asset-id'] == token.addr)
              is_asset_present = true;
          });
        }

        if (!is_asset_present) {
          _alert({ message: `Asset ${token_name} is not present in ${from_address}` }, 'danger');
          return;
        }

        let has_enough_asset_balance = false;

        balance.assets.map(asset => {
          if (asset['asset-id'] == token.addr && asset['amount'] <= amount * 10 ** token.decimals)
            has_enough_asset_balance = true;
        });

        if (has_enough_asset_balance) {
          _alert({ message: `Insufficent balance in address ${from_address}` }, 'danger');
          return;
        }
      }
      
      // step4: set modal to waiting state
      vm.updatePaymentStatus(grant.grant_id, 'waiting');

      // step5: get txnParams

      const txParams = await AlgoSigner.algod({
        ledger: NETWORK,
        path: '/v2/transactions/params'
      });

      let txn;
      // step5: sign transaction

      if (token_name == 'ALGO') {
        // ALGO token
        txn = {
          from: from_address.toUpperCase(),
          to: to_address.toUpperCase(),
          fee: txParams['fee'],
          type: 'pay',
          amount: amount * 10 ** token.decimals,
          firstRound: txParams['last-round'],
          lastRound: txParams['last-round'] + 1000,
          genesisID: txParams['genesis-id'],
          genesisHash: txParams['genesis-hash'],
          note: 'contributing to gitcoin grant'
        };
      } else {
        // ALGO assets
        txn = {
          from: from_address.toUpperCase(),
          to: to_address.toUpperCase(),
          assetIndex: Number(token.addr),
          note: 'contributing to gitcoin grant',
          amount: amount * 10 ** token.decimals,
          type: 'axfer',
          fee: txParams['min-fee'],
          firstRound: txParams['last-round'],
          lastRound: txParams['last-round'] + 1000,
          genesisID: txParams['genesis-id'],
          genesisHash: txParams['genesis-hash']
        };
      }

      AlgoSigner.sign(txn).then(signedTx => {
        // step7: broadcast txn
        AlgoSigner.send({
          ledger: NETWORK,
          tx: signedTx.blob
        }).then(tx => {
          callback(null, from_address, tx.txId);
        }).catch((e) => {
          console.log(e);
          _alert({ message: 'Unable to broadcast transaction. Please try again' }, 'danger');
          vm.updatePaymentStatus(grant.grant_id, 'failed');
          return;
        });

      }).catch(e => {
        console.log(e);
        _alert({ message: 'Unable to sign transaction. Please try again' }, 'danger');
        vm.updatePaymentStatus(grant.grant_id, 'failed');
        return;
      });

    }).catch(e => {
      console.log(e);
      _alert({ message: 'Please allow Gitcoin to connect to AlgoSigner extension' }, 'danger');
      vm.updatePaymentStatus(grant.grant_id, 'failed');
      return;
    });
  } catch (e) {
    callback(err);
    return;
  }
  

  function callback(error, from_address, txn) {
    if (error) {
      vm.updatePaymentStatus(grant.grant_id, 'failed');
      _alert({ message: gettext('Unable to contribute to grant due to ' + error) }, 'danger');
      console.log(error);
    } else {

      const payload = {
        'contributions': [{
          'grant_id': grant.grant_id,
          'contributor_address': from_address,
          'tx_id': txn,
          'token_symbol': grant.grant_donation_currency,
          'tenant': 'ALGORAND',
          'amount_per_period': grant.grant_donation_amount
        }]
      };

      const apiUrlBounty = 'v1/api/contribute';

      fetchData(apiUrlBounty, 'POST', JSON.stringify(payload)).then(response => {

        if (200 <= response.status && response.status <= 204) {
          console.log('success', response);
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

          vm.updatePaymentStatus(grant.grant_id, 'done', txn);

        } else {
          vm.updatePaymentStatus(grant.grant_id, 'failed');
          _alert('Unable to contribute to grant. Please try again later', 'danger');
          console.error(`error: grant contribution failed with status: ${response.status} and message: ${response.message}`);
        }
      }).catch(function(error) {
        vm.updatePaymentStatus(grant.grant_id, 'failed');
        _alert('Unable to contribute to grant. Please try again later', 'danger');
        console.log(error);
      });
    }
  }
};
const contributeWithAlgorandExtensionMyAlgo = async(
  grant = {},
  vm = {},
  from_address = "QLLLYBITHLFUX3BWLPAXD23SBMLUYHGCG6NOPOBWY7KQHBLHLC3JC7LVBA"
) => {

  //const token_name = grant.grant_donation_currency;
  //const amount = grant.grant_donation_amount;
  //const to_address = grant.algorand_payout_address;
  //const token = vm.getTokenByName(token_name);

  // ALGO
  const token_name = "ALGO"
  const amount = 1
  const to_address = "LOXKESTUNTAAYX53P3VT3TWMFO2ZDSPORZGMZNAITSLUXGSG4N4UYCYQIE"
  const token = { decimals: 6 }
  vm.updatePaymentStatus = () => {}

  const NETWORK = 'TestNet';
  //const NETWORK = 'MainNet';

  try {

    const myAlgoConnect = new MyAlgoConnect();
    myAlgoConnect.connect().then(async() => {
      
      // step3: check if enough balance is present
      const balance = await AlgoSigner.algod({
        ledger: NETWORK,
        path: `/v2/accounts/${from_address}`
      });
      console.log(balance)

      if (token_name == 'ALGO') {
        // ALGO token
        if (Number(balance.amount) <= amount * 10 ** token.decimals) {
          _alert({ message: `Insufficent balance in address ${from_address}` }, 'danger');
          return;
        }
      } else {
        // ALGO assets
        let is_asset_present = false;

        if (balance.assets && balance.assets.length > 0) {
          balance.assets.map(asset => {
            if (asset['asset-id'] == token.addr)
              is_asset_present = true;
          });
        }

        if (!is_asset_present) {
          _alert({ message: `Asset ${token_name} is not present in ${from_address}` }, 'danger');
          return;
        }

        let has_enough_asset_balance = false;

        balance.assets.map(asset => {
          if (asset['asset-id'] == token.addr && asset['amount'] <= amount * 10 ** token.decimals)
            has_enough_asset_balance = true;
        });

        if (has_enough_asset_balance) {
          _alert({ message: `Insufficent balance in address ${from_address}` }, 'danger');
          return;
        }
      }
      
      // step4: set modal to waiting state
      vm.updatePaymentStatus(grant.grant_id, 'waiting');

      // step5: get txnParams
      const algodClient = new algosdk.Algodv2("",'https://api.testnet.algoexplorer.io', '');
      const params = await algodClient.getTransactionParams().do();
      var enc = new TextEncoder(); // always utf-8

      let txn;
      // step5: sign transaction

      if (token_name == 'ALGO') {
        // ALGO token
        txn = algosdk.makePaymentTxnWithSuggestedParamsFromObject({
    		suggestedParams: {
        		...params,
    	},
    	from: from_address.toUpperCase(),
    	to: to_address.toUpperCase(),
    	amount: amount * 10 ** token.decimals,
    	note: enc.encode('contributing to gitcoin grant')
	});
      } else {
        // ALGO assets
        // TODO
        txn = {
          from: from_address.toUpperCase(),
          to: to_address.toUpperCase(),
          assetIndex: Number(token.addr),
          note: 'contributing to gitcoin grant',
          amount: amount * 10 ** token.decimals,
          type: 'axfer',
          fee: txParams['min-fee'],
          firstRound: txParams['last-round'],
          lastRound: txParams['last-round'] + 1000,
          genesisID: txParams['genesis-id'],
          genesisHash: txParams['genesis-hash']
        };
      }
      myAlgoConnect.signTransaction(txn.toByte())
      .then(stx => {
        // step7: broadcast txn
        algodClient.sendRawTransaction(stx.blob).do() // ***
	.then(tx => {
          callback(null, from_address, tx.txId);
        }).catch((e) => {
          console.log(e);
          _alert({ message: 'Unable to broadcast transaction. Please try again' }, 'danger');
          vm.updatePaymentStatus(grant.grant_id, 'failed');
          return;
        });

      }).catch(e => {
        console.log(e);
        _alert({ message: 'Unable to sign transaction. Please try again' }, 'danger');
        vm.updatePaymentStatus(grant.grant_id, 'failed');
        return;
      });

    }).catch(e => {
      console.log(e);
      _alert({ message: 'Please allow Gitcoin to connect to AlgoSigner extension' }, 'danger');
      vm.updatePaymentStatus(grant.grant_id, 'failed');
      return;
    });
  } catch (e) {
    callback(err);
    return;
  }
  

  function callback(error, from_address, txn) {
    if (error) {
      vm.updatePaymentStatus(grant.grant_id, 'failed');
      _alert({ message: gettext('Unable to contribute to grant due to ' + error) }, 'danger');
      console.log(error);
    } else {
      const payload = {
        'contributions': [{
          'grant_id': grant.grant_id,
          'contributor_address': from_address,
          'tx_id': txn,
          'token_symbol': grant.grant_donation_currency,
          'tenant': 'ALGORAND',
          'amount_per_period': grant.grant_donation_amount
        }]
      };

      const apiUrlBounty = 'v1/api/contribute';

      fetchData(apiUrlBounty, 'POST', JSON.stringify(payload)).then(response => {

        if (200 <= response.status && response.status <= 204) {
          console.log('success', response);
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

          vm.updatePaymentStatus(grant.grant_id, 'done', txn);

        } else {
          vm.updatePaymentStatus(grant.grant_id, 'failed');
          _alert('Unable to contribute to grant. Please try again later', 'danger');
          console.error(`error: grant contribution failed with status: ${response.status} and message: ${response.message}`);
        }
      }).catch(function(error) {
        vm.updatePaymentStatus(grant.grant_id, 'failed');
        _alert('Unable to contribute to grant. Please try again later', 'danger');
        console.log(error);
      });
    }
  }
};
const contributeWithAlgorandExtensionWalletConnect = async(
  grant = {},
  vm = {},
  from_address = "7UBGYVIHJKBIDSVZABRZSGAMN55HZSBX4MK3VBCHVM6F7OIWSGEN3Z75L4"
) => {

  //const token_name = grant.grant_donation_currency;
  //const amount = grant.grant_donation_amount;
  //const to_address = grant.algorand_payout_address;
  //const token = vm.getTokenByName(token_name);

  // ALGO
  const token_name = "ALGO"
  const amount = 1
  const to_address = "LOXKESTUNTAAYX53P3VT3TWMFO2ZDSPORZGMZNAITSLUXGSG4N4UYCYQIE"
  const token = { decimals: 6 }
  vm.updatePaymentStatus = () => {}

  const NETWORK = 'TestNet';
  //const NETWORK = 'MainNet';

  try {
    const connector = new WalletConnect.default({
    	bridge: "https://bridge.walletconnect.org",
    	qrcodeModal:  WalletConnectQRCodeModal.default
    });
    console.log(connector)

    const myAlgoConnect = new MyAlgoConnect();
    myAlgoConnect.connect()
	.then(async() => {
      
      // step3: check if enough balance is present
      const balance = await AlgoSigner.algod({
        ledger: NETWORK,
        path: `/v2/accounts/${from_address}`
      });
      console.log(balance)

      if (token_name == 'ALGO') {
        // ALGO token
        if (Number(balance.amount) <= amount * 10 ** token.decimals) {
          _alert({ message: `Insufficent balance in address ${from_address}` }, 'danger');
          return;
        }
      } else {
        // ALGO assets
        let is_asset_present = false;

        if (balance.assets && balance.assets.length > 0) {
          balance.assets.map(asset => {
            if (asset['asset-id'] == token.addr)
              is_asset_present = true;
          });
        }

        if (!is_asset_present) {
          _alert({ message: `Asset ${token_name} is not present in ${from_address}` }, 'danger');
          return;
        }

        let has_enough_asset_balance = false;

        balance.assets.map(asset => {
          if (asset['asset-id'] == token.addr && asset['amount'] <= amount * 10 ** token.decimals)
            has_enough_asset_balance = true;
        });

        if (has_enough_asset_balance) {
          _alert({ message: `Insufficent balance in address ${from_address}` }, 'danger');
          return;
        }
      }
      
      // step4: set modal to waiting state
      vm.updatePaymentStatus(grant.grant_id, 'waiting');

      // step5: get txnParams
      const algodClient = new algosdk.Algodv2("",'https://api.testnet.algoexplorer.io', '');
      const params = await algodClient.getTransactionParams().do();
      var enc = new TextEncoder(); // always utf-8

      let txn;
      // step5: sign transaction

    if (token_name == 'ALGO') {
      // ALGO token
      txn = algosdk.makePaymentTxnWithSuggestedParamsFromObject({
        suggestedParams: {
          ...params,
        },
        from: from_address.toUpperCase(),
        to: to_address.toUpperCase(),
        amount: amount * 10 ** token.decimals,
        note: enc.encode('contributing to gitcoin grant')
      });
    } else {
        // ALGO assets
	// TODO
        txn = {
          from: from_address.toUpperCase(),
          to: to_address.toUpperCase(),
          assetIndex: Number(token.addr),
          note: 'contributing to gitcoin grant',
          amount: amount * 10 ** token.decimals,
          type: 'axfer',
          fee: txParams['min-fee'],
          firstRound: txParams['last-round'],
          lastRound: txParams['last-round'] + 1000,
          genesisID: txParams['genesis-id'],
          genesisHash: txParams['genesis-hash']
        };
      }
    const txns = [txn]
    const txnsToSign = txns.map(txn => {
      const encodedTxn = btoa(String.fromCharCode.apply(null, 
        //enc.encode(
          algosdk.encodeUnsignedTransaction(txn)
        //)//.toString("base64");
      ));
      console.log({encodedTxn})
      return {
        txn: encodedTxn,
        message: 'Contributing to gitcoin grant'
        // Note: if the transaction does not need to be signed (because it's part of an atomic group
        // that will be signed by another party), specify an empty singers array like so:
        // signers: [],
      };
    });
    const requestParams = [txnsToSign];

    const ToBase64 = function (u8) {
      return btoa(String.fromCharCode.apply(null, u8));
    }

    const FromBase64 = function (str) {
      return atob(str).split('').map(function (c) { return c.charCodeAt(0); });
    }

    const request = formatJsonRpcRequest("algo_signTxn", requestParams);
    const result = await connector.sendCustomRequest(request);
    const decodedResult = result.map(element => {
      console.log(FromBase64(element))
      return element ? new Uint8Array(FromBase64(element)) : null;
    });
    algodClient.sendRawTransaction(decodedResult).do()
      .then(tx => {
        callback(null, from_address, tx.txId);
      }).catch((e) => {
        console.log(e);
        _alert({ message: 'Unable to broadcast transaction. Please try again' }, 'danger');
        vm.updatePaymentStatus(grant.grant_id, 'failed');
        return;
      });

  }).catch(e => {
    console.log(e);
    _alert({ message: 'Unable to sign transaction. Please try again' }, 'danger');
    vm.updatePaymentStatus(grant.grant_id, 'failed');
    return;
  });
  } catch (e) {
    callback(err);
    return;
  }
  function callback(error, from_address, txn) {
    if (error) {
      vm.updatePaymentStatus(grant.grant_id, 'failed');
      _alert({ message: gettext('Unable to contribute to grant due to ' + error) }, 'danger');
      console.log(error);
    } else {
      const payload = {
        'contributions': [{
          'grant_id': grant.grant_id,
          'contributor_address': from_address,
          'tx_id': txn,
          'token_symbol': grant.grant_donation_currency,
          'tenant': 'ALGORAND',
          'amount_per_period': grant.grant_donation_amount
        }]
      };

      const apiUrlBounty = 'v1/api/contribute';

      fetchData(apiUrlBounty, 'POST', JSON.stringify(payload)).then(response => {

        if (200 <= response.status && response.status <= 204) {
          console.log('success', response);
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

          vm.updatePaymentStatus(grant.grant_id, 'done', txn);

        } else {
          vm.updatePaymentStatus(grant.grant_id, 'failed');
          _alert('Unable to contribute to grant. Please try again later', 'danger');
          console.error(`error: grant contribution failed with status: ${response.status} and message: ${response.message}`);
        }
      }).catch(function(error) {
        vm.updatePaymentStatus(grant.grant_id, 'failed');
        _alert('Unable to contribute to grant. Please try again later', 'danger');
        console.log(error);
      });
    }
  }
};
const contributeWithAlgorandExtension = async(grant, vm, from_address) => {
  switch(localStorage.getItem("algowallet") || "AlgoSigner") {
    default:
    case 'AlgoSigner':
      contributeWithAlgorandExtensionAlgoSigner(grant, vm, from_address)
      break
    case 'MyAlgoConnect':
      contributeWithAlgorandExtensionMyAlgo(grant, vm, from_address)
      break
    case 'WalletConnect':
      contributeWithAlgorandExtensionWalletConnect(grant, vm, from_address)
      break
  }
};