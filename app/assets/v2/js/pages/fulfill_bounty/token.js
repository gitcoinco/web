/**
 * Handles Bounty Fulfillement for crypto tokens
 * Data is stored in the db
 */
fulfillBounty = data => {

  if (!data.githubPRLink) {
    _alert({ message: gettext('Add Github Link to let the funder know where they can check out your work') }, 'danger');
    unloading_button($('.js-submit'));
    return;
  }

  if (web3_type == 'fiat' && !data.fulfiller_identifier) {
    _alert({ message: gettext('Add valid email you would want the bounty to be sent to') }, 'danger');
    unloading_button($('.js-submit'));
  } else if (web3_type != 'fiat' && !data.payoutAddress) {
    _alert({ message: gettext('Add valid address you would want the bounty to be sent to') }, 'danger');
    unloading_button($('.js-submit'));
    return;
  } else if (!is_valid_address(data.payoutAddress)) {
    $('#payoutAddress-container input').removeClass('valid');
    $('#payoutAddress-container input').addClass('invalid');
    $('#payoutAddress-container').addClass('invalid');
    $('#payoutAddress-container .text-danger').removeClass('hidden');
    unloading_button($('.js-submit'));
    return;
  } else {
    $('#payoutAddress-container input').addClass('valid');
    $('#payoutAddress-container input').removeClass('invalid');
    $('#payoutAddress-container').removeClass('invalid');
    $('#payoutAddress-container .text-danger').addClass('hidden');
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
      _alert('Unable to fulfill bounty. Please try again later', 'danger');
      unloading_button($('.js-submit'));
      console.error(`error: bounty fulfillment failed with status: ${response.status} and message: ${response.message}`);
    }
  });
};

const is_valid_address = (address) => {
  return validateWalletAddress(chainId, address);
};
