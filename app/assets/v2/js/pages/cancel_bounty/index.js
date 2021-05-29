/* eslint-disable no-console */
window.onload = function() {

  if (getParam('source')) {
    $('input[name=issueURL]').val(getParam('source'));
  }

  $('#cancelBounty').validate({
    submitHandler: function(form) {

      let data = {};

      $.each($(form).serializeArray(), function() {
        if (this.value) {
          data[this.name] = this.value;
        }
      });

      const selectedRadio = $('input[name=canceled_bounty_reason]:checked').val();
      const reasonCancel = selectedRadio == 'other' ? $('#reason_text').val() : selectedRadio;

      if (!reasonCancel || reasonCancel == '') {
        _alert('Please select a reason before cancelling the bounty');
        return;
      }

      const payload = {
        pk: $('input[name=pk]').val(),
        canceled_bounty_reason: reasonCancel
      };

      data.payload = payload;

      if (is_bounties_network) {
        ethCancelBounty(data);
      } else {
        cancelBounty(data);
      }

      MauticEvent.createEvent({
        'alias': 'products',
        'data': [
          {
            'name': 'product',
            'attributes': {
              'product': 'bounties',
              'persona': 'bounty-funder',
              'action': 'cancel'
            }
          }
        ]
      });
    }
  });
};
