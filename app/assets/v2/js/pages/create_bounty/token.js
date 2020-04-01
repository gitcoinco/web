/**
 * Handles Bounty for crypto tokens
 * Data is stored in the db
 */
createBounty = data => {

  const metadata  = data.metadata;
  const privacy_preferences = {
    show_email_publicly: data.show_email_publicly,
    show_name_publicly: data.show_name_publicly
  };
  const hiring = {
    hiringRightNow: !!data.hiringRightNow,
    jobDescription: data.jobDescription
  };
  const bountyNeverExpires = 9999999999;

  const expiresDate =
    data.neverExpires == 'on' ?
    bountyNeverExpires :
    new Date(data.expirationTimeDelta).getTime() / 1000;

  let is_featured = data.is_featured ? 'True' : 'False';
  let coupon_code = $('#coupon_code').val();
  let fee_amount;
  let fee_tx_id;
  let network;

  const tokenAddress = data.denomination;
  const token = tokenAddressToDetails(tokenAddress);

  if (qr_tokens.includes(metadata.tokenName)) {
    is_featured = 'True';
    coupon_code = null;
    fee_amount = 0;
    fee_tx_id = null;
    network = 'mainnet';
  }


  const params = {
    'title': metadata.issueTitle,
    'amount': data.amount,
    'value_in_token': data.amount * 10 ** token.decimals,
    'token_name': metadata.tokenName,
    'token_address': tokenAddress,
    'bounty_type': metadata.bountyType,
    'project_length': metadata.projectLength,
    'estimated_hours': metadata.estimatedHours,
    'experience_level': metadata.experienceLevel,
    'github_url': data.issueURL,
    'bounty_owner_email': metadata.notificationEmail,
    'bounty_owner_github_username': metadata.githubUsername,
    'bounty_owner_name': metadata.fullName, // ETC-TODO REMOVE ?
    'bounty_reserved_for': metadata.reservedFor,
    'release_to_public': metadata.releaseAfter,
    'expires_date': expiresDate,
    'metadata': JSON.stringify(metadata),
    'raw_data': {}, // ETC-TODO REMOVE ?
    'network': network,
    'issue_description': metadata.issueDescription,
    'funding_organisation': metadata.fundingOrganisation,
    'balance': data.amount * 10 ** token.decimals, // ETC-TODO REMOVE ?
    'project_type': data.project_type,
    'permission_type': data.permission_type,
    'bounty_categories': metadata.bounty_categories,
    'repo_type': data.repo_type,
    'is_featured': is_featured,
    'featuring_date': metadata.featuring_date,
    'fee_amount': fee_amount,
    'fee_tx_id': fee_tx_id,
    'coupon_code': coupon_code,
    'unsigned_nda': '', // ETC-TODO
    'privacy_preferences': JSON.stringify(privacy_preferences),
    'attached_job_description': hiring.jobDescription,
    'eventTag': metadata.eventTag,
    'auto_approve_workers': data.auto_approve_workers ? 'True' : 'False',
    'web3_type': 'qr',
    'activity': data.activity,
    'bounty_owner_address': data.funderAddress
  };

  const url  = '/api/v1/bounty/create';

  $.post(url, params, function(response) {    
    if (200 <= response.status && response.status <= 204) {
      console.log('success', response);
      window.location.href = response.bounty_url;
    } else if (response.status == 304) {
      _alert('Bounty already exists for this github issue.', 'error');
      console.error(`error: bounty creation failed with status: ${response.status} and message: ${response.message}`);
    } else {
      _alert('Unable to create a bounty. Please try again later', 'error');
      console.error(`error: bounty creation failed with status: ${response.status} and message: ${response.message}`);  
    }
  });

}