// document.result.pk
const submitProject = (logo, data, callback) => {
  let formData = new FormData();

  formData.append('logo', logo);

  for (let i = 0; i < data.length; i++) {
    formData.append(data[i].name, data[i].value);
  }

  const sendConfig = {
    url: '/modal/save_project/',
    method: 'POST',
    data: formData,
    processData: false,
    dataType: 'json',
    contentType: false
  };

  $.ajax(sendConfig).done(function(response) {
    if (!response.success) {
      if (callback) {
        callback(response);
      }
      return _alert(response.msg, 'danger');
    }
    delete localStorage['pendingProject'];
    $('#modalProject').bootstrapModal('hide');
    if (callback) {
      callback(response);
    }
    if (document.location.pathname.includes('fulfill')) {
      document.location.reload();
    }
    return _alert({message: response.msg}, 'info');


  }).fail(function(data) {
    _alert(data.responseJSON['error'], 'danger');

    if (callback) {
      callback(data);
    }
    return true;
  });
};

const projectModal = (bountyId, projectId, callback) => {
  $('#modalProject').bootstrapModal('hide');
  const modalUrl = projectId ? `/modal/new_project/${bountyId}/${projectId}/` : `/modal/new_project/${bountyId}/`;

  $.ajax({
    url: modalUrl,
    type: 'GET',
    cache: false
  }).done(function(result) {
    $('body').append(result);
    let data = $('.team-users').data('initial') ? $('.team-users').data('initial').split(', ') : [];

    userSearch('.team-users', false, '', data, true, false);
    $('.project__tags').select2({
      tags: true,
      tokenSeparators: [ ',', ' ' ]
    });
    $('#modalProject').bootstrapModal('show');
    $('[data-toggle="tooltip"]').bootstrapTooltip();
    $('#looking-members').on('click', function() {
      $('.looking-members').toggle();
    });
    $('#projectForm').on('submit', function(e) {
      e.preventDefault();
      const url = $('#videodemo-url').val();
      const metadata = getVideoMetadata(url);

      let logo = $(this)[0]['logo'].files[0];
      let data = $(this).serializeArray();

      if (metadata) {
        data.push({name: 'videodemo-provider', value: metadata.provider});
      }

      submitProject(logo, data, callback);
    });
  });

  $(document).on('change', '#project_logo', function() {
    previewFile($(this));
  });
};

$(document, '#modalProject').on('hide.bs.modal', function(e) {
  $('#modalProject').remove();
  $('#modalProject').bootstrapModal('dispose');
});

const previewFile = function(elem) {
  let preview = document.querySelector('#img-preview');
  let file = elem[0].files[0];
  let reader = new FileReader();

  reader.onloadend = function() {
    let imageURL = reader.result;

    getImageSize(imageURL, function(imageWidth, imageHeight) {
      if (imageWidth !== imageHeight) {
        elem.val('');
        preview.src = elem.data('imgplaceholder');
        return alert('Please use a square image');
      }
      preview.src = reader.result;
    });
  };

  if (file) {
    reader.readAsDataURL(file);
  }
};

function getImageSize(imageURL, callback) {
  let image = new Image();

  image.onload = function() {
    callback(this.naturalWidth, this.naturalHeight);
  };
  image.src = imageURL;
}
