const grants = {};

grants.search = () => {
  $('#grants__search--text').on('click', event => {
    event.preventDefault();
    if ($('#grants__search--text').val())
      $('#close-icon').show();
    else
      $('#close-icon').hide();
  });

  $('#grants__search--text').on('input', () => {
    if ($('#grants__search--text').val())
      $('#close-icon').show();
    else
      $('#close-icon').hide();
  });

  $('#close-icon').on('click', () => {
    $('#grants__search--text').val('');
    $('#close-icon').hide();
  });

  $('#search__grant').on('click', event => {
    event.preventDefault();
    const filter = $('#grants__search--text').val();

    window.history.pushState('', '', '/grants?q=' + filter);
    if (grants.search_request && grants.search_request.readyState !== 4) {
      grants.search_request.abort();
    }

    const url = '/grants?q=' + filter;

    grants.search_request = $.get(url, (results, status) => {
      // TODO : Repaint Grants
    });
  });
};

grants.sort = () => {
  $('#sort_option').select2({
    minimumResultsForSearch: Infinity
  });
  $('.select2-selection__rendered').removeAttr('title');
};

$(document).ready(() => {
  let keywords = getParam('q');

  if (keywords)
    $('#grants__search--text').val(keywords);

  grants.search();
  grants.sort();
});