// Overwrite from shared.js
// eslint-disable-next-line no-empty-function
function trigger_form_hooks() {
}

let usersBySkills;
let processedData;

const populateFromAPI = bounty => {
  if (bounty && bounty.is_featured) {
    $('#featuredBounty').prop('checked', true);
    $('#featuredBounty').prop('disabled', true);
  }

  $.each(bounty, function(key, value) {
    let ctrl = $('[name=' + key + ']', $('#submitBounty'));

    switch (ctrl.prop('type')) {
      case 'radio':
        $(`.${value}`).button('toggle');
        break;

      case 'checkbox':
        ctrl.each(function() {
          if (value.length) {
            $.each(value, function(key, val) {
              $(`.${val}`).button('toggle');
            });
          } else {
            $(this).prop('checked', value);
          }
        });
        break;

      case 'select-one':
        $('#' + key).val(value).trigger('change');
        break;

      default:
        if (value > 0) {
          ctrl.val(value);
        }
    }
  });

  if (bounty && bounty.keywords) {

    let keywords = bounty['keywords'].split(',');

    $('#keywords').select2({
      placeholder: 'Select tags',
      data: keywords,
      tags: true,
      allowClear: true,
      tokenSeparators: [ ',', ' ' ]
    }).trigger('change');

    $('#keywords').val(keywords).trigger('change');
    $('#keyword-suggestion-container').hide();
  }
};

const formatUser = user => {
  if (!user.text || user.children) {
    return user.text;
  }

  const markup = `
    <div class="d-flex align-items-baseline">
      <div class="mr-2">
        <img class="rounded-circle" src="${'/dynamic/avatar/' + user.text }" width="20" height="20"/>
      </div>
      <div>${user.text}</div>
    </div>`;

  return markup;
};

const formatUserSelection = user => {
  let selected;

  if (user.id) {
    selected = `
      <img class="rounded-circle" src="${'/dynamic/avatar/' + user.text }" width="20" height="20"/>
      <span class="ml-2">${user.text}</span>`;
  } else {
    selected = user.text;
  }

  return selected;
};

const getSuggestions = () => {

  let keywords = $('#keywords').val();

  const settings = {
    url: `/api/v0.1/get_suggested_contributors?keywords=${keywords}`,
    method: 'GET',
    processData: false,
    dataType: 'json',
    contentType: false
  };

  $.ajax(settings).done(function(response) {
    let groups = {
      'contributors': 'Recently worked with you',
      'recommended_developers': 'Recommended based on skills',
      'verified_developers': 'Verified contributors'
    };

    let options = Object.entries(response).map(([ text, children ]) => (
      { text: groups[text], children }
    ));

    usersBySkills = [].map.call(response['recommended_developers'], function(obj) {
      return obj;
    });

    if (keywords.length && usersBySkills.length) {
      $('#invite-all-container').show();
      $('.select2-add_byskill span').text(keywords.join(', '));
    } else {
      $('#invite-all-container').hide();
    }

    let generalIndex = 0;

    processedData = $.map(options, function(obj) {
      if (obj.children.length < 1) {
        return;
      }

      obj.children.forEach(children => {
        children.text = children.profile__handle || children.user__profile__handle;
        children.id = generalIndex;
        generalIndex++;
      });
      return obj;
    });

    $('#invite-contributors').select2().empty();
    $('#invite-contributors.js-select2').select2({
      data: processedData,
      placeholder: 'Select contributors',
      escapeMarkup: function(markup) {
        return markup;
      },
      templateResult: formatUser,
      templateSelection: formatUserSelection
    });

  }).fail(function(error) {
    console.log('Could not fetch contributors', error);
  });
};

