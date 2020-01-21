function update_session(sessionId, data) {
  let session = {};

  if (data.name) {
    session.name = data.name
  }

  if (data.description) {
    session.description = data.description
  }

  if (data.metadata) {
    session.metadata = JSON.stringify(data.metadata)
  }

  if (data.active !== undefined) {
    session.active = Boolean(data.active)
  }

  if (data.amount) {
    session.amount = parseFloat(data.amount)
  }

  let tx_status = ['na', 'pending', 'success', 'error', 'error', 'unknown', 'dropped'];

  if (tx_status.indexOf(data.txStatus) !== -1) {
    session.tx_status = data.txStatus;
  }

  if (data.txId) {
    session.tx_id = data.txId;
    session.tx_time = data.txTime.toISOString();
  }

  if (data.tags && Array.isArray(data.tags)) {
    session.tags = JSON.stringify(data.tags)
  }

  if (data.menteeHandler) {
    session.mentee_handler = data.menteeHandler
  }

  return fetchData('/mentor/session/' + sessionId + '/update', 'POST', session);
}


function finish_session(sessionId) {
  return fetchData('/mentor/session/' + sessionId + '/finish', 'POST');
}

function get_session(sessionId) {
  return fetchData('/mentor/session/' + sessionId + '/get', 'GET');
}
