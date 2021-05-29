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
harmony_utils.initHarmonyExtension = async (network='mainnet') => {

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

  let ext = new HarmonyJs.HarmonyExtension(window.onewallet);
  ext.provider = new HarmonyNetwork.Provider(rpcUrl).provider;
  ext.messenger = new HarmonyNetwork.Messenger(
    ext.provider,
    chainType,
    chainId
  );

  return ext;
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


harmony_utils.isOnewalletInstalled = () => {
  return window.onewallet && window.onewallet.isOneWallet;
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
    from: new HarmonyCrypto.HarmonyAddress(from).checksum,
    to: new HarmonyCrypto.HarmonyAddress(to).checksum,
    value: new HarmonyUtils.Unit(amount).asOne().toWei(),
    gasLimit: '21000',
    shardID: 0,
    toShardID: 0,
    gasPrice: new hmy.utils.Unit(1).asGwei().toWei(),
  });


  const signedTxn = await harmonyExt.wallet.signTransaction(txn);
  // const signedTxn = await window.onewallet.signTransaction(txn);
  const response = await signedTxn.sendTransaction();

  if (response[0] && response[0].txStatus == 'REJECTED') {
    throw response[1];
  }

  if (response.error && response.error.code) {
    throw response.error.message
  }

  if (response[0] && response[0].id) {
    return response[0].id;
  }

  return response.result;
}
