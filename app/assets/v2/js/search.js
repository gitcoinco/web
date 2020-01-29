function search(elem) {
  var selectItem = elem || '#search';

  $(selectItem).each(function() {
    if (!$(this).length) {
      return;
    }
    var name = $(this).attr('name');

    $(this).select2({
      ajax: {
        url: '/api/v0.1/search/',
        dataType: 'json',
        delay: 250,
        data: function(params) {

          let query = {
            term: params.term[0] === '@' ? params.term.slice(1) : params.term
          };

          return query;
        },
        processResults: function(data) {
          return {
            results: data
          };
        },
        cache: true
      },
      theme: 'search',
      placeholder: '<i class="fas fa-search"></i>',
      allowClear: true,
      minimumInputLength: 3,
      escapeMarkup: function(markup) {
        return markup;
      },
      templateResult: formatRow
    });

    // fix for wrong position on select open
    var select2Instance = $(this).data('select2');

    select2Instance.on('results:message', function(params) {
      this.dropdown._resizeDropdown();
      this.dropdown._positionDropdown();
    });

    function formatRow(element) {

      if (element.loading) {
        return element.text;
      }
      var markup;

      markup = `<div data-url="${element.url}" class="d-flex m-2 align-items-center element-search-result search-result">
                      <div style="min-width: 0;width: 100%;">
                        <img class=search__avatar src="${element.img_url}">
                        <div class="d-flex justify-content-between">
                          <div class="element-title search__title">${element.title}</div>
                        </div>
                        <div class="text-truncate element-description search-result__description">${element.description}</div>
                        <div class="element-type tag float-right">View ${element.source_type}</div>
                      <div>
                    </div>`;

      return markup;
    }

    $(selectItem).on('select2:unselecting', function(e) {
      $(this).val(null).trigger('change');
      document.selected_element = null;
      e.preventDefault();
    });
    $(selectItem).on('select2:select', function(e) {
      console.log(e);
      console.log($('#search').val());
      var data = e.params.data;

      console.log(data);
    });
  });
}

$('document').ready(function() {
  $('#search_container').html('<select id=search name="search" class="custom-select gc-border-blue"><option></option></select>');
  search();

  $('body').on('click', '.search_autocomplete', function(e) {
    var search_term = $(this).text();

    e.preventDefault();
  });

  $(document).on ('click', '.element-search-result', function() {
    document.location.href = $(this).data('url');
  });

  $('.select2-nosearch').select2({
    minimumResultsForSearch: 20
  });

  $('.select2-search').select2({});

  // listen for keyups in both input widget AND dropdown
  $('body').on('keyup', '.select2,.select2-dropdown', function(e) {
    var KEYS = { UP: 38, DOWN: 40, ENTER: 13 };
    var $sel = $('.select2.select2-container--open');

    if ($sel.length) {
      var target;

      if (e.keyCode === KEYS.DOWN && !e.altKey) {
        target = $('.select2-results__option.selected');
        if (!target.length) {
          target = $('.select2-results__option:first-child');
        } else if (target.next().length) {
          target.removeClass('selected');
          target = target.next();
        }
        target.addClass('selected');
      } else if (e.keyCode === KEYS.UP) {
        target = $('.select2-results__option.selected');
        if (!target.length) {
          target = $('.select2-results__option:first-child');
        } else if (target.prev().length) {
          target.removeClass('selected');
          target = target.prev();
        }
        target.addClass('selected');
      } else if (e.keyCode === KEYS.ENTER) {
        target = $('.select2-results__option.selected');
        var url = target.find('.search-result').data('url');
        if (target && url) {
          document.location.href = url;
        }
      }
    }

  });


});

