document.addEventListener("DOMContentLoaded",function(){


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


	// inside the wallet menu i reused the .provider class
	// what was initial there to display all providers
	// now with other functions like "change wallet, pick wallet, disconnect"
	// on click of one of these options of the menu
	// the menu itself will disapear by this code.

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

		// on load check if any hash in collapsables to open directly
		if(window.location.hash) {
		  id = window.location.hash.replace('#','')
		  let collapsed = document.getElementById(id);
		  collapsed.classList.add("visible")
		}

		item.addEventListener("click", () => {
			collapse.forEach(item => { item.classList.remove("visible") }) //reset all to invis 
			item.classList.add("visible") // set current visible
			document.getElementById(item.id).scrollIntoView({behavior: 'smooth'})
			history.pushState (null, null, "#"+item.id) // update history
		});

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





// SHORTEN ADRESS
//
// shortens an ETH adress to something like this 0xFFFF…FFFF

function shortenAdress(adress){
	return adress.substring(0,6) + "…" + adress.substr(-4);
}










