// security token
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

document.addEventListener('DOMContentLoaded', function() {

  const inputs = document.querySelectorAll('input');

  /** ********* VIEW ON LOAD */
  updateInterface('voting');

  /** ********* VIEW:VOTING > INPUT FIELD CHANGE EVENT */
  inputs.forEach(i => {

    i.addEventListener('focus', (event) => {
      // reset all options to not have class .active
      document.querySelectorAll('.option').forEach(r => {
        r.classList.remove('active');
      });
      // set parent div.option to class .active
      event.target.parentNode.parentNode.classList.add('active');
    });

    // input validate
    i.addEventListener('input', input => {

      if (isNaN(i.value)) {
        i.value = 0;
      }
      if (i.value <= 0) {
        i.value = 0;
      }
      if (i.value >= 100) {
        i.value = 100;
      }

      let usedPercent = 0;

      // select all not current inputs to see usedPercent so far
      let inputs = document.querySelectorAll('.option:not(.active) input');

      inputs.forEach(i => {
        usedPercent = parseInt(usedPercent) + parseInt(i.value);
      });

      let availablePercent = 100 - usedPercent;

      // users input will be more than availablePercent
      if (i.value >= availablePercent) {
        i.value = availablePercent;
      }

      // update background percent bar on this user input
      let bar = document.querySelector('.option.active div.bar');

      bar.style.width = i.value + '%';

      // update % left status in nav ( bottom right)
      let used = (100 - usedPercent) - i.value;
      let interfaceAvailablePercentSpan = document.querySelector('#availablePercent span');

      interfaceAvailablePercentSpan.innerHTML = used;

      // user spend 100% > show button to vote
      let btnVoting = document.getElementById('btnVoting');
      let interfaceAvailablePercent = document.getElementById('availablePercent');

      if (used == 0) {
        btnVoting.classList.remove('hide');
        interfaceAvailablePercent.classList.add('hide');
      } else {
        btnVoting.classList.add('hide');
        interfaceAvailablePercent.classList.remove('hide');
      }

      // update global progressbar (separator)
      let free = Math.abs(used - 100);
      const progressbar = document.getElementById('progressbar');

      progressbar.style.width = free + '%';

    });

  });


  /** ********* VIEW:VOTING > OPTION CLICK EVENT */
  // additional helper to enable a click on any .option
  // to focus its related child input field

  const options = document.querySelectorAll('.option');

  options.forEach(o => {
    o.addEventListener('click', () => {
      let input = o.querySelector('input');

      input.focus();
      input.select();
    });
  });

  /** ********* VIEW:VOTING > BUTTON TO SUBMIT */
  const btnVoting = document.getElementById('btnVoting');

  btnVoting.addEventListener('click', () => {
    const inputs = document.querySelectorAll('input');
    const selection = {};

    inputs.forEach(i => {
      selection[i.name] = i.value;
    });

    // submit function with users selection
    submit();

  });
});

/** ********* VIEWS */
function updateInterface(status) {

  // views
  const interfaceVoting = document.getElementById('voting');

  // hide all views
  interfaceVoting.classList.add('hide');

  // hide all things in nav bar that might change based on view
  let btnStart = document.getElementById('btnStart');

  btnStart.classList.add('hide');

  let availablePercent = document.getElementById('availablePercent');

  availablePercent.classList.add('hide');

  // update interface based on interface status
  if (status == 'voting') {
    interfaceVoting.classList.remove('hide');
    availablePercent.classList.remove('hide');
    // flashMessage("UP/DOWN key's to quickly distribute your voting power",8000);
  }

  if (status == 'success') {
    // forward
    window.location = '/quadraticlands/mission/use/outro';
  }
}


/** ******* SUBMIT VOTE */
function submit() {

  const primaryType = 'CastVote';
  const domain = { name: 'GTCVote', chainId: 4, verifyingContract: '0xc00e94Cb662C3520282E6f5717214004A7f26888' };

  types = build_types();
  message = build_message();
  msgParams = JSON.stringify({ types, primaryType, domain, message });

  web3.currentProvider.sendAsync(
    {
      method: 'eth_signTypedData_v4',
      params: [ selectedAccount, msgParams ],
      from: selectedAccount
    },
    async(err, result) => {
      if (err) {
        if (err.code == '4001') {
          console.debug('User canceled Sig');
        }
        console.error('ERROR', err);
        return;
      } else if (result.error) {
        console.error('ERROR', result.error.message);
        return;
      }
      const signature = result.result.substring(2);
      const r = '0x' + signature.substring(0, 64);
      const s = '0x' + signature.substring(64, 128);
      const v = parseInt(signature.substring(128, 130), 16);

      save_vote(signature, r, s, v, msgParams);

    }
  );
}

function save_vote(sig, r, s, v, full_vote_msg) {
  var saveVoteSig = fetchData('/quadraticlands/vote', 'POST', {
    'sig': sig,
    'r': r,
    's': s,
    'v': v,
    'full_vote_msg': full_vote_msg
  }, { 'X-CSRFToken': csrftoken });

  $.when(saveVoteSig).then((response, status, statusCode) => {
    updateInterface('success');
  }).catch((error) => {
    console.error('There was an issue saving your vote', error);
  });
}

function build_types() {
  votes = castVote();
  const types = {
    EIP712Domain: [
      { name: 'name', type: 'string' },
      { name: 'chainId', type: 'uint256' },
      { name: 'verifyingContract', type: 'address' }
    ],
    CastVote: votes
  };

  return types;
}

// helper to build the CastVote types struct
function castVote() {
  let vote = [];
  let inputs = document.querySelectorAll('input');

  inputs.forEach(i => {
    if (i.name != 'csrfmiddlewaretoken') {
      vote.push({ 'name': i.name, 'type': 'uint256' });
    }
  });

  return vote;
}

// helper to build the message Object
function build_message() {
  let _message = {};
  let inputs = document.querySelectorAll('input');

  inputs.forEach(i => {
    if (i.name != 'csrfmiddlewaretoken') {
      _message[i.name] = i.value;
    }
  });
  return _message;
}
