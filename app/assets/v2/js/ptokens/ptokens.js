const TX_STATUS_PENDING = 'pending';
const TX_STATUS_SUCCESS = 'success';
const TX_STATUS_ERROR = 'error';
const TX_STATUS_UNKNOWN = 'unknown';
const TX_STATUS_DROPPED = 'dropped';
const redemption_states = [ 'request', 'accepted', 'denied', 'completed' ];

function get_ptokens() {
  return fetchData('/ptokens/', 'GET');
}

function get_ptoken_redemptions(tokenId, state) {
  if (redemption_states.indexOf(state)) {
    return fetchData(`/ptokens/${tokenId}/redemptions?state=${state}`, 'GET');
  }

  return fetchData('/ptokens/', 'GET');
}

function create_ptoken(name, symbol, address, value, minted, owner_address, txId, web3_created, network) {
  return fetchData('/ptokens/?minimal=true', 'POST', {
    'token_name': name,
    'token_symbol': symbol,
    'token_address': address,
    'token_owner_address': owner_address,
    'network': network,
    'tx_status': TX_STATUS_PENDING,
    'txid': txId,
    'total_minted': minted,
    'value': value,
    'web3_created': web3_created
  });
}

function update_ptoken_address(tokenId, token_address) {
  return fetchData(`/ptokens/${tokenId}/`, 'POST', {
    'event_name': 'update_address',
    'tx_status': TX_STATUS_SUCCESS,
    'token_address': token_address
  });
}

function mint_tokens(tokenId, amount) {
  return fetchData(`/ptokens/${tokenId}/`, 'POST', {
    'event_name': 'mint_ptoken',
    'amount': amount
  });
}

function change_price(tokenId, value) {
  return fetchData(`/ptokens/${tokenId}/`, 'POST', {
    'event_name': 'edit_price_ptoken',
    'value': value
  });
}

function purchase_ptoken(tokenId, amount, to_address, web3_created, txid) {
  return fetchData(`/ptokens/${tokenId}/purchase/`, 'POST', {
    'network': network,
    'web3_created': web3_created,
    'token_holder_address': to_address,
    'txid': txid,
    'tx_status': TX_STATUS_PENDING,
    'amount': amount
  });
}

function request_redemption(tokenId, total, network) {
  return fetchData(`/ptokens/${tokenId}/redemptions/`, 'POST', {
    'network': network,
    'total': total
  });
}

function complete_redemption(redemptionId, txid, tx_status, network, web3_created) {
  return fetchData(`/ptokens/redemptions/${redemptionId}/`, 'POST', {
    'event_name': 'complete_redemption_ptoken',
    'web3_created': web3_created,
    'tx_status': tx_status,
    'txid': txid,
    'network': network
  });
}

function denied_redemption(redemptionId) {
  return fetchData(`/ptokens/redemptions/${redemptionId}/`, 'POST', {
    'event_name': 'denies_redemption_ptoken'
  });
}

function accept_redemption(redemptionId) {
  return fetchData(`/ptokens/redemptions/${redemptionId}/`, 'POST', {
    'event_name': 'accept_redemption_ptoken'
  });
}

