/* eslint-disable no-console */
// TODO: form data validation

// const token = tokenAddressToDetails(tokenAddress);

$(document).ready(function() {

  const START_DATE = new Date(new Date().setMinutes(new Date().getMinutes() + 10))
  const tokenDecimals = 18;
  const sessionDuration = 900; // seconds

  let sessionCost = 5;

  const requestDetails = {
    sablierAddress: web3.utils.toChecksumAddress('0xc04Ad234E01327b24a831e3718DBFcbE245904CC'),
    tokenAddress: web3.utils.toChecksumAddress('0xc3dbf84abb494ce5199d5d4d815b10ec29529ff8'),
    deposit: depositToBigNumber(sessionCost, sessionDuration, tokenDecimals),
    duration: sessionDuration,
    mentorAddress: web3.utils.toChecksumAddress('0x62051BfD3A4f7039a849142e6E5ea172cBdA5949'),
    menteeAddress: web3.utils.toChecksumAddress('0xd21aEff7Fc73AB5D608808c99427B1B9084D372e')
  }

  let testDAI = new web3.eth.Contract(token_abi, requestDetails.tokenAddress);
  let approveTx = testDAI.methods.approve(requestDetails.sablierAddress, requestDetails.deposit.toFixed());

  // bug: does apply current date until you click and apply another day and then return to the current day
  $('input[name="session_datetime"]').daterangepicker({
    singleDatePicker: true,
    startDate: START_DATE,
    timePicker: true,
    timePicker24Hour: true,
    // timePickerIncrement: 10,
    showDropdowns: true,
    minDate : START_DATE,
    maxDate: new Date(new Date().setFullYear(new Date().getFullYear() + 2)),
    autoApply: true,
    autoUpdateInput: false,
    locale: {
      format: 'YYYY-MM-DD HH:mm'
    }
  }, function(chosen_date) {
    $('input[name="session_datetime"]').val(chosen_date.format('YYYY-MM-DD HH:mm'));

    requestDetails.sessionStartDate = chosen_date.utc().unix();
    requestDetails.sessionEndDate = requestDetails.sessionStartDate + requestDetails.duration;
  });

  $('#submitRequest').one('click', function() {
    Promise
      .delay(approveToken, 300)
      .delay(createStream, 30000);
  });

  // function disableRequestButton() {
  //   $('#submitRequest').prop('disabled', true);
  //


  function approveToken() {
    approveTx.send({
      from: requestDetails.menteeAddress,
      value: 0,
    })
    .on('transactionHash', function(hash){
      console.log('approveTx Hash: ');
      console.log(hash);
    })
    .on('confirmation', function(confirmationNumber, receipt){
      console.log("approveTx confirmation: ")
      console.log(confirmationNumber);
      console.log(receipt);
    })
    .on('receipt', function(receipt){
      console.log("approveTx receipt: ");
      console.log(receipt);
    })
    .on('error', console.error);
  }

  function createStream() {
    // hardcode values for demo
    if (typeof requestDetails['sessionStartDate'] !== 'undefined') {
      let sablier = new web3.eth.Contract(sablier_abi, requestDetails.sablierAddress);
      let sablierTx = sablier.methods.createStream(
        requestDetails.mentorAddress,
        requestDetails.deposit.toFixed(),
        requestDetails.tokenAddress,
        requestDetails.sessionStartDate,
        requestDetails.sessionEndDate
      );

      sablierTx.send({
        from: requestDetails.menteeAddress,
        gas: 500000,
        value: 0,
      })
      .on('transactionHash', function(hash){
        console.log('sablierTx Hash: ');
        console.log(hash);
      })
      .on('confirmation', function(confirmationNumber, receipt){
        console.log("sablierTx confirmation: ")
        console.log(confirmationNumber);
        console.log(receipt.events.CreateStream.returnValues);
      })
      .on('receipt', function(receipt){
        console.log("sablierTx receipt: ");
        console.log(receipt);

        let formData = new FormData();
        formData.append('sablier_tx_receipt', JSON.stringify(receipt));
        formData.append('session_datetime', requestDetails.sessionStartDate)

        let streamId = String(receipt.events.CreateStream.returnValues.streamId)
        let sessionId = streamId.concat(String(request.sessionEndDate))
        formData.append('gitmentor_session_id', sessionId)

        console.log(sessionId)

        saveSessionRequest(formData, true);
      })
      .on('error', console.error);
    }
  }

  userSearch('.mentor', false, undefined, false, false, true);
});

function depositToBigNumber(tokenAmount, timeDelta, tokenDecimals) {
  let decimalDivisor = new BigNumber(10).pow(tokenDecimals);
  let deposit = new BigNumber(tokenAmount).multipliedBy(decimalDivisor);
  let delta = new BigNumber(timeDelta);
  let depositByDeltaRemainder = deposit.mod(delta);
  let intermediateDiff = deposit.minus(deposit.minus(depositByDeltaRemainder));

  let finalResult = new BigNumber(deposit).minus(intermediateDiff)

  return finalResult
}

function saveSessionRequest(requestData, isFinal) {
  let csrftoken = $("#request-session input[name='csrfmiddlewaretoken']").val();

  $.ajax({
    type: 'post',
    url: '',
    processData: false,
    contentType: false,
    data: requestData,
    headers: {'X-CSRFToken': csrftoken},
    success: json => {
      if (isFinal) {
        if (json.url) {
          document.suppress_loading_leave_code = true;
          window.location = json.url;
        } else {
          console.error('Session request failed to save');
        }
      }
    },
    error: () => {
      console.error('Session request failed to save');
      _alert({ message: gettext('Session request failed to save.') }, 'error');
    }
  });
}

// utility function for returning a promise that resolves after a delay
// https://stackoverflow.com/a/6921279/6784817
function delay(t) {
    return new Promise(function (resolve) {
        setTimeout(resolve, t);
    });
}

Promise.delay = function (fn, t) {
    // fn is an optional argument
    if (!t) {
        t = fn;
        fn = function () {};
    }
    return delay(t).then(fn);
}

Promise.prototype.delay = function (fn, t) {
    // return chained promise
    return this.then(function () {
        return Promise.delay(fn, t);
    });
}
