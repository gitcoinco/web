// TODO: capitalization

// Global state
let currentStream = null;
let jitsy = null;
let address = null;

// Utils
const two_digit = n => ("0" + n).slice(-2);

const selectScreen = screen => {
  [
    $(".main"),
    $(".create-stream"),
    $(".wait"),
    $(".wait-stream"),
    $(".wait-stream-deletion"),
    $(".wait-stream-register"),
    $(".wait-metamask"),
    $(".stream-busy")
  ].map(screen => screen.hide());
  screen.show();
};

const resetScreen = () => {
  if (room_address.toLowerCase() === address.toLowerCase()) {
    selectScreen($(".wait"));
		$('.withdran-btn').show();
  } else {
    selectScreen($(".create-stream"));
		$('.withdran-btn').hide();
  }
};

$('#depositDescribe').hide()	
const updatePrice = () => {
	const value = $('#deposit').val();
	const depositMin = parseInt(value);
	if(depositMin === NaN) {
		$('#depositDescribe').hide()	
	}
	else {
		$('#depositDescribe').show()	
		const depositDai = depositMin * rate_per_min / TESTDAI_DECIMAL;
		$('.deposit-dai').text(depositDai.toFixed(2));
		$('.deposit-rate').text(rate_per_min / TESTDAI_DECIMAL);
	}
}

$('#deposit').keyup(updatePrice).change(updatePrice);

// Test DAI have 18 decimals
const TESTDAI_DECIMAL = Math.pow(10, 18);
// Waiting time between approval and attempting to call the contract (in ms)
const CONFIRMATION_WAIT_TIME = 25000;
// Delay before stream startTime (in s)
const STREAM_START_TIME_DELAY = 120;

// Find the closer multiple
const closerMultiple = (deposit, delta) => deposit - (deposit % delta);
// Show an element if a condition is filled, hide it otherwise
const showIf = (condition, element) =>
  condition ? element.show() : element.hide();

// Load contracts

const sablier_contract = web3.eth.contract(sablier_abi).at(sablier_address());
const testdai_contract = web3.eth.contract(token_abi).at(testdai_address());

// Start the main session loop
const startEarningRefresh = function() {
  const { startTime, stopTime } = currentStream;
  const refresh = setInterval(() => {
    const now = Math.round(new Date().getTime() / 1000);
    const diff = now - startTime;

    $(".diff .min").text(two_digit(Math.floor(diff / 60)));
    $(".diff .sec").text(two_digit(diff % 60));

    const total = stopTime - startTime;
    $(".total .min").text(two_digit(Math.floor(total / 60)));
    $(".total .sec").text(two_digit(total % 60));

    // TODO: not working
    const depositDai = currentStream.deposit / TESTDAI_DECIMAL;
    $(".deposit-dai").text(depositDai.toFixed(2));
		console.log('diff', diff);
		console.log('total', total);
		console.log('depositDai', depositDai)
    const streamedDai = ((diff / total) * depositDai) / TESTDAI_DECIMAL;
		console.log('streamedDai',streamedDai)	
    $(".streamed-dai").text(streamedDai.toFixed(2));
		$('.progress-bar').css('width', `${diff / total}%`);

    if (now > stopTime) {
      console.log("address", address);
      console.log("room_address", address);
      resetScreen();
      destroyJitsy();
      startAPIPooling(address);
      clearInterval(refresh);
    }
  });
};

// Start the countdown loop
const startStreamCountdown = function() {
  const { startTime, stopTime } = currentStream;
  const countDown = setInterval(() => {
    const now = Math.round(new Date().getTime() / 1000);
    const diff = startTime - now;
    const diffMin = Math.floor(diff / 60);
    const diffSec = diff % 60;

    $(".wait-stream .min").text(two_digit(diffMin));
    showIf(diffMin > 0, $(".wait-stream .if-min"));
    $(".wait-stream .sec").text(two_digit(diffSec));

    if (now > startTime) {
      selectScreen($(".main"));
      clearInterval(countDown);
      startEarningRefresh();
      initJitsy();
    }
  }, 1000);
};

// Check cancellations before calling the cancelStream contracts
const checkCancellations = function(streamId) {
  const query = `
			{
				cancellations {
					id
				}
			}
		`;

  return fetch(
    "https://api.thegraph.com/subgraphs/name/sablierhq/sablier-rinkeby",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    }
  )
    .then(answer => answer.json())
    .then(answer => answer.data.cancellations.map(stream => stream.id))
    .then(cancelledStreams => cancelledStreams.includes(streamId));
};

const startAPIPooling = function() {
  console.warn("starting fetching");
  // TODO filter cancellations
  const query = `
			{
				streams (where: {recipient: "${room_address}"}) {
					id
					deposit
					sender
					recipient
					startTime
					stopTime
				}
				cancellations {
					id
				}
			}
		`;

  console.log("query", query);
  const pooling = setInterval(() => {
    console.warn("fetching");
    fetch("https://api.thegraph.com/subgraphs/name/sablierhq/sablier-rinkeby", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query })
    })
      .then(answer => answer.json())
      .then(answer => {
        console.log("answer", answer);
        // Find if there's a next stream
        if (answer.data.streams.length) {
          const now = Math.round(new Date().getTime() / 1000);
          const cancelled = answer.data.cancellations.map(stream => stream.id);
          console.log("cancelled", cancelled);
          const streams = answer.data.streams
            .filter(stream => !cancelled.includes(stream.id))
            .sort((a, b) => a.startTime < b.startTime);
          console.log("streams", streams);

          const ongoingStream = streams.find(
            stream => stream.startTime < now && now < stream.stopTime
          );
          console.log("ongoingStream", ongoingStream);

          if (ongoingStream) {
            if (
              ongoingStream.recipient.toLowerCase() === address.toLowerCase() ||
              ongoingStream.sender.toLowerCase() === address.toLowerCase()
            ) {
              currentStream = ongoingStream;
              startEarningRefresh();
              clearInterval(pooling);
              selectScreen($(".main"));
              initJitsy();
            } else {
              selectScreen($(".stream-busy"));
              // TODO what happens next?
            }
          }

          const nextStream = streams.find(stream => stream.startTime > now);
          console.log("nextStream", nextStream);

          if (nextStream) {
						// Contact the API to signal the backend a session have been joined
						join_session(address);
            currentStream = nextStream;
						// Launch the countdown
            startStreamCountdown(nextStream, address);
						// Delete the pooling loop
            clearInterval(pooling);
						//	Open the wait-stream screen
            selectScreen($(".wait-stream"));
          }
        }
      });
  }, 10000);
};

