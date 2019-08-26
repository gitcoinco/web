var locationComponent = {};
const save_location = function() {
  if (!document.contxt.github_handle) {
    _alert('No profile', 'error');
  }
  const formData = new FormData();
  const location = $('#userLocation').val();

  formData.append('locationComponent', JSON.stringify(locationComponent));

  const profile = {
    url: '/api/v0.1/profile/' + document.contxt.github_handle + '/setlocation',
    method: 'POST',
    headers: {'X-CSRFToken': csrftoken},
    data: formData,
    processData: false,
    dataType: 'json',
    contentType: false
  };

  $.ajax(profile).done(function(response) {
    if (response.status == 200) {
      _alert(response.message, 'info');
    } else {
      _alert(response.message, 'error');
    }
  }).fail(function(error) {
    _alert(error, 'error');
  });
};

let autocomplete;

function initPlacecomplete() {
  let input = document.getElementById('userLocation');

  const options = {
    types: ['(regions)']
  };

  autocomplete = new google.maps.places.Autocomplete(input, options);

  autocomplete.addListener('place_changed', function() {
    let location = autocomplete.getPlace();

    for (var i = 0; i < location.address_components.length; i++) {
      var addressObj = location.address_components[i];

      for (var j = 0; j < addressObj.types.length; j++) {
        if (addressObj.types[j] == 'country') {
          locationComponent['country'] = addressObj.long_name;
          locationComponent['code'] = addressObj.short_name;
        }
        if (addressObj.types[j] == 'locality') {
          locationComponent['locality'] = addressObj.long_name;
        }
      }
    }
  });
}
