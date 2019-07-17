// Overwrite from shared.js
// eslint-disable-next-line no-empty-function
function trigger_form_hooks() {
}

$(document).ready(function() {
  const oldBounty = document.result;
  const keys = Object.keys(oldBounty);
  const form = $('#submitBounty');

  if (oldBounty.is_featured === true) {
    $('#featuredBounty').prop('checked', true);
    $('#featuredBounty').prop('disabled', true);
  }

  $.each(oldBounty, function(key, value) {
    let ctrl = $('[name=' + key + ']', form);

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
      default:
        if (value > 0) {
          ctrl.val(value);
        }
    }
  });

  $('.js-select2').each(function() {
    $(this).select2({
      minimumResultsForSearch: Infinity
    });
  });

  $('[name=project_type]').on('change', function() {
    let val = $('input[name=project_type]:checked').val();

    if (val !== 'traditional') {
      $('#reservedFor').attr('disabled', true);
      $('#reservedFor').select2().trigger('change');
    } else {
      $('#reservedFor').attr('disabled', false);
      userSearch('#reservedFor', false);
    }
  }).triggerHandler('change');

  $('[name=permission_type]').on('change', function() {
    let val = $('input[name=permission_type]:checked').val();

    if (val === 'approval') {
      $('#admin_override_suspend_auto_approval').attr('disabled', false);
    } else {
      $('#admin_override_suspend_auto_approval').prop('checked', false);
      $('#admin_override_suspend_auto_approval').attr('disabled', true);
    }
  }).triggerHandler('change');

  const reservedForHandle = oldBounty['reserved_for_user_handle'];

  userSearch(
    '#reservedFor',
    // show address
    false,
    // theme
    '',
    // initial data
    reservedForHandle ? [reservedForHandle] : [],
    // allowClear
    true
  );

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
        required: 'Please select the right keywords.'
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

      // update bounty reserved for
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

      if (formData['featuredBounty'] === '1') {
        formData['is_featured'] = true;
        formData['featuring_date'] = new Date().getTime() / 1000;
      } else {
        formData['is_featured'] = false;
      }

      const bountyId = document.pk;
      const payload = JSON.stringify(formData);

      var payFeaturedBounty = function() {
        indicateMetamaskPopup();
        web3.eth.sendTransaction({
          to: '0x00De4B13153673BCAE2616b67bf822500d325Fc3',
          from: web3.eth.coinbase,
          value: web3.toWei(ethFeaturedPrice, 'ether'),
          gasPrice: web3.toHex(5 * Math.pow(10, 9)),
          gas: web3.toHex(318730),
          gasLimit: web3.toHex(318730)
        },
        function(error, result) {
          indicateMetamaskPopup(true);
          if (error) {
            _alert({ message: gettext('Unable to upgrade to featured bounty. Please try again.') }, 'error');
            console.log(error);
          } else {
            saveAttestationData(
              result,
              ethFeaturedPrice,
              '0x00De4B13153673BCAE2616b67bf822500d325Fc3',
              'featuredbounty'
            );
            saveBountyChanges();
          }
        });
      };

      var saveBountyChanges = function() {
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

            var alertMsg = result && result.responseJSON ? result.responseJSON.error : null;

            if (alertMsg === null) {
              alertMsg = gettext('Network error. Please reload the page and try again.');
            }
            _alert({ message: alertMsg }, 'error');
          }
        );
      };

      if (formData['is_featured'] && !oldBounty.is_featured) {
        payFeaturedBounty();
      } else {
        saveBountyChanges();
      }
    }
  });

  let usdFeaturedPrice = $('.featured-price-usd').text();
  let ethFeaturedPrice;

  getAmountEstimate(usdFeaturedPrice, 'ETH', function(amountEstimate) {
    ethFeaturedPrice = amountEstimate['value'];
    $('.featured-price-eth').text(`+${amountEstimate['value']} ETH`);
  });

  var processedData;

  $('.select2-tag__choice').on('click', function() {
    $('#invite-contributors.js-select2').data('select2').dataAdapter.select(processedData[0].children[$(this).data('id')]);
  });

  const getSuggestions = () => {

    const settings = {
      url: `/api/v0.1/get_suggested_contributors?keywords=${$('#keywords').val()}`,
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

      var generalIndex = 0;

      processedData = $.map(options, function(obj, index) {
        if (obj.children.length < 1) {
          return;
        }

        obj.children.forEach((children, childIndex) => {
          children.text = children.fulfiller_github_username || children.user__profile__handle;
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

  getSuggestions();

  function formatUser(user) {
    if (!user.text || user.children) {
      return user.text;
    }
    let markup = `<div class="d-flex align-items-baseline">
                    <div class="mr-2">
                      <img class="rounded-circle" src="${'/dynamic/avatar/' + user.text }" width="20" height="20"/>
                    </div>
                    <div>${user.text}</div>
                  </div>`;

    return markup;
  }

  function formatUserSelection(user) {
    let selected;

    if (user.id) {
      selected = `
        <img class="rounded-circle" src="${'/dynamic/avatar/' + user.text }" width="20" height="20"/>
        <span class="ml-2">${user.text}</span>`;
    } else {
      selected = user.text;
    }
    return selected;
  }
});
