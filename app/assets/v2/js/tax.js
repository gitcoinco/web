var locationComponent = {};
var addressComponent = '';
const save_tax_settings = function() {
  if (!document.contxt.github_handle) {
    _alert('No profile', 'danger');
  }
  const formData = new FormData();

  formData.append('locationComponent', JSON.stringify(locationComponent));
  formData.append('addressComponent', addressComponent);
  let userLocation = $('#userLocation').val();
  let userAddress = $('#userAddress').val();


  const profile = {
    url: '/api/v0.1/profile/' + document.contxt.github_handle + '/setTaxSettings',
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
      _alert(response.message, 'danger');
    }
  }).fail(function(error) {
    _alert(error, 'danger');
  });
};

let autocomplete;

function initPlacecomplete() {
  let inputLocation = userLocation;
  let inputAddress = userAddress;

  const optionsLocation = {
    types: ['(regions)']
  };

  const optionsAddress = {
    types: ['address']
  };

  autocompleteLocation = new google.maps.places.Autocomplete(inputLocation, optionsLocation);
  autocompleteAddress = new google.maps.places.Autocomplete(inputAddress, optionsAddress);

  autocompleteLocation.addListener('place_changed', function() {
    let location = autocompleteLocation.getPlace();

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

  autocompleteAddress.addListener('place_changed', function() {
    let address = autocompleteAddress.getPlace();

    addressComponent = address.formatted_address;
  });
}
