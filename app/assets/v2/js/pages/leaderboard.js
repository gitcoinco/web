/* eslint-disable no-invalid-this */

var removeFilter = function() {
  document.location.href = '/leaderboard';
};

$(document).ready(function() {
  var document_url_object = new URL(document.location.href);
  var keyword_search = document_url_object.searchParams.get('keyword');
  var order_by = document_url_object.searchParams.get('orderby');

  technologies.forEach(function(tech) {
    if (keyword_search === tech) {
      $('.tech-options').append(`<option value="${tech}" selected>${tech}</option>`);
    } else {
      $('.tech-options').append(`<option value="${tech}">${tech}</option>`);
    }
  });

  $('.leaderboard_entry .progress-bar').each(function() {
    const max = parseInt($(this).attr('aria-valuemax'));
    const now = parseInt($(this).attr('aria-valuenow'));
    const width = (now * 100) / max;

    $(this).css('width', `${width}%`);
  });

  $('.clickable-row').click(function(e) {
    if (typeof $(this).data('href') == 'undefined') {
      return;
    }
    window.location = $(this).data('href');
    e.preventDefault();
  });

  $('#key').change(function() {
    const val = $(this).val();
    const orderBy = $('#orderBy').val();

    document.location.href = `/leaderboard/${val}?orderby=${orderBy}`;
  });

  $('#orderBy').change(function() {
    const val = $('#key').val();
    const orderBy = $(this).val();

    document.location.href = `/leaderboard/${val}?orderby=${orderBy}`;
  });

  $('#tech-keyword').change(function() {
    const keyword = $(this).val();

    if (keyword === 'all') {
      var new_location = window.location.href.split('?')[0];

      window.location.href = new_location + (order_by ? `?orderby=${order_by}` : '');
    } else {
      var base_url = window.location.href;

      if (keyword_search) {
        base_url = window.location.href.split('?')[0];
      }
      const order_by_param = order_by ? `&orderby=${order_by}` : '';

      window.location.href = base_url + `?keyword=${keyword}${order_by_param}`;
    }
  });
});
