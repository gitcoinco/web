function upload() {
  const reader = new FileReader();

  reader.onloadend = function() {
    const buf = buffer.Buffer(reader.result); // Convert data into buffer

    ipfs.ipfsApi = IpfsApi(ipfsConfig);
    ipfs.setProvider(ipfsConfig);
    ipfs.ipfsApi.files.add(buf, (err, result) => { // Upload buffer to IPFS
      if (err) {
        _alert(err);
        return;
      }
      let url = `https://${ipfsConfig.host}/ipfs/${result[0].hash}`;

      console.log(`Url --> ${url}`);
      $('#artwork_url').val(url);
    });
  };
  const photo = document.getElementById('photo');

  if (!photo.files.length) {
    _alert('you must provide a file');
  } else {
    reader.readAsArrayBuffer(photo.files[0]); // Read Provided File

  }
}


$('#newkudos').validate();

$('#photo').on({
  'drop': function(e) {
    setTimeout(upload, 100);
  }
});
$('#upload').click(function(e) {
  upload();
  e.preventDefault();
});

$(document).ready(function() {
  $('#newkudos input.btn-go').click(function(e) {
    mixpanel.track('New Kudos Request', {});
    setTimeout(function() {
      $('#newkudos input.btn-go').attr('disabled', 'disabled');
    }, 1);
  });
});