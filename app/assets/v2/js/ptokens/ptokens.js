const TX_STATUS_PENDING = 'pending';
const TX_STATUS_SUCCESS = 'success';
const TX_STATUS_ERROR = 'error';
const TX_STATUS_UNKNOWN = 'unknown';
const TX_STATUS_DROPPED = 'dropped';
const redemption_states = [ 'request', 'accepted', 'denied', 'completed' ];

function getPToken(tokenId) {
  return fetchData(`/ptokens/${tokenId}/?minimal=true`, 'GET');
}

function get_personal_token() {
  return fetchData('/ptokens/me/?minimal=true', 'GET');
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

function update_ptokens() {
  return fetchData('/ptokens/update', 'POST');
}

function update_ptoken_address(tokenId, token_address) {
  return fetchData(`/ptokens/${tokenId}/`, 'POST', {
    'event_name': 'update_address',
    'tx_status': TX_STATUS_SUCCESS,
    'token_address': token_address
  });
}

function mint_tokens(tokenId, amount, txid, network) {
  return fetchData(`/ptokens/${tokenId}/`, 'POST', {
    'event_name': 'mint_ptoken',
    'amount': amount,
    'txid': txid,
    'network': network
  });
}

function burn_tokens(tokenId, amount, txid, network) {
  return fetchData(`/ptokens/${tokenId}/`, 'POST', {
    'event_name': 'burn_ptoken',
    'amount': amount,
    'txid': txid,
    'network': network
  });
}

function change_price(tokenId, value, txid, network) {
  return fetchData(`/ptokens/${tokenId}/`, 'POST', {
    'event_name': 'edit_price_ptoken',
    'value': value,
    'txid': txid,
    'network': network
  });
}

function purchase_ptoken(tokenId, amount, to_address, web3_created, txid, network, value_token) {
  return fetchData(`/ptokens/${tokenId}/purchase/`, 'POST', {
    'network': network,
    'web3_created': web3_created,
    'token_holder_address': to_address,
    'txid': txid,
    'tx_status': TX_STATUS_PENDING,
    'amount': amount,
    'token': value_token.id,
    'token_address': value_token.addr,
    'token_name': value_token.name
  });
}

function request_redemption(tokenId, total, redemptionDescription, network) {
  return fetchData(`/ptokens/${tokenId}/redemptions/`, 'POST', {
    'network': network,
    'total': total,
    'description': redemptionDescription
  });
}

function complete_redemption(redemptionId, txid, tx_status, address, network, web3_created) {
  return fetchData(`/ptokens/redemptions/${redemptionId}/`, 'POST', {
    'event_name': 'complete_redemption_ptoken',
    'web3_created': web3_created,
    'tx_status': tx_status,
    'txid': txid,
    'network': network,
    'address': address
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

async function ptoken_name_exists(ptoken_name) {
  let data = await fetchData(`/ptokens/verify?name=${ptoken_name}`, 'GET');

  return data['name'];
}

async function ptoken_symbol_exists(ptoken_symbol) {
  let data = await fetchData(`/ptokens/verify?symbol=${ptoken_symbol}`, 'GET');

  return data['symbol'];
}
