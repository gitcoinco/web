const FromBase64 = (str) =>
  atob(str)
    .split('')
    .map((c) => c.charCodeAt(0));

const buildTransactionASA = (token) => ({
  assetIndex: Number(token.addr),
  amount: amount * 10 ** token.decimals,
  type: 'axfer'
});

const buildTransactionALGO = (amount) => ({
  amount: amount * 10 ** 6,
  type: 'pay'
});

const buildTransaction = async(
  grant,
  vm,
  from_address,
  to_address,
  algodClient
) => {
  const token_name = grant.grant_donation_currency;
  const amount = grant.grant_donation_amount;
  const token = vm.getTokenByName(token_name);
  const params = await algodClient.getTransactionParams().do();
  const enc = new TextEncoder(); // always utf-8
  const txn = ((txn) => {
    switch (token_name) {
      case 'ALGO':
        return {
          ...txn,
          ...buildTransactionALGO(amount)
        };
      default:
        return {
          ...txn,
          ...buildTransactionASA(token)
        };
    }
  })({
    from: from_address.toUpperCase(),
    to: to_address.toUpperCase(),
    note: enc.encode('contributing to gitcoin grant'),
    suggestedParams: {
      ...params
    }
  });
  let binaryTx = ((tx) => {
    tx.flatfee = true;
    tx.fee = 1000;
    return tx;
  })(new algosdk.Transaction(txn).toByte());

  return binaryTx;
};

const buildWalletConnectRequest = async(
  grant,
  vm,
  from_address,
  to_address,
  algodClient
) => {
  const token_name = grant.grant_donation_currency;
  const amount = grant.grant_donation_amount;
  const token = vm.getTokenByName(token_name);
  const params = await algodClient.getTransactionParams().do();
  let txn = {
    from: from_address.toUpperCase(),
    to: to_address.toUpperCase(),
    note: new TextEncoder().encode('contributing to gitcoin grant'),
    suggestedParams: {
      ...params
    }
  };

  if (token_name == 'ALGO') {
    // ALGO token
    txn = algosdk.makePaymentTxnWithSuggestedParamsFromObject({
      ...txn,
      from: from_address.toUpperCase(),
      to: to_address.toUpperCase(),
      amount: amount * 10 ** 6
    });
  } else {
    // ALGO assets
    txn = algosdk.makeAssetTransferTxnWithSuggestedParamsFromObject({
      ...txn,
      assetIndex: Number(token.addr),
      amount: amount * 10 ** token.decimals
    });
  }
  const txns = [txn];
  const txnsToSign = txns.map((txn) => {
    const encodedTxn = btoa(
      String.fromCharCode.apply(null, algosdk.encodeUnsignedTransaction(txn))
    );

    return {
      txn: encodedTxn,
      message: 'Contributing to gitcoin grant'
      // Note: if the transaction does not need to be signed (because it's part of an atomic group
      // that will be signed by another party), specify an empty singers array like so:
      // signers: [],
    };
  });
  const requestParams = [txnsToSign];
  const FromBase64 = function(str) {
    return atob(str)
      .split('')
      .map(function(c) {
        return c.charCodeAt(0);
      });
  };
  const request = formatJsonRpcRequest('algo_signTxn', requestParams);

  return request;
};

const checkWalletAlgoBalance = (balance, from_address, amount) => {
  // ALGO token
  if (Number(balance.amount) <= amount * 10 ** 6) {
    _alert(
      { message: `Insufficient balance in address ${from_address}` },
      'danger'
    );
    return false;
  }
  return true;
};

const checkWalletASABalanceAssetPresent = (balance, from_address, token) => {
  let is_asset_present = false;

  if (balance.assets && balance.assets.length > 0) {
    balance.assets.map((asset) => {
      if (asset['asset-id'] == token.addr)
        is_asset_present = true;
    });
  }
  if (!is_asset_present) {
    _alert(
      {
        message: `Asset ${token_name} is not present in ${from_address}`
      },
      'danger'
    );
    return false;
  }
  return true;
};

const checkWalletASABalanceAssetHasEnough = (balance, from_address, token) => {
  let has_enough_asset_balance = false;

  balance.assets.map((asset) => {
    if (
      asset['asset-id'] == token.addr &&
      asset['amount'] <= amount * 10 ** token.decimals
    )
      has_enough_asset_balance = true;
  });
  if (has_enough_asset_balance) {
    _alert(
      { message: `Insufficient balance in address ${from_address}` },
      'danger'
    );
    return false;
  }
  return true;
};

