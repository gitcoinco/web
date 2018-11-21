function suggestKudos(tags, kudosQt) {

  var kudosArray = kudosArray || [];
  var processCounter = 0;

  return new Promise(resolve => {
    tags.forEach(tag => {

      const url = '/api/v0.1/kudos_search/';

      let query = {
        term: tag,
        network: document.web3network
      };

      const kudos = fetchData(url, 'GET', query);

      $.when(kudos).then(response => {
        processCounter++;

        if (response.length === 1 && response[0].copy) {
          console.log('error', response);
        } else {
          kudosArray = kudosArray.concat(response);
        }

        if (processCounter === tags.length || kudosArray.length >= kudosQt) {
          resolve(kudosArray);
        }
      });
    });
  });
}

var resultData;
var auto_terms = ['soft skills'];

async function getSuggestions(tags) {
  try {
    resultData = await suggestKudos(tags);

    if (!resultData.length) {
      resultData = await suggestKudos(auto_terms, 4);
    }
    fillTmp(resultData);

  } catch (error) {
    console.log(error);
  }
}

function fillTmp(results) {
  const kudosHolder = $('#kudos-holder');

  let template = `<div class="scroll-carousel">
    ${templateSuggestions(results)}
  </div>`;

  kudosHolder.html(template);
}

function templateSuggestions(kudosGroup) {

  return `
    ${kudosGroup.map((kudos, index) => `
      <div class="scroll-carousel__item">
      <img class="scroll-carousel__img" src="${static_url + kudos.image}" />
        <div class="scroll-carousel__text">
          ${kudos.name_human}
          ${kudos.price_finney} ETH
        </div>
        <button class="scroll-carousel__btn" onclick="fillKudos(${index} )">Add</button>
      </div>
    `).join(' ')}
  `;
}

function fillKudos(index) {
  const data = resultData[index];

  $('.kudos-search').data('select2').dataAdapter.select(data);
}

var refreshIntervalId = setInterval(checkVariable, 1000);

function checkVariable() {
  if (typeof result !== 'undefined') {
    clearInterval(refreshIntervalId);
    bountyKeywords = result.keywords.split(',');
    getSuggestions(bountyKeywords);
  }
}

