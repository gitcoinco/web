
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
// open & close wallet menu.
// this is JUST to SHOW AND HIDE the div "#wallet-provider"
// nothing more nothing less !!!!
const navWallet = document.getElementById("nav-wallet");
const walletProvider = document.getElementById("wallet-provider");
const closeWalletProvider = document.getElementById("close-wallet-provider");

navWallet.addEventListener("click", () => {
  walletProvider.classList.toggle("active");
});

closeWalletProvider.addEventListener("click", () => {
  walletProvider.classList.toggle("active");
});


// as we do not have a provider select anymore in the menu i build
// but use the modal ...  we not have .provider  anymore for all providers...
// but we reuse this class for other menu options...
// on CLICK we wana CLOSE ( toggle ) the menu to not be "active"
// what means its invisible again ...
const navWalletCloseOnClick = document.querySelectorAll(".provider");
navWalletCloseOnClick.forEach(item => {
  item.addEventListener("click", () => {
    walletProvider.classList.toggle("active");
  });
});



// COLLAPSE
//
// find all classes .collapse 
// 
// click div.question
// toggle visibility on div.awnser

const collapse = document.querySelectorAll(".collapse");

collapse.forEach(item => {
	item.addEventListener("click", () => {
		item.classList.toggle("visible");
	});
});




// FLASH MESSAGE
//
// display all kind of errors and messages to a users client


function flashMessage(text, duration=8000){

	const flashMessageContainer = document.getElementById("flashMessageContainer");

	var msg = document.createElement("div");
	msg.innerHTML = text;
	flashMessageContainer.appendChild(msg);

	setTimeout(() => {  
		flashMessageContainer.removeChild(msg);
	}, duration);

}

//test flash message 
//setTimeout(() => {  flashMessage("eine sekunde"); }, 1000);
//setTimeout(() => {  flashMessage("zehn sekunden",10000); }, 3000);
//setTimeout(() => {  flashMessage("zwei sekunden",2000); }, 5000);











