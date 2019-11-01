// document.result.pk
const projectModal = (bountyId, projectId) => {
  console.log('test')
  $('#modalProject').bootstrapModal('hide')
  let modalUrl = `/modal/new_project/${bountyId}/`;
  if (projectId) {
    modalUrl = `/modal/new_project/${bountyId}/${projectId}/`;
  }

  $.ajax({
    url: modalUrl,
    type: 'GET',
    cache: false
  }).done(function(result) {
    $('body').append(result);
    let data = $('.team-users').data('initial') ? $('.team-users').data('initial').split(', ') : [];
    // var data ={
    //   avatar_url: "/media/avatars/d4c706a64befd4e79f38b09200874038/octavioamu.png",
    //   id: 13,
    //   text: 'octavioamu',
    // };


    userSearch('.team-users',false,'',data, true, false);
    $('#modalProject').bootstrapModal('show');
    $('[data-toggle="tooltip"]').bootstrapTooltip();

    $('#projectForm').on('submit', function(e) {
      e.preventDefault();
      console.log($(this))
      let logo = $(this)[0]['logo'].files[0];
      console.log(logo)
      var formData = new FormData();
      formData.append('logo', logo );
      console.log(formData)
      let data = $(this).serializeArray();

      for (var i=0; i<data.length; i++) {
        formData.append(data[i].name, data[i].value);
      }

      const sendConfig = {
        url: '/modal/save_project/',
        method: 'POST',
        // headers: {'X-CSRFToken': csrftoken},
        data: formData,
        processData: false,
        dataType: 'json',
        contentType: false
      };
      $.ajax(sendConfig).done(function(response) {
        if (!response.success) {
          return _alert(response.msg, 'error');
        }

        $('#modalProject').bootstrapModal('hide');
        return _alert({message: gettext('Thanks for your feedback.')}, 'info');

      }).fail(function(error) {
        // _alert(error, 'error');
      });
      // let sendProject = fetchData ('/modal/save_project/', 'POST', formData);

      // $.when(sendProject).then(response => {
      //   if (!response.success) {
      //     return _alert(response.msg, 'error');
      //   }

      //   $('#modalProject').bootstrapModal('hide');
      //   return _alert({message: gettext('Thanks for your feedback.')}, 'info');
      // });
    });
  });


  $(document).on('change', '#project_logo', function(){ previewFile($(this))})


};
    $(document, '#modalProject').on('hide.bs.modal', function(e) {
      $('#modalProject').remove();
      $('#modalProject').bootstrapModal('dispose');
    });
  // $(document, '#modalProject').on('show.bs.modal', function(e) {
  //   var curModal;
  //   curModal = this;
  //   $("#modalProject").each(function() {
  //       if (this !== curModal) {
  //         $(this).bootstrapModal("hide");
  //         $('#modalProject').remove();
  //         $('#modalProject').bootstrapModal('dispose');
  //       }
  //     });
  // });
  // $(function() {
  //   return $(document, "#modalProject").on("show.bs.modal", function() {
  //     var curModal;
  //     curModal = this;
  //     $("#modalProject").each(function() {
  //       if (this !== curModal) {
  //         $(this).bootstrapModal("hide");
  //       }
  //     });
  //   });
  // });

  const previewFile = function (elem) {
    console.log(elem)
    var preview = document.querySelector('#img-preview');
    var file    = elem[0].files[0];
    var reader  = new FileReader();
    let isValid = true

    reader.onloadend = function () {
      var imageURL = reader.result;
      getImageSize(imageURL, function(imageWidth, imageHeight) {
        // Do stuff here.
        console.log(imageWidth, imageHeight)
        if (imageWidth !== imageHeight) {
          elem.val("");
          return alert('The image need to be an square')
        }
        preview.src = reader.result;
        isValid = false

      });
    }
    reader.onload = function() {


    }

    if (file && isValid) {
      reader.readAsDataURL(file);
    } else {
      preview.src = "http://placehold.it/200x200/&text=Image Preview";
    }
  }

  function getImageSize(imageURL, callback) {
    // Create image object to ascertain dimensions.
    var image = new Image();

    // Get image data when loaded.
    image.onload = function() {
       // No callback? Show error.
       if (!callback) {
          console.log("Error getting image size: no callback. Image URL: " + imageURL);

       // Yes, invoke callback with image size.
       } else {
          callback(this.naturalWidth, this.naturalHeight);
       }
    }

    // Load image.
    image.src = imageURL;
 }
