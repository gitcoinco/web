import axios from 'axios';

// axios.defaults.xsrfHeaderName = "X-CSRFToken";
// axios.defaults.xsrfCookieName = "csrftoken";

export default function gitCoinApi(url) {

  let api = axios.create({
    baseURL: url || 'http://localhost/api/v0.1/',
    xsrfHeaderName: "X-CSRFTOKEN",
    xsrfCookieName: "csrftoken"
  });

  function authCheck() {
    return api.get('user-info/');
  }

  function getSession(sessionId) {
    return api.get('sessions/' + sessionId + '/');
  }

  function getAppInit(sessionId) {
    return api.get('sessions/' + sessionId + '/app_init/');
  }

  function sendJoinRequest(joinRequest) {
    // express intent to join session
    console.log(joinRequest);
    return api.post('sessions/' + joinRequest.session_id + '/send_join_request/', joinRequest);
  }

  function acceptJoinRequest(joinRequest) {
    // accept intent to join session
    return api.post('sessions/' + joinRequest.session_id + '/accept_join_request/', {
      interest_id: joinRequest.id
    });
  }

  function cancelJoinRequest(joinRequest) {
    // retract intent to join session
    return api.post('sessions/' + joinRequest.session_id + '/cancel_join_request/', {
      interest_id: joinRequest.id
    });
  }

  function requestSessionTicket(ticketRequest) {
    // request an updated ticket/IOU
    return api.post('sessions/' + ticketRequest.session_id + '/request_ticket/',
      ticketRequest);
  }

  function sendSessionTicket(ticket) {
    // send an updated ticket/IOU
    return api.post('sessions/' + ticket.session_id + '/send_ticket/',
      ticket);
  }

  // function startSession(sessionId, txHash) {
  //   // Host has broadcast the tx to start the session
  //   return api.post('sessions/' + sessionId + '/start/', {
  //     tx_hash: txHash
  //   });
  // }

  function startSessionConfirmed(sessionId, txHash, channelId) {
    // startSession tx has been confirmed
    return api.post('sessions/' + sessionId + '/start_confirmed/', {
      tx_hash: txHash,
      channel_id: channelId
    });
  }

  function endSession(sessionId) {
    // Host or guest has ended the session
    return api.post('sessions/' + sessionId + '/end/');
  }

  function fundsClaimed(sessionId, txHash) {
    return api.post('sessions/' + sessionId + '/funds_claimed/', {
      tx_hash: txHash
    });
  }

  function createSession(sessionDetails) {
    return api.post('sessions/new/', {
      title: sessionDetails.title,
      description: sessionDetails.description
    });
  }

  return {
    authCheck: authCheck,
    getAppInit: getAppInit,
    getSession: getSession,
    // startSession: startSession,
    startSessionConfirmed: startSessionConfirmed,
    endSession: endSession,
    sendJoinRequest: sendJoinRequest,
    acceptJoinRequest: acceptJoinRequest,
    cancelJoinRequest: cancelJoinRequest,
    requestSessionTicket: requestSessionTicket,
    sendSessionTicket: sendSessionTicket,
    fundsClaimed: fundsClaimed,
    createSession: createSession
  }
}
