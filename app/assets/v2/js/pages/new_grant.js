/* eslint-disable no-console */

window.onload = function() {

  $('#js-drop').on('dragover', function(event) {
    event.preventDefault();
    event.stopPropagation();
    $(this).addClass('is-dragging');
  });

  $('#js-drop').on('dragleave', function(event) {
    event.preventDefault();
    event.stopPropagation();
    $(this).removeClass('is-dragging');
  });

  $('#js-drop').on('drop', function(event) {
    if (event.originalEvent.dataTransfer.files.length) {
      event.preventDefault();
      event.stopPropagation();
      $(this).removeClass('is-dragging');
    }
  });

  $('.js-select2').each(function() {
    $(this).select2();
  });

  $('#js-newGrant').validate({
    submitHandler: function(form) {
      var action = $(form).attr('action');
      var data = {};

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

      console.log(data);
    }

    $(form).submit();

  });



  $('#new-milestone').on('click', function(event) {
    event.preventDefault();
    var milestones = $('.milestone-form .row');
    var milestoneId = milestones.length || 1;

    $('.milestone-form').append('<div class="row" id="milestone' + milestoneId + '">' +
      '<div class="col-12">\n' +
      '<input type="text" class="form__input" placeholder="Title" name="milestone-title[' + milestoneId + ']" required/>' +
      '<input type="date" class="form__input" placeholder="Date" name="milestone-date[' + milestoneId + ']" required/>' +
      '<textarea class="form__input" type="text" placeholder="Description" name="milestone-description[' + milestoneId + ']" required></textarea>' +
      '</div>' +
      '</div>');
  });

  waitforWeb3(function() {
    tokens(document.web3network).forEach(function(ele) {
      var option = document.createElement('option');

      option.text = ele.name;
      option.value = ele.addr;

      $('#js-token').append($('<option>', {
        value: ele.addr,
        text: ele.name
      }));
    });

    $('#js-token').select2();
  });

};
