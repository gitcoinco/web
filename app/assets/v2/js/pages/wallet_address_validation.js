
var validateWalletAddress = function(chainId, address) {
  let isValid = true;

  switch (chainId) {
    // case '1000':
    // // Harmony
    // if (!address.toLowerCase().startsWith('one')) {
    //   isValid = false;
    // }
    // break;

    case '1935': // Sia
    case '58': // Polkadot
      if (address.toLowerCase().startsWith('0x')) {
        isValid = false;
      }
      break;

    case '50': // Xinfin
      if (!address.toLowerCase().startsWith('xdc')) {
        isValid = false;
      }
      break;

    case '1995': {
      // nervos
      const ADDRESS_REGEX = new RegExp('^(ckb){1}[0-9a-zA-Z]{43,92}$');
      const isNervosValid = ADDRESS_REGEX.test(address);

      if (!isNervosValid && !address.toLowerCase().startsWith('0x')) {
        isValid = false;
      }
      break;
    }

    case '50797': {
      // tezos
      const ADDRESS_REGEX = new RegExp('^(tz1|tz2|tz3)[0-9a-zA-Z]{33}$');
      const isTezosValid = ADDRESS_REGEX.test(address);

      if (!isTezosValid) {
        isValid = false;
      }
      break;
    }

    case '0': {
      // btc
      const ADDRESS_REGEX = new RegExp('^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$');
      const BECH32_REGEX = new RegExp('^bc1[ac-hj-np-zAC-HJ-NP-Z02-9]{11,71}$');
      const valid_legacy = ADDRESS_REGEX.test(address);
      const valid_segwit = BECH32_REGEX.test(address);

      if (!valid_legacy && !valid_segwit) {
        isValid = false;
      }
      break;
    }

    case '600': // Filecoin
      if (!address.toLowerCase().startsWith('fil')) {
        isValid = false;
      }
      break;

    case '102':// Zilliqa
      if (!address.toLowerCase().startsWith('zil')) {
        isValid = false;
      }
      break;


    case '270895': {
      // casper
      let addr = address;

      if (!addr.toLowerCase().startsWith('01') && !addr.toLowerCase().startsWith('02')) {
        isValid = false;
      }
      break;
    }


    // include validation for other chains here
  }

  return isValid;
};
