import {setLengthRight} from "ethereumjs-util";
import BN from "bn.js";

export class PaymentChannelManager {
  // time-based state channel manager
  // send a request for a "ticket" (IOU) every x seconds. if the IOU is not received
  // within y seconds, terminate the channel
  // this represents someone e.g. getting paid in advance for 5 minute chunks of telephone support

  constructor(sessionId, onTimeoutCallback, ticketRequestCallback) {
    this.stateHash = '';
    this.nonce = 0;
    this.onTimeoutCallback = onTimeoutCallback;
    this.ticketRequestCallback = ticketRequestCallback;
    // this.isPayee = false
    this.active = false;

    this.channelId = undefined; // on-chain channel ID

    this.sessionId = sessionId;

    this.ratePerMinute = 0.5 * 10 ** 18 // rate per interval in wei
    this.paymentInterval = 2000; // request payment tickets in chunks of this size - set to 2 seconds for testing
    this.ticketTimeout = 1000; // if no response to request in this time, cancel channel

    // this.sessionStartTime = 0; // timestamp when session started
    this.lastTicketRequest = 0; // timestamp last ticket was set
    this.pendingTicketTimerId = 0; // reference to timeout interal
  }

  openChannel = (channelId, isPayer) => {
    // channel has been created on-chain and participants are ready to begin
    this.channelId = channelId;
    this.active = true;
    if (!isPayer) {
      this.startPaymentRequests()
    }
  };

  closeChannel = () => {
    this.active = false;
    this.channelId = undefined;
    console.log('closing channel');
    this.stopPaymentRequests();
  }

  startPaymentRequests = () => {
    /* refactor this so it handles connection failures. send multiple ticket requests
    until we have one for this time frame. identify a window in which requests should
    be sent (80% of interval passed?). after this, send ticket requests every x seconds
    until we have a response. if it times out, cancel the session.

    should also do the same when sending tickets? add an ack stage, resend until ackd?
     */
    // start sending payment requests - i.e. the session just started
    this.sessionStartTime = Math.floor(Date.now() / 1000);
    this.requestTicketIntervalId = setInterval(this.sendTicketRequest, this.paymentInterval);
    this.sendTicketRequest(); // request the first ticket
  };

  stopPaymentRequests = () => {
    clearTimeout(this.pendingTicketTimerId);
    clearTimeout(this.requestTicketIntervalId);
  };

  ticketReceived = (ticket) => {
    console.log('received ticket')
    console.log(ticket);
    if (!this.active === true) {
      console.log('received ticket on closed channel')
    }
    clearTimeout(this.pendingTicketTimerId)
    // validate ticket signature, time, etc.
    if (ticket.nonce !== this.nonce) {
      // TODO error handling
      console.log('error: invalid nonce')
      return
    }

    this.nonce += 1;
  };

  sendTicketRequest = () => {

    const duration = (Math.floor(Date.now() / 1000) - this.sessionStartTime) + (this.paymentInterval / 1000);
    const value = (this.ratePerMinute / 60) * duration;
    const ticketRequest = {
      session_id: this.sessionId,
      value: String(value),
      nonce: this.nonce
    }
    console.log('sending ticket request')
    console.log(ticketRequest);
    this.pendingTicketTimerId = setTimeout(this.onTicketRequestTimeout, this.ticketTimeout);
    this.ticketRequestCallback(ticketRequest)
  };

  onTicketRequestTimeout = () => {
    console.log("timeout")
    clearTimeout(this.requestTicketIntervalId);
    // TODO call callback function with tx for claiming session so far?
    this.onTimeoutCallback()
  }

  ticketRequestReceived = (ticketRequest, web3, privateKey) => {

    console.log('received ticket request')
    console.log(ticketRequest);
    // TODO verify nonce, timer, etc.
    if (!this.active) {
      console.error('Received request for ticket on closed channel')
    }

    let stringBytes = web3.utils.hexToBytes(web3.utils.toHex('close_channel'));
    let stringBytesPadded = setLengthRight(stringBytes, 32);
    let channelIdBytes = web3.utils.hexToBytes(web3.utils.toHex(this.channelId));
    let channelIdBytesPadded = setLengthRight(channelIdBytes, 32);

    let hash = web3.utils.soliditySha3(
      web3.utils.bytesToHex(channelIdBytesPadded),
      web3.utils.bytesToHex(stringBytesPadded),
      web3.utils.toBN(ticketRequest.value),
    );

    // verify nonce, value. if valid, return a signed ticket
    let ticket = {
      session_id: this.sessionId,
      nonce: this.nonce,
      value: ticketRequest.value,
      signature: web3.eth.accounts.sign(hash, privateKey).signature
    };
    this.nonce += 1;
    return ticket
  }


}

