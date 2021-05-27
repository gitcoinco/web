document.addEventListener('DOMContentLoaded', function() {

  const stewards = document.querySelectorAll('.steward-card');

  // senators address
  const delegate_address = document.getElementById('delegate_address');

  // custom input field
  const custom_delegate_address = document.getElementById('custom_delegate_address');

  // buttons to pick a steward ( one button per steward )
  const btnStewardSelect = document.querySelectorAll('.button-steward-select');

  btnStewardSelect.forEach(steward => {
    steward.addEventListener('click', () => {

      // reset a maybe set custom_delegate_address - as the user want to pick a steward address
      custom_delegate_address.value = '';

      // read adress from data atribute rendered on "delegate" button
      delegate_address.value = steward.dataset.address;
      console.debug('delegate address: ', delegate_address.value);

      // reset current selection (by remove classes from all cards) in interface
      stewards.forEach(steward => {
        steward.classList.remove('selected');
      });

      // select a steward in interface
      delegate = steward.closest('.steward-card');
      delegate.classList.add('selected');

      // enable continue button as user selected a steward
      btn_continue.classList.remove('hide');

    });
  });

  // connect submit button with submit function
  const btn_continue = document.getElementById('btn_continue');

  btn_continue.addEventListener('click', () => {
    submit();
  });


  // check for inputs on the custom_delegate_address input field
  // + remove a picked steward from delegate_address
  // + unselect a picked steward from interface
  // + enable the "continue" button on a valid address

  custom_delegate_address.addEventListener('input', () => {

    // reset current selection of stewards (by remove classes from all cards) in interface
    stewards.forEach(steward => {
      steward.classList.remove('selected');
    });

    // reset the delegate_address as user have a custom address
    delegate_address.value = '';

    // disable the continue button
    btn_continue.classList.add('hide');

    // check if this adress is a valid address

    if (web3.utils.toChecksumAddress(custom_delegate_address.value)) {
      btn_continue.classList.remove('hide');
    } else {
      console.log('no valid address');
    }

  });

});


// save delegate addy to local storage and forward to outro page
function submit() {

  // picked address of a steward
  delegate_address = document.getElementById('delegate_address').value;

  // custom address
  custom_delegate_address = document.getElementById('custom_delegate_address').value;

  if (delegate_address) {
    address = delegate_address;
    console.debug('STEWARD DELEGATE ADDRESS :' + delegate_address);
  }

  if (custom_delegate_address) {
    address = custom_delegate_address;
    console.debug('CUSTOM DELEGATE ADDRESS :' + delegate_address);
  }

  console.debug('delegate address', address);

  // set stewards address to localStorage ( will be used in /receive/claim once )
  localStorage.setItem('stewardsaddress', address);

  // then forward to this url
  window.location = '/quadraticlands/mission/use/outro';

}
