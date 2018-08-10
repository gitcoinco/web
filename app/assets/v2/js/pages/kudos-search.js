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
