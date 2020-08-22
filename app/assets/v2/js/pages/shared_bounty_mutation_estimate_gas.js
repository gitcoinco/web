var gas_amount = function(page_url) {
  let gasLimitEstimate = 0;

  if (page_url.indexOf('issue/fulfill') != -1) {
    gasLimitEstimate = 207103;
  } else if (page_url.indexOf('grants/matic/new') != -1) {
    gasLimitEstimate = 3000000;
  } else if (page_url.indexOf('grants/new') != -1) { // new grant contribution
    gasLimitEstimate = 3000000;
  } else if (page_url.indexOf('/new') != -1) { // new fulfill funding page
    gasLimitEstimate = 318730;
  } else if (page_url.indexOf('issue/increase') != -1) { // new fulfill funding page
    gasLimitEstimate = 96269;
  } else if (page_url.indexOf('issue/accept') != -1) { // new process funding page
    gasLimitEstimate = 103915;
  } else if (page_url.indexOf('issue/cancel') != -1) { // new kill funding page
    gasLimitEstimate = 67327;
  } else if (page_url.indexOf('issue/advanced_payout') != -1) { // advanced payout page
    gasLimitEstimate = 67327;
  } else if (page_url.indexOf('issue/payout') != -1) { // bulk payout
    gasLimitEstimate = 103915;
  } else if (page_url.indexOf('tip/send') != -1) { // tip
    gasLimitEstimate = 21000;
  } else if (page_url.indexOf('tip/receive') != -1) { // tip
    gasLimitEstimate = 21000;
  } else if (page_url.indexOf('subscription') != -1) { // subscribe grant contribution
    gasLimitEstimate = 318730;
  } else if (page_url.indexOf('grants/fund') != -1) { // fund grant contribution
    gasLimitEstimate = 69169;
  } else if (page_url.indexOf('grants/cancel') != -1) { // cancel grant contribution
    gasLimitEstimate = 45805;
  } else if (page_url.indexOf('grants/') != -1) { // cancel grant contribution
    gasLimitEstimate = 318730;
  } else if (page_url.indexOf('/fund') != -1) { // grant contribution
    gasLimitEstimate = 318730;
  } else if (page_url.indexOf('subscribe') != -1) { // gitcoin subscription plans
    gasLimitEstimate = 318730;
  }
  return gasLimitEstimate;
};
