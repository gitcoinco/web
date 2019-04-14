/* eslint-disable no-console */
/* eslint-disable nonblock-statement-body-position */
load_tokens();

/* Check if quickstart page is to be shown */
var localStorage;
var quickstartURL = document.location.origin + '/bounty/quickstart';

const FEE_PERCENTAGE = 10;

var new_bounty = {
  last_sync: new Date()
};

try {
  localStorage = window.localStorage;
} catch (e) {
  localStorage = {};
}

if (localStorage['quickstart_dontshow'] !== 'true' &&
    doShowQuickstart(document.referrer) &&
    doShowQuickstart(document.URL)) {
  window.location = quickstartURL;
}

function doShowQuickstart(url) {
  var fundingURL = document.location.origin + '/funding/new\\?';
  var bountyURL = document.location.origin + '/bounty/new\\?';
  var blacklist = [ fundingURL, bountyURL, quickstartURL ];

  for (var i = 0; i < blacklist.length; i++) {
    if (url.match(blacklist[i])) {
      return false;
    }
  }

  return true;
}

function lastSynced(current, last_sync) {
  var time = timeDifference(current, last_sync);

  return time;
}

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
    if ($('input[name=issueURL]').val() == '' || !validURL($('input[name=issueURL]').val())) {
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
    $('#no-issue-banner').hide();
    $('#edit-issue').attr('href', $('input[name=issueURL]').val());
    $('#issue-details, #issue-details-edit').show();

    $('#sync-issue').removeClass('disabled');
    $('.js-submit').removeClass('disabled');

    new_bounty.last_sync = new Date();
    retrieveIssueDetails();
    $('#last-synced').show();
    $('#last-synced span').html(lastSynced(new Date(), new_bounty.last_sync));
  }
});

$('#last-synced').hide();

$(document).ready(function() {

  $('#summary-bounty-amount').html($('input[name=amount]').val());
  $('#summary-fee-amount').html(($('input[name=amount]').val() / FEE_PERCENTAGE).toFixed(4));
  populateBountyTotal();

  // Load sidebar radio buttons from localStorage
  if (getParam('source')) {
    $('input[name=issueURL]').val(getParam('source'));
  } else if (getParam('url')) {
    $('input[name=issueURL]').val(getParam('url'));
  } else if (localStorage['issueURL']) {
    $('input[name=issueURL]').val(localStorage['issueURL']);
  }

  // fetch issue URL related info
  $('input[name=amount]').keyup(setUsdAmount);
  $('input[name=amount]').blur(setUsdAmount);
  $('input[name=usd_amount]').keyup(usdToAmount);
  $('input[name=usd_amount]').blur(usdToAmount);
  $('input[name=hours]').keyup(setUsdAmount);
  $('input[name=hours]').blur(setUsdAmount);
  $('select[name=denomination]').change(setUsdAmount);
  $('select[name=denomination]').change(promptForAuth);

  setTimeout(setUsdAmount, 1000);
  waitforWeb3(function() {
    promptForAuth();
  });

  $('#reservedForDiv').hide();
  
  $('select[name=permission_type]').on('change', function() {
    var val = $('select[name=permission_type] option:selected').val();

    if (val === 'approval') {
      $('#auto_approve_workers_container').show();
    } else {
      $('#auto_approve_workers_container').hide();
    }

    if (val === 'reserved') {
      $('#reservedForDiv').show();
    } else {
      $('#reservedForDiv').hide();
    }
  });

  var option = gettext('Reserved For - I will select a Gitcoin user.');

  $('select[name=project_type]').on('change', function() {
    var val = $('select[name=project_type] option:selected').val();

    if (String(val).toLowerCase() != 'traditional') {
      $("#permission_type option[value='reserved']").remove();
    } else {
      $('#permission_type').append('<option id="reservedForOptionID" value="reserved">' + option + '</option>');
    }
  });

  // revision action buttons
  $('#subtractAction').on('click', function() {
    var revision = parseInt($('input[name=revisions]').val());

    revision = revision - 1;
    if (revision > 0) {
      $('input[name=revisions]').val(revision);
    }
  });

  $('#addAction').on('click', function() {
    var revision = parseInt($('input[name=revisions]').val());

    revision = revision + 1;
    $('input[name=revisions]').val(revision);
  });

  if ($('input[name=issueURL]').val() != '' && !isPrivateRepo) {
    retrieveIssueDetails();
  }

  $('.js-select2').each(function() {
    $(this).select2();
  });

  $('.submit_bounty select').each(function(evt) {
    $('.select2-selection__rendered').removeAttr('title');
  });

  $('.select2-container').on('click', function() {
    $('.select2-container .select2-search__field').remove();
  });

  $('select[name=denomination]').select2();
  if ($('input[name=amount]').val().trim().length > 0) {
    setUsdAmount();
  }

  var open_panel = function(checkboxSelector, targetSelector, do_focus) {
    setTimeout(function() {
      var isChecked = $(checkboxSelector).is(':checked');

      if (isChecked) {
        $(targetSelector).removeClass('hidden');
        if (do_focus) {
          $(targetSelector).focus();
        }
      } else {
        $(targetSelector).addClass('hidden');
      }
    }, 10);
  };

  $('#hiringRightNow').on('click', () => {
    open_panel('#hiringRightNow', '#jobDescription', true);
  });

  $('#specialEvent').on('click', () => {
    open_panel('#specialEvent', '#eventTag', true);
  });

  userSearch('#reservedFor', false);

  $('#submitBounty').validate({
    submitHandler: function(form) {
      try {
        bounty_address();
      } catch (exception) {
        _alert(gettext('You are on an unsupported network.  Please change your network to a supported network.'));
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
        tokenName
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
          expire_date: expire_date
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

      if (!isETH) {
        check_balance_and_alert_user_if_not_enough(
          tokenAddress,
          amount,
          'You do not have enough tokens to fund this bounty.');
      }

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
        const fee = Number((Number(data.amount) / FEE_PERCENTAGE).toFixed(4));
        const to_address = '0x00De4B13153673BCAE2616b67bf822500d325Fc3';
        const gas_price = web3.toHex($('#gasPrice').val() * Math.pow(10, 9));

        indicateMetamaskPopup();
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
              ipfsBounty.payload.issuer.address = account;
              ipfsBounty.payload.fee_tx_id = txnId;
              ipfsBounty.payload.fee_amount = fee;
              ipfs.addJson(ipfsBounty, newIpfsCallback);
              if (typeof ga != 'undefined') {
                ga('send', 'event', 'new_bounty', 'new_bounty_fee_paid');
              }
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
              } else {
                ipfsBounty.payload.issuer.address = account;
                ipfsBounty.payload.fee_tx_id = txnId;
                ipfsBounty.payload.fee_amount = fee;
                ipfs.addJson(ipfsBounty, newIpfsCallback);
                if (typeof ga != 'undefined') {
                  ga('send', 'event', 'new_bounty', 'new_bounty_fee_paid');
                }
              }
            }
          );
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
          _alert(response.message, 'info');
          ipfsBounty.payload.unsigned_nda = response.bounty_doc_id;
          if (data.featuredBounty) payFeaturedBounty();
          else do_bounty();
        }).fail(function(error) {
          _alert('Unable to upload NDA. ', 'error');
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

      if ($("input[type='radio'][name='repo_type']:checked").val() == 'private' && $('#issueNDA')[0].files[0]) {
        uploadNDA();
      } else if (data.featuredBounty) {
        payFeaturedBounty();
      } else {
        do_bounty();
      }
    }
  });
});