const checkWalletASABalance = (balance, from_address, token) => {
  return (
    checkWalletASABalanceAssetPresent(balance, from_address, token) &&
    checkWalletASABalanceAssetHasEnough(balance, from_address, token)
  );
};

const checkWalletBalance = (grant, vm, from_address, balance) => {
  const token_name = grant.grant_donation_currency;
  const amount = grant.grant_donation_amount;
  const token = vm.getTokenByName(token_name);

  switch (token_name) {
    case 'ALGO':
      return checkWalletAlgoBalance(balance, from_address, amount);
    default:
      return checkWalletASABalance(balance, from_address, token);
  }
};

const getBalance = async(ledger, address) => {
  const balance = await AlgoSigner.algod({
    ledger,
    path: `/v2/accounts/${address}`
  });

  return balance;
};

const initAlgorandConnectionAlgoSigner = async(grant, vm) => {
  // 1. check if AlgoSigner is available
  if (!AlgoSigner) {
    _alert(
      { message: 'Please download or enable AlgoSigner extension' },
      'danger'
    );
    return;
  }
  // const NETWORK = 'TestNet';
  const NETWORK = 'MainNet';

  // step2: get connected accounts
  AlgoSigner.connect().then(async() => {
    const addresses = await AlgoSigner.accounts({ ledger: NETWORK });

    if (addresses.length == 0) {
      _alert(
        { message: 'No wallet addresses detected on AlgoSigner extension' },
        'danger'
      );
      return;
    }
    vm.updatePaymentStatus(grant.grant_id, 'waiting-on-user-input', null, {
      addresses
    });
  });
};
const initAlgorandConnectionMyAlgo = async(grant, vm) => {
  // 1. check if wallet is available
  if (!MyAlgoConnect) {
    _alert({ message: 'Unable to initialize MyAlgo Connect' }, 'danger');
    return;
  }
  // 1. get connected accounts
  let addresses;
  const address = localStorage.getItem('addr');

  if (address) {
    addresses = [{ address }];
  } else {
    const myAlgoConnect = new MyAlgoConnect();
    const accountsSharedByUser = await myAlgoConnect.connect();

    addresses = accountsSharedByUser.map((el) => ({ address: el.address }));
    localStorage.setItem('addr', addresses[0].address);
  }
  vm.updatePaymentStatus(grant.grant_id, 'waiting-on-user-input', null, {
    addresses
  });
  true;
};
const initAlgorandConnectionWalletConnect = async(grant, vm) => {
  // 1. check if wallet is available
  if (!WalletConnect) {
    _alert({ message: 'Unable to initialize WalletConnect' }, 'danger');
    return;
  }
  // 1. get connected accounts
  const connector = new WalletConnect.default({
    bridge: 'https://bridge.walletconnect.org',
    qrcodeModal: WalletConnectQRCodeModal.default
  });

  if (connector.connected) {
    const addresses = connector.accounts.map((el) => ({ address: el }));

    console.log(addresses);
    vm.updatePaymentStatus(grant.grant_id, 'waiting-on-user-input', null, {
      addresses
    });
  }

  // Check if connection is already established
  if (!connector.connected) {
    // create new session
    connector.createSession();
  }

  // Subscribe to connection events
  connector.on('connect', (error, payload) => {
    if (error) {
      throw error;
    }
    // Get provided accounts and chainId
    const { accounts /* , chainId */ } = payload.params[0]; // [1,2,...] 4160
    const addresses = accounts.map((el) => ({ address: el }));

    vm.updatePaymentStatus(grant.grant_id, 'waiting-on-user-input', null, {
      addresses
    });
  });

  connector.on('session_update', (error, payload) => {
    if (error) {
      throw error;
    }

    // Get updated accounts and chainId
    const { accounts /* , chainId */ } = payload.params[0]; // [1,2,...] 4160
    const addresses = accounts.map((el) => ({ address: el }));

    vm.updatePaymentStatus(grant.grant_id, 'waiting-on-user-input', null, {
      addresses
    });
  });

  connector.on('disconnect', (error, payload) => {
    if (error) {
      throw error;
    }
    // Delete connector
  });
};

/*
 * initAlgorandConnection
 * returns connect wallet addresses to update payment status
 * for grant through vm
 */
