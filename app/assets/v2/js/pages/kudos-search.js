/* eslint-disable no-div-regex */

$(document).ready(function() {

  $(".kd-card ").hover(function(){
    var id = $(this).find('img').data('id');
    var selector = ".kudos-" + id;
    console.log(selector);
    var cssSelector = anime({
      targets: selector,
      rotate: 5,
      duration: 100,
    });
  }, function(){
    var id = $(this).find('img').data('id');
    var selector = ".kudos-" + id;
    console.log(selector);
    var cssSelector = anime({
      targets: selector,
      rotate: 0,
      duration: 100,
    });
  });

  var queryParam = getQueryParams(document.location.search);
  var clearBtn = $('.clear-search');

  if (queryParam && queryParam.q) {
    $('#kudos-search').val(queryParam.q);
    clearBtn.removeClass('hidden');
  }

  if (queryParam && queryParam.order_by) {
    $('#sort_order').val(queryParam.order_by);
  }

  $('#sort_order').change(function() {
    if (queryParam && queryParam.q) {
      window.location.search = '?q=' + queryParam.q + '&order_by=' + $(this).val();
    } else {
      window.location.search = '?order_by=' + $(this).val();
    }

  });
});

function getQueryParams(query) {
  if (!query.length) {
    return;
  }

  var search = query.substring(1);
  var myJson = {};
  var hashes = search.split('&');

  for (var i = 0; i < hashes.length; i++) {
    hash = hashes[i].split('=');
    myJson[hash[0]] = hash[1];
  }
  return myJson;
}
