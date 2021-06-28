document.addEventListener('DOMContentLoaded', function() {
  // BURGER MENU -  open & close
  const nav = document.querySelector('#nav-links ul');
  const burger = document.getElementById('burger');

  burger.addEventListener('click', () => {
    nav.classList.toggle('active');
  });

  // WALLET MENU
  // open & close wallet menu
  // this is JUST to SHOW AND HIDE the div "#wallet-provider"
  // nothing more nothing less !!!!

  const navbarDropdownWallet = document.getElementById('navbarDropdownWallet');
  const walletProvider = document.getElementById('wallet-provider');
  const closeWalletProvider = document.getElementById('close-wallet-provider');

  if (navbarDropdownWallet) {
    navbarDropdownWallet.addEventListener('click', () => {
      console.log('click');
      walletProvider.classList.toggle('active');
    });

    closeWalletProvider.addEventListener('click', () => {
      walletProvider.classList.toggle('active');
    });
  }

  // make noprovider icon also open the menue.
  const noproviderIcon = document.getElementById('noproviderIcon');

  noproviderIcon.addEventListener('click', () => {
    console.log('noprovider');
    walletProvider.classList.toggle('active');
  });


  // inside the wallet menu i reused the .provider class
  // what was initial there to display all providers
  // now with other functions like "change wallet, pick wallet, disconnect"
  // on click of one of these options of the menu
  // the menu itself will disappear by this code.

  const navWalletCloseOnClick = document.querySelectorAll('.provider');

  navWalletCloseOnClick.forEach((item) => {
    item.addEventListener('click', () => {
      walletProvider.classList.toggle('active');
    });
  });
});

// FLASH MESSAGE - display all kind of errors and messages to a users client
function flashMessage(text, duration = 8000) {
  const flashMessageContainer = document.getElementById(
    'flashMessageContainer'
  );

  var msg = document.createElement('div');

  msg.innerHTML = text;
  flashMessageContainer.appendChild(msg);

  setTimeout(() => {
    flashMessageContainer.removeChild(msg);
  }, duration);
}

// init a synth and add map data-attributes
// to play sounds on click
function initToneJs() {
  var synth = new Tone.Synth().toDestination();

  console.debug('Init SFX');

  // random tone
  toneClickRandom = document.querySelectorAll('[data-tone-click-random]');
  toneClickRandom.forEach((tone) => {
    tone.addEventListener('click', () => {
      key = [ 'c', 'd', 'e', 'f', 'g', 'a', 'b' ]
        .sort(() => Math.random() - Math.random())
        .slice(0, 1);
      octave = getRandomInt(2, 5);
      lenght = getRandomInt(8, 64);
      synth.triggerAttackRelease(key + octave, lenght + 'n');
    });
  });
}

function getRandomFloat(min, max) {
  return Math.random() * (max - min) + min;
}

function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min);
}
