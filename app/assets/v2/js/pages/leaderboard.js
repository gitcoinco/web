/* eslint-disable no-invalid-this */

var removeFilter = function() {
  document.location.href = '/leaderboard';
};

$(document).ready(function() {
  var document_url_object = new URL(document.location.href);
  var keyword_search = document_url_object.searchParam && document_url_object.searchParams.get('keyword');

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

  $('.clickable-row').on('click', function(e) {
    if (typeof $(this).data('href') == 'undefined') {
      return;
    }
    window.location = $(this).data('href');
    e.preventDefault();
  });

  $('#key').change(function() {
    const val = $(this).val();

    document.location.href = `/leaderboard/${val}?cadence=` + $('#cadence').val() + '&keyword=' + $('#tech-keyword').val() + '&product=' + $('#product').val();
  });


  $('#cadence').change(function() {

    document.location.href = document.location.pathname + '?cadence=' + $('#cadence').val() + '&keyword=' + $('#tech-keyword').val() + '&product=' + $('#product').val();
  });

  $('#product').change(function() {

    document.location.href = document.location.pathname + '?cadence=' + $('#cadence').val() + '&keyword=' + $('#tech-keyword').val() + '&product=' + $('#product').val();
  });


  $('#tech-keyword').change(function() {
    const keyword = $(this).val();

    if (keyword === 'all') {
      document.location.href = document.location.pathname + '?cadence=' + $('#cadence').val() + '&keyword=&product=' + $('#product').val();

      window.location.href = new_location;
    } else {
      var base_url = window.location.href;

      if (keyword_search) {
        base_url = window.location.href.split('?')[0];
      }

      document.location.href = document.location.pathname + '?cadence=' + $('#cadence').val() + '&keyword=' + $('#tech-keyword').val() + '&product=' + $('#product').val();
    }
  });

  const options = {
    rootMargin: '0px 0px 100px 0px',
    threshold: 0,
  };
  function preloadImage(img) {
    const src = img.getAttribute('data-src');
    if (!src) { return; }
    img.src = src;
  }

  let observer = new IntersectionObserver(function(entries, self) {
    entries.forEach(entry => {
      if(entry.isIntersecting) {
        preloadImage(entry.target);
        self.unobserve(entry.target);
      }
    });
  }, options);

  const imgs = document.querySelectorAll('[data-src]');
  imgs.forEach(img => {
    observer.observe(img);
  });
});
