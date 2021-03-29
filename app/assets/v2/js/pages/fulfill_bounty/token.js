/**
 * Handles Bounty Fulfillement for crypto tokens
 * Data is stored in the db
 */
fulfillBounty = data => {

  if (!data.githubPRLink) {
    _alert({ message: gettext('Add Github Link to let the funder know where they can check out your work') }, 'error');
    unloading_button($('.js-submit'));
    return;
  }

  if (web3_type == 'fiat' && !data.fulfiller_identifier) {
    _alert({ message: gettext('Add valid email you would want the bounty to be sent to') }, 'error');
    unloading_button($('.js-submit'));
  } else if (web3_type != 'fiat' && !data.payoutAddress) {
    _alert({ message: gettext('Add valid address you would want the bounty to be sent to') }, 'error');
    unloading_button($('.js-submit'));
    return;
  } else if (!is_valid_address(data.payoutAddress)) {
    unloading_button($('.js-submit'));
    return;
  }

  const url = '/api/v1/bounty/fulfill';

  const metadata = {
    'data': {
      'payload': {
        'fulfiller': {
          'address': data.payoutAddress,
          'hoursWorked': data.hoursWorked,
          'githubPRLink': data.githubPRLink
        }
      }
    },
    'accepted': false,
    'fulfiller': data.payoutAddress,
    'fulfiller_identifier': data.fulfiller_identifier,
    'bountyPk': data.bountyPk
  };

  const params = {
    'issueURL': data.issueURL,
    'githubPRLink': data.githubPRLink,
    'hoursWorked': data.hoursWorked,
    'metadata': JSON.stringify(metadata),
    'fulfiller_address': data.payoutAddress,
    'fulfiller_identifier': data.fulfiller_identifier,
    'payout_type': web3_type,
    'projectId': data.projectId,
    'bountyPk': data.bountyPk
  };

  if (data.videoDemoLink) {
    const metadata = getVideoMetadata(data.videoDemoLink);

    params['videoDemoLink'] = data.videoDemoLink;
    params['videoDemoProvider'] = metadata ? metadata['provider'] : null;
  }

  $.post(url, params, function(response) {
    if (200 <= response.status && response.status <= 204) {
      // redirect to bounty page
      console.log('success', response);
      window.location.href = response.bounty_url;
    } else {
      _alert('Unable to fulfill bounty. Please try again later', 'error');
      unloading_button($('.js-submit'));
      console.error(`error: bounty fulfillment failed with status: ${response.status} and message: ${response.message}`);
    }
  });
};


const is_valid_address = (address) => {
  switch (web3_type) {

    // etc
    // celo
    // rsk

    case 'binance_ext':
      if (!address.toLowerCase().startsWith('bnb')) {
        _alert('Enter a valid binance address', 'error');
        return false;
      }
      return true;

    case 'harmony_ext':
      if (!address.toLowerCase().startsWith('one')) {
        _alert('Enter a valid harmony address', 'error')
        return false;
      }
      return true;


    case 'polkadot_ext':
      if (address.toLowerCase().startsWith('0x')) {
        _alert('Enter a valid polkadot address', 'error')
        return false;
      }
      return true;


    case 'xinfin_ext':
      if (!address.toLowerCase().startsWith('xdc')) {
        _alert('Enter a valid xinfin address', 'error');
        return false;
      }
      return true;

    case 'qr':

      if (token_name == 'BTC') {
        if (address.toLowerCase().startsWith('0x')) {
          _alert('Enter a valid bitcoin address', 'error');
          return false;
        }
        return true;
      }

      if (token_name == 'FIL') {
        if (!address.toLowerCase().startsWith('fil')) {
          _alert('Enter a valid filecoin address', 'error');
          return false;
        }
        return true;
      }

      if (token_name == 'ZIL') {
        if (!address.toLowerCase().startsWith('zil')) {
          _alert('Enter a valid zilliqa address', 'error');
          return false;
        }
        return true;
      }

    default:
      return true;
  }

}