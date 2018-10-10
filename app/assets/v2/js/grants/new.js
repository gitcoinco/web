/* eslint-disable no-console */

$(document).ready(function() {


  userSearch('.team_members');

  $("#img-project").on('change', function() {
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
         $.each($(form).serializeArray(), function() {
          data[this.name] = this.value;
        });
       // Begin New Deploy Subscription Contract
       let SubscriptionContract = new web3.eth.Contract(compiledSubscription.abi);
       console.log('SubscriptionContract', SubscriptionContract);

       let realTokenAmount = Number(data.amount_goal*10**18)

       console.log(realTokenAmount);


       let args = [
         '0xe87529a6123a74320e13a6dabf3606630683c029',
         // testing token
         '0x6760Deb39EcFc70c8261E0CC3550B1099A14f584',
         web3.utils.toTwosComplement(1),
         web3.utils.toTwosComplement(60),
         web3.utils.toTwosComplement(0)]

         console.log('args', args);

       web3.eth.getAccounts(function(err, accounts){
        web3.eth.net.getId(function(err, network){
           $('#network').val(network)
         SubscriptionContract.deploy({
          data: compiledSubscription.bytecode,
          arguments: args
        })
        .send({
          from: accounts[0],
          gas: 2500000
        })
        .on('error', function(error){
          console.log('1', error);
         })
        .on('transactionHash', function(transactionHash){
          console.log('2', transactionHash);
          $('#transaction_hash').val(transactionHash)
          })
        .on('receipt', function(receipt){

            $('#contract_address').val(receipt.contractAddress)

          })
          .then(function(contractInstance){

            console.log(contractInstance);

            $.each($(form).serializeArray(), function() {
              data[this.name] = this.value;
            });
            console.log(data);
            form.submit();
          })
        })
      })
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
});
