(function($) {
  const syncComplete = res => {
    console.log('sync complete');
  };

  const syncFailure = () => {
    _alert(
      { message: gettext('Failed to backup profile data to 3Box. Please try again.') },
      'error'
    );
    switchIcons(false);
  };

  const openBox = callback => {
    window.ethereum.enable().then(addresses => {
      window.Box.openBox(addresses[0], window.ethereum, {}).then(box => {
        box.onSyncDone(syncComplete);
        window.box = box;
        console.log('openBox succeeded');
        callback(box);
      }).catch(err => {
        syncFailure();
      });
    });
  };

  const openSpace = (box, callback) => {
    const name = 'GitCoin';

    window.currentSpace = name;
    const opts = {
      onSyncDone: () => {
        console.log('sync done in space', name);
        callback(box, box.spaces[name]);
      }
    };

    box.openSpace(name, opts).catch(err => {
      syncFailure();
    });
  };

  const backupProfile = async space => {
    const profile_json = await fetchProfieData();
    console.log("profile_json", profile_json.profile);
    profile_json.grants = profile_json.grants;
    profile_json.bounties = profile_json.bounties;
    profile_json.activities = profile_json.activities;

    if (profile_json) {
      // get public key-value
      const public_keys = Object.keys(profile_json).filter(k => k[0] !== '_');
      const public_values = public_keys.map(k => profile_json[k]);
      // get private key-value
      let private_keys = Object.keys(profile_json).filter(k => k[0] === '_');
      const private_values = private_keys.map(k => profile_json[k]);

      private_keys = private_keys.map(k => k.substring(1));

      // save data to space
      const r_public = await space.public.setMultiple(public_keys, public_values);
      const r_private = await space.private.setMultiple(private_keys, private_values);

      // remove the unused key/value pairs from the space
      await removeUnusedFields(space, public_keys, private_keys);

      if (r_public && r_private) {
        _alert(
          { message: gettext('Your profile data has been synchronized to 3Box.') },
          'success'
        );
      } else {
        syncFailure();
      }
    }

    switchIcons(false);
  };

  const removeUnusedFields = async(space, public_keys, private_keys) => {
    const public_data = await space.public.all();
    const private_data = await space.private.all();

    const unused_public_keys = Object.keys(public_data).filter(x => !public_keys.includes(x));
    const unused_private_keys = Object.keys(private_data).filter(x => !private_keys.includes(x));

    await removeFields(space.public, unused_public_keys);
    await removeFields(space.private, unused_private_keys);

    const count = unused_public_keys.length + unused_private_keys.length;

    console.log(`remove ${count} outdated fields from space`, unused_public_keys, unused_private_keys);
  };

  const removeFields = async(subspace, keys) => {
    if (keys && keys.length > 0) {
      for (let x of keys) {
        await subspace.remove(x);
      }
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
      console.log('Error ', err);
    }
  };

  const fetchProfieData = async () => {
    const data = new FormData();
    data.append('csrfmiddlewaretoken', $('input[name="csrfmiddlewaretoken"]').val());
    try {
      const response = await fetch('/api/v0.1/profile/backup', {
        method: 'post',
        body: data
      });

      if (response.status === 200) {
        const result = await response.json();
        return result.data;
      }
    } catch (err) {
      console.log('Error ', err);
    }
    return null;
  }

  const startProfileDataBackup = async () => {
    console.log('start sync data to 3box');

    const data = await fetchProfieData();
    console.log("data", data);
    window.data = data;

    // User is prompted to approve the messages inside their wallet (openBox() and
    // openSpace() methods via 3Box.js). This logs them in to 3Box.

    if (window.Box) {
      // 1. Open box and space
      // 2. Backing up my Gitcoin data to 3Box, inside of a "Gitcoin" space
      switchIcons(true);
      openBox(box => {
        openSpace(box, (box, space) => {
          console.log('backup data into space');
          backupProfile(space);
        });
      });
    } else {
      setTimeout(() => {
        startProfileDataBackup();
      }, 1000);
    }
  };

  const switchIcons = (loading) => {
    if (loading) {
      $('.profile-header__sync img.loading').show();
      $('.profile-header__sync img.action').hide();
    } else {
      $('.profile-header__sync img.loading').hide();
      $('.profile-header__sync img.action').show();
    }
  };

  // add click listener
  $('#sync-to-3box').on('click', (event) => {
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
