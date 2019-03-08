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

        if (!response[0].copy) {
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
    resultData = await suggestKudos(tags, 15);

    if (!resultData.length) {
      resultData = await suggestKudos(auto_terms, 4);
    }
    const shuffledData = shuffleArray(resultData);

    fillTmp(shuffledData);

  } catch (error) {
    // return error;
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
      <a class="scroll-carousel__item" id="kudos-${kudos.id}" onclick="fillKudos(${index}, this )">
        <img class="scroll-carousel__img" src="${static_url + kudos.image}" />
        <div class="scroll-carousel__text">
          ${kudos.name_human}
          ${kudos.price_finney} ETH
        </div>
      </a>
    `).join(' ')}
  `;
}

function fillKudos(index, e) {
  const data = resultData[index];

  $('.scroll-carousel__item').not(e).removeClass('selected');
  $(e).toggleClass('selected');
  $('.kudos-search').data('select2').dataAdapter.select(data);
}

$('.kudos-search').on('select2:select select2:unselecting', function(e) {
  $('.scroll-carousel__item').removeClass('selected');

  if (e.params._type === 'select') {
    const kudoId = e.params.data.id;

    $('#kudos-' + kudoId).toggleClass('selected');
  }
});

function checkVariable() {
  bountyKeywords = $('input[name=keywords]').val().split(',');
  waitforWeb3(function() {
    getSuggestions(bountyKeywords);
    console.log(bountyKeywords);
  });
}
$(document).ready(function() {
  checkVariable();
});