$(window).on('load', function() {
  if (params.has('type')) {
    let checked = params.get('type');

    toggleCtaPlan(checked);
    $(`input[name=repo_type][value=${checked}]`).prop('checked', 'true');
  } else {
    params.append('type', 'public');
    window.history.replaceState({}, '', location.pathname + '?' + params);
  }
  $('input[name=repo_type]').change(function() {
    toggleCtaPlan($(this).val());
  });
});

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
  const bountyToken = $('#summary-bounty-token').html();
  const bountyAmount = Number($('#summary-bounty-amount').html());
  const bountyFee = Number((bountyAmount / FEE_PERCENTAGE).toFixed(4));
  const isFeaturedBounty = $('input[name=featuredBounty]:checked').val();
  let totalBounty = bountyAmount + bountyFee;
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

  $('#fee-percentage').html(FEE_PERCENTAGE);
  $('#fee-amount').html(bountyFee);
  $('#fee-token').html(bountyToken);
  $('#summary-total-amount').html(total);
};

let isPrivateRepo = false;
let params = (new URL(document.location)).searchParams;

const setPrivateForm = () => {
  $('#title').removeClass('hidden');
  $('#description, #title').prop('readonly', false);
  $('#description, #title').prop('required', true);
  $('#no-issue-banner').hide();
  $('#issue-details, #issue-details-edit').show();
  $('#sync-issue').removeClass('disabled');
  $('#last-synced, #edit-issue, #sync-issue, #title--text').hide();
  $('#featured-bounty-add').hide();

  $('#admin_override_suspend_auto_approval').prop('checked', false);
  $('#admin_override_suspend_auto_approval').attr('disabled', true);
  $('#show_email_publicly').attr('disabled', true);
  $('#cta-subscription, #private-repo-instructions').removeClass('d-md-none');
  $('#nda-upload').show();
  $('#issueNDA').prop('required', true);

  $('#project_type').select2().val('traditional');
  $('#permission_type').select2().val('approval');
  $('#project_type, #permission_type').select2().prop('disabled', true).trigger('change');
  $('#keywords').select2({
    placeholder: 'Select tags',
    tags: 'true',
    allowClear: true
  });
};

const setPublicForm = () => {
  $('#title').addClass('hidden');
  $('#description, #title').prop('readonly', true);
  $('#no-issue-banner').show();
  $('#issue-details, #issue-details-edit').hide();
  $('#sync-issue').addClass('disabled');
  $('.js-submit').addClass('disabled');
  $('#last-synced, #edit-issue , #sync-issue, #title--text').show();
  $('#featured-bounty-add').show();

  $('#admin_override_suspend_auto_approval').prop('checked', true);
  $('#admin_override_suspend_auto_approval').attr('disabled', false);
  $('#show_email_publicly').attr('disabled', false);
  $('#cta-subscription, #private-repo-instructions').addClass('d-md-none');
  $('#nda-upload').hide();
  $('#issueNDA').prop('required', false);

  $('#project_type, #permission_type').select2().prop('disabled', false).trigger('change');
  retrieveIssueDetails();
};

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
