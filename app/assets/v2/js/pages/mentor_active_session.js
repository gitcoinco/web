// TODO: capitalization
const two_digit = n => ('0' + n).slice(-2)
const selectScreen = screen => {
	[
		$('.main'),
		$('.create-stream'),
		$('.wait'),
		$('.wait-stream'),
		$('.wait-stream-register')
	].map(screen => screen.hide());
	screen.show();
}

const resetScreen = (room_address, address) => {
	if (room_address.toLowerCase() === address.toLowerCase()) {
		selectScreen($('.wait'));
	} else {
		selectScreen($('.create-stream'));
	}
}

// Test DAI have 18 decimals
const TESTDAI_DECIMAL = Math.pow(10, 18);
// Waiting time between approval and attempting to call the contract (in ms)
const CONFIRMATION_WAIT_TIME = 30000;
// Delay before stream startTime (in s)
const STREAM_START_TIME_DELAY = 120;

// Find the closer multiple
const closerMultiple = (deposit, delta) => deposit - (deposit % delta);
// Show an element if a condition is filled, hide it otherwise
const showIf = (condition, element) =>
  condition ? element.show() : element.hide();

const startEarningRefresh = function(stream, address) {
	console.log('yo')
  const { startTime, stopTime } = stream;
  const refresh = setInterval(() => {
    const now = Math.round(new Date().getTime() / 1000);
    const diff = now - startTime;;

    $(".diff .min").text(two_digit(Math.floor(diff / 60)));
    $(".diff .sec").text(two_digit(diff % 60));

    const total = stopTime - startTime;
    $(".total .min").text(two_digit(Math.floor(total / 60)));
    $(".total .sec").text(two_digit(total % 60));

    const depositDai = stream.deposit / TESTDAI_DECIMAL;
    $(".deposit-dai").text(depositDai.toFixed(2));

    const streamedDai = ((diff / total) * deposit) / TESTDAI_DECIMAL;
    $(".streamed-dai").text(streamedDai.toFixed(2));

		if(now > stopTime) {
			resetScreen(room_address, address);
		}

  });
};

const startStreamCountdown = function(stream, address) {
  const { startTime, stopTime } = stream;
  const countDown = setInterval(() => {
    const now = Math.round(new Date().getTime() / 1000);
    const diff = startTime - now;
    const diffMin = Math.floor(diff / 60);
    const diffSec = diff % 60;
    $(".wait-stream .min").text(two_digit(diffMin));
    showIf(diffMin > 0, $(".wait-stream .if-min"));
    $(".wait-stream .sec").text(two_digit(diffSec));
		console.log('now', now);
		console.log('stopTime', stopTime);
    if (now > startTime) {
			selectScreen($('.main'));
      clearInterval(countDown);
      startEarningRefresh(stream, address);
    }
  }, 1000);
};

$(document).ready(function() {
  // Connect the videoplayer

  /*
			const domain = 'meet.jit.si';
			const options = {
					roomName: room_address,
					width: 700,
					height: 700,
					parentNode: document.querySelector('#jitsy-placeholder')
			};
			const api = new JitsiMeetExternalAPI(domain, options);
			*/

  ethereum.enable().then(([address]) => {
    // Pool to recover stream from Sablier API

    console.log("address", address);
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
			}
		`;

    console.log("query", query);

    const pooling = setInterval(() => {
			console.warn('fetching');
      fetch(
        "https://api.thegraph.com/subgraphs/name/sablierhq/sablier-rinkeby",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query })
        }
      )
        .then(answer => answer.json())
        .then(answer => {
          console.log("answer", answer);
          // Find if there's a next stream
          if (answer.data.streams.length) {
            const now = Math.round(new Date().getTime() / 1000);
            const streams = answer.data.streams.sort(
              (a, b) => a.startTime < b.startTime
            );
            console.log("streams", streams);

            const ongoingStream = streams.find(
							stream => stream.startTime < now && now < stream.stopTime
            );
            console.log("ongoingStream", ongoingStream);

            if (ongoingStream) {
              // TODO: Check if the user is the sender or the reciever
              // of the stream
              startEarningRefresh(ongoingStream, address);
              clearInterval(pooling);
							selectScreen($('.main'))
            }

            const nextStream = streams.find(stream => stream.startTime > now);
            console.log("nextStream", nextStream);

            if (nextStream) {
              startStreamCountdown(nextStream);
              clearInterval(pooling);

							console.log('wait-stream loading')
							selectScreen($('.wait-stream'));
            }
          }
        });
    }, 10000);

    // Check if the user is the room owner
		resetScreen(room_address, address)

    // Load contracts

    const sablier_contract = web3.eth
      .contract(sablier_abi)
      .at(sablier_address());
    const testdai_contract = web3.eth.contract(token_abi).at(testdai_address());

    // Create the stream

    $(".create-btn").click(() => {
      const depositMin = parseInt($("#deposit").val());
      if (depositMin === NaN) return;
      // TODO: show an error message

      const mentor_address = room_address;

      // Compute a deposit_rounded (deposit should be a multiple of delta)
      const now = Math.round(new Date().getTime() / 1000);
      const startTime = now + STREAM_START_TIME_DELAY;
      const stopTime = now + STREAM_START_TIME_DELAY + (depositMin * 60);
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
					selectScreen($('.wait-stream-register'));
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
    });

    // Stop the stream
    // TODO: react to button click

    $("stop-stream-btn").click(() => {
      sablier_contract.cancelStream(currentStream.id, () => {
				resetScreen(room_address, address);
      });
    });

    // Withdraw money
    $("withdraw-btn").click(() => {
      // TODO: show a dialog to ask how much to withdraw
      const sum = parseInt($("withdraw-btn-show").val());
      sablier_contract.takeEarnings(address, sum, () => {
        // 	TODO: show a dialog to signal the user fund
        //	have been withdrawn
      });
    });
  });
});
