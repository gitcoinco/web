$(document).ready(function() {
  var queryParam = getParameterByName('q')

  $('#kudos-search').val(queryParam)
  checkSearch()
})
var searchInput = $('#kudos-search')
var clearBtn = $('.clear-search')

searchInput.change(  function () {
  checkSearch()
})
function checkSearch(){
  console.log('test')
  if (searchInput.val() === '') {
    clearBtn.addClass('hidden')
  } else {
    clearBtn.removeClass('hidden')
  }
}

function getParameterByName(name) {
  name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
  var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
      results = regex.exec(location.search);
  return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}


function getQueryParams(qs) {
    qs = qs.split('+').join(' ');

    var params = {},
        tokens,
        re = /[?&]?([^=]+)=([^&]*)/g;

    while (tokens = re.exec(qs)) {
        params[decodeURIComponent(tokens[1])] = decodeURIComponent(tokens[2]);
    }

    return params;
}
$(document).ready(function(){


  var query = getQueryParams(document.location.search);

  if (query.order_by) {
    console.log(query.order_by)
    $('#sort_order').val(query.order_by)
  }

  $('#sort_order').change(function(){
      var query = getQueryParams(document.location.search);
      // window.location.href = window.location.href + '?order_by=' + $(this).val();
      if (query.q) {
        window.location.search = '?q=' + query.q + '&order_by=' + $(this).val();
      } else {
        window.location.search = '?order_by=' + $(this).val();
      }

  });
});
