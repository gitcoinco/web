/* eslint-disable no-console */

$(document).ready(function() {

  // web3.version.getNetwork()
  // .then(function(result){
  //   console.log("network", result);
  // })

  console.log('say something else');


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
    console.log(web3);

    $(this).select2();
  });

  $('#js-newGrant').validate({
    submitHandler: function(form) {
      try {
        web3.version.network == "1" || "4"
      } catch (exception) {
        _alert(gettext('You are on an unsupported network.  Please change your network to a supported network.'));
        return;
      }


      var data = {};
      var disabled = $(form)
        .find(':input:disabled')
        .removeAttr('disabled');

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });

    //   disabled.attr('disabled', 'disabled');
    //   // mixpanel.track('Submit New Grant Clicked', {});
    //
    //   // setup
    //   // loading_button($('.js-submit'));
    //   // var githubUsername = data.githubUsername;
    //   // var issueURL = data.issueURL.replace(/#.*$/, '');
    //   // var notificationEmail = data.notificationEmail;
    //   // var amount = data.amount;
    //   var tokenAddress = data.denomination;
    //   console.log(tokenAddress);
      // var token = tokenAddressToDetails(tokenAddress);
      // var decimals = token['decimals'];
      // var tokenName = token['name'];
      // var decimalDivisor = Math.pow(10, decimals);
      // var expirationTimeDelta = data.expirationTimeDelta;

      // var metadata = {
      //   issueTitle: data.title,
      //   issueDescription: data.description,
      //   issueKeywords: data.keywords,
      //   githubUsername: data.githubUsername,
      //   notificationEmail: data.notificationEmail,
      //   fullName: data.fullName,
      //   experienceLevel: data.experience_level,
      //   projectLength: data.project_length,
      //   bountyType: data.bounty_type,
      //   tokenName
      // };

      // var privacy_preferences = {
      //   show_email_publicly: data.show_email_publicly,
      //   show_name_publicly: data.show_name_publicly
      // };

      // validation
      // var isError = false;
      //
      // $(this).attr('disabled', 'disabled');
      //
      // // save off local state for later
      // localStorage['issueURL'] = issueURL;
      // localStorage['notificationEmail'] = notificationEmail;
      // localStorage['githubUsername'] = githubUsername;
      // localStorage['tokenAddress'] = tokenAddress;
      // localStorage.removeItem('bountyId');
      //
      // setup web3
      // TODO: web3 is using the web3.js file.  In the future we will move
      // to the node.js package.  github.com/ethereum/web3.js
      // var isETH = tokenAddress == '0x0000000000000000000000000000000000000000';
      // var token_contract = web3.eth.contract(token_abi).at(tokenAddress);
      // var account = web3.eth.coinbase;
      //
      // if (!isETH) {
      //   check_balance_and_alert_user_if_not_enough(tokenAddress, amount);
      // }
      //
      // amount = amount * decimalDivisor;
      // // Create the bounty object.
      // // This function instantiates a contract from the existing deployed Standard Bounties Contract.
      // // bounty_abi is a giant object containing the different network options
      // // bounty_address() is a function that looks up the name of the network and returns the hash code
      // var bounty = web3.eth.contract(bounty_abi).at(bounty_address());
      // StandardBounties integration begins here
      // Set up Interplanetary file storage
      // IpfsApi is defined in the ipfs-api.js.
      // Is it better to use this JS file than the node package?  github.com/ipfs/

      // setup inter page state
      // localStorage[issueURL] = JSON.stringify({
      //   timestamp: null,
      //   dataHash: null,
      //   issuer: account,
      //   txid: null
      // });
      //
      // function syncDb() {
      //   // Need to pass the bountydetails as well, since I can't grab it from the
      //   // Standard Bounties contract.
      //   dataLayer.push({ event: 'fundissue' });
      //
      //   // update localStorage issuePackage
      //   var issuePackage = JSON.parse(localStorage[issueURL]);
      //
      //   issuePackage['timestamp'] = timestamp();
      //   localStorage[issueURL] = JSON.stringify(issuePackage);
      //
      //   _alert({ message: gettext('Submission sent to web3.') }, 'info');
      //   setTimeout(function() {
      //     delete localStorage['issueURL'];
      //     mixpanel.track('Submit New Bounty Success', {});
      //     document.location.href = '/funding/details/?url=' + issueURL;
      //   }, 1000);
      // }
      //
      // var do_bounty = function(callback) {
      // // Add data to IPFS and kick off all the callbacks.
      //   ipfsBounty.payload.issuer.address = account;
      //   ipfs.addJson(ipfsBounty, newIpfsCallback);
      // };
      //
      // do_bounty();

      // var instance = grants_abi.new( data.admin_address, data.token_address, data.amount_goal, data.frequency, data.gas_price, { from: web3.eth.coinbase gas: 4000000 });
      //
      // console.log(instance);

      //   const web3ContractInstance =
      //       web3.eth.contract(instance.abi).at(instance.address);
      //
      //   Subscription = new SubscriptionContract(
      //       web3ContractInstance, { from: OWNER, gas: 40000000 });
      //
      //
      // let newInstance = new web3.eth.Contract(grants_abi)

      // form.submit();

    }
  });

// Will need this for a subscription

  var check_balance_and_alert_user_if_not_enough = function(tokenAddress, amount) {
    var token_contract = web3.eth.contract(token_abi).at(tokenAddress);
    var from = web3.eth.coinbase;
    var token_details = tokenAddressToDetails(tokenAddress);
    var token_decimals = token_details['decimals'];
    var token_name = token_details['name'];

    token_contract.balanceOf.call(from, function(error, result) {
      if (error) return;
      var balance = result.toNumber() / Math.pow(10, 18);
      var balance_rounded = Math.round(balance * 10) / 10;

      if (parseFloat(amount) > balance) {
        var msg = gettext('You do not have enough tokens to fund this bounty. You have ') + balance_rounded + ' ' + token_name + ' ' + gettext(' but you need ') + amount + ' ' + token_name;

        _alert(msg, 'warning');
      }
    });
  };




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
