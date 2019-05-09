
// Overwrite from shared.js
// eslint-disable-next-line no-empty-function
function trigger_form_hooks() {
}

$(document).ready(function() {
  const oldBounty = document.result;
  const keys = Object.keys(oldBounty);
  const form = $('#submitBounty');

  // do some form pre-checks
  // if (String(oldBounty.project_type).toLowerCase() !== 'traditional') {
  //   $('#reservedForDiv').hide();
  // }

  if (oldBounty.is_featured === true) {
    $('#featuredBounty').prop('checked', true);
    $('#featuredBounty').prop('disabled', true);
  }

  while (keys.length) {
    const key = keys.pop();
    const val = oldBounty[key];
    const ele = form.find('[name=' + key + ']');

    ele.val(val);
    ele.find(
      'option:contains(' + val + ')'
    ).prop('selected', true);
  }

  $('.js-select2').each(function() {
    $(this).select2();
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
  });

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
    submitHandler: function(form) {
      const inputElements = $(form).find(':input');
      const formData = {};

      inputElements.removeAttr('disabled');
      $.each($(form).serializeArray(), function() {
        formData[this.name] = this.value;
      });
      inputElements.attr('disabled', 'disabled');

      loading_button($('.js-submit'));

      // update bounty reserved for
      const reservedFor = $('.username-search').select2('data')[0];

      if (reservedFor) {
        formData['reserved_for_user_handle'] = reservedFor.text;
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
});
