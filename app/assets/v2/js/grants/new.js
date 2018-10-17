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
      var data = {};
      var disabled = $(form)
        .find(':input:disabled')
        .removeAttr('disabled');

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });


      // Begin New Deploy Subscription Contract
      let SubscriptionContract = new web3.eth.Contract(compiledSubscription.abi);

      console.log('SubscriptionContract', SubscriptionContract);

      let realTokenAmount = Number(data.amount_goal * 10 ** 18);

      console.log(realTokenAmount);

      // These args are baseline requirements for the contract set by the sender. Will set most to zero to abstract complexity from user.
      let args = [
        // admin_address
        data.admin_address,
        // required token, if any. Will need to make dynamic
        // data.token_address,
        '0x0000000000000000000000000000000000000000',
        // required tokenAmount - setting to zero
        web3.utils.toTwosComplement(0),
        // data.frequency
        web3.utils.toTwosComplement(0),
        // data.gas_price
        web3.utils.toTwosComplement(0)
      ];

      console.log('args', args);

      web3.eth.getAccounts(function(err, accounts) {
        web3.eth.net.getId(function(err, network) {
          $('#network').val(network);
          SubscriptionContract.deploy({
            data: compiledSubscription.bytecode,
            arguments: args
          })
            .send({
              from: accounts[0],
              gas: 2500000
            })
            .on('error', function(error) {
              console.log('1', error);
            })
            .on('transactionHash', function(transactionHash) {
              console.log('2', transactionHash);
              $('#transaction_hash').val(transactionHash);

              // Waiting State screen
              $('#new-grant').hide();
              $('.interior .body').addClass('open');
              $('.interior .body').addClass('loading');
              $('.grant_waiting').show();
              document.issueURL = $('#input-url').val();
              waitingStateActive();

            })
            .on('receipt', function(receipt) {

              $('#block_number').val(receipt.blockNumber);
              $('#contract_address').val(receipt.contractAddress);

            })
            .then(function(contractInstance) {

              console.log(contractInstance);

              $.each($(form).serializeArray(), function() {
                data[this.name] = this.value;
              });
              console.log(data);
              form.submit();
            });
        });
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