$(document).ready(function() {

  const bounty = document.result;
  const form = $('#submitBounty');

  populateFromAPI(bounty);

  $('.js-select2').each(function() {
    $(this).select2({
      minimumResultsForSearch: Infinity
    });
  });

  $('[name=project_type]').on('change', function() {
    const val = $('input[name=project_type]:checked').val();

    if (val !== 'traditional') {
      $('#reservedFor').attr('disabled', true);
      $('#reservedFor').select2().trigger('change');
    } else {
      $('#reservedFor').attr('disabled', false);
      userSearch('#reservedFor', false);
    }
  }).triggerHandler('change');

  $('[name=permission_type]').on('change', function() {
    const val = $('input[name=permission_type]:checked').val();

    if (val === 'approval') {
      $('#admin_override_suspend_auto_approval').attr('disabled', false);
    } else {
      $('#admin_override_suspend_auto_approval').prop('checked', false);
      $('#admin_override_suspend_auto_approval').attr('disabled', true);
    }
  }).triggerHandler('change');

  let usdFeaturedPrice = $('.featured-price-usd').text();
  let ethFeaturedPrice;

  getAmountEstimate(usdFeaturedPrice, 'ETH', function(amountEstimate) {
    ethFeaturedPrice = amountEstimate['value'];
    $('.featured-price-eth').text(`+${amountEstimate['value']} ETH`);
  });

  getSuggestions();
  $('#keywords').on('change', getSuggestions);

  $('.select2-tag__choice').on('click', function() {
    $('#invite-contributors.js-select2').data('select2').dataAdapter.select(processedData[0].children[$(this).data('id')]);
  });

  $('.select2-add_byskill').on('click', function(e) {
    e.preventDefault();
    $('#invite-contributors.js-select2').val(usersBySkills.map((item) => {
      return item.id;
    })).trigger('change');
  });

  $('.select2-clear_invites').on('click', function(e) {
    e.preventDefault();
    $('#invite-contributors.js-select2').val(null).trigger('change');
  });

  const reservedForHandle = bounty && bounty.reserved_for_user_handle ? bounty.reserved_for_user_handle : [];

  userSearch('#reservedFor', false, '', reservedForHandle, true);

  if ($('input[name=amount]').length) {

    const denomination = $('input[name=denomination]').val();

    setTimeout(() => setUsdAmount(denomination), 1000);

    $('input[name=hours]').keyup(() => setUsdAmount(denomination));
    $('input[name=hours]').blur(() => setUsdAmount(denomination));
    $('input[name=amount]').keyup(() => setUsdAmount(denomination));

    $('input[name=usd_amount]').on('focusin', function() {
      $('input[name=usd_amount]').attr('prev_usd_amount', $(this).val());
      $('input[name=amount]').trigger('change');
    });

    $('input[name=usd_amount]').on('focusout', function() {
      $('input[name=usd_amount]').attr('prev_usd_amount', $(this).val());
      $('input[name=amount]').trigger('change');
    });

    $('input[name=usd_amount]').keyup(() => {
      const prev_usd_amount = $('input[name=usd_amount]').attr('prev_usd_amount');
      const usd_amount = $('input[name=usd_amount').val();

      $('input[name=amount]').trigger('change');

      if (prev_usd_amount != usd_amount) {
        usdToAmount(usd_amount, denomination);
      }
    });
  }

  form.validate({
    errorPlacement: function(error, element) {
      if (element.attr('name') == 'bounty_categories') {
        error.appendTo($(element).parents('.btn-group-toggle').next('.cat-error'));
      } else {
        error.insertAfter(element);
      }
    },
    ignore: '',
    messages: {
      select2Start: {
        required: 'Please select the keyword tags for this bounty.'
      }
    },
    submitHandler: function(form) {
      const inputElements = $(form).find(':input');
      const formData = {};

      inputElements.removeAttr('disabled');
      $.each($(form).serializeArray(), function() {
        if (formData[this.name]) {
          formData[this.name] += ',' + this.value;
        } else {
          formData[this.name] = this.value;
        }
      });
      inputElements.attr('disabled', 'disabled');

      loading_button($('.js-submit'));

      const reservedFor = $('.username-search').select2('data')[0];
      let inviteContributors = $('#invite-contributors.js-select2').select2('data').map((user) => {
        return user.user__profile__id;
      });

      if (reservedFor) {
        formData['reserved_for_user_handle'] = reservedFor.text;
      }

      if (inviteContributors.length) {
        formData['invite'] = inviteContributors;
      }

      if (document.result && document.result.is_featured) {
        formData['is_featured'] = true;
      } else if (formData['featuredBounty'] === '1') {
        formData['is_featured'] = true;
        formData['featuring_date'] = new Date().getTime() / 1000;
      } else {
        formData['is_featured'] = false;
      }

      const token = tokenAddressToDetailsByNetwork(token_address, bounty_network);

      formData['value_in_token'] = formData['amount'] * 10 ** token.decimals;

      const bountyId = document.pk;
      const payload = JSON.stringify(formData);

      const payFeaturedBounty = function() {
        indicateMetamaskPopup();
        web3.eth.sendTransaction({
          to: '0x88c62f1695DD073B43dB16Df1559Fda841de38c6',
          from: selectedAccount,
          value: web3.utils.toWei(String(ethFeaturedPrice)),
          gasPrice: web3.utils.toHex(5 * Math.pow(10, 9)),
          gas: web3.utils.toHex(318730),
          gasLimit: web3.utils.toHex(318730)
        },
        function(error, result) {
          indicateMetamaskPopup(true);
          if (error) {
            _alert({ message: gettext('Unable to upgrade to featured bounty. Please try again.') }, 'danger');
            console.log(error);
          } else {
            saveAttestationData(
              result,
              ethFeaturedPrice,
              '0x88c62f1695DD073B43dB16Df1559Fda841de38c6',
              'featuredbounty'
            );
            saveBountyChanges();
          }
        });
      };

      const saveBountyChanges = function() {
        $.post('/bounty/change/' + bountyId, payload).then(
          function(result) {
            inputElements.removeAttr('disabled');
            unloading_button($('.js-submit'));

            result = sanitizeAPIResults(result);
            _alert({ message: result.msg }, 'success');

            if (result.url) {
              setTimeout(function() {
                document.location.href = result.url;
              }, 1000);
            }
          }
        ).fail(
          function(result) {
            inputElements.removeAttr('disabled');
            unloading_button($('.js-submit'));

            const alertMsg = result && result.responseJSON ?
              result.responseJSON.error :
              'Something went wrong. Please reload the page and try again.';

            _alert({ message: alertMsg }, 'danger');
          }
        );
      };

      if (formData['is_featured'] && !bounty.is_featured) {
        payFeaturedBounty();
      } else {
        saveBountyChanges();
      }
    }
  });

});
