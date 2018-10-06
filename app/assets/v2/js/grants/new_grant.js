/* eslint-disable no-console */

$(document).ready(function() {

console.log('1', web3.eth.coinbase);
console.log('network', web3.version.network);
console.log('web3', Web3);


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

      var data = {};
      var disabled = $(form)
        .find(':input:disabled')
        .removeAttr('disabled');




      // Begin New Deploy Subscription Contract

      let bytecode = compiledSubscription.bytecode;


      let SubscriptionContract = web3.eth.contract(compiledSubscription.abi);

      SubscriptionContract.new(data.admin_address, data.token_address, data.amount_goal, data.frequency, data.gas_price, {
            from:web3.eth.accounts[0],
            data:bytecode,
            gas:2500000}, function(err, subscriptionContract){
              if(!err) {

                // NOTE: The callback will fire twice!
                // Once the contract has the transactionHash property set and once its deployed on an address.
                // e.g. check tx hash on the first call (transaction send)

                if(!subscriptionContract.address) {
                  console.log(subscriptionContract.transactionHash)


                } else {
                  console.log(subscriptionContract.address)

                  $('#transaction_hash').val(subscriptionContract.transactionHash)
                  $('#contract_address').val(subscriptionContract.address)
                  $('#network').val(web3.version.network)

                  $.each($(form).serializeArray(), function() {
                    data[this.name] = this.value;
                  });

                  console.log(data);

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


});
