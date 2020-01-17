const closer_multiple = (deposit, delta) => deposit - (deposit % delta);

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

  $(".main").hide();

  ethereum.enable().then(address => {
    // Check if the stream is ongoing

    const query = `
					{
						streams (where:{recipient: "${address}"}) {
							id
							deposit
							sender
							recipient
						}
					}
				`;

    setInterval(() => {
      fetch("https://api.thegraph.com/subgraphs/name/sablierhq/sablier", {
        method: "POST",
        body: query
      }).then(answer => {
        if (answer.data.streams.length) {
          // Check beginning and end
          // Show the stream
          $(".main").show();
          // Hide the form and the waiting message
          $(".out").hide();
        }
      });
    }, 10000);

    // Check if the user is the room owner
    console.warn("room_address == address", room_address === address);
    if (room_address === address) {
      $(".wait").show();
    } else {
      $(".create-stream").show();
    }

    // Create the stream

    $(".create-btn").click(() => {
      const deposit_min = parseInt($("#deposit").val());
			if(deposit_min === NaN) return;

      const sablier_contract = web3.eth
        .contract(sablier_abi)
        .at(sablier_address());
      const testdai_contract = web3.eth
        .contract(token_abi)
        .at(testdai_address());

      const mentor_address = room_address;

      // Compute a deposit_rounded (deposit should be a multiple of delta)
      const deposit = deposit_min * rate_per_min;
      const deposit_rounded = closer_multiple(deposit);
      const now = Math.round(new Date().getTime() / 1000);
      const startTime = now + 3600;
      const stopTime = now + 3600 * 2;
      const delta = stopTime - startTime;

      if (deposit_rounded % delta) throw "Not multiple";

      console.warn("mentor_address", mentor_address);

      console.warn("deposit", deposit);
			console.warn("deposit in dai", deposit / 1000000000000000000);
      console.warn("now", now);
      console.warn("startTime", startTime);
      console.warn("stopTime", stopTime);

      testdai_contract.approve(sablier_address(), deposit, () => {
        setTimeout(() => {
          console.warn(
            "creating the stream at ",
            Math.round(new Date().getTime() / 1000)
          );
          sablier_contract.createStream(
            mentor_address,
            deposit,
            testdai_address(),
            startTime,
            stopTime,
            () => {
              // Wait for the beginning of the stream
              console.warn("DONE", Math.round(new Date().getTime() / 1000));
            }
          );
        }, 30000);
      });
    });

    // Update data during streaming

    // Stop the stream

    // Withdrawn money
  });
});
