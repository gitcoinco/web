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
var resultData;

async  function getSuggestions(tags){
  const kudosHolder = $('#kudos-holder');

  try {
    resultData = await suggestKudos(tags);
    const resu = await fillTmp(resultData);

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
    ${kudosGroup.map((kudos, index) => `
      <div>
      <img src="${static_url + kudos.image}" />
        ${kudos.name_human}
        ${kudos.price_finney} ETH
        <button onclick="fillKudos(${index} )">Add</button>
      </div>
    `).join(" ")}
  `;
}

function createButton() {
  var btnAdd = document.createElement("button");
  btnAdd.innerHTML = "link";
  btnAdd.onclick = function () {
    that.fillKudos(index);
  };
}

$(document).ready(function() {


})

function fillKudos (index) {
  const data = resultData[index]
  console.log(data)

  $('.kudos-search').data('select2')
  .dataAdapter.select(data);
}

var refreshIntervalId = null;
refreshIntervalId = setInterval(checkVariable, 1000);

  function checkVariable() {
    console.log('test')

    if (typeof result !== "undefined") {
      clearInterval(refreshIntervalId);
      bountyKeywords = result.keywords.split(',')

      getSuggestions(bountyKeywords[0])
    }
  }

