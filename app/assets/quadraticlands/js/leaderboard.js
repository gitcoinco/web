// LEADERBOARD 
// - all <th> on page gets clickable to sort by th
// - add data-atributes data-direction="asc" / data-direction="desc" to current clicked
// - read data-by values ( e.g. order-by adress, order-by amount )
// - triggers fetchGraph() function on <th> with all needed values
// - loadmore button to fetch more values
// needs to run after app.js as its using a helper to trunciate the eth adress from it.
// https://thegraph.com/explorer/subgraph/nopslip/wolf-vision?query=VestingGrants

document.addEventListener("DOMContentLoaded",function(){

	let first = 5 // show first X results
	let perpage = 5 // load X more per page
	let th = document.querySelectorAll("th")

	th.forEach(i => {

		i.addEventListener("click", () => {

			if (!i.hasAttribute("data-direction")){
				interfaceResetDirection()
				i.dataset.direction = "desc"
			}
			else{
				if (i.dataset.direction == "asc"){
					interfaceResetDirection()
					i.dataset.direction = "desc"
				}
				else {
					interfaceResetDirection()
					i.dataset.direction = "asc" 
				}
			}

			fetchGraph(i.dataset.by, i.dataset.direction, first)

	  })

	})


	// button to load more results 
	const more = document.getElementById("more");
	more.addEventListener("click", () => {

		// add a "perpage" to first param for thegraph
		first = first + perpage;

		// on "more" button click we still have to know what direction and order by
		th.forEach(i => {
			if (i.hasAttribute("data-direction")){
				by = i.dataset.by
				direction = i.dataset.direction
			}
		})
		
		// fetch on click on th
		fetchGraph(by, direction, first)

	})


	// fetch initial data on load
	fetchGraph("account", "desc", 5)
	
})





// interfaceResetDirection
// on click of a table head reset all the other directions
// to ensure its always just "one" option for an order direction
//
function interfaceResetDirection(){
	let th = document.querySelectorAll("th")
	th.forEach(i => {
		i.removeAttribute('data-direction')
	})
}




// fetchGraph
// connect to API with variables
// and then call render function with returned data
//
function fetchGraph(by, direction, first){

	console.debug("orderBy:" + by)
	console.debug("orderDirection:" + direction)
	console.debug("first:" + first)


	var query = `{
		tokenClaims(
			first: ${first},
			orderBy : ${by},
			orderDirection : ${direction}
			)
		{
			id,
			count,
			user_id,
			account
		}
	}`

	fetch('https://api.thegraph.com/subgraphs/name/nopslip/wolf-vision', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'Accept': 'application/json',
		},
		body: JSON.stringify({query: query})
	})

	.then(response => response.json())

	.then(response => {
		console.log (response.data.tokenClaims)
		render(response.data.tokenClaims)
	})
	
	.catch(err => console.error(err));




}






// render data to tbody
// data comes from thegraph
// position, adress, token_amount, votes, delegates

function render(data){

	console.log("RENDER DATA TO TBODY")

	let total_tokens = 3000000 // max tokens available

	// clear tbody
	let tbody = document.getElementById("tbody");
	tbody.innerHTML = '';

	// for each data add tds
	data.forEach(col => {

		// new row
		var tr = document.createElement("tr"); 

			// account
			var account = document.createElement("td");
			account.innerHTML = '<a href="/quadraticlands/profile/'+col.account+'">'+shortenAdress(col.account)+'</a>'
			tr.appendChild(account)


			// userid
			var userid = document.createElement("td")
			userid.innerHTML = col.user_id
			tr.appendChild(userid)

			// id
			var id = document.createElement("td")
			id.innerHTML = col.id
			tr.appendChild(id)


			/*
			// position
			var position = document.createElement("td");
			position.innerHTML = col.position;
			tr.appendChild(position)

			// account
			var account = document.createElement("td");
			account.innerHTML = '<a href="/quadraticlands/profile/'+col.account+'">'+shortenAdress(col.account)+'</a>'
			tr.appendChild(account)

			// token_amount
			var token_amount = document.createElement("td");
			token_amount.innerHTML = col.token_amount;
			tr.appendChild(token_amount)

			// power ( token_amount / total_tokens )
			var power = document.createElement("td");
			power.innerHTML = ( col.token_amount / total_tokens ) + "%" ;
			tr.appendChild(power)

			// votes
			var votes = document.createElement("td");
			votes.innerHTML = col.votes;
			tr.appendChild(votes)

			// delegates
			var delegates = document.createElement("td");
			delegates.innerHTML = col.delegates;
			tr.appendChild(delegates)

			// delegated_tokens
			var delegated_tokens = document.createElement("td");
			delegated_tokens.innerHTML = col.delegated_tokens;
			tr.appendChild(delegated_tokens)
			*/


		// append new row
		tbody.appendChild(tr)


	})

}


  