const initAlgorandConnection = async(grant, vm) => {
  let callback;

  switch (localStorage.getItem('algowallet') || 'AlgoSigner') {
    default:
    case 'AlgoSigner':
      callback = initAlgorandConnectionAlgoSigner;
      break;
    case 'MyAlgoConnect':
      callback = initAlgorandConnectionMyAlgo;
      break;
    case 'WalletConnect':
      callback = initAlgorandConnectionWalletConnect;
      break;
  }
  callback(grant, vm);
};
const contributeWithAlgorandExtensionAlgoSigner = async(
  grant,
  vm,
  from_address,
  to_address
) => {
  // const NETWORK = 'TestNet';
  const NETWORK = 'MainNet';

  try {
    AlgoSigner.connect()
      .then(async() => {
        // step3: check if enough balance is present
        const balance = await getBalance(NETWORK, from_address);

        if (!checkWalletBalance(grant, vm, from_address, balance)) {
          return;
        }

        // step4: set modal to waiting state
        vm.updatePaymentStatus(grant.grant_id, 'waiting');

        // step5: get txnParams

        console.log('Setting up params ...');

        const algodClient = new algosdk.Algodv2(
          '',
          'https://node.algoexplorerapi.io',
          ''
        );

        const binaryTx = await buildTransaction(
          grant,
          vm,
          from_address,
          to_address,
          algodClient
        );

        let base64Tx = AlgoSigner.encoding.msgpackToBase64(binaryTx);

        AlgoSigner.signTxn([{ txn: base64Tx }])
          .then((signedTxs) => {
            let binariySignedTx = AlgoSigner.encoding.base64ToMsgpack(
              signedTxs[0].blob
            );
            // step7: broadcast txn

            algodClient
              .sendRawTransaction(binariySignedTx)
              .do()
              .then((tx) => {
                contributeWithAlgorandExtensionCallback(
                  null,
                  tx.txId,
                  grant,
                  vm,
                  from_address
                );
              })
              .catch((e) => {
                console.log(e);
                _alert(
                  {
                    message:
                      'Unable to broadcast transaction. Please try again'
                  },
                  'danger'
                );
                vm.updatePaymentStatus(grant.grant_id, 'failed');
                return;
              });
          })
          .catch((e) => {
            console.log(e);
            _alert(
              { message: 'Unable to sign transaction. Please try again' },
              'danger'
            );
            vm.updatePaymentStatus(grant.grant_id, 'failed');
            return;
          });
      })
      .catch((e) => {
        console.log(e);
        _alert(
          {
            message: 'Please allow Gitcoin to connect to AlgoSigner extension'
          },
          'danger'
        );
        vm.updatePaymentStatus(grant.grant_id, 'failed');
        return;
      });
  } catch (err) {
    contributeWithAlgorandExtensionCallback(err);
    return;
  }
};
const contributeWithAlgorandExtensionMyAlgo = async(
  grant,
  vm,
  from_address,
  to_address
) => {
  // const NETWORK = 'TestNet';
  const NETWORK = 'MainNet';

  try {
    const myAlgoConnect = new MyAlgoConnect();
    // step3: check if enough balance is present
    const balance = await getBalance(NETWORK, from_address);

    if (!checkWalletBalance(grant, vm, from_address, balance)) {
      return;
    }

    // step4: set modal to waiting state
    vm.updatePaymentStatus(grant.grant_id, 'waiting');

    const algodClient = new algosdk.Algodv2(
      '',
      'https://node.algoexplorerapi.io',
      ''
    );

    const binaryTx = await buildTransaction(
      grant,
      vm,
      from_address,
      to_address,
      algodClient
    );

    myAlgoConnect
      .signTransaction(binaryTx)
      .then((stx) => {
        // step7: broadcast txn
        algodClient
          .sendRawTransaction(stx.blob)
          .do()
          .then((tx) => {
            contributeWithAlgorandExtensionCallback(
              null,
              tx.txId,
              grant,
              vm,
              from_address
            );
          })
          .catch((e) => {
            console.log(e);
            _alert(
              {
                message: 'Unable to broadcast transaction. Please try again'
              },
              'danger'
            );
            vm.updatePaymentStatus(grant.grant_id, 'failed');
            return;
          });
      })
      .catch((e) => {
        console.log(e);
        _alert(
          { message: 'Unable to sign transaction. Please try again' },
          'danger'
        );
        vm.updatePaymentStatus(grant.grant_id, 'failed');
        return;
      });
  } catch (e) {
    contributeWithAlgorandExtensionCallback(err);
    return;
  }
};
const contributeWithAlgorandExtensionWalletConnect = async(
  grant,
  vm,
  from_address,
  to_address
) => {
  // const NETWORK = 'TestNet';
  const NETWORK = 'MainNet';

  try {
    const connector = new WalletConnect.default({
      bridge: 'https://bridge.walletconnect.org',
      qrcodeModal: WalletConnectQRCodeModal.default
    });

    // Check if connection is already established
    if (!connector.connected) {
      // create new session
      connector.createSession();
    }

    // step3: check if enough balance is present
    const balance = await getBalance(NETWORK, from_address);

    if (!checkWalletBalance(grant, vm, from_address, balance)) {
      return;
    }

    // step4: set modal to waiting state
    vm.updatePaymentStatus(grant.grant_id, 'waiting');

    // step5: get txnParams
    const algodClient = new algosdk.Algodv2(
      '',
      'https://node.algoexplorerapi.io',
      ''
    );
    const request = await buildWalletConnectRequest(
      grant,
      vm,
      from_address,
      to_address,
      algodClient
    );
    const result = await connector.sendCustomRequest(request);
    const decodedResult = result.map((element) => {
      return element ? new Uint8Array(FromBase64(element)) : null;
    });

    algodClient
      .sendRawTransaction(decodedResult)
      .do()
      .then((tx) => {
        contributeWithAlgorandExtensionCallback(
          null,
          tx.txId,
          grant,
          vm,
          from_address
        );
      })
      .catch((e) => {
        _alert(
          { message: 'Unable to broadcast transaction. Please try again' },
          'danger'
        );
        vm.updatePaymentStatus(grant.grant_id, 'failed');
        return;
      });
  } catch (e) {
    contributeWithAlgorandExtensionCallback(err);
    return;
  }
};
const contributeWithAlgorandExtension = async(grant, vm, from_address) => {
  const to_address = grant.algorand_payout_address;

  if (from_address === to_address) {
    _alert(
      {
        message:
          'Grant payment to self detected! Please try again with a different account.'
      },
      'danger'
    );
    return;
  }
  let callback;

  switch (localStorage.getItem('algowallet') || 'AlgoSigner') {
    default:
    case 'AlgoSigner':
      callback = contributeWithAlgorandExtensionAlgoSigner;
      break;
    case 'MyAlgoConnect':
      callback = contributeWithAlgorandExtensionMyAlgo;
      break;
    case 'WalletConnect':
      callback = contributeWithAlgorandExtensionWalletConnect;
      break;
  }
  callback(grant, vm, from_address, to_address);
};

