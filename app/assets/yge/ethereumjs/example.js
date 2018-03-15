            // Make alias of document.getElementById -> $
            function makeAlias(object, name) {
                var fn = object ? object[name] : null;
                if (typeof fn == 'undefined') return function () {}
                return function () {
                    return fn.apply(object, arguments)
                }
            }

            // Make document.getElementById aliased by $
            $ = makeAlias(document, 'getElementById');

            // Create Accounts Object
            var Accounts = new Accounts();

            // Set web3 provider
            var provider = new HookedWeb3Provider({
              host: "http://localhost:8545",
              transaction_signer: Accounts
            });
            web3.setProvider(provider);

            // Extend the web3 object
            Accounts.log = function(msg){console.log(msg);};

            // When the window DOM loads
            window.onload = function () {
                // Send ether to the account you want to use (for testing)
                //web3.eth.sendTransaction({from: web3.eth.accounts[0], to: '0x6f801e7bfea263fa60a1ed1afcffd124f749ee79', value: web3.toWei(30, 'ether')}, function(err, result){console.log(err, result);});

                // When 'Generate Account' is clicked
                $("new").onclick = function() {
                    console.log($("new_passphrase").value);

                    var newAccount = document.Accounts.new($("new_passphrase").value);
                    $("new_result").innerHTML = JSON.stringify(newAccount, null, 2);
                };

                // When 'Get Accounts' is clicked
                $("get").onclick = function() {
                    $("get_result").innerHTML = JSON.stringify(
                        Accounts.get(
                        $("get_address").value
                        , $("get_passphrase").value
                    ), null, 2);
                };

                // When 'Get Selected' is clicked
                $("selected").onclick = function() {
                    $("get_result").innerHTML = JSON.stringify(
                        Accounts.get(
                        'selected'
                        , $("get_passphrase").value
                    ), null, 2);
                };

                // When 'Clear' is clicked
                $("clear").onclick = function() {
                    Accounts.clear();
                    $("clear_result").innerHTML = 'Accounts cleared!';
                };

                // When 'Clear' is clicked
                $("backup").onclick = function() {
                    Accounts.backup();
                    $("backup_result").innerHTML = 'Backup created!';
                };

                // When 'Import Accounts' is clicked
                $("import").onclick = function() {
                    Accounts.import($('importInput').value);
                    $("import_result").innerHTML = 'Imported accounts.';
                };

                // When 'Clear' is clicked
                $("export").onclick = function() {
                    $('importInput').value = Accounts.export();
                    $("import_result").innerHTML = 'Exported accounts!';
                };

                $('web3Accounts')
                    .innerHTML = JSON.stringify(web3.eth.accounts);

                var source = "" +
                    "contract test {\n" +
                    "   function multiply(uint a) constant returns(uint d) {\n" +
                    "       return a * 7;\n" +
                    "   }\n" +
                    "}\n",
                    code = '6060604052602a8060116000396000f300606060405260e060020a6000350463c6888fa18114601a575b005b6007600435026060908152602090f3',
                    abi = [
                      {
                        "constant": true,
                        "inputs": [
                          {
                            "name": "a",
                            "type": "uint256"
                          }
                        ],
                        "name": "multiply",
                        "outputs": [
                          {
                            "name": "d",
                            "type": "uint256"
                          }
                        ],
                        "type": "function"
                      }
                    ],
                    myContract;

                function createExampleContract() {
                    // hide create button
                    document.getElementById('multiplyResult').innerText = code;
                    // let's assume that coinbase is our account
                    web3.eth.defaultAccount = web3.eth.coinbase;
                    // create contract
                    document.getElementById('multiplyResult').innerText = "transaction sent, waiting for confirmation";
                    web3.eth.contract(abi).new({from: $('multiply_fromAddress').value, data: code, gas: 300000}, function (err, contract) {
                        console.log(err, contract);

                        if(err) {
                            document.getElementById('multiplyResult').innerText = 'There was an error deploying Multply contract: ' + String(err);
                            return;
                        // callback fires twice, we only want the second call when the contract is deployed
                        } else if(contract.address){
                            myContract = contract;
                            document.getElementById('multiplyResult').innerText = 'Multiply contract deployed to address: ' + myContract.address;
                        }
                    });
                };

                function callExampleContract() {
                    // this should be generated by ethereum
                    var param = parseInt(document.getElementById('multiplyValue').value);
                    // call the contract
                    var res = myContract.multiply(param);
                    document.getElementById('multiplyResult').innerText = res.toString(10);
                };

                $('deploy').onclick = function() {
                    // solidity code code
                    createExampleContract();
                };

                $('multiply').onclick = function() {
                    // solidity code code
                    callExampleContract();
                };

                // When 'Send Transaciton' is clicked
                $("send").onclick = function() {
                    $("web3_result").innerHTML = 'Processing transaction...';

                    web3.eth.getBalance(
                        '0x16269a6af79fe24b595e458586ba1f54c24d3c80'
                    , function(err, result){
                        if(!err)
                            $("web3_result").innerHTML = 'Account has a balance of ' + String(web3.fromWei(result, 'ether')) + ' ether...';
                    });

                    web3.eth.sendTransaction({
                        from: $("web3_fromAddress").value
                        , to: $("web3_toAddress").value
                        , value: web3.toWei($("web3_value").value, 'ether')
                        , gas: 300000
                    }, function(err, result){
                        var html = '';

                        if(err)
                            html = 'There was an error with the transaciton: ' + String(err);
                        else
                            html = 'The transaction went through succesfully, hash: ' + String(result);

                        $("web3_result").innerHTML = html;
                    });
                };
            };