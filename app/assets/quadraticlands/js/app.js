/** 
// BURGER MENU
//
// open & close burger menu
const nav = document.querySelector('#nav-links ul');
const burger = document.getElementById("burger");

burger.addEventListener("click", () => {
  nav.classList.toggle("active");
});




// WALLET MENU
//
// open & close wallet menu
const navWallet = document.getElementById("nav-wallet");
const walletProvider = document.getElementById("wallet-provider");
const closeWalletProvider = document.getElementById("close-wallet-provider");

navWallet.addEventListener("click", () => {
  walletProvider.classList.toggle("active");
});

closeWalletProvider.addEventListener("click", () => {
  walletProvider.classList.toggle("active");
});


// PROVIDER SELECT
//
// i know its a bit repeatable code
// it is just here to see how things look.
// as i do not know how hard and different it is
// to integrate different providers, i picked a
// bit a repititiv code over a for each -
// so you can do custom things based on each provider

const providerMetamask = document.getElementById("providerMetamask");
const providerWalletconnect = document.getElementById("providerWalletconnect");
const providerPortis = document.getElementById("providerPortis");
const providerFortmatic = document.getElementById("providerFortmatic");
const providerAuthereum = document.getElementById("providerAuthereum");
const providerDisconnect = document.getElementById("providerDisconnect");


// had to technical split providerIcon and noproviderIcon as 
// providerIcons are embeded as img with src that change with this code.
// but noproviderIcon ( the neon blinked wallet ) is an inline svg with animations
// that simply hides if there is a provider selected.
// what also means that provider icons have to hide when no provider is selected.
// i explained in first providerMetamask ...
const providerIcon = document.getElementById("providerIcon").firstElementChild;
const noproviderIcon = document.getElementById("noproviderIcon");


providerMetamask.addEventListener("click", () => {
  //show custom provider icon
  providerIcon.classList.remove("hide");
  //change img source of providerIcon
  providerIcon.src="/static/quadraticlands/images/provider/metamask.svg"; 
  //hide default wallet icon (noprovider)
  noproviderIcon.classList.add("hide"); 
  //close walletProvider menu
  walletProvider.classList.toggle("active"); 
});

providerWalletconnect.addEventListener("click", () => {
  providerIcon.classList.remove("hide");
  providerIcon.src="/static/quadraticlands/images/provider/walletconnect.svg";
  noproviderIcon.classList.add("hide");
  walletProvider.classList.toggle("active");
});

providerPortis.addEventListener("click", () => {
  providerIcon.classList.remove("hide");
  providerIcon.src="/static/quadraticlands/images/provider/portis.svg";
  noproviderIcon.classList.add("hide");
  walletProvider.classList.toggle("active");
});

providerFortmatic.addEventListener("click", () => {
  providerIcon.classList.remove("hide");
  providerIcon.src="/static/quadraticlands/images/provider/fortmatic.svg";
  noproviderIcon.classList.add("hide");
  walletProvider.classList.toggle("active");
});

providerAuthereum.addEventListener("click", () => {
  providerIcon.classList.remove("hide");
  providerIcon.src="/static/quadraticlands/images/provider/authereum.svg";
  noproviderIcon.classList.add("hide");
  walletProvider.classList.toggle("active");
});

providerDisconnect.addEventListener("click", () => {
  providerIcon.classList.add("hide"); // hide provider icon
  providerIcon.src=""; //reset source of provider icon image
  noproviderIcon.classList.remove("hide"); // show default noproviderIcon 
  walletProvider.classList.toggle("active"); // hide walletProvider menu
});

*/