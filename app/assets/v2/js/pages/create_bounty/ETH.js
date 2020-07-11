/**
 * Handles Bounty creation for bounties funded in ETH/ERC20 tokens
 * Data is stored on IPFS + the data is stored in
 * standard bounties contract on the ethereum blockchain
 */

const promisify = (fun, params=[]) => {
  return new Promise((resolve, reject) => {
    fun(...params, (err, data) => {
      if (err) {
        reject(err);
      } else {
        resolve(data);
      }
    });
  });
};

const ethCreateBounty = async (data) => {
  try {
    bounty_address();
  } catch (exception) {
    _alert(gettext('You are on an unsupported network.  Please change your network to a supported network.'));
    unloading_button($('.js-submit'));
    return;
  }
  console.log(data)
  const githubUsername = data.githubUsername;
  const issueURL = data.issueURL.replace(/#.*$/, '');
  const notificationEmail = data.notificationEmail;
  let amount = data.amount;
  const tokenAddress = data.denomination;
  const token = tokenAddressToDetails(tokenAddress);
  const decimals = token['decimals'];
  const decimalDivisor = Math.pow(10, decimals);
  const expirationTimeDelta = $('#expirationTimeDelta').data('daterangepicker').endDate.utc().unix();
  const metadata = data.metadata;
  const privacy_preferences = {
    show_email_publicly: data.show_email_publicly,
    show_name_publicly: data.show_name_publicly
  };

  const mock_expire_date = 9999999999;
  let expire_date = expirationTimeDelta;

  if ($('#neverExpires').is(':checked')) {
    expire_date = mock_expire_date;
  }

  // https://github.com/ConsenSys/StandardBounties/issues/21
  let ipfsBounty = {
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
      tokenName: token['name'],
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
  const isETH = tokenAddress == '0x0000000000000000000000000000000000000000';
  new web3.eth.Contract(token_abi, tokenAddress)
  // const account = await promisify(web3.eth.getCoinbase);
  const account = selectedAccount;
  console.log(selectedAccount)
  const amountNoDecimal = amount;
  amount = amount * decimalDivisor;

  const bigAmount = new web3.utils.BN(BigInt(amount)).toString();

  // Create the bounty object.
  // This function instantiates a contract from the existing deployed Standard Bounties Contract.
  // bounty_abi is a giant object containing the different network options
  // bounty_address() is a function that looks up the name of the network and returns the hash code
  var bounty = new web3.eth.Contract(bounty_abi, bounty_address());
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
    if (typeof dataLayer !== 'undefined') {
      dataLayer.push({ event: 'fundissue' });
    }

    let issuePackage = JSON.parse(localStorage[issueURL]);

    issuePackage['timestamp'] = timestamp();
    localStorage[issueURL] = JSON.stringify(issuePackage);

    _alert({ message: gettext('Submission sent to web3.') }, 'info');
    setTimeout(() => {
      delete localStorage['issueURL'];
      document.location.href = '/funding/details/?url=' + issueURL + '&sb=1';
    }, 1000);
  }

  // web3 callback
  function web3Callback(result, error) {
    console.log(error,result);

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
      dataLayer.push({
        'event': 'new_bounty',
        'category': 'new_bounty',
        'action': 'metamask_signature_achieved'
      });
    }

    // update localStorage issuePackage
    let issuePackage = JSON.parse(localStorage[issueURL]);

    issuePackage['txid'] = result;
    localStorage[issueURL] = JSON.stringify(issuePackage);

    syncDb();
  }

  function newIpfsCallback(error, result) {
    console.log(error, result)
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
    let issuePackage = JSON.parse(localStorage[issueURL]);

    issuePackage['dataHash'] = result;
    localStorage[issueURL] = JSON.stringify(issuePackage);

    // bounty is a web3.js eth.contract address
    // The Ethereum network requires using ether to do stuff on it
    // issueAndActivateBounty is a method defined in the StandardBounties solidity contract.

    const eth_amount = isETH ? bigAmount : 0;
    const _paysTokens = !isETH;

    bounty.methods.issueAndActivateBounty(
      account, // _issuer
      mock_expire_date, // _deadline
      result, // _data (ipfs hash)
      bigAmount, // _fulfillmentAmount
      '0xf209d2b723b6417cbf04c07e733bee776105a073', // _arbiter
      _paysTokens, // _paysTokens
      tokenAddress, // _tokenContract
      bigAmount, // _value
    ).send({
      from: account,
      value: eth_amount,
      gas: web3.utils.toHex(318730),
      gasLimit: web3.utils.toHex(318730)
    }).then((result) => {web3Callback(result)}).catch(err => {
      web3Callback(undefined, err);
      console.log(err);
    });
  }

  const checkTokenAllowance = async () => {
    let currentAllowance = await getAllowance(bounty_address(), tokenAddress);

    if (BigInt(currentAllowance) < BigInt(bigAmount)) {
      let approvedAllowance;

      approvedAllowance = await approveAllowance(
        bounty_address(),
        tokenAddress
      );
    }
  }

  var do_bounty = function(callback) {
    handleTokenAuth().then(async () => {
      const fee = Number((Number(data.amount) * FEE_PERCENTAGE).toFixed(4));
      const to_address = '0x00De4B13153673BCAE2616b67bf822500d325Fc3';
      if (!isETH) {
        await checkTokenAllowance();
      }
      console.log(fee)
      indicateMetamaskPopup();
      if (FEE_PERCENTAGE == 0) {
        deductBountyAmount(fee, '');
      } else {
        if (isETH) {
          console.log(to_address,account, fee )
          web3.eth.sendTransaction({
            to: to_address,
            from: account,
            value: web3.utils.toWei(String(fee), "ether"),
          }).once('transactionHash', (txnHash, errors) => {

            console.log(txnHash, errors);
            indicateMetamaskPopup(true);
            if (errors) {
              _alert({ message: gettext('Unable to pay bounty fee. Please try again.') }, 'error');
            } else {
              console.log('saveAttestationData', result,fee)
              deductBountyAmount(fee, txnHash);
              saveAttestationData(
                txnHash,
                fee,
                '0x00De4B13153673BCAE2616b67bf822500d325Fc3',
                'bountyfee'
              );
            }
          });
        } else {
          const amountInWei = fee * 1.0 * Math.pow(10, token.decimals);
          const amountAsString = new web3.utils.BN(BigInt(amountInWei)).toString();
          const token_contract = new web3.eth.Contract(token_abi, tokenAddress);

          token_contract.methods.transfer(to_address, web3.utils.toHex(amountAsString)).send({from: selectedAccount},
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
    });
  };

  const deductBountyAmount = function(fee, txnId) {
    console.log('account',account)
    ipfsBounty.payload.issuer.address = account;
    ipfsBounty.payload.fee_tx_id = txnId;
    ipfsBounty.payload.fee_amount = fee;
    ipfs.addJson(ipfsBounty, newIpfsCallback);
    if (typeof ga != 'undefined') {
      if (fee == 0)
        dataLayer.push({
          'event': 'new_bounty',
          'category': 'new_bounty',
          'action': 'new_bounty_no_fees'
        });
      else
        dataLayer.push({
          'event': 'new_bounty',
          'category': 'new_bounty',
          'action': 'new_bounty_fee_paid'
        });
    }
  };

  const payFeaturedBounty = function() {
    indicateMetamaskPopup();
    web3.eth.sendTransaction({
      to: '0x00De4B13153673BCAE2616b67bf822500d325Fc3',
      from: selectedAccount,
      value: web3.utils.toWei(String(ethFeaturedPrice), 'ether'),
      gas: web3.utils.toHex(318730),
      gasLimit: web3.utils.toHex(318730)
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
    handleTokenAuth().then(isAuthedToken => {
      if (isAuthedToken) {
        data.featuredBounty ? payFeaturedBounty() : do_bounty();
      }
    });
  }

  if (check_balance_and_alert_user_if_not_enough(tokenAddress, amountNoDecimal)) {
    processBounty();
  } else {
     unloading_button($('.js-submit'));
     return false;
  }

  function check_balance_and_alert_user_if_not_enough(tokenAddress, amount, msg) {
    const token_contract = new web3.eth.Contract(token_abi, tokenAddress);
    const from = selectedAccount;
    const token_details = tokenAddressToDetails(tokenAddress);
    const token_decimals = token_details['decimals'];
    const token_name = token_details['name'];
    let total = parseFloat(amount) +
                  parseFloat((parseFloat(amount) * FEE_PERCENTAGE).toFixed(4)) +
                  (data.featuredBounty ? ethFeaturedPrice : 0);

    const checkBalance = (balance, total, token_name) => {
      console.log(balance, total, token_name)
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

    if (tokenAddress == '0x0000000000000000000000000000000000000000') {
      const walletBalance = web3.utils.fromWei(new web3.utils.BN(BigInt(balance)),'ether');

      return checkBalance(walletBalance, total, token_name);

    } else {
      token_contract.methods.balanceOf(from).call({from: from}, function(error, result) {
        if (error) return;
        const walletBalance = Number(new web3.utils.BN(BigInt(result)))

        return checkBalance(walletBalance, total, token_name);
      });
    }
  }
}
