/* eslint-disable no-div-regex */

$(document).ready(function() {
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

  return JSON.parse('{"' + decodeURI(search).replace(/"/g, '\\"').replace(/&/g, '","').replace(/=/g, '":"') + '"}');
}
