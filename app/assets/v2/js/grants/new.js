/* eslint-disable no-console */

let description = new Quill('#input-description', {
  theme: 'snow'
});

$(document).ready(function() {
  if (web3 && web3.eth) {
    web3.eth.net.isListening((error, connectionStatus) => {
      if (connectionStatus)
        init();
      document.init = true;
    });
  }
  // fix for triage bug https://gitcoincore.slack.com/archives/CAXQ7PT60/p1551220641086800
  setTimeout(function() {
    if (!document.init) {
      show_error_banner();
    }
  }, 1000);
});

function saveGrant(grantData, isFinal) {
  let csrftoken = $("#create-grant input[name='csrfmiddlewaretoken']").val();

  $.ajax({
    type: 'post',
    url: '',
    processData: false,
    contentType: false,
    data: grantData,
    headers: {'X-CSRFToken': csrftoken},
    success: json => {
      if (isFinal) {
        if (json.url) {
          document.suppress_loading_leave_code = true;
          window.location = json.url;
        } else {
          console.error('Grant failed to save');
        }
      }
    },
    error: () => {
      console.error('Grant failed to save');
      _alert({ message: gettext('Your grant failed to save. Please try again.') }, 'error');
    }
  });
}

const processReceipt = receipt => {
  let formData = new FormData();

  formData.append('contract_address', receipt.contractAddress);
  formData.append('transaction_hash', $('#transaction_hash').val());

  saveGrant(formData, true);
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

  userSearch('.team_members', false, undefined, false, false, true);

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

      console.log(compiledSubscription.abi);

      // These args are baseline requirements for the contract set by the sender. Will set most to zero to abstract complexity from user.
      let args;

      if ($('#contract_version').val() == 1) {
        args = [
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
          web3.utils.toTwosComplement(1),
          // trusted relayer
          web3.utils.toChecksumAddress(data.trusted_relayer)
        ];
      } else if ($('#contract_version').val() == 0) {
        args = [
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
      }

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
            const linkURL = get_etherscan_url(transactionHash);
            let file = $('#img-project')[0].files[0];
            let formData = new FormData();

            formData.append('input_image', file);
            formData.append('transaction_hash', $('#transaction_hash').val());
            formData.append('title', $('#input_title').val());
            formData.append('description', description.getText());
            formData.append('description_rich', JSON.stringify(description.getContents()));
            formData.append('reference_url', $('#input-url').val());
            formData.append('admin_address', $('#input-admin_address').val());
            formData.append('contract_owner_address', $('#contract_owner_address').val());
            formData.append('token_address', $('#token_address').val());
            formData.append('token_symbol', $('#token_symbol').val());
            formData.append('amount_goal', $('#amount_goal').val());
            formData.append('contract_version', $('#contract_version').val());
            formData.append('transaction_hash', $('#transaction_hash').val());
            formData.append('network', $('#network').val());
            formData.append('team_members', $('#input-team_members').val());
            saveGrant(formData, false);

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
