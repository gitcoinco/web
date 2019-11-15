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
            term: params.term[0] === '@' ? params.term.slice(1) : params.term,
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
      templateResult: formatRow,
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

      markup = `<div data-url="${element.url}" class="d-flex m-2 align-items-center element-search-result">
                      <div style="min-width: 0;width: 100%;">
                        <div class="d-flex justify-content-between">
                          <div class="element-title">${element.title}</div>
                        </div>
                        <div class="text-truncate element-description">${element.description}</div>
                      <div>
                    </div>`;

      return markup;
    }

    $(selectItem).on('select2:unselecting', function(e) {
      $(this).val(null).trigger('change');
      document.selected_element = null;
      e.preventDefault();
    });
    $(selectItem).on('select2:selecting', function(e) {
      e.preventDefault();
      alert('todo - forward to this url')
    });
  });
}

$('document').ready(function() {
  $("#search_container").html('<select id=search name="search" class="custom-select gc-border-blue"><option></option></select>');
  search();
  $('body').on('click', '.search_autocomplete', function(e) {
    var search_term = $(this).text();
    select2SiteSearch($(this).parents('.element-module').find('#search'), search_term);
    e.preventDefault();
  });
});

function select2SiteSearch(elem, term, select) {
  elem.select2('open');
  var $search = elem.data('select2').dropdown.$search || elem.data('select2').selection.$search;
  $search.val(term);
  $search.trigger('input');
  if (select) {
    setTimeout(function() {
      $('.select2-results__option').trigger('mouseup');
    }, 500);
  }
}
