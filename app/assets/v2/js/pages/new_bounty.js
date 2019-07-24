/* eslint-disable no-console */
/* eslint-disable nonblock-statement-body-position */
/* eslint-disable no-lonely-if */
load_tokens();

var localStorage = window.localStorage ? window.localStorage : {};
const quickstartURL = document.location.origin + '/bounty/quickstart';

let params = (new URL(document.location)).searchParams;

const FEE_PERCENTAGE = document.FEE_PERCENTAGE / 100.0;

var new_bounty = {
  last_sync: new Date()
};

if (localStorage['quickstart_dontshow'] !== 'true' &&
    doShowQuickstart(document.referrer) &&
    doShowQuickstart(document.URL)) {
  window.location = quickstartURL;
}

function doShowQuickstart(url) {
  let blacklist = [];

  blacklist.push(document.location.origin + '/bounty/quickstart');
  blacklist.push(document.location.origin + '/bounty/new\\?');
  blacklist.push(document.location.origin + '/funding/new\\?');
  blacklist.push(document.location.origin + '/new\\?');

  for (let i = 0; i < blacklist.length; i++) {
    if (url.match(blacklist[i]))
      return false;
  }

  return true;
}

var processedData;

$('.select2-tag__choice').on('click', function() {
  $('#invite-contributors.js-select2').data('select2').dataAdapter.select(processedData[0].children[$(this).data('id')]);
});

