function kudosSearch(elem) {
  var selectItem = elem || '.kudos-search';

  $(selectItem).each(function() {
    if (!$(this).length) {
      return;
    }

    $(this).select2({
      ajax: {
        url: '/api/v0.1/kudos_search/',
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
      theme: 'kudos',
      placeholder: 'Search kudos',
      allowClear: true,
      minimumInputLength: 3,
      escapeMarkup: function(markup) {

        return markup;
      },
      templateResult: formatUser,
      templateSelection: formatUserSelection
    });

    // fix for wrong position on select open
    var select2Instance = $(this).data('select2');

    select2Instance.on('results:message', function(params) {
      this.dropdown._resizeDropdown();
      this.dropdown._positionDropdown();
    });

    function formatUser(kudos) {

      if (kudos.loading) {
        return kudos.text;
      }
      let markup = `<div class="d-flex m-2 align-items-center">
                      <div class="mr-3">
                        <img class="" src="${static_url + kudos.image || static_url + 'v2/images/user-placeholder.png'}" width="40" height="50"/>
                      </div>
                      <div style="min-width: 0;width: 100%;">
                        <div class="d-flex justify-content-between">
                          <div class="kudos-name">${kudos.name_human}</div>
                          <div class="kudos-price">${kudos.price_finney} ETH</div>
                        </div>
                        <div class="text-truncate kudos-description">${kudos.description}</div>
                      <div>
                    </div>`;

      return markup;
    }

    function formatUserSelection(kudos) {

      let selected;
      if (kudos.id === '') { // adjust for custom placeholder values
        // $('.kudos-comment').hide()
        kudosIsSelected()
        return kudos.text;
      } else if (kudos.id) {
        // $('.kudos-comment').show()
        kudosIsSelected(true)
        selected = `<div class="d-flex m-2 align-items-center">
                      <div class="mr-3">
                        <img class="" src="${static_url + kudos.image || static_url + 'v2/images/user-placeholder.png'}" width="40" height="50"/>
                      </div>
                      <div style="min-width: 0;width: 100%;">
                        <div class="d-flex justify-content-between">
                          <div class="kudos-name"><a target="_blank" href="/kudos/${kudos.id}/${kudos.name}"> <i class="fas fa-external-link-alt"></i></a> ${kudos.name_human} ${kudos.price_finney} ETH</div>
                        </div>
                        <div class="text-truncate kudos-description">${kudos.description}</div>
                      <div>
                    </div>`;
         document.selected_kudos = {
          name : kudos.name,
          id : kudos.id,
          price_finney : kudos.price_finney,
         };
      } else {
        selected = kudos.name_human;
      }
      return selected;
    }

    function kudosIsSelected(state){
      let comments = $('.kudos-comment')
      let alert = $('.msg-alert')

      if (state) {
        comments.show()
        alert.show()
      } else {
        comments.hide()
        alert.hide()
      }

    }

    $(selectItem).on("select2:unselecting", function (e) {
      $(this).val(null).trigger('change');
      document.selected_kudos = null;
      e.preventDefault();
    });

  });
}

$('document').ready(function() {
  kudosSearch();
});
