var AvatarPage = (function() {

  let myAvatars;
  let presetAvatars;
  let myAvatarsInitialized = false;
  let presetAvatarsInitialized = false;

  function postSelection(url, avatarPk) {
    return fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({ avatarPk: avatarPk })
    });
  }

  function updateNavAvatar(svgUrl) {
    $('.nav_avatar').css('background-image', 'url(' + svgUrl + ')');
  }

  function handleApiError(response) {
    response.json().then((response) => {
      let text = gettext('Error occurred while saving. Please try again.');

      if (response.message) {
        text = response.message;
      }
      _alert(text, 'error');
    });
  }

  function avatarTileHtml(avatar, clickCb) {
    const avatarTile = $('<div class="avatar-tile" data-avatar-pk="' +
      avatar.pk +
      '"><div><img src="' + avatar.avatar_url + '"></div></div>');

    if (avatar.active) {
      avatarTile.addClass('active');
    }
    avatarTile.click(clickCb);
    return avatarTile;
  }

  function appendAvatars(el, avatars, clickCb) {
    avatars.forEach((avatar) => {
      el.find('.avatars-container').append(avatarTileHtml(avatar, clickCb));
    });
    if (avatars.length > 0) {
      el.find('.empty-avatars').remove();
    }
  }

  function markAvatarAsActive(el) {
    $('.avatar-tile').removeClass('active');
    el.addClass('active');
  }

  function selectMyAvatar(e) {
    const targetEl = $(e.currentTarget);

    if (targetEl.hasClass('active')) {
      return;
    }
    const avatarToActivatePk = targetEl.data('avatar-pk');

    postSelection('/avatar/activate/', avatarToActivatePk)
      .then((response) => {
        if (response.ok) {
          markAvatarAsActive(targetEl);
          const activatedAvatar = myAvatars.filter((avatar) => avatar.pk === avatarToActivatePk)[0];

          updateNavAvatar(activatedAvatar.avatar_url);
          _alert({ message: gettext('Your Avatar Has Been Changed!') }, 'success');
        } else {
          handleApiError(response);
        }
      });
  }

  function selectPresetAvatar(e) {
    const targetEl = $(e.currentTarget);
    const avatarToSelectPk = targetEl.data('avatar-pk');

    postSelection('/avatar/select-preset/', avatarToSelectPk)
      .then((response) => {
        if (response.ok) {
          const activatedAvatar = presetAvatars.filter((avatar) => avatar.pk === avatarToSelectPk)[0];
          const userAvatar = myAvatars ? myAvatars.filter((avatar) => activatedAvatar.hash && avatar.hash === activatedAvatar.hash)[0] : null;

          if (userAvatar) {
            userAvatar.active = true;
            markAvatarAsActive($(`#my-avatars div[data-avatar-pk='${userAvatar.pk}'] `));
          } else if (myAvatarsInitialized) {
            activatedAvatar.active = true;
            $('#my-avatars .avatars-container').prepend(avatarTileHtml(activatedAvatar, selectMyAvatar));
          }
          updateNavAvatar(activatedAvatar.avatar_url);
          _alert({ message: gettext('Your Avatar Has Been Changed!') }, 'success');
        } else {
          handleApiError(response);
        }
      });
  }

  function loadPresetAvatars() {
    fetch('/api/v0.1/recommended-by-staff/')
      .then((resp) => resp.json())
      .then((response) => {
        presetAvatars = response;
        appendAvatars($('#preset-avatars'), presetAvatars, selectPresetAvatar);
        presetAvatarsInitialized = true;
      })
      .catch(() => {
        _alert('There was an error during preset avatars load.', 'error');
      });
  }

  function loadMyAvatars() {
    fetch('/api/v0.1/user-avatars/')
      .then((resp) => resp.json())
      .then((response) => {
        myAvatars = response;
        myAvatarsInitialized = true;
        appendAvatars($('#my-avatars'), myAvatars, selectMyAvatar);
      })
      .catch(() => {
        _alert('There was an error during Your avatars load.', 'error');
      });
  }

  function setupTabActivationListener() {
    $('#avatar-tabs a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
      let targetTab = $(e.target).attr('href');

      if (targetTab === '#my-avatars-tab' && !myAvatarsInitialized) {
        loadMyAvatars();
      } else if (targetTab === '#preset-avatars-tab' && !presetAvatarsInitialized) {
        loadPresetAvatars();
      }
    });
  }

  setupTabActivationListener();

}());
