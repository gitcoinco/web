var harmony_utils = {};

/**
 * inject harmony instance
 */
harmony_utils.initHarmony = (network='mainnet') => {

  let chainId;
  let chainType = HarmonyUtils.ChainType.Harmony;
  let rpcUrl;

  if (network == 'test') {
    chainId = HarmonyUtils.ChainID.HmyTestnet;
    rpcUrl = 'https://api.s0.b.hmny.io';
  } else {
    chainId = HarmonyUtils.ChainID.HmyMainnet;
    rpcUrl = 'https://api.s0.t.hmny.io';
  }

  let hmy = new HarmonyJs.Harmony(rpcUrl, {
    chainType: chainType,
    chainId: chainId
  });

  return hmy;
}

/**
 * retrieve balance from address
 *
 * hmy    : (Object) injected harmony instance
 * address: (String) one wallet address
 */
harmony_utils.getAddressBalance = async (hmy, address) => {
  return hmy.blockchain
    .getBalance({ address: address })
    .then(response => {
      const balance = HarmonyUtils.fromWei(HarmonyUtils.hexToNumber(response.result), HarmonyUtils.Units.one);

      console.log('balance in ONEs: ' + balance);
      return balance;
  });
}


/**
 * init the harmony extension to be used for transfer
 * */
harmony_utils.initHarmonyExtension = async () => {
  return new HarmonyJs.HarmonyExtension(window.onewallet);
}

/**
 * retrieve account address
 *
 * harmonyExt : (Object) injected extension
 **/
harmony_utils.loginHarmonyExtension = async harmonyExt => {

  return harmonyExt.login().then(account => {
    return account.address;
  }).catch(err => {
      console.error(err);
      return err;
  });
}

/**
 * logout harmony extension to enable switch account
 *
 * harmonyExt : (Object) injected extension
 */
harmony_utils.logoutHarmonyExtension = async harmonyExt => {
  return harmonyExt.logout();
}

/**
 *  transfer tokens between shard 0 address via harmony extension
 *
 * hmy        : (Object) injected harmony instance
 * harmonyExt : (Object) injected extension
 * from       : (String) from address
 * to         : (String) to address
 * amount     : (String) amount
 */
harmony_utils.transfer = async(hmy, harmonyExt, from, to, amount) => {
  const txn = hmy.transactions.newTx({
    from: from,
    to: to,
    value: new HarmonyUtils.Unit(amount).asOne().toWei(),
    gasLimit: '31000',
    shardID: 0,
    toShardID: 0,
    gasPrice: new hmy.utils.Unit(amount).asGwei().toWei(),
  });

  console.log(txn);

  // hmy.wallet.addByPrivateKey('');
  // const signedTxn = await hmy.wallet.signTransaction(txn);
  // const response = await hmy.blockchain.sendTransaction(signedTxn);

  const signedTxn = await harmonyExt.wallet.signTransaction(txn);
  const response = await signedTxn.sendTransaction();

  if (response[0] && response[0].txStatus == 'REJECTED') {
    throw response[1];
  }

  if (response.error && response.error.code) {
    throw response.error.message
  }

  return response.result;
}
