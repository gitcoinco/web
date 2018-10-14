/* eslint-disable no-console */

const validate = () => {
  if ($('#frequency_unit').select2('data')[0].text === 'any')
    $('#frequency_count').val('0');
};

$(document).ready(function() {

  userSearch('.team_members');

  $('#img-project').on('change', function() {
    if (this.files && this.files[0]) {
      let reader = new FileReader();

      reader.onload = function(e) {
        $('#preview').attr('src', e.target.result);
        $('#preview').css('width', '100%');
        $('#js-drop span').hide();
        $('#js-drop input').css('visible', 'invisible');
        $('#js-drop').css('padding', 0);
      };
      reader.readAsDataURL(this.files[0]);
    }
  });

  $('.js-select2, #frequency_unit').each(function() {
    $(this).select2();
  });

  $('#create-grant').validate({
    submitHandler: function(form) {

      let data = {};

      $(form).find(':input:disabled').removeAttr('disabled');

      // Begin New Deploy Subscription Contract
      let bytecode = compiledSubscription.bytecode;
      let SubscriptionContract = web3.eth.contract(compiledSubscription.abi);

      // Waiting State screen
      $('#new-grant').hide();
      $('.interior .body').addClass('open');
      $('.interior .body').addClass('loading');
      $('.grant_waiting').show();
      document.issueURL = $('#input-url').val();
      waitingStateActive();

      SubscriptionContract.new(data.admin_address, data.token_address, data.amount_goal, data.frequency, data.gas_price, {
        from: web3.eth.accounts[0],
        data: bytecode,
        gas: 2500000}, function(err, subscriptionContract) {
        if (!err) {

          // NOTE: The callback will fire twice!
          // Once the contract has the transactionHash property set and once its deployed on an address.
          // e.g. check tx hash on the first call (transaction send)

          if (!subscriptionContract.address) {
            console.log(subscriptionContract.transactionHash);
          } else {
            console.log(subscriptionContract.address);

            $('#transaction_hash').val(subscriptionContract.transactionHash);
            $('#contract_address').val(subscriptionContract.address);
            $('#network').val(web3.version.network);

            $.each($(form).serializeArray(), function() {
              if (this.name == 'team_members[]')
                data.team_members = $('#input-team_members').select2('data').map(
                  member => member['text']
                );
              else
                data[this.name] = this.value;
            });
            form.submit();
          }
        }
      });
    }
  });

  $('#new-milestone').on('click', function(event) {
    event.preventDefault();
    var milestones = $('.milestone-form .row');
    var milestoneId = milestones.length || 1;

    $('.milestone-form').append(
      '<div class="row" id="milestone' + milestoneId + '">' +
        '<div class="col-12">\n' +
          '<input type="text" class="form__input" placeholder="Title" name="milestone-title[' + milestoneId + ']" required/>' +
          '<input type="date" class="form__input" placeholder="Date" name="milestone-date[' + milestoneId + ']" required/>' +
          '<textarea class="form__input" type="text" placeholder="Description" name="milestone-description[' + milestoneId + ']" required></textarea>' +
        '</div>' +
      '</div>'
    );
  });

  waitforWeb3(function() {
    tokens(document.web3network).forEach(function(ele) {
      let option = document.createElement('option');

      option.text = ele.name;
      option.value = ele.addr;

      $('#js-token').append($('<option>', {
        value: ele.addr,
        text: ele.name
      }));
    });
    $('#js-token').select2();
  });

  $('.select2-selection__rendered').removeAttr('title');
});
