/**
 * Handles Bounty Fulfillement for crypto tokens
 * Data is stored in the db
 */
fulfillBounty = data => {

  if (!data.githubPRLink) {
    _alert({ message: gettext('Add Github Link to let the funder know where they can check out your work') }, 'error');
    return;
  }

  if (!data.payoutAddress) {
    _alert({ message: gettext('Add address you would want to be paid out upon payout') }, 'error');
    return;
  }

  const url  = '/api/v1/bounty/fulfill';

  const metadata = {
    'data': {
      'payload': {
        'fulfiller': {
          'email': data.notificationEmail,
          'address': data.payoutAddress,
          'hoursWorked': data.hoursWorked,
          'githubPRLink': data.githubPRLink
        }
      }
    },
    'accepted': false,
    'fulfiller': data.payoutAddress
  };

  const params = {
    'issueURL': data.issueURL,
    'email': data.notificationEmail,
    'githubPRLink': data.githubPRLink,
    'hoursWorked': data.hoursWorked,
    'metadata': JSON.stringify(metadata),
    'fulfiller_address': data.payoutAddress
  };

  $.post(url, params, function(response) {
    if (200 <= response.status && response.status <= 204) {
      // redirect to bounty page
      console.log('success', response);
      window.location.href = response.bounty_url;
    } else {
      _alert('Unable to fulfill bounty. Please try again later', 'error');
      console.error(`error: bounty fulfillment failed with status: ${response.status} and message: ${response.message}`);
    }
  });
}