const createStream = () => {
	const depositMin = parseInt($("#deposit").val());
	if (depositMin === NaN) return;
	// TODO: show an error message
	
	selectScreen($(".wait-stream-register"));

	const mentor_address = room_address;

	// Compute a deposit_rounded (deposit should be a multiple of delta)
	const now = Math.round(new Date().getTime() / 1000);
	const startTime = now + STREAM_START_TIME_DELAY;
	const stopTime = now + STREAM_START_TIME_DELAY + depositMin * 60;
	const delta = stopTime - startTime;
	const deposit = depositMin * rate_per_min;
	const deposit_rounded = closerMultiple(deposit, delta);

	console.warn("mentor_address", mentor_address);

	console.warn("deposit", deposit);
	console.warn("deposit_rounded", deposit_rounded);
	console.warn("deposit in dai", deposit / 1000000000000000000);
	console.warn("now", now);
	console.warn("startTime", startTime);
	console.warn("stopTime", stopTime);
	console.warn("delta", delta);

	// if (deposit_rounded % delta) throw "Not multiple";
	if (now > startTime) throw "startTime should be in the future";
	if (startTime > stopTime) throw "stopTime should be after startTime";

	testdai_contract.approve(sablier_address(), deposit, () => {
		setTimeout(() => {
			console.warn(
				"creating the stream at ",
				Math.round(new Date().getTime() / 1000)
			);
			sablier_contract.createStream(
				mentor_address,
				deposit_rounded,
				testdai_address(),
				startTime,
				stopTime,
				() => {
					// Wait for the beginning of the stream
					console.warn("DONE", Math.round(new Date().getTime() / 1000));
				}
			);
		}, CONFIRMATION_WAIT_TIME);
	});
}

// Jitsy-related functions

const cancelStream = () => {
	setTimeout(() => {
		// Check if the stream have already been cancelled from the API
		checkCancellations(currentStream.id).then(cancelled => {
			if (cancelled) {
				// Attempt to signal the API the session have been terminated
				finish_session(room_address);
				jitsy.executeCommand("hangup");
				destroyJitsy();
				resetScreen();
				startAPIPooling(address);
			} else {
				sablier_contract.cancelStream(currentStream.id, () => {
					jitsy.executeCommand("hangup");
					destroyJitsy();
					resetScreen();
					startAPIPooling(address);
				});
			}
		});
	}, CONFIRMATION_WAIT_TIME);
};

const initJitsy = function() {
  // const domain = "meet.jit.si";
  // const options = {
  //   roomName: room_address,
  //   width: 700,
  //   height: 700,
  //   parentNode: document.querySelector("#jitsy-placeholder")
  // };
  // jitsy = new JitsiMeetExternalAPI(domain, options);
	// If the session disconnect, we will attempt to cancel the stream
  jitsy.on("participantLeft", () => {
    console.warn("other participant left the room");
		selectScreen($('.wait-stream-deletion'))
		setTimeout(() => {
			checkCancellations(currentStream.id).then(cancelled => {
				if (cancelled) {
					jitsy.executeCommand("hangup");
					destroyJitsy();
					resetScreen();
					startAPIPooling(address);
				} else {
					sablier_contract.cancelStream(currentStream.id, () => {
						jitsy.executeCommand("hangup");
						destroyJitsy();
						resetScreen();
						startAPIPooling(address);
					});
				}
			});
		}, CONFIRMATION_WAIT_TIME);
  });
};

const destroyJitsy = function() {
  console.log("freeing jitsy");
  jitsy.dispose();
};

selectScreen($('.wait-metamask'))
$(document).ready(function() {
  // Connect the videoplayer

  ethereum.enable().then(([metamask_address]) => {
    // Register address in global variable
    address = metamask_address;

    // Pool to recover stream from Sablier API
    startAPIPooling(address);

    console.log("address", address);

    // Initiate screen
    resetScreen();

    // Create the stream
    $(".create-btn").click(createStream);
		$(".create-retry-btn").click(createStream)
		$(".create-cancel-btn").click(() => {
			selectScreen($('.create-stream'));	
		})

    // Stop the stream

		$(".stop-stream-btn").click(() => {
			selectScreen($('.wait-stream-deletion'))
			sablier_contract.cancelStream(currentStream.id, () => {
				jitsy.executeCommand("hangup");
				destroyJitsy();
				setTimeout(() => {
					resetScreen();
					startAPIPooling(address);
				}, CONFIRMATION_WAIT_TIME);
			});
		});

    // Withdraw money
    $(".withdraw-btn").click(() => {
      // TODO: show a dialog to ask how much to withdraw
      const sum = parseInt($("withdraw-btn-show").val());
      sablier_contract.takeEarnings(address, sum, () => {
        // 	TODO: show a dialog to signal the user fund
        //	have been withdrawn
      });
    });
  });
});

window.onbeforeunload = function(){
	finish_session(room_address);
}
