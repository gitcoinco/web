const domain = window.location.protocol + '//' + window.location.host;

async function save_collection_data(schema, elements, space) {
  console.log('Collection data');
  let public_keys = ['schema'];
  let public_values = [schema];
  let private_keys = [];
  let private_values = [];

  elements.forEach(function(data) {
    let key = 'gitcoin.' + data.id;
    let filtered_data = {
      'public': {},
      'private': {}
    };

    Object.keys(schema.fields).forEach(function(field) {
      let field_schema = schema.fields[field];

      if (field_schema.visibility === 'public') {
        filtered_data.public[field] = data[field];
      } else {
        filtered_data.private[field] = data[field];
      }
    });

    if (Object.values(filtered_data.public).length > 0) {
      public_keys.push(key);
      public_values.push(filtered_data.public);
    }
    if (Object.values(filtered_data.private).length > 0) {
      private_keys.push(key);
      private_values.push(filtered_data.private);
    }
  });

  if (public_values.length > 0) {
    console.log('Public');
    console.log(public_keys);
    console.log(public_values);
    await space.public.setMultiple(public_keys, public_values);
  }
  if (private_values.length > 0) {
    console.log('Private');
    console.log(private_keys);
    console.log(private_values);
    await space.private.setMultiple(private_keys, private_values);
  }
}

async function save_single_data(schema, data, space) {
  console.log('Single data');
  let public_keys = ['schema'];
  let public_values = [schema];
  let private_keys = [];
  let private_values = [];

  Object.keys(schema.fields).forEach(function(field) {
    const field_schema = schema.fields[field];

    if (field_schema.visibility === 'public') {
      public_keys.push(field);
      public_values.push(data[field]);
    } else {
      private_keys.push(field);
      private_values.push(data[field]);
    }
  });

  console.log('Public');
  console.log(public_keys);
  console.log(public_values);
  console.log('Private');
  console.log(private_keys);
  console.log(private_values);

  await space.public.setMultiple(public_keys, public_values);
  await space.private.setMultiple(private_keys, private_values);
}

function backup(space_name, box) {
  return new Promise(function(resolve, reject) {
    $.ajax({
      type: 'GET',
      url: '/backup/data/' + space_name,
      contentType: 'text/json',
      success: async function(data) {
        let space;
        let schema = data.schema;
        let space_data = data.data;

        if (schema === undefined || schema === null) {
          return reject('Definition for ' + space_name + ' doesn\'t exists');
        }

        if (space_name === 'profile') {
          space = box;
        } else {
          try {
            space = await box.openSpace(space_name);
          } catch (e) {
            console.log(e);
            return reject(e);
          }
        }
        await space.syncDone;

        try {
          if (schema.collection === true) {
            save_collection_data(schema, space_data, space);
          } else {
            await save_single_data(schema, space_data, space);
          }
          resolve(true);
        } catch (e) {
          reject(e);
        }
        console.log('baking data: ' + space_name);
      }
    });
  });
}

function start_backup() {
  // Ref: https://github.com/3box/3box-js/blob/develop/example/index.js
  window.ethereum.enable().then(async function(accounts) {
    const address = accounts[0];

    Box.openBox(address, window.ethereum, {}).then(function(box) {
      console.log(box);
      $.ajax({
        type: 'GET',
        url: '/settings/backup',
        contentType: 'application/json; charset=utf-8',
        success: async function(data) {
          if (data.backup_profile) {
            let space_name = 'profile';

            try {
              status(space_name, 'start');
              await backup(space_name, box);
              status(space_name, 'done');
            } catch (e) {
              hide_loading();
              _alert('Backup profile failed', 'error');
              return;
            }
          }
          if (data.backup_bounties) {
            let space_name = 'bounties';

            try {
              status(space_name, 'start');
              await backup(space_name, box);
              status(space_name, 'done');
            } catch (e) {
              hide_loading();
              _alert('Backup bounties failed', 'error');
              console.log(e);
            }
          }
          if (data.backup_tips) {
            let space_name = 'tips';

            try {
              status(space_name, 'start');
              await backup(space_name, box);
              status(space_name, 'done');
            } catch (e) {
              hide_loading();
              _alert('Backup tips history failed', 'error');
              return;
            }
          }
          if (data.backup_stats) {
            let space_name = 'stats';

            try {
              status(space_name, 'start');
              await backup(space_name, box);
              status(space_name, 'done');
            } catch (e) {
              hide_loading();
              _alert('Backup stats failed', 'error');
              return;
            }
          }
          if (data.backup_activity) {
            let space_name = 'activity';

            try {
              status(space_name, 'start');
              await backup(space_name, box);
              status(space_name, 'done');
            } catch (e) {
              hide_loading();
              _alert('Backup activity history failed', 'error');
              return;
            }
          }
          if (data.backup_acknowledgment) {
            let space_name = 'acknowledgment';

            try {
              status(space_name, 'start');
              await backup(space_name, box);
              status(space_name, 'done');
            } catch (e) {
              hide_loading();
              _alert('Backup kudos failed', 'error');
              return;
            }
          }
          if (data.backup_preferences) {
            let space_name = 'preferences';

            try {
              status(space_name, 'start');
              await backup(space_name, box);
              status(space_name, 'done');
            } catch (e) {
              hide_loading();
              _alert('Backup preferences failed', 'error');
              return;
            }
          }

          let now = new Date().toISOString();

          $('#last-synced').text('Last synced: ' + now.slice(0, 10) + ' ' + now.slice(11, 16));
          _alert('Backup to 3box complete!');
          hide_loading();
        }
      });
    }).catch(function () {
      hide_loading();
      _alert('Backup profile failed', 'error');
    });
  });
}

function show_loading() {
  $('.bg-container').show();
  $('#loading').show();
  $('#backup_options').hide();
}

function hide_loading() {
  $('.bg-container').hide();
  $('#loading').hide();
  $('#backup_status p').hide();
  $('#backup_options').show();
}

function status(space, status) {
  let icon = $('#status_' + space + '_icon');
  let element = $('#status_' + space);

  if (status === 'start') {
    element.show();
    icon.removeClass();
    icon.addClass('fas fa-upload');
  } else if (status === 'done') {
    icon.removeClass();
    icon.addClass('fas fa-check');
  }
}

$('#backup_data').submit(function(e) {
  e.preventDefault();
  $.ajax({
    type: 'POST',
    url: '/settings/backup',
    data: $('#backup_data').serialize(),
    processData: false,
    contentType: 'application/x-www-form-urlencoded',
    success: function(data) {
      _alert('Backup configurations saved successfully!');
      show_loading();
      start_backup();

    }
  });
});

$('#sync-issue').on('click', function(e) {
  e.preventDefault();
  $.ajax({
    type: 'POST',
    url: '/settings/backup',
    data: $('#backup_data').serialize(),
    processData: false,
    contentType: 'application/x-www-form-urlencoded',
    success: function(data) {
      _alert('Backup configurations saved successfully!');
      show_loading();
      start_backup();

    }
  });
});
