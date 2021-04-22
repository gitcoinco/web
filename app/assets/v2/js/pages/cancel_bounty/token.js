/**
 * Handles Bounty cancellation for crypto tokens
 * Data is stored in the db
 */
cancelBounty = data => {

  const url = '/api/v1/bounty/cancel';

  params = data.payload;

  $.post(url, params, function(response) {
    if (200 <= response.status && response.status <= 204) {
      // redirect to bounty page
      console.log('success', response);
      window.location.href = response.bounty_url;
    } else {
      _alert('Unable to cancel a bounty. Please try again later', 'danger');
      console.error(`error: bounty creation failed with status: ${response.status} and message: ${response.message}`);
    }
  });

};