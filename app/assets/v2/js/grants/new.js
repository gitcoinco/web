/* eslint-disable no-console */

$(document).ready(function() {
  if (web3 && web3.eth) {
    web3.eth.net.isListening((error, connectionStatus) => {
      if (connectionStatus)
        init();
    });
  }
});

function saveGrant({grantData = [], isFinal = false}) {
  $.ajax({
    type: 'post',
    url: '',
    data: grantData,
    success: json => {
      if (isFinal) {
        document.suppress_loading_leave_code = true;
        window.location = json.url;
      }
    },
    error: () => {
      _alert({ message: gettext('Your grant failed to save. Please try again.') }, 'error');
    }
  });
}

const processReceipt = receipt => {
  let data = {
    'contract_address': receipt.contractAddress,
    'csrfmiddlewaretoken': $("#create-grant input[name='csrfmiddlewaretoken']").val(),
    'transaction_hash': $('#transaction_hash').val()
  };

  saveGrant({grantData: data, isFinal: true});
};

const init = () => {
  if (localStorage['grants_quickstart_disable'] !== 'true') {
    window.location = document.location.origin + '/grants/quickstart';
  }

  web3.eth.getAccounts(function(err, accounts) {
    $('#input-admin_address').val(accounts[0]);
    $('#contract_owner_address').val(accounts[0]);
  });

  $('#js-token').append("<option value='0x0000000000000000000000000000000000000000'>Any Token");

  userSearch('.team_members');

  addGrantLogo();

  $('.js-select2, #frequency_unit').each(function() {
    $(this).select2();
  });

  $('#create-grant').validate({
    submitHandler: function(form) {
      let data = {};

      $(form).find(':input:disabled').removeAttr('disabled');

      $.each($(form).serializeArray(), function() {
        data[this.name] = this.value;
      });


      $('#token_symbol').val($('#js-token option:selected').text());
      $('#token_address').val($('#js-token option:selected').val());

      if (document.web3network) {
        $('#network').val(document.web3network);
      }

      // Begin New Deploy Subscription Contract
      let SubscriptionContract = new web3.eth.Contract(compiledSubscription.abi);

      // These args are baseline requirements for the contract set by the sender. Will set most to zero to abstract complexity from user.
      let args = [
        // admin_address
        web3.utils.toChecksumAddress(data.admin_address),
        // required token
        web3.utils.toChecksumAddress(data.denomination),
        // required tokenAmount
        web3.utils.toTwosComplement(0),
        // data.frequency
        web3.utils.toTwosComplement(0),
        // data.gas_price
        web3.utils.toTwosComplement(0),
        // contract version
        web3.utils.toTwosComplement(0)
      ];

      web3.eth.getAccounts(function(err, accounts) {
        web3.eth.net.getId(function(err, network) {
          SubscriptionContract.deploy({
            data: compiledSubscription.bytecode,
            arguments: args
          }).send({
            from: accounts[0],
            gas: 3000000,
            gasPrice: web3.utils.toHex($('#gasPrice').val() * Math.pow(10, 9))
          }).on('error', function(error) {
            console.log('1', error);
          }).on('transactionHash', function(transactionHash) {
            console.log('2', transactionHash);
            $('#transaction_hash').val(transactionHash);
            const linkURL = etherscan_tx_url(transactionHash);

            let data = {
              'title': $('#input_title').val(),
              'description': $('#input-description').val(),
              'reference_url': $('#input-url').val(),
              'admin_address': $('#input-admin_address').val(),
              'contract_owner_address': $('#contract_owner_address').val(),
              'token_address': $('#token_address').val(),
              'token_symbol': $('#token_symbol').val(),
              'amount_goal': $('#amount_goal').val(),
              'contract_version': $('#contract_version').val(),
              'transaction_hash': $('#transaction_hash').val(),
              'network': $('#network').val(),
              'team_members': $('#input-team_members').val(),
              'csrfmiddlewaretoken': $("#create-grant input[name='csrfmiddlewaretoken']").val()
            };

            saveGrant({grantData: data});

            document.issueURL = linkURL;
            $('#transaction_url').attr('href', linkURL);
            enableWaitState('#new-grant');

            let checkedBlocks = [];
            let blockToCheck = null;

            const checkForContractCreation = transactionHash => {

              web3.eth.getTransactionReceipt(transactionHash, (error, receipt) => {
                if (receipt && receipt.contractAddress) {
                  processReceipt(receipt);
                } else if (blockToCheck === null) {
                  // start watching for re-issued transaction with same sender, TODO: nonce, contract hash, etc?
                  web3.eth.getBlockNumber((error, blockNumber) => {
                    blockToCheck = blockNumber;
                    setTimeout(() => {
                      checkForContractCreation(transactionHash);
                    }, 1000);
                  });
                } else if (blockToCheck in checkedBlocks) {
                  setTimeout(() => {
                    checkForContractCreation(transactionHash);
                  }, 1000);
                } else {
                  web3.eth.getBlock(blockToCheck, true, (error, block) => {
                    if (error) {
                      setTimeout(() => {
                        checkForContractCreation(transactionHash);
                      }, 1000);
                    } else if (block && block.transactions) {
                      checkedBlocks.push(blockToCheck);
                      blockToCheck = blockToCheck + 1;

                      let didFindTransaction = false;

                      for (let i = 0; i < block.transactions.length; i += 1) {
                        if (block.transactions[i].from == accounts[0]) {
                          didFindTransaction = true;
                          web3.eth.getTransactionReceipt(block.transactions[i].hash, (error, result) => {
                            if (result && result.contractAddress) {
                              processReceipt(result);
                              return;
                            }
                          });
                        }
                      }

                      if (!didFindTransaction) {
                        setTimeout(() => {
                          checkForContractCreation(transactionHash);
                        }, 1000);
                      }

                    } else {
                      setTimeout(() => {
                        checkForContractCreation(transactionHash);
                      }, 1000);
                    }
                  });
                }
              });
            };

            checkForContractCreation(transactionHash);

          });
        });
      });
    }
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
    $("#js-token option[value='0x0000000000000000000000000000000000000000']").remove();
    $('#js-token').append("<option value='0x0000000000000000000000000000000000000000' selected='selected'>Any Token");
  });

  $('.select2-selection__rendered').removeAttr('title');
};
