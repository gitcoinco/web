
(function($) {
  const switchIcons = (loading) => {
    if (loading) {
      $('.profile-header__sync img.loading').show();
      $('.profile-header__sync img.action').hide();
    } else {
      $('.profile-header__sync img.loading').hide();
      $('.profile-header__sync img.action').show();
    }
  };

  const toggleAutomaticUpdateFlag = async() => {
    const data = new FormData();

    data.append('csrfmiddlewaretoken', $('input[name="csrfmiddlewaretoken"]').val());
    try {
      const response = await fetch('/api/v0.1/profile/settings', {
        method: 'post',
        body: data
      });

      if (response.status === 200) {
        const result = await response.json();
        const automatic_backup = result.automatic_backup ? 'ENABLED' : 'DISABLED';

        _alert(
          { message: gettext(`Profile automatic backup has been ${automatic_backup}`) },
          'success'
        );
      } else {
        _alert(
          { message: gettext('An error occurred. Please try again.') },
          'error'
        );
      }

    } catch (err) {
      console.log('Error when toggling automatic backup flag', err);
    }
  };

  const startProfileDataBackup = () => {
    if (window.syncTo3Box) {
      syncTo3Box({
        onLoading: switchIcons,
        model: 'profile'
      });
    }
  };

  // add click listener
  $('#sync-to-3box').on('click', (event) => {
    event.preventDefault();
    _alert('... starting backup ... ', 'info', 500);
    if (!long_pressed) {
      startProfileDataBackup();
    }
    long_pressed = false;
  });

  // add long press listener
  let timer = null;
  let long_pressed = false;

  $('#sync-to-3box').on('mousedown', () => {
    timer = setTimeout(() => {
      long_pressed = true;
      toggleAutomaticUpdateFlag();
    }, 500);
  }).on('mouseup mouseleave', () => {
    clearTimeout(timer);
  });

  $(document).ready(function() {
    setTimeout(() => {
      console.log('check profile backup flag', window.profile_automatic_backup);
      // backup automatically if the flag is true
      if (window.profile_automatic_backup) {
        startProfileDataBackup();
      }
    }, 3000);
  });

}(jQuery));
