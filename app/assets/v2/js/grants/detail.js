const editableFields = [
  '#form--input__title',
  '#form--twitter__account',
  '#form--input__reference-url',
  '#contract_owner_address',
  '#grant-members',
  '#grant-categories'
];

function getCategoryIndex(categoryName, categories) {
  const resultSet = categories.filter(category => {
    const name = category[0];

    return name === categoryName;
  });

  if (resultSet.length === 1) {
    const matchingCategory = resultSet[0];

    const index = matchingCategory[1];

    return index.toString();
  }

  return '-1';
}

function initGrantCategoriesInput() {
  const grant_type = $('#grant-type').html();

  if (grant_type && grant_type.length > 0) {
    grantCategoriesSelection(
      '#grant-categories',
      `/grants/categories?type=${grant_type.toLowerCase()}`
    );
  }
}

$(document).ready(function() {
  showMore();
  addGrantLogo();
  initGrantCategoriesInput();


  var lgi = localStorage.getItem('last_grants_index');
  var lgt = localStorage.getItem('last_grants_title');

  if (lgi) {
    $('#backgrants').attr('href', lgi);
    $('#backgrants').html('<i class="fas fa-chevron-left mr-2"></i> Back to ' + lgt);
  }

  var algi = localStorage.getItem('last_all_grants_index');
  var algt = localStorage.getItem('last_all_grants_title');

  if (algi) {
    $('#cart_backgrants').attr('href', algi);
    $('#cart_backgrants').html('<i class="fas fa-chevron-left mr-2"></i> Back to ' + algt);
  }

  setInterval (() => {
    notifyOwnerAddressMismatch(
      $('#grant-admin').text(),
      $('#grant_contract_owner_address').text(),
      '#cancel_grant',
      'Looks like your grant has been created with ' +
      $('#grant_contract_owner_address').text() + '. Switch to take action on your grant.'
    );

    if ($('#cancel_grant').attr('disabled')) {
      $('#cancel_grant').addClass('disable-btn').addClass('disable-tooltip');
      $('#cancel_grant_tooltip').attr(
        'data-original-title', 'switch to below contract owner address to cancel grant.'
      );
    } else {
      $('#cancel_grant').removeClass('disable-btn').removeClass('disable-tooltip');
      $('#cancel_grant_tooltip').attr('data-original-title', '');
    }
  }, 1000);

  $('#flag').click(function(e) {
    e.preventDefault();
    const comment = prompt('What is your reason for flagging this Grant?');

    if (!comment) {
      return;
    }
    const data = {
      'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
      'comment': comment
    };

    if (!document.contxt.github_handle) {
      _alert({ message: gettext('Please login.') }, 'error', 1000);
      return;
    }
    $.ajax({
      type: 'post',
      url: $(this).data('href'),
      data,
      success: function(json) {
        _alert({ message: gettext('Your flag has been sent to Gitcoin.') }, 'success', 1000);
      },
      error: function() {
        _alert({ message: gettext('Your report failed to save Please try again.') }, 'error', 1000);
      }
    });

  });

  userSearch('#grant-members', false, undefined, false, false, true);
  $('.select2-selection__rendered').removeAttr('title');
  $('#form--input__title').height($('#form--input__title').prop('scrollHeight'));
  $('#form--input__reference-url').height($('#form--input__reference-url').prop('scrollHeight'));
  $('#form--twitter__account').height($('#form--twitter__account').prop('scrollHeight'));

  $('#edit-details').on('click', (event) => {
    event.preventDefault();

    if (grant_description !== undefined) {
      grant_description.enable(true);
      grant_description.getContents();
    }

    $('#edit-details').addClass('hidden');
    $('#save-details').removeClass('hidden');
    $('#cancel-details').removeClass('hidden');
    $('.grant__progress').addClass('hidden');

    $('#section-nav-description .ql-toolbar').css('display', 'inherit');
    $('#section-nav-description .ql-container').css('border-color', '#ccc');

    copyDuplicateDetails();

    editableFields.forEach(field => {
      makeEditable(field);
    });
  });

  $('#save-details').on('click', event => {
    $('#edit-details').removeClass('hidden');
    $('#save-details').addClass('hidden');
    $('#cancel-details').addClass('hidden');
    $('.grant__progress').removeClass('hidden');

    $('#section-nav-description .ql-toolbar').css('display', 'none');
    $('#section-nav-description .ql-container').css('border-color', 'transparent');

    let edit_title = $('#form--input__title').val();
    let edit_reference_url = $('#form--input__reference-url').val();
    let twitter_account = $('#form--twitter__account').val().replace('@', '');
    let edit_grant_members = $('#grant-members').val();
    let edit_categories = $('#grant-categories').val();

    let data = {
      'edit-title': edit_title,
      'edit-reference_url': edit_reference_url,
      'edit-twitter_account': twitter_account,
      'edit-grant_members[]': edit_grant_members,
      'edit-categories[]': edit_categories
    };

    if (grant_description !== undefined) {
      const edit_description = grant_description.getText();
      const edit_description_rich = JSON.stringify(grant_description.getContents());

      grant_description.enable(false);
      data = Object.assign({}, data, {
        'edit-description': edit_description,
        'edit-description_rich': edit_description_rich
      });
    }

    $.ajax({
      type: 'post',
      url: '',
      data,
      success: function(json) {
        window.location.reload(false);
      },
      error: function() {
        _alert({ message: gettext('Your edits failed to save. Please try again.') }, 'error');
      }
    });

    editableFields.forEach(field => disableEdit(field));
  });

  $('#cancel-details').on('click', event => {
    if (grant_description !== undefined) {
      grant_description.enable(false);
      grant_description.setContents(grant_description.getContents());
    }
    $('#edit-details').removeClass('hidden');
    $('#save-details').addClass('hidden');
    $('#cancel-details').addClass('hidden');
    $('.grant__progress').removeClass('hidden');

    $('#section-nav-description .ql-toolbar').css('display', 'none');
    $('#section-nav-description .ql-container').css('border-color', 'transparent');

    editableFields.forEach(field => disableEdit(field));
  });

  $('#cancel_grant').on('click', function(e) {
    $('.modal-cancel-grants').on('click', function(e) {
      $.ajax({
        type: 'post',
        url: '',
        data: {
          'grant_cancel_tx_id': '0x0'
        },
        success: function(json) {
          window.location.reload(false);
        },
        error: function() {
          _alert({ message: gettext('Canceling your grant failed to save. Please try again.') }, 'error');
        }
      });
    });
  });
});

const makeEditable = (input) => {
  $(input).addClass('editable');
  $(input).prop('readonly', false);
  $(input).prop('disabled', false);
};

const disableEdit = (input) => {
  $(input).removeClass('editable');
  $(input).prop('readonly', true);
  $(input).prop('disabled', true);
};

const copyDuplicateDetails = () => {
  let obj = {};

  editableFields.forEach(field => {
    obj[field] = $(field).val() ? $(field).val() : $(field).last().text();
  });

  $('#cancel-details').on('click', () => {
    editableFields.forEach(field => {
      if ([ '#grant-members', '#grant-categories' ].includes(field))
        $(field).val(obj[field]).trigger('change');
      else
        $(field).val(obj[field]);
    });
  });
};

$(document).ready(() => {
  $('#grant-profile-tabs button').click(function() {
    document.location = $(this).attr('href');
  });
  $('.select2-selection__choice').removeAttr('title');
});
