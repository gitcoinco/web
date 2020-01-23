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
			// TODO: Recover eth address here??
			session.mentee_handler = data.menteeHandler
		}
	
		return fetchData('/mentor/session/' + sessionId + '/update', 'POST', session);

}

function join_session(sessionId) {
  return fetchData('/mentor/session/' + sessionId, 'POST');
}

function finish_session(sessionId) {
  return fetchData('/mentor/session/' + sessionId + '/finish', 'POST');
}

function get_session(sessionId) {
  return fetchData('/mentor/session/' + sessionId + '/get', 'GET');
}

function myAvailability() {
  return fetchData('/mentor/availability', 'GET');
}

function availableMentor(period_time) {
	return fetchData('/mentor/available', 'POST', {
		period_time: period_time,
		current_time: new Date().toISOString()
	});
}

function unavailableMentor() {
  return fetchData('/mentor/unavailable', 'POST');
}

function toggleAvailableMentor() {
  return fetchData('/mentor/availability/toggle', 'POST');
}

function availableMentors() {
  return fetchData('/mentors', 'GET');
}


function update_availability(period_time) {
  if (period_time) {
    availableMentor(period_time).then(function(res) {
      console.log(res);
      var date = new Date(res.active_until);
      var time = date.getHours() + ':' + date.getMinutes();

      $('#avaialableStatus').html('Mentoring: Active<br><span style="font-size: 12px">Until: ' + time + '</span>');
      $('.active-mentor').hide();
      $('.inactive-mentor').show();
    });
  } else {
    unavailableMentor().then(function(res) {
      console.log(res);
      $('#avaialableStatus').html('Mentoring: Inactive');
      $('.active-mentor').show();
      $('.inactive-mentor').hide();
    });
  }

  $('#avaialableStatus + .dropdown-menu').toggle();
}
