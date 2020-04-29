(function($) {
  function syncComplete(res) {
    console.log('openBox done!');
  }

  function onFailure() {
    _alert(
      { message: gettext('Failed to backup data to 3Box. Please try again.') },
      'error'
    );
    inProgress(false);
  }

  let onLoading = null;

  function inProgress(loading) {
    if (onLoading) {
      onLoading(loading);
    }
  }

  function openBox(callback) {
    window.ethereum.enable().then(addresses => {
      window.Box.openBox(addresses[0], window.ethereum, {}).then(box => {
        box.onSyncDone(syncComplete);
        window.box = box;
        window.curentEthAddr = addresses[0];
        callback(box);
      }).catch(err => {
        onFailure();
      });
    });
  }

  function openSpace(box, callback) {
    const name = 'GitCoin';

    window.currentSpace = name;
    const opts = {
      onSyncDone: () => {
        console.log(`Open [${name}] Space completed!`);
        callback(box, box.spaces[name]);
      }
    };

    box.openSpace(name, opts).catch(err => {
      onFailure();
    });
  }

  async function saveDataToSpace(space, model) {
    const res = await fetchProfieData(model);

    console.log(`Received [${model}] data: `, res.data);

    if (res.data) {
      let data = res.data;

      if (data) {
        // get public key-value
        const public_keys = Object.keys(data).filter(k => k[0] !== '_');
        const public_values = public_keys.map(k => data[k]);
        // get private key-value
        let private_keys = Object.keys(data).filter(k => k[0] === '_');
        const private_values = private_keys.map(k => data[k]);

        private_keys = private_keys.map(k => k.substring(1));

        // save data to space
        const r_public = await space.public.setMultiple(public_keys, public_values);
        const r_private = await space.private.setMultiple(private_keys, private_values);

        // remove the unused key/value pairs from the space
        await removeUnusedFields(space, res.keys);

        if (r_public && r_private) {
          const three_box_link = `https://3box.io/${window.curentEthAddr}/data`;

          _alert(
            {
              message: gettext(`<span>Your ${model} data has been synchronized to 3Box -- </span> <a href="${three_box_link}" target="_blank">Check out the details on 3Box Hub</a>.`)},
            'success'
          );
        } else {
          onFailure();
        }
      } else {
        onFailure();
      }
    } else {
      onFailure();
    }

    inProgress(false);
  }

  async function removeUnusedFields(space, keys) {
    const public_keys = keys.filter(k => k[0] !== '_');
    let private_keys = keys.filter(k => k[0] === '_');

    private_keys = private_keys.map(k => k.substring(1));

    const public_data = await space.public.all();
    const private_data = await space.private.all();

    const unused_public_keys = Object.keys(public_data).filter(x => !public_keys.includes(x));
    const unused_private_keys = Object.keys(private_data).filter(x => !private_keys.includes(x));

    await removeFields(space.public, unused_public_keys);
    await removeFields(space.private, unused_private_keys);
  }

  async function removeFields(subspace, keys) {
    if (keys && keys.length > 0) {
      for (let x of keys) {
        await subspace.remove(x);
      }
    }
  }

  async function fetchProfieData(model) {
    const data = new FormData();

    data.append('csrfmiddlewaretoken', $('input[name="csrfmiddlewaretoken"]').val());
    data.append('model', model);
    try {
      const response = await fetch('/api/v0.1/profile/backup', {
        method: 'post',
        body: data
      });

      if (response.status === 200) {
        const result = await response.json();

        return result;
      }
    } catch (err) {
      console.log('Error when fetching profile data', err);
    }
    return null;
  }

  async function syncTo3Box(option) {
    console.log('Start sync data to 3Box ...');

    onLoading = option ? option.onLoading : null;
    const models = option ? option.models : [];

    // User is prompted to approve the messages inside their wallet (openBox() and
    // openSpace() methods via 3Box.js). This logs them in to 3Box.

    try {
      if (window.Box) {
        // 1. Open box and space
        // 2. Backing up my Gitcoin data to 3Box, inside of a "Gitcoin" space
        inProgress(true);
        openBox(box => {
          openSpace(box, (box, space) => {
            models.forEach(async model => {
              console.log(`Saving [${model}] data into space ... `);
              await saveDataToSpace(space, model);
            });
          });
        });
      } else {
        setTimeout(() => {
          syncTo3Box(onLoading);
        }, 1000);
      }
    } catch (err) {
      console.log('Error when backing up profile data', err);
      onFailure();
    }
  }

  if (typeof window !== 'undefined') {
    window.syncTo3Box = syncTo3Box;
  }
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = syncTo3Box;
  }

}(jQuery));