function contributeWithAlgorandExtensionCallback(
  error,
  txn_id,
  grant,
  vm,
  from_address
) {
  if (error) {
    vm.updatePaymentStatus(grant.grant_id, 'failed');
    _alert(
      { message: gettext('Unable to contribute to grant due to ' + error) },
      'danger'
    );
  } else {
    const payload = {
      contributions: [
        {
          grant_id: grant.grant_id,
          contributor_address: from_address,
          tx_id: txn_id,
          token_symbol: grant.grant_donation_currency,
          tenant: 'ALGORAND',
          amount_per_period: grant.grant_donation_amount
        }
      ]
    };

    const apiUrlBounty = 'v1/api/contribute';

    fetchData(apiUrlBounty, 'POST', JSON.stringify(payload))
      .then((response) => {
        if (200 <= response.status && response.status <= 204) {
          console.log('success', response);
          MauticEvent.createEvent({
            alias: 'products',
            data: [
              {
                name: 'product',
                attributes: {
                  product: 'grants',
                  persona: 'grants-contributor',
                  action: 'contribute'
                }
              }
            ]
          });
          vm.updatePaymentStatus(grant.grant_id, 'done', txn_id);
        } else {
          vm.updatePaymentStatus(grant.grant_id, 'failed');
          _alert(
            'Unable to contribute to grant. Please try again later',
            'danger'
          );
          console.error(
            `error: grant contribution failed with status: ${response.status} and message: ${response.message}`
          );
        }
      })
      .catch(function(error) {
        vm.updatePaymentStatus(grant.grant_id, 'failed');
        _alert(
          'Unable to contribute to grant. Please try again later',
          'danger'
        );
        console.log(error);
      });
  }
}
