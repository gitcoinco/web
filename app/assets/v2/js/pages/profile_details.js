var renderKudos = function(kudos){
  // Input is a kudos object array obtained from the Django Kudos API.
  // let numKudos = kudos.length;
  // console.log(numKudos);

  let kudosContainer = document.createElement('div')
  $(kudosContainer).attr('class', 'col-xs-12 col-sm-6 col-lg-3 mb-3')

  let kudosCard = document.createElement('div')
  $(kudosCard).attr('class', 'kd-card kd-extended')

  let kudosLink = document.createElement('a')
  $(kudosLink).attr('href', '/kudos/' + kudos.id)

  let kudosImage = document.createElement('img')
  $(kudosImage).attr('alt', kudos.name).attr('src', '/static/' + kudos.image)
  .attr('class', 'img-thumbnail border-transparent kd-shadow').attr('width', '250')

  let kudosContent = document.createElement('div')
  $(kudosContent).attr('class', 'kd-content')

  let kudosDescription = document.createElement('p')
  $(kudosDescription).html(kudos.description)

  let kudosTitle = document.createElement('div')
  $(kudosTitle).attr('class', 'kd-title').html(kudos.name)

  let kudosListerLink = document.createElement('a')
  $(kudosListerLink).attr('class', 'd-block mb-1').attr('title', kudos.lister).html(kudos.lister)

  $(kudosLink).append(kudosImage)
  $(kudosContent).append(kudosTitle, kudosDescription, kudosListerLink)
  $(kudosCard).append(kudosLink, kudosContent)
  $(kudosContainer).append(kudosCard)
  $('#my-kudos').append(kudosContainer)
}


$(document).ready(function() {
  let address = web3.eth.coinbase;
  console.log(address);
  $.get('/api/v0.1/kudos?lister=' + address, function(results, status) {
    console.log(status)
    console.log(results)
    let numKudos = results.length;
    results.forEach(renderKudos)
    // renderKudos(results)
  })
})