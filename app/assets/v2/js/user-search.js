function userSearch(elem, showAddress, theme, initialData, allowClear, suppress_non_gitcoiners) {
  var themeChoice = theme || undefined;
  var selectItem = elem || '.username-search';

  if (initialData) {
    initialData = initialData.map(
      function(userHandle) {
        return {
          'id': userHandle,
          'text': userHandle,
          'avatar_url': '/dynamic/avatar/' + userHandle,
          'selected': true
        };
      }
    );
  }

  $(selectItem).each(function() {
    if (!$(this).length) {
      return;
    }
    var url = '/api/v0.1/users_search/?token=' + currentProfile.githubToken;

    if (suppress_non_gitcoiners) {
      url += '&suppress_non_gitcoiners=true';
    }
    $(this).select2({
      ajax: {
        url: url,
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
      data: initialData,
      allowClear: allowClear,
      theme: themeChoice,
      placeholder: 'Search by Github/Gitcoin username',
      minimumInputLength: 3,
      escapeMarkup: function(markup) {
        return markup;
      },
      templateResult: formatUser,
      templateSelection: showAddress ? formatUserSelectionWithAddress : formatUserSelection
    });

    // fix for wrong position on select open
    var select2Instance = $(this).data('select2');

    select2Instance.on('results:message', function(params) {
      this.dropdown._resizeDropdown();
      this.dropdown._positionDropdown();
    });

    function formatUser(user) {

      if (user.loading) {
        return user.text;
      }
      let markup = `<div class="d-flex align-items-baseline">
                      <div class="mr-2">
                        <img class="rounded-circle" src="${user.avatar_url || static_url + 'v2/images/user-placeholder.png'}" width="40" height="40"/>
                      </div>
                      <div>${user.text}</div>
                    </div>`;

      return markup;
    }

    function formatUserSelection(user) {
      let selected;

      if (user.id) {
        selected = `
          <img class="rounded-circle" src="${user.avatar_url || static_url + 'v2/images/user-placeholder.png'}" width="20" height="20"/>
          <span class="ml-2">${user.text}</span>`;
      } else {
        selected = user.text;
      }
      return selected;
    }

    function formatUserSelectionWithAddress(user) {
      let selected;

      if (user.id) {
        selected = `
          <img class="rounded-circle" src="${user.avatar_url || static_url + 'v2/images/user-placeholder.png'}" width="20" height="20"/>
          ${user.text} <i style="font-size: 5px; position:relative; top: -2px;" class="px-1 fas fa-circle"></i> `;
        if (user.preferred_payout_address)
          selected += truncate(user.preferred_payout_address, 4);
        else
          selected += '<span style="color: grey">( Secure Proxy Address )</span>';
      } else {
        selected = user.text;
      }
      return selected;
    }
  });
}
