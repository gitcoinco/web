 function suggestKudos(tags){
  const url = '/api/v0.1/kudos_search/';
  let query = {
    term: tags,
    network: document.web3network
  };
  return new Promise(resolve => {
    const kudos = fetchData(url, 'GET', query)

    $.when(kudos).then(response => {
      resolve(response)
    })
  });
}
// get tags
// request for each tag until quantify
// return array with kudos data

async  function getSuggestions(tags){
  const kudosHolder = $('#kudos-holder');
  try {
    const resultData = await suggestKudos(tags);
    console.log(resultData)

    const resu = await fillTmp(resultData)
    function fillTmp(results){
      let template = `<div>
        ${templateSuggestions(results)}
      </div>`;
      kudosHolder.html(template);

    }
  } catch(error) {
    console.log(error);
  }
}


function templateSuggestions(kudosGroup) {
  return `
    ${kudosGroup.map(kudos => `
      <div>
      <img src="${static_url + kudos.image}" />
        ${kudos.name_human}
        ${kudos.price_finney} ETH
        <button onclick="fillKudos('${kudos.name_human}', '${kudos.id}', ${kudos})">Add</button>
      </div>
    `).join(" ")}
  `;
}

$(document).ready(function() {
  getSuggestions('front')

})

function fillKudos (name, id,kudos) {
  console.log(name, id)
  var newOption = new Option(name, id, false, true);

  $('.kudos-search').append(newOption).trigger('change');
  $('.kudos-search').trigger({
    type: 'select2:select',
    params: {
        data: kudos
    }
  });
}
