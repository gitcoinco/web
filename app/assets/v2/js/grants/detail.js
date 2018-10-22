$(document).ready(function() {
  $('#tabs').tabs();

  $('#form--input__description').height($('#form--input__description').prop('scrollHeight'));

  userSearch('#grant-admin');
  userSearch('#grant-members');

  $('.select2-selection__rendered').removeAttr('title');

  $('#edit--title').on('click', () => {
    inlineEdit('#form--input__title', '#edit--title');
  });

  $('#edit--owner').on('click', () => {
    inlineEdit('#grant-admin', '#edit--owner');
  });

  $('#edit--description').on('click', () => {
    inlineEdit('#form--input__description', '#edit--description');
    $('#form--input__description').height($('#form--input__description').prop('scrollHeight'));
  });

  $('#edit--reference-url').on('click', () => {
    inlineEdit('#form--input__reference-url', '#edit--reference-url');
  });

  $('#edit--members').on('click', () => {
    inlineEdit('#grant-members', '#edit--members');
  });
});

const inlineEdit = (input, icon) => {
  if ($(icon).hasClass('fa-edit'))
    makeEditable(input, icon);
  else
    inlineSave(input, icon);
};

const makeEditable = (input, icon) => {
  $(input).addClass('editable');
  $(input).prop('readonly', false);
  $(input).prop('disabled', false);
  $(icon).toggleClass('fa-edit').toggleClass('fa-save');

  if ($(icon + '-cancel').length == 0) {
    const cancelIcon = '<i id="' + icon.slice(1, icon.length) + '-cancel" class="ml-2 fa fa-times" onclick=\'inlineSave("' + input + '", "' + icon + '", true)\'></i>';

    $(icon).parent().append(cancelIcon);
  }

  $(icon + '-cancel').show();
};

const inlineSave = (input, icon, cancel) => {

  $(input).removeClass('editable');
  $(input).prop('readonly', true);
  $(input).prop('disabled', true);
  $(icon).toggleClass('fa-edit').toggleClass('fa-save');
  $(icon + '-cancel').hide();

  if (cancel)
    return;

  // TODO : fire API
};
