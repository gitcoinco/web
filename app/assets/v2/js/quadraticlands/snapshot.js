// check shapshot.page API if userAddress
// is in a proposal
// true : Interface > unhide nextButton + hide waitingSpinner
// false : Interface > nothing to do

// this parameters come from page

// space name of snapshot.page
// const space = "balancer";
// specific proposal to check all addresses
// const proposal = "QmQpKL29E6ydTvC6p9NoEbTda9ddDkVtWe2YWpWK3NFYqq";
// users eth adress to check if its in addresses
// const userAddress = "0xA95b42B41D84d5CD176df38eFDFA0d8706018F21";

// build api path
const url = 'https://hub.snapshot.page/api/' + space + '/proposal/' + proposal;
// refresh timer in milliseconds
const refresh = 5000;

// trigger check directly on load  ( i hide to simulate both states )
// checkApi();

// trigger refresh ever x seconds
setInterval(checkApi, refresh);

function checkApi() {
  fetch(url)
    .then((response) => response.json())
    .then((data) => {
      console.log(data);

      for (const [address] of Object.entries(data)) {
        if (address == userAddress) {
          console.log('checkAPi : true (userAddress is in Proposal)');
          // hide spinner
          const waitingSpinner = document.getElementById('waitingSpinner');

          waitingSpinner.classList.add('hide');
          // show next button
          const nextButton = document.getElementById('nextButton');

          nextButton.classList.remove('hide');
        }
      }
    });
}
