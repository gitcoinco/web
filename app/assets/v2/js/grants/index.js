$(document).ready(() => {
  $('#sort_option').select2({
    minimumResultsForSearch: Infinity
  });

  $('#network').select2({
    minimumResultsForSearch: Infinity
  });

  searchGrant();
  populateFilters();

  $('.select2-selection__rendered').removeAttr('title');

  $('.flip-card').on('click keypress', e => {
    if ($(e.target).is('a') || $(e.target).is('img')) {
      e.stopPropagation();
      return;
    }
    $(e.currentTarget).toggleClass('turn');
  });

  waitforWeb3(() => {
    let _network = $('#grant-network').html();

    $('#sub_tx_link').attr('href', etherscan_tx_url($('#sub_tx_link').attr('href'), _network));
    $('#tx_link').attr('href', etherscan_tx_url($('#tx_link').attr('href'), _network));
    $('#cancel_tx_link').attr('href', etherscan_tx_url($('#cancel_tx_link').attr('href'), _network));
  });

});

const searchGrant = () => {
  $('#sort_option').on('change', function(e) {
    updateParams('sort_option', $('#sort_option').val());
  });

  $('#network').on('change', function(e) {
    updateParams('network', $('#network').val());
  });

  $('#search_form').on('submit', (e) => {
    e.preventDefault();
    updateParams('keyword', $('#keyword').val());
  });
};

const populateFilters = () => {
  const sort = getURLParams('sort_option');
  const network = getURLParams('network');
  const keyword = getURLParams('keyword');

  if (sort)
    $('#sort_option').val(getURLParams('sort_option')).trigger('change');
  if (network)
    $('#network').val(getURLParams('network')).trigger('change');
  if (keyword)
    $('#keyword').val(keyword);
};
