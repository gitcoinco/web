/**
 * Handles Fulfillment for bounties funded in ETH/ERC20 tokens
 * Data is stored on IPFS + the data is stored in
 * standard bounties contract on the ethereum blockchain
 */

window.addEventListener('load', function() {
  setInterval(listen_for_web3_changes, 5000);
});

const ethFulfillBounty = data => {
  if (is_bounties_network) {
    waitforWeb3(actions_page_warn_if_not_on_same_network);
  }

  try {
    bounty_address();
  } catch (exception) {
    _alert(gettext('You are on an unsupported network.  Please change your network to a supported network.'));
    return;
  }

  loading_button($('.js-submit'));
  const githubUsername = data.githubUsername;
  const issueURL = data.issueURL;
  const notificationEmail = data.notificationEmail;
  const githubPRLink = data.githubPRLink;
  const hoursWorked = data.hoursWorked;
  const address = data.payoutAddress;

  localStorage['githubUsername'] = githubUsername;

  const account = web3.eth.coinbase;
  let bounty = web3.eth.contract(bounty_abi).at(bounty_address());

  ipfs.ipfsApi = IpfsApi(ipfsConfig);
  ipfs.setProvider(ipfsConfig);

  // https://github.com/ConsenSys/StandardBounties/issues/21
  const ipfsFulfill = {
    payload: {
      description: issueURL,
      sourceFileName: '',
      sourceFileHash: '',
      sourceDirectoryHash: '',
      fulfiller: {
        githubPRLink: githubPRLink,
        hoursWorked: hoursWorked,
        email: notificationEmail,
        githubUsername: githubUsername,
        address: address
      },
      metadata: {}
    },
    meta: {
      platform: 'gitcoin',
      schemaVersion: '0.1',
      schemaName: 'gitcoinFulfillment'
    }
  };

  const _callback = function(error, result) {
    let ignore_error = false;

    if (error) {
      console.error(error);
      ignore_error = String(error).indexOf('BigNumber') != -1;
    }
    document.ipfsDataHash = result;
    const run_main = !error || ignore_error;

    if (error && !ignore_error) {
      _alert({ message: gettext('Could not get bounty details.') });
      unloading_button($('.js-submit'));
    }

    if (run_main) {
      if (!ignore_error) {
        const web3Callback = function(error, result) {
          indicateMetamaskPopup(true);
          const next = function() {
            localStorage[issueURL] = JSON.stringify({
              timestamp: timestamp(),
              dataHash: null,
              issuer: account,
              txid: result
            });

            if (eventTag) {
              localStorage['pendingProject'] = standardBountyId;
            }

            const finishedComment = function() {
              dataLayer.push({ event: 'claimissue' });
              _alert({ message: gettext('Fulfillment submitted to web3.') }, 'info');
              setTimeout(() => {
                document.location.href = '/funding/details?url=' + issueURL;
              }, 1000);
            };

            finishedComment();
          };

          if (error) {
            console.error('err', error);
            _alert({ message: gettext('There was an error') });
            unloading_button($('.js-submit'));
          } else {
            next();
          }
        };

        const uri = '/api/v0.1/bounties/?event_tag=all&github_url=' + issueURL +
          '&network=' + $('input[name=network]').val() + '&standard_bounties_id=' +
          $('input[name=standard_bounties_id]').val();

        $.get(uri, function(results) {
          results = sanitizeAPIResults(results);
          result = results[0];
          if (result == null) {
            _alert({
              message: 'No active bounty found for this Github URL.'
            });
            unloading_button($('.js-submit'));
            return;
          }

          const bountyId = result['standard_bounties_id'];

          indicateMetamaskPopup();
          bounty.fulfillBounty(
            bountyId,
            document.ipfsDataHash,
            {
              from: web3.eth.accounts[0],
              gasPrice: web3.toHex($('#gasPrice').val() * Math.pow(10, 9))
            },
            web3Callback
          );
        });
      }
    }
  };
  ipfs.addJson(ipfsFulfill, _callback);
}