const getSuggestions = () => {
  let queryParams = {};

  queryParams.keywords = $('#keywords').val();
  queryParams.invite = params.get('invite') || '';

  let searchParams = new URLSearchParams(queryParams);

  const settings = {
    url: `/api/v0.1/get_suggested_contributors?${searchParams}`,
    method: 'GET',
    processData: false,
    dataType: 'json',
    contentType: false
  };

  $.ajax(settings).done(function(response) {
    let groups = {
      'contributors': 'Recently worked with you',
      'recommended_developers': 'Recommended based on skills',
      'verified_developers': 'Verified contributors',
      'invites': 'Invites'
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
        children.text = children.fulfiller_github_username || children.user__profile__handle || children.handle;
        children.id = generalIndex;
        if (obj.text == 'Invites') {
          children.selected = true;
          $('#reserve-section').collapse('show');
        }
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
$('#keywords').on('change', getSuggestions);

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

function lastSynced(current, last_sync) {
  var time = timeDifference(current, last_sync);

  return time;
}

const setPrivateForm = () => {
  $('#description, #title').prop('readonly', false);
  $('#description, #title').prop('required', true);
  $('#no-issue-banner').hide();
  $('#issue-details').removeClass('issue-details-public');
  $('#issue-details, #issue-details-edit').show();
  $('#sync-issue').removeClass('disabled');
  $('#last-synced, #edit-issue, #sync-issue').hide();
  $('#show_email_publicly').attr('disabled', true);
  $('#cta-subscription, #private-repo-instructions').removeClass('d-md-none');
  $('#nda-upload').show();
  $('#issueNDA').prop('required', true);
  $('.permissionless').addClass('disabled');
  $('#permissionless').attr('disabled', true);
  $('#admin_override_suspend_auto_approval').prop('checked', false);
  $('#admin_override_suspend_auto_approval').attr('disabled', true);
  $('#keywords').select2({
    placeholder: 'Select tags',
    tags: 'true',
    allowClear: true,
    tokenSeparators: [ ',', ' ' ]
  }).trigger('change');
};

const setPublicForm = () => {
  $('#description, #title').prop('readonly', true);
  $('#no-issue-banner').show();
  $('#issue-details').addClass('issue-details-public');
  $('#issue-details, #issue-details-edit').hide();
  $('#sync-issue').addClass('disabled');
  $('.js-submit').addClass('disabled');
  $('#last-synced, #edit-issue , #sync-issue').show();
  $('#show_email_publicly').attr('disabled', false);
  $('#cta-subscription, #private-repo-instructions').addClass('d-md-none');
  $('#nda-upload').hide();
  $('#issueNDA').prop('required', false);
  $('.permissionless').removeClass('disabled');
  $('#permissionless').attr('disabled', false);
  $('#admin_override_suspend_auto_approval').prop('checked', true);
  $('#admin_override_suspend_auto_approval').attr('disabled', false);
  retrieveIssueDetails();
};


$(function() {

  $('#last-synced').hide();
  $('.js-select2').each(function() {
    $(this).select2({
      minimumResultsForSearch: Infinity
    });
  });

  let checked = params.get('type');

  if (params.has('type')) {

    $(`.${checked}`).button('toggle');

  } else {
    params.append('type', 'public');
    window.history.replaceState({}, '', location.pathname + '?' + params);
  }
  toggleCtaPlan(checked);

  $('input[name=repo_type]').change(function() {
    toggleCtaPlan($(this).val());
  });

  populateBountyTotal();

  // Load sidebar radio buttons from localStorage
  if (getParam('source')) {
    $('input[name=issueURL]').val(getParam('source'));
  } else if (getParam('url')) {
    $('input[name=issueURL]').val(getParam('url'));
  } else if (localStorage['issueURL']) {
    $('input[name=issueURL]').val(localStorage['issueURL']);
  }


  setTimeout(setUsdAmount, 1000);
  waitforWeb3(function() {
    promptForAuth();
  });
  // fetch issue URL related info
  $('input[name=amount]').keyup(setUsdAmount);
  $('input[name=amount]').blur(setUsdAmount);
  $('input[name=usd_amount]').keyup(usdToAmount);
  $('input[name=usd_amount]').blur(usdToAmount);
  $('input[name=hours]').keyup(setUsdAmount);
  $('input[name=hours]').blur(setUsdAmount);
  $('input[name=amount]').on('change', function() {
    const amount = $('input[name=amount]').val();

    $('#summary-bounty-amount').html(amount);
    $('#summary-fee-amount').html((amount * FEE_PERCENTAGE).toFixed(4));
    populateBountyTotal();
  });

  var triggerDenominationUpdate = function(e) {
    setUsdAmount();
    promptForAuth();
    const token_val = $('select[name=denomination]').val();
    const tokendetails = tokenAddressToDetails(token_val);
    var token = tokendetails['name'];


    $('#summary-bounty-token').html(token);
    $('#summary-fee-token').html(token);
    populateBountyTotal();
  };

  $('select[name=denomination]').change(triggerDenominationUpdate);
  waitforWeb3(function() {
    setTimeout(function() {
      triggerDenominationUpdate();
    }, 1000);
  });

  $('#featuredBounty').on('change', function() {
    if ($(this).prop('checked')) {
      if (document.FEE_PERCENTAGE == 0)
        $('#confirmation').html('2');
      else
        $('#confirmation').html('3');

      $('.feature-amount').show();
    } else {
      if (document.FEE_PERCENTAGE == 0)
        $('#confirmation').html('1');
      else
        $('#confirmation').html('2');

      $('.feature-amount').hide();
    }
    populateBountyTotal();
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

  if ($('input[name=issueURL]').val() != '' && !isPrivateRepo) {
    retrieveIssueDetails();
  }

  $('select[name=denomination]').select2();
  if ($('input[name=amount]').val().trim().length > 0) {
    setUsdAmount();
  }

  if (params.get('reserved')) {
    $('#reserve-section').collapse('show');
  }

  userSearch(
    '#reservedFor',
    // show address
    false,
    // theme
    '',
    // initial data
    params.get('reserved') ? [params.get('reserved')] : [],
    // allowClear
    true
  );


});

$('#reservedFor').on('select2:select', function(e) {
  $('#permissionless').click();
});

$('#sync-issue').on('click', function(event) {
  event.preventDefault();
  if (!$('#sync-issue').hasClass('disabled')) {
    new_bounty.last_sync = new Date();
    retrieveIssueDetails();
    $('#last-synced span').html(lastSynced(new Date(), new_bounty.last_sync));
  }
});

$('#issueURL').focusout(function() {
  if (isPrivateRepo) {
    setPrivateForm();
    var validated = $('input[name=issueURL]').val() == '' || !validURL($('input[name=issueURL]').val());

    if (validated) {
      $('.js-submit').addClass('disabled');
    } else {
      $('.js-submit').removeClass('disabled');
    }
    return;
  }

  setInterval(function() {
    $('#last-synced span').html(timeDifference(new Date(), new_bounty.last_sync));
  }, 6000);

  if ($('input[name=issueURL]').val() == '' || !validURL($('input[name=issueURL]').val())) {
    $('#issue-details, #issue-details-edit').hide();
    $('#no-issue-banner').show();

    $('#title').val('');
    $('#description').val('');

    $('#last-synced').hide();
    $('.js-submit').addClass('disabled');
  } else {
    $('#edit-issue').attr('href', $('input[name=issueURL]').val());

    $('#sync-issue').removeClass('disabled');
    $('.js-submit').removeClass('disabled');

    new_bounty.last_sync = new Date();
    retrieveIssueDetails();
    $('#last-synced').show();
    $('#last-synced span').html(lastSynced(new Date(), new_bounty.last_sync));
  }
});

const togggleEnabled = function(checkboxSelector, targetSelector, do_focus) {
  let isChecked = $(checkboxSelector).is(':checked');

  if (isChecked) {
    $(targetSelector).attr('disabled', false);

    if (do_focus) {
      $(targetSelector).focus();
    }
  } else {
    $(targetSelector).attr('disabled', true);
    if ($(targetSelector).hasClass('select2-hidden-accessible')) {
      $(targetSelector).select2().trigger('change');
    }
  }
};

$('#hiringRightNow').on('click', () => {
  togggleEnabled('#hiringRightNow', '#jobDescription', true);
});

$('#specialEvent').on('click', () => {
  togggleEnabled('#specialEvent', '#eventTag', true);
});

$('#submitBounty').validate({
  errorPlacement: function(error, element) {
    if (element.attr('name') == 'bounty_category') {
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
    try {
      bounty_address();
    } catch (exception) {
      _alert(gettext('You are on an unsupported network.  Please change your network to a supported network.'));
      unloading_button($('.js-submit'));
      return;
    }
    if (typeof ga != 'undefined') {
      ga('send', 'event', 'new_bounty', 'new_bounty_form_submit');
    }

    var data = {};
    var disabled = $(form)
      .find(':input:disabled')
      .removeAttr('disabled');

    $.each($(form).serializeArray(), function() {
      if (data[this.name]) {
        data[this.name] += ',' + this.value;
      } else {
        data[this.name] = this.value;
      }
    });

    if (data.repo_type == 'private' && data.project_type != 'traditional' && data.permission_type != 'approval') {
      _alert(gettext('The project type and/or permission type of bounty does not validate for a private repo'));
      unloading_button($('.js-submit'));
    }

    disabled.attr('disabled', 'disabled');

    // setup
    loading_button($('.js-submit'));
    var githubUsername = data.githubUsername;
    var issueURL = data.issueURL.replace(/#.*$/, '');
    var notificationEmail = data.notificationEmail;
    var amount = data.amount;
    var tokenAddress = data.denomination;
    var token = tokenAddressToDetails(tokenAddress);
    var decimals = token['decimals'];
    var tokenName = token['name'];
    var decimalDivisor = Math.pow(10, decimals);
    var expirationTimeDelta = data.expirationTimeDelta;
    let reservedFor = $('.username-search').select2('data')[0];
    let inviteContributors = $('#invite-contributors.js-select2').select2('data').map((user) => {
      return user.profile__id;
    });

    var metadata = {
      issueTitle: data.title,
      issueDescription: data.description,
      issueKeywords: data.keywords ? data.keywords : '',
      githubUsername: data.githubUsername,
      notificationEmail: data.notificationEmail,
      fullName: data.fullName,
      experienceLevel: data.experience_level,
      projectLength: data.project_length,
      bountyType: data.bounty_type,
      estimatedHours: data.hours,
      fundingOrganisation: data.fundingOrganisation,
      eventTag: data.specialEvent ? (data.eventTag || '') : '',
      is_featured: data.featuredBounty,
      repo_type: data.repo_type,
      featuring_date: data.featuredBounty && ((new Date().getTime() / 1000) | 0) || 0,
      reservedFor: reservedFor ? reservedFor.text : '',
      tokenName,
      invite: inviteContributors,
      bounty_categories: data.bounty_category
    };

    var privacy_preferences = {
      show_email_publicly: data.show_email_publicly,
      show_name_publicly: data.show_name_publicly
    };

    var expire_date =
      parseInt(expirationTimeDelta) + ((new Date().getTime() / 1000) | 0);
    var mock_expire_date = 9999999999; // 11/20/2286, https://github.com/Bounties-Network/StandardBounties/issues/25

    // https://github.com/ConsenSys/StandardBounties/issues/21
    var ipfsBounty = {
      payload: {
        title: metadata.issueTitle,
        description: metadata.issueDescription,
        sourceFileName: '',
        sourceFileHash: '',
        sourceDirectoryHash: '',
        issuer: {
          name: metadata.fullName,
          email: metadata.notificationEmail,
          githubUsername: metadata.githubUsername,
          address: '' // Fill this in later
        },
        schemes: {
          project_type: data.project_type,
          permission_type: data.permission_type,
          auto_approve_workers: !!data.auto_approve_workers
        },
        hiring: {
          hiringRightNow: !!data.hiringRightNow,
          jobDescription: data.jobDescription
        },
        funding_organisation: metadata.fundingOrganisation,
        is_featured: metadata.is_featured,
        repo_type: metadata.repo_type,
        featuring_date: metadata.featuring_date,
        privacy_preferences: privacy_preferences,
        funders: [],
        categories: metadata.issueKeywords.split(','),
        created: (new Date().getTime() / 1000) | 0,
        webReferenceURL: issueURL,
        fee_amount: 0,
        fee_tx_id: '0x0',
        // optional fields
        metadata: metadata,
        tokenName: tokenName,
        tokenAddress: tokenAddress,
        expire_date: expire_date,
        coupon_code: $('#coupon_code').val()
      },
      meta: {
        platform: 'gitcoin',
        schemaVersion: '0.1',
        schemaName: 'gitcoinBounty'
      }
    };

    // validation
    var isError = false;

    $(this).attr('disabled', 'disabled');

    // save off local state for later
    localStorage['issueURL'] = issueURL;
    localStorage['notificationEmail'] = notificationEmail;
    localStorage['githubUsername'] = githubUsername;
    localStorage['tokenAddress'] = tokenAddress;
    localStorage.removeItem('bountyId');

    // setup web3
    // TODO: web3 is using the web3.js file.  In the future we will move
    // to the node.js package.  github.com/ethereum/web3.js
    var isETH = tokenAddress == '0x0000000000000000000000000000000000000000';
    var token_contract = web3.eth.contract(token_abi).at(tokenAddress);
    var account = web3.eth.coinbase;
    let amountNoDecimal = amount;

    amount = amount * decimalDivisor;
    // Create the bounty object.
    // This function instantiates a contract from the existing deployed Standard Bounties Contract.
    // bounty_abi is a giant object containing the different network options
    // bounty_address() is a function that looks up the name of the network and returns the hash code
    var bounty = web3.eth.contract(bounty_abi).at(bounty_address());
    // StandardBounties integration begins here
    // Set up Interplanetary file storage
    // IpfsApi is defined in the ipfs-api.js.
    // Is it better to use this JS file than the node package?  github.com/ipfs/

    ipfs.ipfsApi = IpfsApi(ipfsConfig);
    ipfs.setProvider(ipfsConfig);

    // setup inter page state
    localStorage[issueURL] = JSON.stringify({
      timestamp: null,
      dataHash: null,
      issuer: account,
      txid: null
    });

    function syncDb() {
      // Need to pass the bountydetails as well, since I can't grab it from the
      // Standard Bounties contract.
      if (typeof dataLayer !== 'undefined') {
        dataLayer.push({ event: 'fundissue' });
      }

      // update localStorage issuePackage
      var issuePackage = JSON.parse(localStorage[issueURL]);

      issuePackage['timestamp'] = timestamp();
      localStorage[issueURL] = JSON.stringify(issuePackage);

      _alert({ message: gettext('Submission sent to web3.') }, 'info');
      setTimeout(() => {
        delete localStorage['issueURL'];
        document.location.href = '/funding/details/?url=' + issueURL;
      }, 1000);
    }

    // web3 callback
    function web3Callback(error, result) {
      indicateMetamaskPopup(true);
      if (error) {
        console.error(error);
        _alert(
          {
            message:
              gettext('There was an error.  Please try again or contact support.')
          },
          'error'
        );
        unloading_button($('.js-submit'));
        return;
      }

      if (typeof ga != 'undefined') {
        ga('send', 'event', 'new_bounty', 'metamask_signature_achieved');
      }


      // update localStorage issuePackage
      var issuePackage = JSON.parse(localStorage[issueURL]);

      issuePackage['txid'] = result;
      localStorage[issueURL] = JSON.stringify(issuePackage);

      syncDb();
    }

    function newIpfsCallback(error, result) {
      indicateMetamaskPopup();
      if (error) {
        console.error(error);
        _alert({
          message: gettext('There was an error.  Please try again or contact support.')
        }, 'error');
        unloading_button($('.js-submit'));
        return;
      }

      // cache data hash to find bountyId later
      // update localStorage issuePackage
      var issuePackage = JSON.parse(localStorage[issueURL]);

      issuePackage['dataHash'] = result;
      localStorage[issueURL] = JSON.stringify(issuePackage);

      // bounty is a web3.js eth.contract address
      // The Ethereum network requires using ether to do stuff on it
      // issueAndActivateBounty is a method defined in the StandardBounties solidity contract.

      var eth_amount = isETH ? amount : 0;
      var _paysTokens = !isETH;
      var bountyIndex = bounty.issueAndActivateBounty(
        account, // _issuer
        mock_expire_date, // _deadline
        result, // _data (ipfs hash)
        amount, // _fulfillmentAmount
        0x0, // _arbiter
        _paysTokens, // _paysTokens
        tokenAddress, // _tokenContract
        amount, // _value
        {
        // {from: x, to: y}
          from: account,
          value: eth_amount,
          gasPrice: web3.toHex($('#gasPrice').val() * Math.pow(10, 9)),
          gas: web3.toHex(318730),
          gasLimit: web3.toHex(318730)
        },
        web3Callback // callback for web3
      );
    }

    var do_bounty = function(callback) {
      callMethodIfTokenIsAuthed(function(x, y) {
        const fee = Number((Number(data.amount) * FEE_PERCENTAGE).toFixed(4));
        const to_address = '0x00De4B13153673BCAE2616b67bf822500d325Fc3';
        const gas_price = web3.toHex($('#gasPrice').val() * Math.pow(10, 9));

        indicateMetamaskPopup();
        if (FEE_PERCENTAGE == 0) {
          deductBountyAmount(fee, '');
        } else {
          if (isETH) {
            web3.eth.sendTransaction({
              to: to_address,
              from: web3.eth.coinbase,
              value: web3.toWei(fee, 'ether'),
              gasPrice: gas_price
            }, function(error, txnId) {
              indicateMetamaskPopup(true);
              if (error) {
                _alert({ message: gettext('Unable to pay bounty fee. Please try again.') }, 'error');
              } else {
                deductBountyAmount(fee, txnId);
              }
            });
          } else {
            const amountInWei = fee * 1.0 * Math.pow(10, token.decimals);
            const token_contract = web3.eth.contract(token_abi).at(tokenAddress);

            token_contract.transfer(to_address, amountInWei, { gasPrice: gas_price },
              function(error, txnId) {
                indicateMetamaskPopup(true);
                if (error) {
                  _alert({ message: gettext('Unable to pay bounty fee. Please try again.') }, 'error');
                  unloading_button($('.js-submit'));
                } else {
                  deductBountyAmount(fee, txnId);
                }
              }
            );
          }
        }
      }, promptForAuthFailure);
    };

    const deductBountyAmount = function(fee, txnId) {
      ipfsBounty.payload.issuer.address = account;
      ipfsBounty.payload.fee_tx_id = txnId;
      ipfsBounty.payload.fee_amount = fee;
      ipfs.addJson(ipfsBounty, newIpfsCallback);
      if (typeof ga != 'undefined') {
        if (fee == 0)
          ga('send', 'event', 'new_bounty', 'new_bounty_no_fees');
        else
          ga('send', 'event', 'new_bounty', 'new_bounty_fee_paid');
      }
    };

    const uploadNDA = function() {
      const formData = new FormData();

      formData.append('docs', $('#issueNDA')[0].files[0]);
      formData.append('doc_type', 'unsigned_nda');
      const settings = {
        url: '/api/v0.1/bountydocument',
        method: 'POST',
        processData: false,
        dataType: 'json',
        contentType: false,
        data: formData
      };

      $.ajax(settings).done(function(response) {
        if (response.status == 200) {
          _alert(response.message, 'info');
          ipfsBounty.payload.unsigned_nda = response.bounty_doc_id;
          if (data.featuredBounty) payFeaturedBounty();
          else do_bounty();
        } else {
          _alert('Unable to upload NDA. ', 'error');
          unloading_button($('.js-submit'));
          console.log('NDA error:', response.message);
        }
      }).fail(function(error) {
        _alert('Unable to upload NDA. ', 'error');
        unloading_button($('.js-submit'));
        console.log('NDA error:', error);
      });
    };

    const payFeaturedBounty = function() {
      indicateMetamaskPopup();
      web3.eth.sendTransaction({
        to: '0x00De4B13153673BCAE2616b67bf822500d325Fc3',
        from: web3.eth.coinbase,
        value: web3.toWei(ethFeaturedPrice, 'ether'),
        gasPrice: web3.toHex($('#gasPrice').val() * Math.pow(10, 9)),
        gas: web3.toHex(318730),
        gasLimit: web3.toHex(318730)
      },
      function(error, result) {
        indicateMetamaskPopup(true);
        if (error) {
          _alert({ message: gettext('Unable to upgrade to featured bounty. Please try again.') }, 'error');
          unloading_button($('.js-submit'));
          console.log(error);
        } else {
          saveAttestationData(
            result,
            ethFeaturedPrice,
            '0x00De4B13153673BCAE2616b67bf822500d325Fc3',
            'featuredbounty'
          );
        }
        do_bounty();
      });
    };

    function processBounty() {
      if ($("input[type='radio'][name='repo_type']:checked").val() == 'private' && $('#issueNDA')[0].files[0]) {
        uploadNDA();
      } else if (data.featuredBounty) {
        payFeaturedBounty();
      } else {
        do_bounty();
      }
    }

    if (check_balance_and_alert_user_if_not_enough(tokenAddress, amountNoDecimal)) {
      processBounty();
    } else {
      return unloading_button($('.js-submit'));
    }

    function check_balance_and_alert_user_if_not_enough(tokenAddress, amount, msg) {
      const token_contract = web3.eth.contract(token_abi).at(tokenAddress);
      const from = web3.eth.coinbase;
      const token_details = tokenAddressToDetails(tokenAddress);
      const token_decimals = token_details['decimals'];
      const token_name = token_details['name'];
      let total = parseFloat(amount) +
                    parseFloat((parseFloat(amount) * FEE_PERCENTAGE).toFixed(4)) +
                    (data.featuredBounty ? ethFeaturedPrice : 0);

      const checkBalance = (balance, total, token_name) => {

        if (parseFloat(total) > balance) {
          let isFeaturedToken = token_name !== 'ETH' && data.featuredBounty;

          total = isFeaturedToken ? total - ethFeaturedPrice : total;
          const balance_rounded = Math.round(balance * 10) / 10;
          let msg = gettext('You do not have enough tokens to fund this bounty. You have ') +
            balance_rounded + ' ' + token_name + ' ' + gettext(' but you need ') + total +
            ' ' + token_name;

          if (isFeaturedToken) {
            msg += ` + ${ethFeaturedPrice} ETH`;
          }
          _alert(msg, 'warning');
        } else {
          return processBounty();
        }
      };
      var walletBalance;

      if (tokenAddress == '0x0000000000000000000000000000000000000000') {
        let ethBalance = getBalance(from);

        ethBalance.then(
          function(result) {
            walletBalance = result.toNumber() / Math.pow(10, token_decimals);
            return checkBalance(walletBalance, total, token_name);
          }
        );
      } else {
        token_contract.balanceOf.call(from, function(error, result) {
          if (error) return;
          walletBalance = result.toNumber() / Math.pow(10, token_decimals);
          return checkBalance(walletBalance, total, token_name);
        });
      }
    }
  }
});

$('[name=permission_type]').on('change', function() {
  var val = $('input[name=permission_type]:checked').val();

  if (val === 'approval') {
    $('#admin_override_suspend_auto_approval').attr('disabled', false);
  } else {
    $('#admin_override_suspend_auto_approval').prop('checked', false);
    $('#admin_override_suspend_auto_approval').attr('disabled', true);
  }
});

var getBalance = (address) => {
  return new Promise (function(resolve, reject) {
    web3.eth.getBalance(address, function(error, result) {
      if (error) {
        reject(error);
      } else {
        resolve(result);
      }
    });
  });
};

let usdFeaturedPrice = $('.featured-price-usd').text();
let ethFeaturedPrice;
let bountyFee;

getAmountEstimate(usdFeaturedPrice, 'ETH', (amountEstimate) => {
  ethFeaturedPrice = amountEstimate['value'];
  $('.featured-price-eth').text(`+${amountEstimate['value']} ETH`);
  $('#summary-feature-amount').text(`${amountEstimate['value']}`);
});

/**
 * Calculates total amount needed to fund the bounty
 * Bounty Amount + Fee + Featured Bounty
 */
const populateBountyTotal = () => {

  const amount = $('input[name=amount]').val();
  const fee = (amount * FEE_PERCENTAGE).toFixed(4);

  $('#summary-bounty-amount').html(amount);
  $('#summary-fee-amount').html(fee);

  const bountyToken = $('#summary-bounty-token').html();
  const bountyAmount = Number($('#summary-bounty-amount').html());
  const bountyFee = Number((bountyAmount * FEE_PERCENTAGE).toFixed(4));
  const isFeaturedBounty = $('input[name=featuredBounty]:checked').val();
  let totalBounty = Number((bountyAmount + bountyFee).toFixed(4));
  let total = '';

  if (isFeaturedBounty) {
    const featuredBountyAmount = Number($('#summary-feature-amount').html());

    if (bountyToken == 'ETH') {
      totalBounty = (totalBounty + featuredBountyAmount).toFixed(4);
      total = `${totalBounty} ETH`;
    } else {
      total = `${totalBounty} ${bountyToken} + ${featuredBountyAmount} ETH`;
    }
  } else {
    total = `${totalBounty} ${bountyToken}`;
  }

  $('.fee-percentage').html(FEE_PERCENTAGE * 100);
  $('#fee-amount').html(bountyFee);
  $('#fee-token').html(bountyToken);
  $('#summary-total-amount').html(total);
};

let isPrivateRepo = false;

const toggleCtaPlan = (value) => {
  if (value === 'private') {

    params.set('type', 'private');
    isPrivateRepo = true;
    setPrivateForm();
  } else {

    params.set('type', 'public');
    isPrivateRepo = false;
    setPublicForm();
  }
  window.history.replaceState({}, '', location.pathname + '?' + params);
};
