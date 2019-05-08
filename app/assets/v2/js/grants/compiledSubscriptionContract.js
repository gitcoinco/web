let compiledSubscription0 = {
  "contractName": "Subscription",
  "abi": [
    {
      "constant": true,
      "inputs": [],
      "name": "requiredGasPrice",
      "outputs": [
        {
          "name": "",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [],
      "name": "requiredTokenAmount",
      "outputs": [
        {
          "name": "",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [],
      "name": "requiredToAddress",
      "outputs": [
        {
          "name": "",
          "type": "address"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [],
      "name": "requiredPeriodSeconds",
      "outputs": [
        {
          "name": "",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [],
      "name": "requiredTokenAddress",
      "outputs": [
        {
          "name": "",
          "type": "address"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [],
      "name": "relayer",
      "outputs": [
        {
          "name": "",
          "type": "address"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [],
      "name": "author",
      "outputs": [
        {
          "name": "",
          "type": "address"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {
          "name": "",
          "type": "bytes32"
        }
      ],
      "name": "nextValidTimestamp",
      "outputs": [
        {
          "name": "",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [
        {
          "name": "_toAddress",
          "type": "address"
        },
        {
          "name": "_tokenAddress",
          "type": "address"
        },
        {
          "name": "_tokenAmount",
          "type": "uint256"
        },
        {
          "name": "_periodSeconds",
          "type": "uint256"
        },
        {
          "name": "_gasPrice",
          "type": "uint256"
        },
        {
          "name": "_relayer",
          "type": "address"
        }
      ],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "anonymous": false,
      "inputs": [
        {
          "indexed": true,
          "name": "from",
          "type": "address"
        },
        {
          "indexed": true,
          "name": "to",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "tokenAddress",
          "type": "address"
        },
        {
          "indexed": false,
          "name": "tokenAmount",
          "type": "uint256"
        },
        {
          "indexed": false,
          "name": "periodSeconds",
          "type": "uint256"
        },
        {
          "indexed": false,
          "name": "gasPrice",
          "type": "uint256"
        }
      ],
      "name": "ExecuteSubscription",
      "type": "event"
    },
    {
      "constant": true,
      "inputs": [
        {
          "name": "subscriptionHash",
          "type": "bytes32"
        },
        {
          "name": "gracePeriodSeconds",
          "type": "uint256"
        }
      ],
      "name": "isSubscriptionActive",
      "outputs": [
        {
          "name": "",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {
          "name": "from",
          "type": "address"
        },
        {
          "name": "to",
          "type": "address"
        },
        {
          "name": "tokenAddress",
          "type": "address"
        },
        {
          "name": "tokenAmount",
          "type": "uint256"
        },
        {
          "name": "periodSeconds",
          "type": "uint256"
        },
        {
          "name": "gasPrice",
          "type": "uint256"
        }
      ],
      "name": "getSubscriptionHash",
      "outputs": [
        {
          "name": "",
          "type": "bytes32"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {
          "name": "subscriptionHash",
          "type": "bytes32"
        },
        {
          "name": "signature",
          "type": "bytes"
        }
      ],
      "name": "getSubscriptionSigner",
      "outputs": [
        {
          "name": "",
          "type": "address"
        }
      ],
      "payable": false,
      "stateMutability": "pure",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {
          "name": "from",
          "type": "address"
        },
        {
          "name": "to",
          "type": "address"
        },
        {
          "name": "tokenAddress",
          "type": "address"
        },
        {
          "name": "tokenAmount",
          "type": "uint256"
        },
        {
          "name": "periodSeconds",
          "type": "uint256"
        },
        {
          "name": "gasPrice",
          "type": "uint256"
        },
        {
          "name": "signature",
          "type": "bytes"
        }
      ],
      "name": "isSubscriptionReady",
      "outputs": [
        {
          "name": "",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "from",
          "type": "address"
        },
        {
          "name": "to",
          "type": "address"
        },
        {
          "name": "tokenAddress",
          "type": "address"
        },
        {
          "name": "tokenAmount",
          "type": "uint256"
        },
        {
          "name": "periodSeconds",
          "type": "uint256"
        },
        {
          "name": "gasPrice",
          "type": "uint256"
        },
        {
          "name": "signature",
          "type": "bytes"
        }
      ],
      "name": "cancelSubscription",
      "outputs": [
        {
          "name": "success",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "from",
          "type": "address"
        },
        {
          "name": "to",
          "type": "address"
        },
        {
          "name": "tokenAddress",
          "type": "address"
        },
        {
          "name": "tokenAmount",
          "type": "uint256"
        },
        {
          "name": "periodSeconds",
          "type": "uint256"
        },
        {
          "name": "gasPrice",
          "type": "uint256"
        },
        {
          "name": "signature",
          "type": "bytes"
        }
      ],
      "name": "executeSubscription",
      "outputs": [
        {
          "name": "success",
          "type": "bool"
        }
      ],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ],
  "metadata": "{\"compiler\":{\"version\":\"0.5.2+commit.1df8f40c\"},\"language\":\"Solidity\",\"output\":{\"abi\":[{\"constant\":true,\"inputs\":[{\"name\":\"from\",\"type\":\"address\"},{\"name\":\"to\",\"type\":\"address\"},{\"name\":\"tokenAddress\",\"type\":\"address\"},{\"name\":\"tokenAmount\",\"type\":\"uint256\"},{\"name\":\"periodSeconds\",\"type\":\"uint256\"},{\"name\":\"gasPrice\",\"type\":\"uint256\"},{\"name\":\"signature\",\"type\":\"bytes\"}],\"name\":\"isSubscriptionReady\",\"outputs\":[{\"name\":\"\",\"type\":\"bool\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[],\"name\":\"requiredGasPrice\",\"outputs\":[{\"name\":\"\",\"type\":\"uint256\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[{\"name\":\"subscriptionHash\",\"type\":\"bytes32\"},{\"name\":\"signature\",\"type\":\"bytes\"}],\"name\":\"getSubscriptionSigner\",\"outputs\":[{\"name\":\"\",\"type\":\"address\"}],\"payable\":false,\"stateMutability\":\"pure\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[],\"name\":\"requiredTokenAmount\",\"outputs\":[{\"name\":\"\",\"type\":\"uint256\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[],\"name\":\"requiredToAddress\",\"outputs\":[{\"name\":\"\",\"type\":\"address\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[{\"name\":\"from\",\"type\":\"address\"},{\"name\":\"to\",\"type\":\"address\"},{\"name\":\"tokenAddress\",\"type\":\"address\"},{\"name\":\"tokenAmount\",\"type\":\"uint256\"},{\"name\":\"periodSeconds\",\"type\":\"uint256\"},{\"name\":\"gasPrice\",\"type\":\"uint256\"},{\"name\":\"signature\",\"type\":\"bytes\"}],\"name\":\"executeSubscription\",\"outputs\":[{\"name\":\"success\",\"type\":\"bool\"}],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[],\"name\":\"requiredPeriodSeconds\",\"outputs\":[{\"name\":\"\",\"type\":\"uint256\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[],\"name\":\"requiredTokenAddress\",\"outputs\":[{\"name\":\"\",\"type\":\"address\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[],\"name\":\"relayer\",\"outputs\":[{\"name\":\"\",\"type\":\"address\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[],\"name\":\"author\",\"outputs\":[{\"name\":\"\",\"type\":\"address\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[{\"name\":\"subscriptionHash\",\"type\":\"bytes32\"},{\"name\":\"gracePeriodSeconds\",\"type\":\"uint256\"}],\"name\":\"isSubscriptionActive\",\"outputs\":[{\"name\":\"\",\"type\":\"bool\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[{\"name\":\"from\",\"type\":\"address\"},{\"name\":\"to\",\"type\":\"address\"},{\"name\":\"tokenAddress\",\"type\":\"address\"},{\"name\":\"tokenAmount\",\"type\":\"uint256\"},{\"name\":\"periodSeconds\",\"type\":\"uint256\"},{\"name\":\"gasPrice\",\"type\":\"uint256\"}],\"name\":\"getSubscriptionHash\",\"outputs\":[{\"name\":\"\",\"type\":\"bytes32\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"constant\":false,\"inputs\":[{\"name\":\"from\",\"type\":\"address\"},{\"name\":\"to\",\"type\":\"address\"},{\"name\":\"tokenAddress\",\"type\":\"address\"},{\"name\":\"tokenAmount\",\"type\":\"uint256\"},{\"name\":\"periodSeconds\",\"type\":\"uint256\"},{\"name\":\"gasPrice\",\"type\":\"uint256\"},{\"name\":\"signature\",\"type\":\"bytes\"}],\"name\":\"cancelSubscription\",\"outputs\":[{\"name\":\"success\",\"type\":\"bool\"}],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"function\"},{\"constant\":true,\"inputs\":[{\"name\":\"\",\"type\":\"bytes32\"}],\"name\":\"nextValidTimestamp\",\"outputs\":[{\"name\":\"\",\"type\":\"uint256\"}],\"payable\":false,\"stateMutability\":\"view\",\"type\":\"function\"},{\"inputs\":[{\"name\":\"_toAddress\",\"type\":\"address\"},{\"name\":\"_tokenAddress\",\"type\":\"address\"},{\"name\":\"_tokenAmount\",\"type\":\"uint256\"},{\"name\":\"_periodSeconds\",\"type\":\"uint256\"},{\"name\":\"_gasPrice\",\"type\":\"uint256\"},{\"name\":\"_relayer\",\"type\":\"address\"}],\"payable\":false,\"stateMutability\":\"nonpayable\",\"type\":\"constructor\"},{\"anonymous\":false,\"inputs\":[{\"indexed\":true,\"name\":\"from\",\"type\":\"address\"},{\"indexed\":true,\"name\":\"to\",\"type\":\"address\"},{\"indexed\":false,\"name\":\"tokenAddress\",\"type\":\"address\"},{\"indexed\":false,\"name\":\"tokenAmount\",\"type\":\"uint256\"},{\"indexed\":false,\"name\":\"periodSeconds\",\"type\":\"uint256\"},{\"indexed\":false,\"name\":\"gasPrice\",\"type\":\"uint256\"}],\"name\":\"ExecuteSubscription\",\"type\":\"event\"}],\"devdoc\":{\"methods\":{}},\"userdoc\":{\"methods\":{}}},\"settings\":{\"compilationTarget\":{\"/Users/danlipert/gitcoin/grants1337/contracts/Subscription.sol\":\"Subscription\"},\"evmVersion\":\"byzantium\",\"libraries\":{},\"optimizer\":{\"enabled\":false,\"runs\":200},\"remappings\":[]},\"sources\":{\"/Users/danlipert/gitcoin/grants1337/contracts/Subscription.sol\":{\"keccak256\":\"0xb5423c9168e3f68928731da51f18ef5709dc32ec31f6a55113b9a6b167cc1b62\",\"urls\":[\"bzzr://3d437a8d88dd529450a4c463b5cd18b85c0313bb2b904d8d21375867819414c1\"]},\"openzeppelin-solidity/contracts/cryptography/ECDSA.sol\":{\"keccak256\":\"0x0cbeb7f69b70ff62eb5536caebbc8701b6490ae7ee2e252d77891cf6eba11326\",\"urls\":[\"bzzr://58a443499466ee0706d22af81b43ab6779b519255fbc66276546386ec00a30d7\"]},\"openzeppelin-solidity/contracts/math/SafeMath.sol\":{\"keccak256\":\"0xc2a200a877c4a9b2475c246c54ffecc69ffde3e11af83319c63c2dc5458bac80\",\"urls\":[\"bzzr://c8876e2c39b60f155d748d71d715c8f3903fae5a405ac599adcb6ad2f9a583f9\"]},\"openzeppelin-solidity/contracts/token/ERC20/ERC20.sol\":{\"keccak256\":\"0x3dceb7e4aa237a56111c13f77d7efadeceda7271d62bfac94ac79afab7c1f411\",\"urls\":[\"bzzr://2f34152a5bec385352002c31bc89f5e9935f628f1923ccea45c2281e0084a4db\"]},\"openzeppelin-solidity/contracts/token/ERC20/IERC20.sol\":{\"keccak256\":\"0x59e7df16169a498cb8837963b2f5461d88e63bd1eb6c7d58b814d76b84ccbe61\",\"urls\":[\"bzzr://e572c9c4e02e37349702451bf3b5dcbbc86a19da5a51695b5b3e1bfe1e7825dc\"]}},\"version\":1}",
  "bytecode": "0x608060405234801561001057600080fd5b5060405160c080611cfa833981018060405260c081101561003057600080fd5b8101908080519060200190929190805190602001909291908051906020019092919080519060200190929190805190602001909291908051906020019092919050505085600260006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555084600360006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550836004819055508260058190555081600681905550336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555080600160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff160217905550505050505050611b5a806101a06000396000f3fe608060405234801561001057600080fd5b5060043610610107576000357c0100000000000000000000000000000000000000000000000000000000900480636f264b2e116100a9578063ae702ba411610083578063ae702ba414610635578063b01b3e2814610685578063b57b0c7f1461073b578063ff59bff81461088c57610107565b80636f264b2e146105575780638406c079146105a1578063a6c3e6b9146105eb57610107565b806329d428ca116100e557806329d428ca14610380578063384c33351461039e578063691d9352146103e85780636b40bba11461053957610107565b80630ad8ad661461010c57806310d920601461025d57806318f321a31461027b575b600080fd5b610243600480360360e081101561012257600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291908035906020019092919080359060200190929190803590602001906401000000008111156101bd57600080fd5b8201836020820111156101cf57600080fd5b803590602001918460018302840111640100000000831117156101f157600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f8201169050808301925050505050505091929192905050506108ce565b604051808215151515815260200191505060405180910390f35b610265610ba6565b6040518082815260200191505060405180910390f35b61033e6004803603604081101561029157600080fd5b8101908080359060200190929190803590602001906401000000008111156102b857600080fd5b8201836020820111156102ca57600080fd5b803590602001918460018302840111640100000000831117156102ec57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610bac565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b610388610bd1565b6040518082815260200191505060405180910390f35b6103a6610bd7565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b61051f600480360360e08110156103fe57600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff1690602001909291908035906020019092919080359060200190929190803590602001909291908035906020019064010000000081111561049957600080fd5b8201836020820111156104ab57600080fd5b803590602001918460018302840111640100000000831117156104cd57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610bfd565b604051808215151515815260200191505060405180910390f35b61054161156c565b6040518082815260200191505060405180910390f35b61055f611572565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b6105a9611598565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b6105f36115be565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b61066b6004803603604081101561064b57600080fd5b8101908080359060200190929190803590602001909291905050506115e3565b604051808215151515815260200191505060405180910390f35b610725600480360360c081101561069b57600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291908035906020019092919080359060200190929190505050611616565b6040518082815260200191505060405180910390f35b610872600480360360e081101561075157600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291908035906020019092919080359060200190929190803590602001906401000000008111156107ec57600080fd5b8201836020820111156107fe57600080fd5b8035906020019184600183028401116401000000008311171561082057600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050611845565b604051808215151515815260200191505060405180910390f35b6108b8600480360360208110156108a257600080fd5b8101908080359060200190929190505050611946565b6040518082815260200191505060405180910390f35b6000806108df898989898989611616565b905060006108ed8285610bac565b905060008873ffffffffffffffffffffffffffffffffffffffff1663dd62ed3e8c306040518363ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019250505060206040518083038186803b1580156109be57600080fd5b505afa1580156109d2573d6000803e3d6000fd5b505050506040513d60208110156109e857600080fd5b8101908080519060200190929190505050905060008973ffffffffffffffffffffffffffffffffffffffff166370a082318d6040518263ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060206040518083038186803b158015610a9657600080fd5b505afa158015610aaa573d6000803e3d6000fd5b505050506040513d6020811015610ac057600080fd5b810190808051906020019092919050505090508b73ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff16148015610b3a57508a73ffffffffffffffffffffffffffffffffffffffff168c73ffffffffffffffffffffffffffffffffffffffff1614155b8015610b59575060076000858152602001908152602001600020544210155b8015610b775750610b73878a61195e90919063ffffffff16565b8210155b8015610b955750610b91878a61195e90919063ffffffff16565b8110155b945050505050979650505050505050565b60065481565b6000610bc982610bbb8561197f565b6119d790919063ffffffff16565b905092915050565b60045481565b600260009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6000600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff16141515610c5b57600080fd5b6000610c6b898989898989611616565b90506000610c798285610bac565b90508973ffffffffffffffffffffffffffffffffffffffff168173ffffffffffffffffffffffffffffffffffffffff16141515610d1e576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260118152602001807f496e76616c6964205369676e617475726500000000000000000000000000000081525060200191505060405180910390fd5b60076000838152602001908152602001600020544210151515610da9576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260198152602001807f537562736372697074696f6e206973206e6f742072656164790000000000000081525060200191505060405180910390fd5b600073ffffffffffffffffffffffffffffffffffffffff16600260009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff161480610e535750600260009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168973ffffffffffffffffffffffffffffffffffffffff16145b1515610e5e57600080fd5b600073ffffffffffffffffffffffffffffffffffffffff16600360009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff161480610f085750600360009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168873ffffffffffffffffffffffffffffffffffffffff16145b1515610f1357600080fd5b60006004541480610f25575060045487145b1515610f3057600080fd5b60006005541480610f42575060055486145b1515610f4d57600080fd5b60006006541480610f5f575060065485145b1515610f6a57600080fd5b610f7d864261195e90919063ffffffff16565b600760008481526020019081526020016000208190555060008873ffffffffffffffffffffffffffffffffffffffff166370a082318b6040518263ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060206040518083038186803b15801561102f57600080fd5b505afa158015611043573d6000803e3d6000fd5b505050506040513d602081101561105957600080fd5b810190808051906020019092919050505090508873ffffffffffffffffffffffffffffffffffffffff166323b872dd8c8c8b6040518463ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018281526020019350505050602060405180830381600087803b15801561114357600080fd5b505af1158015611157573d6000803e3d6000fd5b505050506040513d602081101561116d57600080fd5b810190808051906020019092919050505015156111f2576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252600f8152602001807f5472616e73666572204661696c6564000000000000000000000000000000000081525060200191505060405180910390fd5b8873ffffffffffffffffffffffffffffffffffffffff166370a082318b6040518263ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060206040518083038186803b15801561128b57600080fd5b505afa15801561129f573d6000803e3d6000fd5b505050506040513d60208110156112b557600080fd5b810190808051906020019092919050505088820114151561133e576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252601c8152602001807f437261707079204552433230206973206120626164206b697474792e0000000081525060200191505060405180910390fd5b8973ffffffffffffffffffffffffffffffffffffffff168b73ffffffffffffffffffffffffffffffffffffffff167fc51b043bf6e44ae9d9e0df67b8ad10c8b5d93be940b9475f4af44e866b2f08f68b8b8b8b604051808573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200184815260200183815260200182815260200194505050505060405180910390a3600086111561155a578873ffffffffffffffffffffffffffffffffffffffff166323b872dd8c33896040518463ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018281526020019350505050602060405180830381600087803b1580156114c757600080fd5b505af11580156114db573d6000803e3d6000fd5b505050506040513d60208110156114f157600080fd5b81019080805190602001909291905050501515611559576040517f08c379a0000000000000000000000000000000000000000000000000000000008152600401808060200182810382526021815260200180611adf6021913960400191505060405180910390fd5b5b60019350505050979650505050505050565b60055481565b600360009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b600061160b82600760008681526020019081526020016000205461195e90919063ffffffff16565b421115905092915050565b600060197f01000000000000000000000000000000000000000000000000000000000000000260007f01000000000000000000000000000000000000000000000000000000000000000230898989898989604051602001808a7effffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff19167effffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff19168152600101897effffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff19167effffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff191681526001018873ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166c010000000000000000000000000281526014018773ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166c010000000000000000000000000281526014018673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166c010000000000000000000000000281526014018573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166c0100000000000000000000000002815260140184815260200183815260200182815260200199505050505050505050506040516020818303038152906040528051906020012090509695505050505050565b600080611856898989898989611616565b90506000611875846118678461197f565b6119d790919063ffffffff16565b90508973ffffffffffffffffffffffffffffffffffffffff168173ffffffffffffffffffffffffffffffffffffffff161415156118fd576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252602f815260200180611b00602f913960400191505060405180910390fd5b7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff6007600084815260200190815260200160002081905550600192505050979650505050505050565b60076020528060005260406000206000915090505481565b600080828401905083811015151561197557600080fd5b8091505092915050565b60008160405160200180807f19457468657265756d205369676e6564204d6573736167653a0a333200000000815250601c01828152602001915050604051602081830303815290604052805190602001209050919050565b6000604182511415156119ed5760009050611ad8565b60008060006020850151925060408501519150606085015160001a90507f7fffffffffffffffffffffffffffffff5d576e7357a4501ddfe92f46681b20a082600190041115611a425760009350505050611ad8565b601b8160ff1614158015611a5a5750601c8160ff1614155b15611a6b5760009350505050611ad8565b60018682858560405160008152602001604052604051808581526020018460ff1660ff1681526020018381526020018281526020019450505050506020604051602081039080840390855afa158015611ac8573d6000803e3d6000fd5b5050506020604051035193505050505b9291505056fe4661696c656420746f20706179206761732061732066726f6d206163636f756e74496e76616c6964205369676e617475726520666f7220737562736372697074696f6e2063616e63656c6c6174696f6ea165627a7a72305820f309d7c02f7208d95d899283d647babd2c9662b760b9583bedd2e974f6042c860029",
  "deployedBytecode": "0x608060405234801561001057600080fd5b5060043610610107576000357c0100000000000000000000000000000000000000000000000000000000900480636f264b2e116100a9578063ae702ba411610083578063ae702ba414610635578063b01b3e2814610685578063b57b0c7f1461073b578063ff59bff81461088c57610107565b80636f264b2e146105575780638406c079146105a1578063a6c3e6b9146105eb57610107565b806329d428ca116100e557806329d428ca14610380578063384c33351461039e578063691d9352146103e85780636b40bba11461053957610107565b80630ad8ad661461010c57806310d920601461025d57806318f321a31461027b575b600080fd5b610243600480360360e081101561012257600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291908035906020019092919080359060200190929190803590602001906401000000008111156101bd57600080fd5b8201836020820111156101cf57600080fd5b803590602001918460018302840111640100000000831117156101f157600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f8201169050808301925050505050505091929192905050506108ce565b604051808215151515815260200191505060405180910390f35b610265610ba6565b6040518082815260200191505060405180910390f35b61033e6004803603604081101561029157600080fd5b8101908080359060200190929190803590602001906401000000008111156102b857600080fd5b8201836020820111156102ca57600080fd5b803590602001918460018302840111640100000000831117156102ec57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610bac565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b610388610bd1565b6040518082815260200191505060405180910390f35b6103a6610bd7565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b61051f600480360360e08110156103fe57600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff1690602001909291908035906020019092919080359060200190929190803590602001909291908035906020019064010000000081111561049957600080fd5b8201836020820111156104ab57600080fd5b803590602001918460018302840111640100000000831117156104cd57600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050610bfd565b604051808215151515815260200191505060405180910390f35b61054161156c565b6040518082815260200191505060405180910390f35b61055f611572565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b6105a9611598565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b6105f36115be565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b61066b6004803603604081101561064b57600080fd5b8101908080359060200190929190803590602001909291905050506115e3565b604051808215151515815260200191505060405180910390f35b610725600480360360c081101561069b57600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291908035906020019092919080359060200190929190505050611616565b6040518082815260200191505060405180910390f35b610872600480360360e081101561075157600080fd5b81019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291908035906020019092919080359060200190929190803590602001906401000000008111156107ec57600080fd5b8201836020820111156107fe57600080fd5b8035906020019184600183028401116401000000008311171561082057600080fd5b91908080601f016020809104026020016040519081016040528093929190818152602001838380828437600081840152601f19601f820116905080830192505050505050509192919290505050611845565b604051808215151515815260200191505060405180910390f35b6108b8600480360360208110156108a257600080fd5b8101908080359060200190929190505050611946565b6040518082815260200191505060405180910390f35b6000806108df898989898989611616565b905060006108ed8285610bac565b905060008873ffffffffffffffffffffffffffffffffffffffff1663dd62ed3e8c306040518363ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019250505060206040518083038186803b1580156109be57600080fd5b505afa1580156109d2573d6000803e3d6000fd5b505050506040513d60208110156109e857600080fd5b8101908080519060200190929190505050905060008973ffffffffffffffffffffffffffffffffffffffff166370a082318d6040518263ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060206040518083038186803b158015610a9657600080fd5b505afa158015610aaa573d6000803e3d6000fd5b505050506040513d6020811015610ac057600080fd5b810190808051906020019092919050505090508b73ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff16148015610b3a57508a73ffffffffffffffffffffffffffffffffffffffff168c73ffffffffffffffffffffffffffffffffffffffff1614155b8015610b59575060076000858152602001908152602001600020544210155b8015610b775750610b73878a61195e90919063ffffffff16565b8210155b8015610b955750610b91878a61195e90919063ffffffff16565b8110155b945050505050979650505050505050565b60065481565b6000610bc982610bbb8561197f565b6119d790919063ffffffff16565b905092915050565b60045481565b600260009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6000600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff16141515610c5b57600080fd5b6000610c6b898989898989611616565b90506000610c798285610bac565b90508973ffffffffffffffffffffffffffffffffffffffff168173ffffffffffffffffffffffffffffffffffffffff16141515610d1e576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260118152602001807f496e76616c6964205369676e617475726500000000000000000000000000000081525060200191505060405180910390fd5b60076000838152602001908152602001600020544210151515610da9576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004018080602001828103825260198152602001807f537562736372697074696f6e206973206e6f742072656164790000000000000081525060200191505060405180910390fd5b600073ffffffffffffffffffffffffffffffffffffffff16600260009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff161480610e535750600260009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168973ffffffffffffffffffffffffffffffffffffffff16145b1515610e5e57600080fd5b600073ffffffffffffffffffffffffffffffffffffffff16600360009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff161480610f085750600360009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168873ffffffffffffffffffffffffffffffffffffffff16145b1515610f1357600080fd5b60006004541480610f25575060045487145b1515610f3057600080fd5b60006005541480610f42575060055486145b1515610f4d57600080fd5b60006006541480610f5f575060065485145b1515610f6a57600080fd5b610f7d864261195e90919063ffffffff16565b600760008481526020019081526020016000208190555060008873ffffffffffffffffffffffffffffffffffffffff166370a082318b6040518263ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060206040518083038186803b15801561102f57600080fd5b505afa158015611043573d6000803e3d6000fd5b505050506040513d602081101561105957600080fd5b810190808051906020019092919050505090508873ffffffffffffffffffffffffffffffffffffffff166323b872dd8c8c8b6040518463ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018281526020019350505050602060405180830381600087803b15801561114357600080fd5b505af1158015611157573d6000803e3d6000fd5b505050506040513d602081101561116d57600080fd5b810190808051906020019092919050505015156111f2576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252600f8152602001807f5472616e73666572204661696c6564000000000000000000000000000000000081525060200191505060405180910390fd5b8873ffffffffffffffffffffffffffffffffffffffff166370a082318b6040518263ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060206040518083038186803b15801561128b57600080fd5b505afa15801561129f573d6000803e3d6000fd5b505050506040513d60208110156112b557600080fd5b810190808051906020019092919050505088820114151561133e576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252601c8152602001807f437261707079204552433230206973206120626164206b697474792e0000000081525060200191505060405180910390fd5b8973ffffffffffffffffffffffffffffffffffffffff168b73ffffffffffffffffffffffffffffffffffffffff167fc51b043bf6e44ae9d9e0df67b8ad10c8b5d93be940b9475f4af44e866b2f08f68b8b8b8b604051808573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200184815260200183815260200182815260200194505050505060405180910390a3600086111561155a578873ffffffffffffffffffffffffffffffffffffffff166323b872dd8c33896040518463ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018281526020019350505050602060405180830381600087803b1580156114c757600080fd5b505af11580156114db573d6000803e3d6000fd5b505050506040513d60208110156114f157600080fd5b81019080805190602001909291905050501515611559576040517f08c379a0000000000000000000000000000000000000000000000000000000008152600401808060200182810382526021815260200180611adf6021913960400191505060405180910390fd5b5b60019350505050979650505050505050565b60055481565b600360009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b600061160b82600760008681526020019081526020016000205461195e90919063ffffffff16565b421115905092915050565b600060197f01000000000000000000000000000000000000000000000000000000000000000260007f01000000000000000000000000000000000000000000000000000000000000000230898989898989604051602001808a7effffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff19167effffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff19168152600101897effffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff19167effffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff191681526001018873ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166c010000000000000000000000000281526014018773ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166c010000000000000000000000000281526014018673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166c010000000000000000000000000281526014018573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff166c0100000000000000000000000002815260140184815260200183815260200182815260200199505050505050505050506040516020818303038152906040528051906020012090509695505050505050565b600080611856898989898989611616565b90506000611875846118678461197f565b6119d790919063ffffffff16565b90508973ffffffffffffffffffffffffffffffffffffffff168173ffffffffffffffffffffffffffffffffffffffff161415156118fd576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040180806020018281038252602f815260200180611b00602f913960400191505060405180910390fd5b7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff6007600084815260200190815260200160002081905550600192505050979650505050505050565b60076020528060005260406000206000915090505481565b600080828401905083811015151561197557600080fd5b8091505092915050565b60008160405160200180807f19457468657265756d205369676e6564204d6573736167653a0a333200000000815250601c01828152602001915050604051602081830303815290604052805190602001209050919050565b6000604182511415156119ed5760009050611ad8565b60008060006020850151925060408501519150606085015160001a90507f7fffffffffffffffffffffffffffffff5d576e7357a4501ddfe92f46681b20a082600190041115611a425760009350505050611ad8565b601b8160ff1614158015611a5a5750601c8160ff1614155b15611a6b5760009350505050611ad8565b60018682858560405160008152602001604052604051808581526020018460ff1660ff1681526020018381526020018281526020019450505050506020604051602081039080840390855afa158015611ac8573d6000803e3d6000fd5b5050506020604051035193505050505b9291505056fe4661696c656420746f20706179206761732061732066726f6d206163636f756e74496e76616c6964205369676e617475726520666f7220737562736372697074696f6e2063616e63656c6c6174696f6ea165627a7a72305820f309d7c02f7208d95d899283d647babd2c9662b760b9583bedd2e974f6042c860029",
  "sourceMap": "1096:9826:1:-;;;1666:465;8:9:-1;5:2;;;30:1;27;20:12;5:2;1666:465:1;;;;;;;;;;;;;13:3:-1;8;5:12;2:2;;;30:1;27;20:12;2:2;1666:465:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;1893:10;1875:17;;:28;;;;;;;;;;;;;;;;;;1934:13;1913:20;;:34;;;;;;;;;;;;;;;;;;1977:12;1957:19;:32;;;;2021:14;1999:21;:36;;;;2062:9;2045:16;:26;;;;2088:10;2081:6;;:17;;;;;;;;;;;;;;;;;;2116:8;2108:7;;:16;;;;;;;;;;;;;;;;;;1666:465;;;;;;1096:9826;;;;;;",
  "deployedSourceMap": "1096:9826:1:-;;;;8:9:-1;5:2;;;30:1;27;20:12;5:2;1096:9826:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;4768:1171;;;;;;13:3:-1;8;5:12;2:2;;;30:1;27;20:12;2:2;4768:1171:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;21:11:-1;8;5:28;2:2;;;46:1;43;36:12;2:2;4768:1171:1;;35:9:-1;28:4;12:14;8:25;5:40;2:2;;;58:1;55;48:12;2:2;4768:1171:1;;;;;;100:9:-1;95:1;81:12;77:20;67:8;63:35;60:50;39:11;25:12;22:29;11:107;8:2;;;131:1;128;121:12;8:2;4768:1171:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;30:3:-1;22:6;14;1:33;99:1;93:3;85:6;81:16;74:27;137:4;133:9;126:4;121:3;117:14;113:30;106:37;;169:3;161:6;157:16;147:26;;4768:1171:1;;;;;;;;;;;;;;;:::i;:::-;;;;;;;;;;;;;;;;;;;;;;;1628:31;;;:::i;:::-;;;;;;;;;;;;;;;;;;;4327:318;;;;;;13:2:-1;8:3;5:11;2:2;;;29:1;26;19:12;2:2;4327:318:1;;;;;;;;;;;;;;;;;;;21:11:-1;8;5:28;2:2;;;46:1;43;36:12;2:2;4327:318:1;;35:9:-1;28:4;12:14;8:25;5:40;2:2;;;58:1;55;48:12;2:2;4327:318:1;;;;;;100:9:-1;95:1;81:12;77:20;67:8;63:35;60:50;39:11;25:12;22:29;11:107;8:2;;;131:1;128;121:12;8:2;4327:318:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;30:3:-1;22:6;14;1:33;99:1;93:3;85:6;81:16;74:27;137:4;133:9;126:4;121:3;117:14;113:30;106:37;;169:3;161:6;157:16;147:26;;4327:318:1;;;;;;;;;;;;;;;:::i;:::-;;;;;;;;;;;;;;;;;;;;;;;1546:34;;;:::i;:::-;;;;;;;;;;;;;;;;;;;1467:32;;;:::i;:::-;;;;;;;;;;;;;;;;;;;;;;;7456:3464;;;;;;13:3:-1;8;5:12;2:2;;;30:1;27;20:12;2:2;7456:3464:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;21:11:-1;8;5:28;2:2;;;46:1;43;36:12;2:2;7456:3464:1;;35:9:-1;28:4;12:14;8:25;5:40;2:2;;;58:1;55;48:12;2:2;7456:3464:1;;;;;;100:9:-1;95:1;81:12;77:20;67:8;63:35;60:50;39:11;25:12;22:29;11:107;8:2;;;131:1;128;121:12;8:2;7456:3464:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;30:3:-1;22:6;14;1:33;99:1;93:3;85:6;81:16;74:27;137:4;133:9;126:4;121:3;117:14;113:30;106:37;;169:3;161:6;157:16;147:26;;7456:3464:1;;;;;;;;;;;;;;;:::i;:::-;;;;;;;;;;;;;;;;;;;;;;;1586:36;;;:::i;:::-;;;;;;;;;;;;;;;;;;;1505:35;;;:::i;:::-;;;;;;;;;;;;;;;;;;;;;;;1285:22;;;:::i;:::-;;;;;;;;;;;;;;;;;;;;;;;1217:21;;;:::i;:::-;;;;;;;;;;;;;;;;;;;;;;;3035:293;;;;;;13:2:-1;8:3;5:11;2:2;;;29:1;26;19:12;2:2;3035:293:1;;;;;;;;;;;;;;;;;;;;;;;;;;:::i;:::-;;;;;;;;;;;;;;;;;;;;;;;3484:782;;;;;;13:3:-1;8;5:12;2:2;;;30:1;27;20:12;2:2;3484:782:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:::i;:::-;;;;;;;;;;;;;;;;;;;6193:1105;;;;;;13:3:-1;8;5:12;2:2;;;30:1;27;20:12;2:2;6193:1105:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;21:11:-1;8;5:28;2:2;;;46:1;43;36:12;2:2;6193:1105:1;;35:9:-1;28:4;12:14;8:25;5:40;2:2;;;58:1;55;48:12;2:2;6193:1105:1;;;;;;100:9:-1;95:1;81:12;77:20;67:8;63:35;60:50;39:11;25:12;22:29;11:107;8:2;;;131:1;128;121:12;8:2;6193:1105:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;30:3:-1;22:6;14;1:33;99:1;93:3;85:6;81:16;74:27;137:4;133:9;126:4;121:3;117:14;113:30;106:37;;169:3;161:6;157:16;147:26;;6193:1105:1;;;;;;;;;;;;;;;:::i;:::-;;;;;;;;;;;;;;;;;;;;;;;2741:53;;;;;;13:2:-1;8:3;5:11;2:2;;;29:1;26;19:12;2:2;2741:53:1;;;;;;;;;;;;;;;;;:::i;:::-;;;;;;;;;;;;;;;;;;;4768:1171;5304:4;5324:24;5351:103;5384:4;5390:2;5394:12;5408:11;5421:13;5436:8;5351:19;:103::i;:::-;5324:130;;5464:14;5481:50;5503:16;5521:9;5481:21;:50::i;:::-;5464:67;;5541:17;5567:12;5561:29;;;5591:4;5605;5561:50;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;8:9:-1;5:2;;;30:1;27;20:12;5:2;5561:50:1;;;;8:9:-1;5:2;;;45:16;42:1;39;24:38;77:16;74:1;67:27;5:2;5561:50:1;;;;;;;13:2:-1;8:3;5:11;2:2;;;29:1;26;19:12;2:2;5561:50:1;;;;;;;;;;;;;;;;5541:70;;5621:15;5645:12;5639:29;;;5669:4;5639:35;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;8:9:-1;5:2;;;30:1;27;20:12;5:2;5639:35:1;;;;8:9:-1;5:2;;;45:16;42:1;39;24:38;77:16;74:1;67:27;5:2;5639:35:1;;;;;;;13:2:-1;8:3;5:11;2:2;;;29:1;26;19:12;2:2;5639:35:1;;;;;;;;;;;;;;;;5621:53;;5715:4;5705:14;;:6;:14;;;:40;;;;;5743:2;5735:10;;:4;:10;;;;5705:40;:111;;;;;5780:18;:36;5799:16;5780:36;;;;;;;;;;;;5761:15;:55;;5705:111;:165;;;;;5845:25;5861:8;5845:11;:15;;:25;;;;:::i;:::-;5832:9;:38;;5705:165;:217;;;;;5897:25;5913:8;5897:11;:15;;:25;;;;:::i;:::-;5886:7;:36;;5705:217;5684:248;;;;;;4768:1171;;;;;;;;;:::o;1628:31::-;;;;:::o;4327:318::-;4548:7;4578:60;4628:9;4578:41;:16;:39;:41::i;:::-;:49;;:60;;;;:::i;:::-;4571:67;;4327:318;;;;:::o;1546:34::-;;;;:::o;1467:32::-;;;;;;;;;;;;;:::o;7456:3464::-;7978:12;8028:7;;;;;;;;;;;8014:21;;:10;:21;;;8006:30;;;;;;;;8196:24;8223:103;8256:4;8262:2;8266:12;8280:11;8293:13;8308:8;8223:19;:103::i;:::-;8196:130;;8336:14;8353:50;8375:16;8393:9;8353:21;:50::i;:::-;8336:67;;8470:4;8460:14;;:6;:14;;;8452:44;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;8607:18;:36;8626:16;8607:36;;;;;;;;;;;;8588:15;:55;;8567:127;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;8848:1;8819:31;;:17;;;;;;;;;;;:31;;;:58;;;;8860:17;;;;;;;;;;;8854:23;;:2;:23;;;8819:58;8810:69;;;;;;;;8930:1;8898:34;;:20;;;;;;;;;;;:34;;;:74;;;;8952:20;;;;;;;;;;;8936:36;;:12;:36;;;8898:74;8889:85;;;;;;;;9016:1;8993:19;;:24;:62;;;;9036:19;;9021:11;:34;8993:62;8984:73;;;;;;;;9101:1;9076:21;;:26;:68;;;;9123:21;;9106:13;:38;9076:68;9067:79;;;;;;;;9185:1;9165:16;;:21;:53;;;;9202:16;;9190:8;:28;9165:53;9156:64;;;;;;;;9349:34;9369:13;9349:15;:19;;:34;;;;:::i;:::-;9310:18;:36;9329:16;9310:36;;;;;;;;;;;:73;;;;9469:23;9501:12;9495:29;;;9525:2;9495:33;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;8:9:-1;5:2;;;30:1;27;20:12;5:2;9495:33:1;;;;8:9:-1;5:2;;;45:16;42:1;39;24:38;77:16;74:1;67:27;5:2;9495:33:1;;;;;;;13:2:-1;8:3;5:11;2:2;;;29:1;26;19:12;2:2;9495:33:1;;;;;;;;;;;;;;;;9469:59;;9563:12;9557:32;;;9590:4;9595:2;9598:11;9557:53;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;8:9:-1;5:2;;;30:1;27;20:12;5:2;9557:53:1;;;;8:9:-1;5:2;;;45:16;42:1;39;24:38;77:16;74:1;67:27;5:2;9557:53:1;;;;;;;13:2:-1;8:3;5:11;2:2;;;29:1;26;19:12;2:2;9557:53:1;;;;;;;;;;;;;;;;9538:111;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;9717:12;9711:29;;;9741:2;9711:33;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;8:9:-1;5:2;;;30:1;27;20:12;5:2;9711:33:1;;;;8:9:-1;5:2;;;45:16;42:1;39;24:38;77:16;74:1;67:27;5:2;9711:33:1;;;;;;;13:2:-1;8:3;5:11;2:2;;;29:1;26;19:12;2:2;9711:33:1;;;;;;;;;;;;;;;;9695:11;9679:15;:27;9678:66;9659:137;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;9851:2;9812:103;;9845:4;9812:103;;;9855:12;9869:11;9882:13;9897:8;9812:103;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;10146:1;10135:8;:12;10131:761;;;10760:12;10754:32;;;10787:4;10793:10;10805:8;10754:60;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;8:9:-1;5:2;;;30:1;27;20:12;5:2;10754:60:1;;;;8:9:-1;5:2;;;45:16;42:1;39;24:38;77:16;74:1;67:27;5:2;10754:60:1;;;;;;;13:2:-1;8:3;5:11;2:2;;;29:1;26;19:12;2:2;10754:60:1;;;;;;;;;;;;;;;;10729:152;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;10131:761;10909:4;10902:11;;;;;7456:3464;;;;;;;;;:::o;1586:36::-;;;;:::o;1505:35::-;;;;;;;;;;;;;:::o;1285:22::-;;;;;;;;;;;;;:::o;1217:21::-;;;;;;;;;;;;;:::o;3035:293::-;3188:4;3251:60;3292:18;3251;:36;3270:16;3251:36;;;;;;;;;;;;:40;;:60;;;;:::i;:::-;3216:15;:95;;3208:113;;3035:293;;;;:::o;3484:782::-;3937:7;4029:4;4024:10;;4057:1;4052:7;;4085:4;4108;4130:2;4150:12;4180:11;4209:13;4240:8;3990:268;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;49:4:-1;39:7;30;26:21;22:32;13:7;6:49;3990:268:1;;;3967:292;;;;;;3960:299;;3484:782;;;;;;;;:::o;6193:1105::-;6714:12;6742:24;6769:103;6802:4;6808:2;6812:12;6826:11;6839:13;6854:8;6769:19;:103::i;:::-;6742:130;;6882:14;6899:60;6949:9;6899:41;:16;:39;:41::i;:::-;:49;;:60;;;;:::i;:::-;6882:77;;7026:4;7016:14;;:6;:14;;;7008:74;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;7266:2;7221:18;:36;7240:16;7221:36;;;;;;;;;;;:48;;;;7287:4;7280:11;;;;6193:1105;;;;;;;;;:::o;2741:53::-;;;;;;;;;;;;;;;;;:::o;1439:145:3:-;1497:7;1516:9;1532:1;1528;:5;1516:17;;1556:1;1551;:6;;1543:15;;;;;;;;1576:1;1569:8;;;1439:145;;;;:::o;2650:265:2:-;2719:7;2902:4;2849:58;;;;;;;;;;;;;;;;;;;;;;49:4:-1;39:7;30;26:21;22:32;13:7;6:49;2849:58:2;;;2839:69;;;;;;2832:76;;2650:265;;;:::o;609:1891::-;687:7;768:2;748:9;:16;:22;;744:72;;;802:1;786:19;;;;744:72;882:9;901;920:7;1166:4;1155:9;1151:20;1145:27;1140:32;;1211:4;1200:9;1196:20;1190:27;1185:32;;1264:4;1253:9;1249:20;1243:27;1240:1;1235:36;1230:41;;2182:66;2177:1;2169:10;;;:79;2165:127;;;2279:1;2264:17;;;;;;;2165:127;2311:2;2306:1;:7;;;;:18;;;;;2322:2;2317:1;:7;;;;2306:18;2302:66;;;2355:1;2340:17;;;;;;;2302:66;2469:24;2479:4;2485:1;2488;2491;2469:24;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;8:9:-1;5:2;;;45:16;42:1;39;24:38;77:16;74:1;67:27;5:2;2469:24:2;;;;;;;;2462:31;;;;;609:1891;;;;;:::o",
  "source": "pragma solidity ^0.5.2;\n\n/*\n  Super Simple Token Subscriptions - https://tokensubscription.com\n\n  //// Breakin’ Through @ University of Wyoming ////\n\n  Austin Thomas Griffith - https://austingriffith.com\n\n  Building on previous works:\n    https://github.com/austintgriffith/token-subscription\n    https://gist.github.com/androolloyd/0a62ef48887be00a5eff5c17f2be849a\n    https://media.consensys.net/subscription-services-on-the-blockchain-erc-948-6ef64b083a36\n    https://medium.com/gitcoin/technical-deep-dive-architecture-choices-for-subscriptions-on-the-blockchain-erc948-5fae89cabc7a\n    https://github.com/ethereum/EIPs/pull/1337\n    https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1077.md\n    https://github.com/gnosis/safe-contracts\n\n  Earlier Meta Transaction Demo:\n    https://github.com/austintgriffith/bouncer-proxy\n\n  Huge thanks, as always, to OpenZeppelin for the rad contracts:\n */\n\nimport \"openzeppelin-solidity/contracts/cryptography/ECDSA.sol\";\nimport \"openzeppelin-solidity/contracts/math/SafeMath.sol\";\nimport \"openzeppelin-solidity/contracts/token/ERC20/ERC20.sol\";\n\n\ncontract Subscription {\n    using ECDSA for bytes32;\n    using SafeMath for uint256;\n\n    //who deploys the contract\n    address public author;\n\n    //restrict who can relay the metatx\n    address public relayer;\n\n    // the publisher may optionally deploy requirements for the subscription\n    // so only meta transactions that match the requirements can be relayed\n    address public requiredToAddress;\n    address public requiredTokenAddress;\n    uint256 public requiredTokenAmount;\n    uint256 public requiredPeriodSeconds;\n    uint256 public requiredGasPrice;\n\n    constructor(\n        address _toAddress,\n        address _tokenAddress,\n        uint256 _tokenAmount,\n        uint256 _periodSeconds,\n        uint256 _gasPrice,\n        address _relayer\n    ) public {\n        requiredToAddress=_toAddress;\n        requiredTokenAddress=_tokenAddress;\n        requiredTokenAmount=_tokenAmount;\n        requiredPeriodSeconds=_periodSeconds;\n        requiredGasPrice=_gasPrice;\n        author=msg.sender;\n        relayer=_relayer;\n    }\n\n    event ExecuteSubscription(\n        address indexed from, //the subscriber\n        address indexed to, //the publisher\n        address tokenAddress, //the token address paid to the publisher\n        uint256 tokenAmount, //the token amount paid to the publisher\n        uint256 periodSeconds, //the period in seconds between payments\n        uint256 gasPrice //the amount of tokens to pay relayer (0 for free)\n    );\n\n    // similar to a nonce that avoids replay attacks this allows a single execution\n    // every x seconds for a given subscription\n    // subscriptionHash  => next valid block number\n    mapping(bytes32 => uint256) public nextValidTimestamp;\n\n    // this is used by external smart contracts to verify on-chain that a\n    // particular subscription is \"paid\" and \"active\"\n    // there must be a small grace period added to allow the publisher\n    // or desktop miner to execute\n    function isSubscriptionActive(\n        bytes32 subscriptionHash,\n        uint256 gracePeriodSeconds\n    )\n        external\n        view\n        returns (bool)\n    {\n        return (block.timestamp <=\n                nextValidTimestamp[subscriptionHash].add(gracePeriodSeconds)\n        );\n    }\n\n    // given the subscription details, generate a hash and try to kind of follow\n    // the eip-191 standard and eip-1077 standard from my dude @avsa\n    function getSubscriptionHash(\n        address from, //the subscriber\n        address to, //the publisher\n        address tokenAddress, //the token address paid to the publisher\n        uint256 tokenAmount, //the token amount paid to the publisher\n        uint256 periodSeconds, //the period in seconds between payments\n        uint256 gasPrice //the amount of tokens or eth to pay relayer (0 for free)\n    )\n        public\n        view\n        returns (bytes32)\n    {\n        return keccak256(\n            abi.encodePacked(\n                byte(0x19),\n                byte(0),\n                address(this),\n                from,\n                to,\n                tokenAddress,\n                tokenAmount,\n                periodSeconds,\n                gasPrice\n        ));\n    }\n\n    //ecrecover the signer from hash and the signature\n    function getSubscriptionSigner(\n        bytes32 subscriptionHash, //hash of subscription\n        bytes memory signature //proof the subscriber signed the meta trasaction\n    )\n        public\n        pure\n        returns (address)\n    {\n        return subscriptionHash.toEthSignedMessageHash().recover(signature);\n    }\n\n    //check if a subscription is signed correctly and the timestamp is ready for\n    // the next execution to happen\n    function isSubscriptionReady(\n        address from, //the subscriber\n        address to, //the publisher\n        address tokenAddress, //the token address paid to the publisher\n        uint256 tokenAmount, //the token amount paid to the publisher\n        uint256 periodSeconds, //the period in seconds between payments\n        uint256 gasPrice, //the amount of the token to incentivize the relay network\n        bytes memory signature //proof the subscriber signed the meta trasaction\n    )\n        public\n        view\n        returns (bool)\n    {\n        bytes32 subscriptionHash = getSubscriptionHash(\n            from, to, tokenAddress, tokenAmount, periodSeconds, gasPrice\n        );\n        address signer = getSubscriptionSigner(subscriptionHash, signature);\n        uint256 allowance = ERC20(tokenAddress).allowance(from, address(this));\n        uint256 balance = ERC20(tokenAddress).balanceOf(from);\n        return (\n            signer == from &&\n            from != to &&\n            block.timestamp >= nextValidTimestamp[subscriptionHash] &&\n            allowance >= tokenAmount.add(gasPrice) &&\n            balance >= tokenAmount.add(gasPrice)\n        );\n    }\n\n    // you don't really need this if you are using the approve/transferFrom method\n    // because you control the flow of tokens by approving this contract address,\n    // but to make the contract an extensible example for later user I'll add this\n    function cancelSubscription(\n        address from, //the subscriber\n        address to, //the publisher\n        address tokenAddress, //the token address paid to the publisher\n        uint256 tokenAmount, //the token amount paid to the publisher\n        uint256 periodSeconds, //the period in seconds between payments\n        uint256 gasPrice, //the amount of tokens or eth to pay relayer (0 for free)\n        bytes memory signature //proof the subscriber signed the meta trasaction\n    )\n        public\n        returns (bool success)\n    {\n        bytes32 subscriptionHash = getSubscriptionHash(\n            from, to, tokenAddress, tokenAmount, periodSeconds, gasPrice\n        );\n        address signer = subscriptionHash.toEthSignedMessageHash().recover(signature);\n\n        //the signature must be valid\n        require(signer == from, \"Invalid Signature for subscription cancellation\");\n\n        //nextValidTimestamp should be a timestamp that will never\n        //be reached during the brief window human existence\n        nextValidTimestamp[subscriptionHash]=uint256(-1);\n\n        return true;\n    }\n\n    // execute the transferFrom to pay the publisher from the subscriber\n    // the subscriber has full control by approving this contract an allowance\n    function executeSubscription(\n        address from, //the subscriber\n        address to, //the publisher\n        address tokenAddress, //the token address paid to the publisher\n        uint256 tokenAmount, //the token amount paid to the publisher\n        uint256 periodSeconds, //the period in seconds between payments\n        uint256 gasPrice, //the amount of tokens or eth to pay relayer (0 for free)\n        bytes memory signature //proof the subscriber signed the meta trasaction\n    )\n        public\n        returns (bool success)\n    {\n        require(msg.sender == relayer);\n        // make sure the subscription is valid and ready\n        // pulled this out so I have the hash, should be exact code as \"isSubscriptionReady\"\n        bytes32 subscriptionHash = getSubscriptionHash(\n            from, to, tokenAddress, tokenAmount, periodSeconds, gasPrice\n        );\n        address signer = getSubscriptionSigner(subscriptionHash, signature);\n\n        //the signature must be valid\n        require(signer == from, \"Invalid Signature\");\n        //timestamp must be equal to or past the next period\n        require(\n            block.timestamp >= nextValidTimestamp[subscriptionHash],\n            \"Subscription is not ready\"\n        );\n\n        // if there are requirements from the deployer, let's make sure\n        // those are met exactly\n        require( requiredToAddress == address(0) || to == requiredToAddress );\n        require( requiredTokenAddress == address(0) || tokenAddress == requiredTokenAddress );\n        require( requiredTokenAmount == 0 || tokenAmount == requiredTokenAmount );\n        require( requiredPeriodSeconds == 0 || periodSeconds == requiredPeriodSeconds );\n        require( requiredGasPrice == 0 || gasPrice == requiredGasPrice );\n\n        //increment the timestamp by the period so it wont be valid until then\n        nextValidTimestamp[subscriptionHash] = block.timestamp.add(periodSeconds);\n\n        // now, let make the transfer from the subscriber to the publisher\n        uint256 startingBalance = ERC20(tokenAddress).balanceOf(to);\n        require(\n          ERC20(tokenAddress).transferFrom(from,to,tokenAmount),\n          \"Transfer Failed\"\n        );\n        require(\n          (startingBalance+tokenAmount) == ERC20(tokenAddress).balanceOf(to),\n          \"Crappy ERC20 is a bad kitty.\"\n        );\n\n        emit ExecuteSubscription(\n            from, to, tokenAddress, tokenAmount, periodSeconds, gasPrice\n        );\n\n        // it is possible for the subscription execution to be run by a third party\n        // incentivized in the terms of the subscription with a gasPrice of the tokens\n        //  - pay that out now...\n        if (gasPrice > 0) {\n            //the relayer is incentivized by a little of the same token from\n            // the subscriber ... as far as the subscriber knows, they are\n            // just sending X tokens to the publisher, but the publisher can\n            // choose to send Y of those X to a relayer to run their transactions\n            // the publisher will receive X - Y tokens\n            // this must all be setup in the constructor\n            // if not, the subscriber chooses all the params including what goes\n            // to the publisher and what goes to the relayer\n\n            require(\n                ERC20(tokenAddress).transferFrom(from, msg.sender, gasPrice),\n                \"Failed to pay gas as from account\"\n            );\n        }\n\n        return true;\n    }\n}\n",
  "sourcePath": "/Users/danlipert/gitcoin/grants1337/contracts/Subscription.sol",
  "ast": {
    "absolutePath": "/Users/danlipert/gitcoin/grants1337/contracts/Subscription.sol",
    "exportedSymbols": {
      "Subscription": [
        560
      ]
    },
    "id": 561,
    "nodeType": "SourceUnit",
    "nodes": [
      {
        "id": 58,
        "literals": [
          "solidity",
          "^",
          "0.5",
          ".2"
        ],
        "nodeType": "PragmaDirective",
        "src": "0:23:1"
      },
      {
        "absolutePath": "openzeppelin-solidity/contracts/cryptography/ECDSA.sol",
        "file": "openzeppelin-solidity/contracts/cryptography/ECDSA.sol",
        "id": 59,
        "nodeType": "ImportDirective",
        "scope": 561,
        "sourceUnit": 642,
        "src": "905:64:1",
        "symbolAliases": [],
        "unitAlias": ""
      },
      {
        "absolutePath": "openzeppelin-solidity/contracts/math/SafeMath.sol",
        "file": "openzeppelin-solidity/contracts/math/SafeMath.sol",
        "id": 60,
        "nodeType": "ImportDirective",
        "scope": 561,
        "sourceUnit": 770,
        "src": "970:59:1",
        "symbolAliases": [],
        "unitAlias": ""
      },
      {
        "absolutePath": "openzeppelin-solidity/contracts/token/ERC20/ERC20.sol",
        "file": "openzeppelin-solidity/contracts/token/ERC20/ERC20.sol",
        "id": 61,
        "nodeType": "ImportDirective",
        "scope": 561,
        "sourceUnit": 1153,
        "src": "1030:63:1",
        "symbolAliases": [],
        "unitAlias": ""
      },
      {
        "baseContracts": [],
        "contractDependencies": [],
        "contractKind": "contract",
        "documentation": null,
        "fullyImplemented": true,
        "id": 560,
        "linearizedBaseContracts": [
          560
        ],
        "name": "Subscription",
        "nodeType": "ContractDefinition",
        "nodes": [
          {
            "id": 64,
            "libraryName": {
              "contractScope": null,
              "id": 62,
              "name": "ECDSA",
              "nodeType": "UserDefinedTypeName",
              "referencedDeclaration": 641,
              "src": "1130:5:1",
              "typeDescriptions": {
                "typeIdentifier": "t_contract$_ECDSA_$641",
                "typeString": "library ECDSA"
              }
            },
            "nodeType": "UsingForDirective",
            "src": "1124:24:1",
            "typeName": {
              "id": 63,
              "name": "bytes32",
              "nodeType": "ElementaryTypeName",
              "src": "1140:7:1",
              "typeDescriptions": {
                "typeIdentifier": "t_bytes32",
                "typeString": "bytes32"
              }
            }
          },
          {
            "id": 67,
            "libraryName": {
              "contractScope": null,
              "id": 65,
              "name": "SafeMath",
              "nodeType": "UserDefinedTypeName",
              "referencedDeclaration": 769,
              "src": "1159:8:1",
              "typeDescriptions": {
                "typeIdentifier": "t_contract$_SafeMath_$769",
                "typeString": "library SafeMath"
              }
            },
            "nodeType": "UsingForDirective",
            "src": "1153:27:1",
            "typeName": {
              "id": 66,
              "name": "uint256",
              "nodeType": "ElementaryTypeName",
              "src": "1172:7:1",
              "typeDescriptions": {
                "typeIdentifier": "t_uint256",
                "typeString": "uint256"
              }
            }
          },
          {
            "constant": false,
            "id": 69,
            "name": "author",
            "nodeType": "VariableDeclaration",
            "scope": 560,
            "src": "1217:21:1",
            "stateVariable": true,
            "storageLocation": "default",
            "typeDescriptions": {
              "typeIdentifier": "t_address",
              "typeString": "address"
            },
            "typeName": {
              "id": 68,
              "name": "address",
              "nodeType": "ElementaryTypeName",
              "src": "1217:7:1",
              "stateMutability": "nonpayable",
              "typeDescriptions": {
                "typeIdentifier": "t_address",
                "typeString": "address"
              }
            },
            "value": null,
            "visibility": "public"
          },
          {
            "constant": false,
            "id": 71,
            "name": "relayer",
            "nodeType": "VariableDeclaration",
            "scope": 560,
            "src": "1285:22:1",
            "stateVariable": true,
            "storageLocation": "default",
            "typeDescriptions": {
              "typeIdentifier": "t_address",
              "typeString": "address"
            },
            "typeName": {
              "id": 70,
              "name": "address",
              "nodeType": "ElementaryTypeName",
              "src": "1285:7:1",
              "stateMutability": "nonpayable",
              "typeDescriptions": {
                "typeIdentifier": "t_address",
                "typeString": "address"
              }
            },
            "value": null,
            "visibility": "public"
          },
          {
            "constant": false,
            "id": 73,
            "name": "requiredToAddress",
            "nodeType": "VariableDeclaration",
            "scope": 560,
            "src": "1467:32:1",
            "stateVariable": true,
            "storageLocation": "default",
            "typeDescriptions": {
              "typeIdentifier": "t_address",
              "typeString": "address"
            },
            "typeName": {
              "id": 72,
              "name": "address",
              "nodeType": "ElementaryTypeName",
              "src": "1467:7:1",
              "stateMutability": "nonpayable",
              "typeDescriptions": {
                "typeIdentifier": "t_address",
                "typeString": "address"
              }
            },
            "value": null,
            "visibility": "public"
          },
          {
            "constant": false,
            "id": 75,
            "name": "requiredTokenAddress",
            "nodeType": "VariableDeclaration",
            "scope": 560,
            "src": "1505:35:1",
            "stateVariable": true,
            "storageLocation": "default",
            "typeDescriptions": {
              "typeIdentifier": "t_address",
              "typeString": "address"
            },
            "typeName": {
              "id": 74,
              "name": "address",
              "nodeType": "ElementaryTypeName",
              "src": "1505:7:1",
              "stateMutability": "nonpayable",
              "typeDescriptions": {
                "typeIdentifier": "t_address",
                "typeString": "address"
              }
            },
            "value": null,
            "visibility": "public"
          },
          {
            "constant": false,
            "id": 77,
            "name": "requiredTokenAmount",
            "nodeType": "VariableDeclaration",
            "scope": 560,
            "src": "1546:34:1",
            "stateVariable": true,
            "storageLocation": "default",
            "typeDescriptions": {
              "typeIdentifier": "t_uint256",
              "typeString": "uint256"
            },
            "typeName": {
              "id": 76,
              "name": "uint256",
              "nodeType": "ElementaryTypeName",
              "src": "1546:7:1",
              "typeDescriptions": {
                "typeIdentifier": "t_uint256",
                "typeString": "uint256"
              }
            },
            "value": null,
            "visibility": "public"
          },
          {
            "constant": false,
            "id": 79,
            "name": "requiredPeriodSeconds",
            "nodeType": "VariableDeclaration",
            "scope": 560,
            "src": "1586:36:1",
            "stateVariable": true,
            "storageLocation": "default",
            "typeDescriptions": {
              "typeIdentifier": "t_uint256",
              "typeString": "uint256"
            },
            "typeName": {
              "id": 78,
              "name": "uint256",
              "nodeType": "ElementaryTypeName",
              "src": "1586:7:1",
              "typeDescriptions": {
                "typeIdentifier": "t_uint256",
                "typeString": "uint256"
              }
            },
            "value": null,
            "visibility": "public"
          },
          {
            "constant": false,
            "id": 81,
            "name": "requiredGasPrice",
            "nodeType": "VariableDeclaration",
            "scope": 560,
            "src": "1628:31:1",
            "stateVariable": true,
            "storageLocation": "default",
            "typeDescriptions": {
              "typeIdentifier": "t_uint256",
              "typeString": "uint256"
            },
            "typeName": {
              "id": 80,
              "name": "uint256",
              "nodeType": "ElementaryTypeName",
              "src": "1628:7:1",
              "typeDescriptions": {
                "typeIdentifier": "t_uint256",
                "typeString": "uint256"
              }
            },
            "value": null,
            "visibility": "public"
          },
          {
            "body": {
              "id": 125,
              "nodeType": "Block",
              "src": "1865:266:1",
              "statements": [
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 98,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "id": 96,
                      "name": "requiredToAddress",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 73,
                      "src": "1875:17:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "id": 97,
                      "name": "_toAddress",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 83,
                      "src": "1893:10:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      }
                    },
                    "src": "1875:28:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "id": 99,
                  "nodeType": "ExpressionStatement",
                  "src": "1875:28:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 102,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "id": 100,
                      "name": "requiredTokenAddress",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 75,
                      "src": "1913:20:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "id": 101,
                      "name": "_tokenAddress",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 85,
                      "src": "1934:13:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      }
                    },
                    "src": "1913:34:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "id": 103,
                  "nodeType": "ExpressionStatement",
                  "src": "1913:34:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 106,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "id": 104,
                      "name": "requiredTokenAmount",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 77,
                      "src": "1957:19:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "id": 105,
                      "name": "_tokenAmount",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 87,
                      "src": "1977:12:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "src": "1957:32:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "id": 107,
                  "nodeType": "ExpressionStatement",
                  "src": "1957:32:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 110,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "id": 108,
                      "name": "requiredPeriodSeconds",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 79,
                      "src": "1999:21:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "id": 109,
                      "name": "_periodSeconds",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 89,
                      "src": "2021:14:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "src": "1999:36:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "id": 111,
                  "nodeType": "ExpressionStatement",
                  "src": "1999:36:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 114,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "id": 112,
                      "name": "requiredGasPrice",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 81,
                      "src": "2045:16:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "id": 113,
                      "name": "_gasPrice",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 91,
                      "src": "2062:9:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "src": "2045:26:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "id": 115,
                  "nodeType": "ExpressionStatement",
                  "src": "2045:26:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 119,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "id": 116,
                      "name": "author",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 69,
                      "src": "2081:6:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "expression": {
                        "argumentTypes": null,
                        "id": 117,
                        "name": "msg",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 1236,
                        "src": "2088:3:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_magic_message",
                          "typeString": "msg"
                        }
                      },
                      "id": 118,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": false,
                      "lValueRequested": false,
                      "memberName": "sender",
                      "nodeType": "MemberAccess",
                      "referencedDeclaration": null,
                      "src": "2088:10:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address_payable",
                        "typeString": "address payable"
                      }
                    },
                    "src": "2081:17:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "id": 120,
                  "nodeType": "ExpressionStatement",
                  "src": "2081:17:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 123,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "id": 121,
                      "name": "relayer",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 71,
                      "src": "2108:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "id": 122,
                      "name": "_relayer",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 93,
                      "src": "2116:8:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      }
                    },
                    "src": "2108:16:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "id": 124,
                  "nodeType": "ExpressionStatement",
                  "src": "2108:16:1"
                }
              ]
            },
            "documentation": null,
            "id": 126,
            "implemented": true,
            "kind": "constructor",
            "modifiers": [],
            "name": "",
            "nodeType": "FunctionDefinition",
            "parameters": {
              "id": 94,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 83,
                  "name": "_toAddress",
                  "nodeType": "VariableDeclaration",
                  "scope": 126,
                  "src": "1687:18:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 82,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "1687:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 85,
                  "name": "_tokenAddress",
                  "nodeType": "VariableDeclaration",
                  "scope": 126,
                  "src": "1715:21:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 84,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "1715:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 87,
                  "name": "_tokenAmount",
                  "nodeType": "VariableDeclaration",
                  "scope": 126,
                  "src": "1746:20:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 86,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "1746:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 89,
                  "name": "_periodSeconds",
                  "nodeType": "VariableDeclaration",
                  "scope": 126,
                  "src": "1776:22:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 88,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "1776:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 91,
                  "name": "_gasPrice",
                  "nodeType": "VariableDeclaration",
                  "scope": 126,
                  "src": "1808:17:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 90,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "1808:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 93,
                  "name": "_relayer",
                  "nodeType": "VariableDeclaration",
                  "scope": 126,
                  "src": "1835:16:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 92,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "1835:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "1677:180:1"
            },
            "returnParameters": {
              "id": 95,
              "nodeType": "ParameterList",
              "parameters": [],
              "src": "1865:0:1"
            },
            "scope": 560,
            "src": "1666:465:1",
            "stateMutability": "nonpayable",
            "superFunction": null,
            "visibility": "public"
          },
          {
            "anonymous": false,
            "documentation": null,
            "id": 140,
            "name": "ExecuteSubscription",
            "nodeType": "EventDefinition",
            "parameters": {
              "id": 139,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 128,
                  "indexed": true,
                  "name": "from",
                  "nodeType": "VariableDeclaration",
                  "scope": 140,
                  "src": "2172:20:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 127,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "2172:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 130,
                  "indexed": true,
                  "name": "to",
                  "nodeType": "VariableDeclaration",
                  "scope": 140,
                  "src": "2219:18:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 129,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "2219:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 132,
                  "indexed": false,
                  "name": "tokenAddress",
                  "nodeType": "VariableDeclaration",
                  "scope": 140,
                  "src": "2263:20:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 131,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "2263:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 134,
                  "indexed": false,
                  "name": "tokenAmount",
                  "nodeType": "VariableDeclaration",
                  "scope": 140,
                  "src": "2335:19:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 133,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "2335:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 136,
                  "indexed": false,
                  "name": "periodSeconds",
                  "nodeType": "VariableDeclaration",
                  "scope": 140,
                  "src": "2405:21:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 135,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "2405:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 138,
                  "indexed": false,
                  "name": "gasPrice",
                  "nodeType": "VariableDeclaration",
                  "scope": 140,
                  "src": "2477:16:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 137,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "2477:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "2162:388:1"
            },
            "src": "2137:414:1"
          },
          {
            "constant": false,
            "id": 144,
            "name": "nextValidTimestamp",
            "nodeType": "VariableDeclaration",
            "scope": 560,
            "src": "2741:53:1",
            "stateVariable": true,
            "storageLocation": "default",
            "typeDescriptions": {
              "typeIdentifier": "t_mapping$_t_bytes32_$_t_uint256_$",
              "typeString": "mapping(bytes32 => uint256)"
            },
            "typeName": {
              "id": 143,
              "keyType": {
                "id": 141,
                "name": "bytes32",
                "nodeType": "ElementaryTypeName",
                "src": "2749:7:1",
                "typeDescriptions": {
                  "typeIdentifier": "t_bytes32",
                  "typeString": "bytes32"
                }
              },
              "nodeType": "Mapping",
              "src": "2741:27:1",
              "typeDescriptions": {
                "typeIdentifier": "t_mapping$_t_bytes32_$_t_uint256_$",
                "typeString": "mapping(bytes32 => uint256)"
              },
              "valueType": {
                "id": 142,
                "name": "uint256",
                "nodeType": "ElementaryTypeName",
                "src": "2760:7:1",
                "typeDescriptions": {
                  "typeIdentifier": "t_uint256",
                  "typeString": "uint256"
                }
              }
            },
            "value": null,
            "visibility": "public"
          },
          {
            "body": {
              "id": 164,
              "nodeType": "Block",
              "src": "3198:130:1",
              "statements": [
                {
                  "expression": {
                    "argumentTypes": null,
                    "components": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        "id": 161,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "expression": {
                            "argumentTypes": null,
                            "id": 153,
                            "name": "block",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 1226,
                            "src": "3216:5:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_magic_block",
                              "typeString": "block"
                            }
                          },
                          "id": 154,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "memberName": "timestamp",
                          "nodeType": "MemberAccess",
                          "referencedDeclaration": null,
                          "src": "3216:15:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "<=",
                        "rightExpression": {
                          "argumentTypes": null,
                          "arguments": [
                            {
                              "argumentTypes": null,
                              "id": 159,
                              "name": "gracePeriodSeconds",
                              "nodeType": "Identifier",
                              "overloadedDeclarations": [],
                              "referencedDeclaration": 148,
                              "src": "3292:18:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256"
                              }
                            }
                          ],
                          "expression": {
                            "argumentTypes": [
                              {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256"
                              }
                            ],
                            "expression": {
                              "argumentTypes": null,
                              "baseExpression": {
                                "argumentTypes": null,
                                "id": 155,
                                "name": "nextValidTimestamp",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 144,
                                "src": "3251:18:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_mapping$_t_bytes32_$_t_uint256_$",
                                  "typeString": "mapping(bytes32 => uint256)"
                                }
                              },
                              "id": 157,
                              "indexExpression": {
                                "argumentTypes": null,
                                "id": 156,
                                "name": "subscriptionHash",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 146,
                                "src": "3270:16:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_bytes32",
                                  "typeString": "bytes32"
                                }
                              },
                              "isConstant": false,
                              "isLValue": true,
                              "isPure": false,
                              "lValueRequested": false,
                              "nodeType": "IndexAccess",
                              "src": "3251:36:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256"
                              }
                            },
                            "id": 158,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": false,
                            "lValueRequested": false,
                            "memberName": "add",
                            "nodeType": "MemberAccess",
                            "referencedDeclaration": 748,
                            "src": "3251:40:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_function_internal_pure$_t_uint256_$_t_uint256_$returns$_t_uint256_$bound_to$_t_uint256_$",
                              "typeString": "function (uint256,uint256) pure returns (uint256)"
                            }
                          },
                          "id": 160,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "kind": "functionCall",
                          "lValueRequested": false,
                          "names": [],
                          "nodeType": "FunctionCall",
                          "src": "3251:60:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        },
                        "src": "3216:95:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      }
                    ],
                    "id": 162,
                    "isConstant": false,
                    "isInlineArray": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "nodeType": "TupleExpression",
                    "src": "3215:106:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    }
                  },
                  "functionReturnParameters": 152,
                  "id": 163,
                  "nodeType": "Return",
                  "src": "3208:113:1"
                }
              ]
            },
            "documentation": null,
            "id": 165,
            "implemented": true,
            "kind": "function",
            "modifiers": [],
            "name": "isSubscriptionActive",
            "nodeType": "FunctionDefinition",
            "parameters": {
              "id": 149,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 146,
                  "name": "subscriptionHash",
                  "nodeType": "VariableDeclaration",
                  "scope": 165,
                  "src": "3074:24:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bytes32",
                    "typeString": "bytes32"
                  },
                  "typeName": {
                    "id": 145,
                    "name": "bytes32",
                    "nodeType": "ElementaryTypeName",
                    "src": "3074:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes32",
                      "typeString": "bytes32"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 148,
                  "name": "gracePeriodSeconds",
                  "nodeType": "VariableDeclaration",
                  "scope": 165,
                  "src": "3108:26:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 147,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "3108:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "3064:76:1"
            },
            "returnParameters": {
              "id": 152,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 151,
                  "name": "",
                  "nodeType": "VariableDeclaration",
                  "scope": 165,
                  "src": "3188:4:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bool",
                    "typeString": "bool"
                  },
                  "typeName": {
                    "id": 150,
                    "name": "bool",
                    "nodeType": "ElementaryTypeName",
                    "src": "3188:4:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "3187:6:1"
            },
            "scope": 560,
            "src": "3035:293:1",
            "stateMutability": "view",
            "superFunction": null,
            "visibility": "external"
          },
          {
            "body": {
              "id": 203,
              "nodeType": "Block",
              "src": "3950:316:1",
              "statements": [
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "arguments": [
                          {
                            "argumentTypes": null,
                            "arguments": [
                              {
                                "argumentTypes": null,
                                "hexValue": "30783139",
                                "id": 186,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": true,
                                "kind": "number",
                                "lValueRequested": false,
                                "nodeType": "Literal",
                                "src": "4029:4:1",
                                "subdenomination": null,
                                "typeDescriptions": {
                                  "typeIdentifier": "t_rational_25_by_1",
                                  "typeString": "int_const 25"
                                },
                                "value": "0x19"
                              }
                            ],
                            "expression": {
                              "argumentTypes": [
                                {
                                  "typeIdentifier": "t_rational_25_by_1",
                                  "typeString": "int_const 25"
                                }
                              ],
                              "id": 185,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": true,
                              "lValueRequested": false,
                              "nodeType": "ElementaryTypeNameExpression",
                              "src": "4024:4:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_type$_t_bytes1_$",
                                "typeString": "type(bytes1)"
                              },
                              "typeName": "byte"
                            },
                            "id": 187,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": true,
                            "kind": "typeConversion",
                            "lValueRequested": false,
                            "names": [],
                            "nodeType": "FunctionCall",
                            "src": "4024:10:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_bytes1",
                              "typeString": "bytes1"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "arguments": [
                              {
                                "argumentTypes": null,
                                "hexValue": "30",
                                "id": 189,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": true,
                                "kind": "number",
                                "lValueRequested": false,
                                "nodeType": "Literal",
                                "src": "4057:1:1",
                                "subdenomination": null,
                                "typeDescriptions": {
                                  "typeIdentifier": "t_rational_0_by_1",
                                  "typeString": "int_const 0"
                                },
                                "value": "0"
                              }
                            ],
                            "expression": {
                              "argumentTypes": [
                                {
                                  "typeIdentifier": "t_rational_0_by_1",
                                  "typeString": "int_const 0"
                                }
                              ],
                              "id": 188,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": true,
                              "lValueRequested": false,
                              "nodeType": "ElementaryTypeNameExpression",
                              "src": "4052:4:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_type$_t_bytes1_$",
                                "typeString": "type(bytes1)"
                              },
                              "typeName": "byte"
                            },
                            "id": 190,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": true,
                            "kind": "typeConversion",
                            "lValueRequested": false,
                            "names": [],
                            "nodeType": "FunctionCall",
                            "src": "4052:7:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_bytes1",
                              "typeString": "bytes1"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "arguments": [
                              {
                                "argumentTypes": null,
                                "id": 192,
                                "name": "this",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 1259,
                                "src": "4085:4:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_contract$_Subscription_$560",
                                  "typeString": "contract Subscription"
                                }
                              }
                            ],
                            "expression": {
                              "argumentTypes": [
                                {
                                  "typeIdentifier": "t_contract$_Subscription_$560",
                                  "typeString": "contract Subscription"
                                }
                              ],
                              "id": 191,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": true,
                              "lValueRequested": false,
                              "nodeType": "ElementaryTypeNameExpression",
                              "src": "4077:7:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_type$_t_address_$",
                                "typeString": "type(address)"
                              },
                              "typeName": "address"
                            },
                            "id": 193,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": false,
                            "kind": "typeConversion",
                            "lValueRequested": false,
                            "names": [],
                            "nodeType": "FunctionCall",
                            "src": "4077:13:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "id": 194,
                            "name": "from",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 167,
                            "src": "4108:4:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "id": 195,
                            "name": "to",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 169,
                            "src": "4130:2:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "id": 196,
                            "name": "tokenAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 171,
                            "src": "4150:12:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "id": 197,
                            "name": "tokenAmount",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 173,
                            "src": "4180:11:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "id": 198,
                            "name": "periodSeconds",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 175,
                            "src": "4209:13:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "id": 199,
                            "name": "gasPrice",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 177,
                            "src": "4240:8:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          }
                        ],
                        "expression": {
                          "argumentTypes": [
                            {
                              "typeIdentifier": "t_bytes1",
                              "typeString": "bytes1"
                            },
                            {
                              "typeIdentifier": "t_bytes1",
                              "typeString": "bytes1"
                            },
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            },
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            },
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            },
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            },
                            {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            },
                            {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            },
                            {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          ],
                          "expression": {
                            "argumentTypes": null,
                            "id": 183,
                            "name": "abi",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 1223,
                            "src": "3990:3:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_magic_abi",
                              "typeString": "abi"
                            }
                          },
                          "id": 184,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": true,
                          "lValueRequested": false,
                          "memberName": "encodePacked",
                          "nodeType": "MemberAccess",
                          "referencedDeclaration": null,
                          "src": "3990:16:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_function_abiencodepacked_pure$__$returns$_t_bytes_memory_ptr_$",
                            "typeString": "function () pure returns (bytes memory)"
                          }
                        },
                        "id": 200,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "kind": "functionCall",
                        "lValueRequested": false,
                        "names": [],
                        "nodeType": "FunctionCall",
                        "src": "3990:268:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      ],
                      "id": 182,
                      "name": "keccak256",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 1230,
                      "src": "3967:9:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_keccak256_pure$_t_bytes_memory_ptr_$returns$_t_bytes32_$",
                        "typeString": "function (bytes memory) pure returns (bytes32)"
                      }
                    },
                    "id": 201,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "3967:292:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes32",
                      "typeString": "bytes32"
                    }
                  },
                  "functionReturnParameters": 181,
                  "id": 202,
                  "nodeType": "Return",
                  "src": "3960:299:1"
                }
              ]
            },
            "documentation": null,
            "id": 204,
            "implemented": true,
            "kind": "function",
            "modifiers": [],
            "name": "getSubscriptionHash",
            "nodeType": "FunctionDefinition",
            "parameters": {
              "id": 178,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 167,
                  "name": "from",
                  "nodeType": "VariableDeclaration",
                  "scope": 204,
                  "src": "3522:12:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 166,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "3522:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 169,
                  "name": "to",
                  "nodeType": "VariableDeclaration",
                  "scope": 204,
                  "src": "3561:10:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 168,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "3561:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 171,
                  "name": "tokenAddress",
                  "nodeType": "VariableDeclaration",
                  "scope": 204,
                  "src": "3597:20:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 170,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "3597:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 173,
                  "name": "tokenAmount",
                  "nodeType": "VariableDeclaration",
                  "scope": 204,
                  "src": "3669:19:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 172,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "3669:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 175,
                  "name": "periodSeconds",
                  "nodeType": "VariableDeclaration",
                  "scope": 204,
                  "src": "3739:21:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 174,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "3739:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 177,
                  "name": "gasPrice",
                  "nodeType": "VariableDeclaration",
                  "scope": 204,
                  "src": "3811:16:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 176,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "3811:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "3512:379:1"
            },
            "returnParameters": {
              "id": 181,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 180,
                  "name": "",
                  "nodeType": "VariableDeclaration",
                  "scope": 204,
                  "src": "3937:7:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bytes32",
                    "typeString": "bytes32"
                  },
                  "typeName": {
                    "id": 179,
                    "name": "bytes32",
                    "nodeType": "ElementaryTypeName",
                    "src": "3937:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes32",
                      "typeString": "bytes32"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "3936:9:1"
            },
            "scope": 560,
            "src": "3484:782:1",
            "stateMutability": "view",
            "superFunction": null,
            "visibility": "public"
          },
          {
            "body": {
              "id": 220,
              "nodeType": "Block",
              "src": "4561:84:1",
              "statements": [
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 217,
                        "name": "signature",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 208,
                        "src": "4628:9:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      ],
                      "expression": {
                        "argumentTypes": null,
                        "arguments": [],
                        "expression": {
                          "argumentTypes": [],
                          "expression": {
                            "argumentTypes": null,
                            "id": 213,
                            "name": "subscriptionHash",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 206,
                            "src": "4578:16:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_bytes32",
                              "typeString": "bytes32"
                            }
                          },
                          "id": 214,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "memberName": "toEthSignedMessageHash",
                          "nodeType": "MemberAccess",
                          "referencedDeclaration": 640,
                          "src": "4578:39:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_function_internal_pure$_t_bytes32_$returns$_t_bytes32_$bound_to$_t_bytes32_$",
                            "typeString": "function (bytes32) pure returns (bytes32)"
                          }
                        },
                        "id": 215,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "kind": "functionCall",
                        "lValueRequested": false,
                        "names": [],
                        "nodeType": "FunctionCall",
                        "src": "4578:41:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      "id": 216,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": false,
                      "lValueRequested": false,
                      "memberName": "recover",
                      "nodeType": "MemberAccess",
                      "referencedDeclaration": 624,
                      "src": "4578:49:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_internal_pure$_t_bytes32_$_t_bytes_memory_ptr_$returns$_t_address_$bound_to$_t_bytes32_$",
                        "typeString": "function (bytes32,bytes memory) pure returns (address)"
                      }
                    },
                    "id": 218,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "4578:60:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "functionReturnParameters": 212,
                  "id": 219,
                  "nodeType": "Return",
                  "src": "4571:67:1"
                }
              ]
            },
            "documentation": null,
            "id": 221,
            "implemented": true,
            "kind": "function",
            "modifiers": [],
            "name": "getSubscriptionSigner",
            "nodeType": "FunctionDefinition",
            "parameters": {
              "id": 209,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 206,
                  "name": "subscriptionHash",
                  "nodeType": "VariableDeclaration",
                  "scope": 221,
                  "src": "4367:24:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bytes32",
                    "typeString": "bytes32"
                  },
                  "typeName": {
                    "id": 205,
                    "name": "bytes32",
                    "nodeType": "ElementaryTypeName",
                    "src": "4367:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes32",
                      "typeString": "bytes32"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 208,
                  "name": "signature",
                  "nodeType": "VariableDeclaration",
                  "scope": 221,
                  "src": "4424:22:1",
                  "stateVariable": false,
                  "storageLocation": "memory",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bytes_memory_ptr",
                    "typeString": "bytes"
                  },
                  "typeName": {
                    "id": 207,
                    "name": "bytes",
                    "nodeType": "ElementaryTypeName",
                    "src": "4424:5:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes_storage_ptr",
                      "typeString": "bytes"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "4357:145:1"
            },
            "returnParameters": {
              "id": 212,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 211,
                  "name": "",
                  "nodeType": "VariableDeclaration",
                  "scope": 221,
                  "src": "4548:7:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 210,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "4548:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "4547:9:1"
            },
            "scope": 560,
            "src": "4327:318:1",
            "stateMutability": "pure",
            "superFunction": null,
            "visibility": "public"
          },
          {
            "body": {
              "id": 309,
              "nodeType": "Block",
              "src": "5314:625:1",
              "statements": [
                {
                  "assignments": [
                    241
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 241,
                      "name": "subscriptionHash",
                      "nodeType": "VariableDeclaration",
                      "scope": 309,
                      "src": "5324:24:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_bytes32",
                        "typeString": "bytes32"
                      },
                      "typeName": {
                        "id": 240,
                        "name": "bytes32",
                        "nodeType": "ElementaryTypeName",
                        "src": "5324:7:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 250,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 243,
                        "name": "from",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 223,
                        "src": "5384:4:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 244,
                        "name": "to",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 225,
                        "src": "5390:2:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 245,
                        "name": "tokenAddress",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 227,
                        "src": "5394:12:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 246,
                        "name": "tokenAmount",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 229,
                        "src": "5408:11:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 247,
                        "name": "periodSeconds",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 231,
                        "src": "5421:13:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 248,
                        "name": "gasPrice",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 233,
                        "src": "5436:8:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      ],
                      "id": 242,
                      "name": "getSubscriptionHash",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 204,
                      "src": "5351:19:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_internal_view$_t_address_$_t_address_$_t_address_$_t_uint256_$_t_uint256_$_t_uint256_$returns$_t_bytes32_$",
                        "typeString": "function (address,address,address,uint256,uint256,uint256) view returns (bytes32)"
                      }
                    },
                    "id": 249,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "5351:103:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes32",
                      "typeString": "bytes32"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "5324:130:1"
                },
                {
                  "assignments": [
                    252
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 252,
                      "name": "signer",
                      "nodeType": "VariableDeclaration",
                      "scope": 309,
                      "src": "5464:14:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      },
                      "typeName": {
                        "id": 251,
                        "name": "address",
                        "nodeType": "ElementaryTypeName",
                        "src": "5464:7:1",
                        "stateMutability": "nonpayable",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 257,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 254,
                        "name": "subscriptionHash",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 241,
                        "src": "5503:16:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 255,
                        "name": "signature",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 235,
                        "src": "5521:9:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        },
                        {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      ],
                      "id": 253,
                      "name": "getSubscriptionSigner",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 221,
                      "src": "5481:21:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_internal_pure$_t_bytes32_$_t_bytes_memory_ptr_$returns$_t_address_$",
                        "typeString": "function (bytes32,bytes memory) pure returns (address)"
                      }
                    },
                    "id": 256,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "5481:50:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "5464:67:1"
                },
                {
                  "assignments": [
                    259
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 259,
                      "name": "allowance",
                      "nodeType": "VariableDeclaration",
                      "scope": 309,
                      "src": "5541:17:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      },
                      "typeName": {
                        "id": 258,
                        "name": "uint256",
                        "nodeType": "ElementaryTypeName",
                        "src": "5541:7:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 269,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 264,
                        "name": "from",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 223,
                        "src": "5591:4:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "arguments": [
                          {
                            "argumentTypes": null,
                            "id": 266,
                            "name": "this",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 1259,
                            "src": "5605:4:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_contract$_Subscription_$560",
                              "typeString": "contract Subscription"
                            }
                          }
                        ],
                        "expression": {
                          "argumentTypes": [
                            {
                              "typeIdentifier": "t_contract$_Subscription_$560",
                              "typeString": "contract Subscription"
                            }
                          ],
                          "id": 265,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": true,
                          "lValueRequested": false,
                          "nodeType": "ElementaryTypeNameExpression",
                          "src": "5597:7:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_type$_t_address_$",
                            "typeString": "type(address)"
                          },
                          "typeName": "address"
                        },
                        "id": 267,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "kind": "typeConversion",
                        "lValueRequested": false,
                        "names": [],
                        "nodeType": "FunctionCall",
                        "src": "5597:13:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      ],
                      "expression": {
                        "argumentTypes": null,
                        "arguments": [
                          {
                            "argumentTypes": null,
                            "id": 261,
                            "name": "tokenAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 227,
                            "src": "5567:12:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          }
                        ],
                        "expression": {
                          "argumentTypes": [
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          ],
                          "id": 260,
                          "name": "ERC20",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 1152,
                          "src": "5561:5:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_type$_t_contract$_ERC20_$1152_$",
                            "typeString": "type(contract ERC20)"
                          }
                        },
                        "id": 262,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "kind": "typeConversion",
                        "lValueRequested": false,
                        "names": [],
                        "nodeType": "FunctionCall",
                        "src": "5561:19:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_contract$_ERC20_$1152",
                          "typeString": "contract ERC20"
                        }
                      },
                      "id": 263,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": false,
                      "lValueRequested": false,
                      "memberName": "allowance",
                      "nodeType": "MemberAccess",
                      "referencedDeclaration": 826,
                      "src": "5561:29:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_external_view$_t_address_$_t_address_$returns$_t_uint256_$",
                        "typeString": "function (address,address) view external returns (uint256)"
                      }
                    },
                    "id": 268,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "5561:50:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "5541:70:1"
                },
                {
                  "assignments": [
                    271
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 271,
                      "name": "balance",
                      "nodeType": "VariableDeclaration",
                      "scope": 309,
                      "src": "5621:15:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      },
                      "typeName": {
                        "id": 270,
                        "name": "uint256",
                        "nodeType": "ElementaryTypeName",
                        "src": "5621:7:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 278,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 276,
                        "name": "from",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 223,
                        "src": "5669:4:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      ],
                      "expression": {
                        "argumentTypes": null,
                        "arguments": [
                          {
                            "argumentTypes": null,
                            "id": 273,
                            "name": "tokenAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 227,
                            "src": "5645:12:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          }
                        ],
                        "expression": {
                          "argumentTypes": [
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          ],
                          "id": 272,
                          "name": "ERC20",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 1152,
                          "src": "5639:5:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_type$_t_contract$_ERC20_$1152_$",
                            "typeString": "type(contract ERC20)"
                          }
                        },
                        "id": 274,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "kind": "typeConversion",
                        "lValueRequested": false,
                        "names": [],
                        "nodeType": "FunctionCall",
                        "src": "5639:19:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_contract$_ERC20_$1152",
                          "typeString": "contract ERC20"
                        }
                      },
                      "id": 275,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": false,
                      "lValueRequested": false,
                      "memberName": "balanceOf",
                      "nodeType": "MemberAccess",
                      "referencedDeclaration": 810,
                      "src": "5639:29:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_external_view$_t_address_$returns$_t_uint256_$",
                        "typeString": "function (address) view external returns (uint256)"
                      }
                    },
                    "id": 277,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "5639:35:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "5621:53:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "components": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        "id": 306,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          },
                          "id": 299,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "commonType": {
                              "typeIdentifier": "t_bool",
                              "typeString": "bool"
                            },
                            "id": 292,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": false,
                            "lValueRequested": false,
                            "leftExpression": {
                              "argumentTypes": null,
                              "commonType": {
                                "typeIdentifier": "t_bool",
                                "typeString": "bool"
                              },
                              "id": 285,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": false,
                              "lValueRequested": false,
                              "leftExpression": {
                                "argumentTypes": null,
                                "commonType": {
                                  "typeIdentifier": "t_address",
                                  "typeString": "address"
                                },
                                "id": 281,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": false,
                                "lValueRequested": false,
                                "leftExpression": {
                                  "argumentTypes": null,
                                  "id": 279,
                                  "name": "signer",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 252,
                                  "src": "5705:6:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_address",
                                    "typeString": "address"
                                  }
                                },
                                "nodeType": "BinaryOperation",
                                "operator": "==",
                                "rightExpression": {
                                  "argumentTypes": null,
                                  "id": 280,
                                  "name": "from",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 223,
                                  "src": "5715:4:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_address",
                                    "typeString": "address"
                                  }
                                },
                                "src": "5705:14:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_bool",
                                  "typeString": "bool"
                                }
                              },
                              "nodeType": "BinaryOperation",
                              "operator": "&&",
                              "rightExpression": {
                                "argumentTypes": null,
                                "commonType": {
                                  "typeIdentifier": "t_address",
                                  "typeString": "address"
                                },
                                "id": 284,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": false,
                                "lValueRequested": false,
                                "leftExpression": {
                                  "argumentTypes": null,
                                  "id": 282,
                                  "name": "from",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 223,
                                  "src": "5735:4:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_address",
                                    "typeString": "address"
                                  }
                                },
                                "nodeType": "BinaryOperation",
                                "operator": "!=",
                                "rightExpression": {
                                  "argumentTypes": null,
                                  "id": 283,
                                  "name": "to",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 225,
                                  "src": "5743:2:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_address",
                                    "typeString": "address"
                                  }
                                },
                                "src": "5735:10:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_bool",
                                  "typeString": "bool"
                                }
                              },
                              "src": "5705:40:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_bool",
                                "typeString": "bool"
                              }
                            },
                            "nodeType": "BinaryOperation",
                            "operator": "&&",
                            "rightExpression": {
                              "argumentTypes": null,
                              "commonType": {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256"
                              },
                              "id": 291,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": false,
                              "lValueRequested": false,
                              "leftExpression": {
                                "argumentTypes": null,
                                "expression": {
                                  "argumentTypes": null,
                                  "id": 286,
                                  "name": "block",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 1226,
                                  "src": "5761:5:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_magic_block",
                                    "typeString": "block"
                                  }
                                },
                                "id": 287,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": false,
                                "lValueRequested": false,
                                "memberName": "timestamp",
                                "nodeType": "MemberAccess",
                                "referencedDeclaration": null,
                                "src": "5761:15:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_uint256",
                                  "typeString": "uint256"
                                }
                              },
                              "nodeType": "BinaryOperation",
                              "operator": ">=",
                              "rightExpression": {
                                "argumentTypes": null,
                                "baseExpression": {
                                  "argumentTypes": null,
                                  "id": 288,
                                  "name": "nextValidTimestamp",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 144,
                                  "src": "5780:18:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_mapping$_t_bytes32_$_t_uint256_$",
                                    "typeString": "mapping(bytes32 => uint256)"
                                  }
                                },
                                "id": 290,
                                "indexExpression": {
                                  "argumentTypes": null,
                                  "id": 289,
                                  "name": "subscriptionHash",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 241,
                                  "src": "5799:16:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_bytes32",
                                    "typeString": "bytes32"
                                  }
                                },
                                "isConstant": false,
                                "isLValue": true,
                                "isPure": false,
                                "lValueRequested": false,
                                "nodeType": "IndexAccess",
                                "src": "5780:36:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_uint256",
                                  "typeString": "uint256"
                                }
                              },
                              "src": "5761:55:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_bool",
                                "typeString": "bool"
                              }
                            },
                            "src": "5705:111:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_bool",
                              "typeString": "bool"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "&&",
                          "rightExpression": {
                            "argumentTypes": null,
                            "commonType": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            },
                            "id": 298,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": false,
                            "lValueRequested": false,
                            "leftExpression": {
                              "argumentTypes": null,
                              "id": 293,
                              "name": "allowance",
                              "nodeType": "Identifier",
                              "overloadedDeclarations": [],
                              "referencedDeclaration": 259,
                              "src": "5832:9:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256"
                              }
                            },
                            "nodeType": "BinaryOperation",
                            "operator": ">=",
                            "rightExpression": {
                              "argumentTypes": null,
                              "arguments": [
                                {
                                  "argumentTypes": null,
                                  "id": 296,
                                  "name": "gasPrice",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 233,
                                  "src": "5861:8:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_uint256",
                                    "typeString": "uint256"
                                  }
                                }
                              ],
                              "expression": {
                                "argumentTypes": [
                                  {
                                    "typeIdentifier": "t_uint256",
                                    "typeString": "uint256"
                                  }
                                ],
                                "expression": {
                                  "argumentTypes": null,
                                  "id": 294,
                                  "name": "tokenAmount",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 229,
                                  "src": "5845:11:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_uint256",
                                    "typeString": "uint256"
                                  }
                                },
                                "id": 295,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": false,
                                "lValueRequested": false,
                                "memberName": "add",
                                "nodeType": "MemberAccess",
                                "referencedDeclaration": 748,
                                "src": "5845:15:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_function_internal_pure$_t_uint256_$_t_uint256_$returns$_t_uint256_$bound_to$_t_uint256_$",
                                  "typeString": "function (uint256,uint256) pure returns (uint256)"
                                }
                              },
                              "id": 297,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": false,
                              "kind": "functionCall",
                              "lValueRequested": false,
                              "names": [],
                              "nodeType": "FunctionCall",
                              "src": "5845:25:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256"
                              }
                            },
                            "src": "5832:38:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_bool",
                              "typeString": "bool"
                            }
                          },
                          "src": "5705:165:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "&&",
                        "rightExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          },
                          "id": 305,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 300,
                            "name": "balance",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 271,
                            "src": "5886:7:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": ">=",
                          "rightExpression": {
                            "argumentTypes": null,
                            "arguments": [
                              {
                                "argumentTypes": null,
                                "id": 303,
                                "name": "gasPrice",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 233,
                                "src": "5913:8:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_uint256",
                                  "typeString": "uint256"
                                }
                              }
                            ],
                            "expression": {
                              "argumentTypes": [
                                {
                                  "typeIdentifier": "t_uint256",
                                  "typeString": "uint256"
                                }
                              ],
                              "expression": {
                                "argumentTypes": null,
                                "id": 301,
                                "name": "tokenAmount",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 229,
                                "src": "5897:11:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_uint256",
                                  "typeString": "uint256"
                                }
                              },
                              "id": 302,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": false,
                              "lValueRequested": false,
                              "memberName": "add",
                              "nodeType": "MemberAccess",
                              "referencedDeclaration": 748,
                              "src": "5897:15:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_function_internal_pure$_t_uint256_$_t_uint256_$returns$_t_uint256_$bound_to$_t_uint256_$",
                                "typeString": "function (uint256,uint256) pure returns (uint256)"
                              }
                            },
                            "id": 304,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": false,
                            "kind": "functionCall",
                            "lValueRequested": false,
                            "names": [],
                            "nodeType": "FunctionCall",
                            "src": "5897:25:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "src": "5886:36:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "src": "5705:217:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      }
                    ],
                    "id": 307,
                    "isConstant": false,
                    "isInlineArray": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "nodeType": "TupleExpression",
                    "src": "5691:241:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    }
                  },
                  "functionReturnParameters": 239,
                  "id": 308,
                  "nodeType": "Return",
                  "src": "5684:248:1"
                }
              ]
            },
            "documentation": null,
            "id": 310,
            "implemented": true,
            "kind": "function",
            "modifiers": [],
            "name": "isSubscriptionReady",
            "nodeType": "FunctionDefinition",
            "parameters": {
              "id": 236,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 223,
                  "name": "from",
                  "nodeType": "VariableDeclaration",
                  "scope": 310,
                  "src": "4806:12:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 222,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "4806:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 225,
                  "name": "to",
                  "nodeType": "VariableDeclaration",
                  "scope": 310,
                  "src": "4845:10:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 224,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "4845:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 227,
                  "name": "tokenAddress",
                  "nodeType": "VariableDeclaration",
                  "scope": 310,
                  "src": "4881:20:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 226,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "4881:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 229,
                  "name": "tokenAmount",
                  "nodeType": "VariableDeclaration",
                  "scope": 310,
                  "src": "4953:19:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 228,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "4953:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 231,
                  "name": "periodSeconds",
                  "nodeType": "VariableDeclaration",
                  "scope": 310,
                  "src": "5023:21:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 230,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "5023:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 233,
                  "name": "gasPrice",
                  "nodeType": "VariableDeclaration",
                  "scope": 310,
                  "src": "5095:16:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 232,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "5095:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 235,
                  "name": "signature",
                  "nodeType": "VariableDeclaration",
                  "scope": 310,
                  "src": "5180:22:1",
                  "stateVariable": false,
                  "storageLocation": "memory",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bytes_memory_ptr",
                    "typeString": "bytes"
                  },
                  "typeName": {
                    "id": 234,
                    "name": "bytes",
                    "nodeType": "ElementaryTypeName",
                    "src": "5180:5:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes_storage_ptr",
                      "typeString": "bytes"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "4796:462:1"
            },
            "returnParameters": {
              "id": 239,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 238,
                  "name": "",
                  "nodeType": "VariableDeclaration",
                  "scope": 310,
                  "src": "5304:4:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bool",
                    "typeString": "bool"
                  },
                  "typeName": {
                    "id": 237,
                    "name": "bool",
                    "nodeType": "ElementaryTypeName",
                    "src": "5304:4:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "5303:6:1"
            },
            "scope": 560,
            "src": "4768:1171:1",
            "stateMutability": "view",
            "superFunction": null,
            "visibility": "public"
          },
          {
            "body": {
              "id": 367,
              "nodeType": "Block",
              "src": "6732:566:1",
              "statements": [
                {
                  "assignments": [
                    330
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 330,
                      "name": "subscriptionHash",
                      "nodeType": "VariableDeclaration",
                      "scope": 367,
                      "src": "6742:24:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_bytes32",
                        "typeString": "bytes32"
                      },
                      "typeName": {
                        "id": 329,
                        "name": "bytes32",
                        "nodeType": "ElementaryTypeName",
                        "src": "6742:7:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 339,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 332,
                        "name": "from",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 312,
                        "src": "6802:4:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 333,
                        "name": "to",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 314,
                        "src": "6808:2:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 334,
                        "name": "tokenAddress",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 316,
                        "src": "6812:12:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 335,
                        "name": "tokenAmount",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 318,
                        "src": "6826:11:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 336,
                        "name": "periodSeconds",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 320,
                        "src": "6839:13:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 337,
                        "name": "gasPrice",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 322,
                        "src": "6854:8:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      ],
                      "id": 331,
                      "name": "getSubscriptionHash",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 204,
                      "src": "6769:19:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_internal_view$_t_address_$_t_address_$_t_address_$_t_uint256_$_t_uint256_$_t_uint256_$returns$_t_bytes32_$",
                        "typeString": "function (address,address,address,uint256,uint256,uint256) view returns (bytes32)"
                      }
                    },
                    "id": 338,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "6769:103:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes32",
                      "typeString": "bytes32"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "6742:130:1"
                },
                {
                  "assignments": [
                    341
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 341,
                      "name": "signer",
                      "nodeType": "VariableDeclaration",
                      "scope": 367,
                      "src": "6882:14:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      },
                      "typeName": {
                        "id": 340,
                        "name": "address",
                        "nodeType": "ElementaryTypeName",
                        "src": "6882:7:1",
                        "stateMutability": "nonpayable",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 348,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 346,
                        "name": "signature",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 324,
                        "src": "6949:9:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      ],
                      "expression": {
                        "argumentTypes": null,
                        "arguments": [],
                        "expression": {
                          "argumentTypes": [],
                          "expression": {
                            "argumentTypes": null,
                            "id": 342,
                            "name": "subscriptionHash",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 330,
                            "src": "6899:16:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_bytes32",
                              "typeString": "bytes32"
                            }
                          },
                          "id": 343,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "memberName": "toEthSignedMessageHash",
                          "nodeType": "MemberAccess",
                          "referencedDeclaration": 640,
                          "src": "6899:39:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_function_internal_pure$_t_bytes32_$returns$_t_bytes32_$bound_to$_t_bytes32_$",
                            "typeString": "function (bytes32) pure returns (bytes32)"
                          }
                        },
                        "id": 344,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "kind": "functionCall",
                        "lValueRequested": false,
                        "names": [],
                        "nodeType": "FunctionCall",
                        "src": "6899:41:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      "id": 345,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": false,
                      "lValueRequested": false,
                      "memberName": "recover",
                      "nodeType": "MemberAccess",
                      "referencedDeclaration": 624,
                      "src": "6899:49:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_internal_pure$_t_bytes32_$_t_bytes_memory_ptr_$returns$_t_address_$bound_to$_t_bytes32_$",
                        "typeString": "function (bytes32,bytes memory) pure returns (address)"
                      }
                    },
                    "id": 347,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "6899:60:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "6882:77:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        "id": 352,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "id": 350,
                          "name": "signer",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 341,
                          "src": "7016:6:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "==",
                        "rightExpression": {
                          "argumentTypes": null,
                          "id": 351,
                          "name": "from",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 312,
                          "src": "7026:4:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          }
                        },
                        "src": "7016:14:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "hexValue": "496e76616c6964205369676e617475726520666f7220737562736372697074696f6e2063616e63656c6c6174696f6e",
                        "id": 353,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": true,
                        "kind": "string",
                        "lValueRequested": false,
                        "nodeType": "Literal",
                        "src": "7032:49:1",
                        "subdenomination": null,
                        "typeDescriptions": {
                          "typeIdentifier": "t_stringliteral_20f3baa67ddd296dfb8b9e0ec971696cfd8630a4bebb38617aeef0cee76fac0b",
                          "typeString": "literal_string \"Invalid Signature for subscription cancellation\""
                        },
                        "value": "Invalid Signature for subscription cancellation"
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        {
                          "typeIdentifier": "t_stringliteral_20f3baa67ddd296dfb8b9e0ec971696cfd8630a4bebb38617aeef0cee76fac0b",
                          "typeString": "literal_string \"Invalid Signature for subscription cancellation\""
                        }
                      ],
                      "id": 349,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1240,
                      "src": "7008:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$_t_string_memory_ptr_$returns$__$",
                        "typeString": "function (bool,string memory) pure"
                      }
                    },
                    "id": 354,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "7008:74:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 355,
                  "nodeType": "ExpressionStatement",
                  "src": "7008:74:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 363,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "baseExpression": {
                        "argumentTypes": null,
                        "id": 356,
                        "name": "nextValidTimestamp",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 144,
                        "src": "7221:18:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_mapping$_t_bytes32_$_t_uint256_$",
                          "typeString": "mapping(bytes32 => uint256)"
                        }
                      },
                      "id": 358,
                      "indexExpression": {
                        "argumentTypes": null,
                        "id": 357,
                        "name": "subscriptionHash",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 330,
                        "src": "7240:16:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      "isConstant": false,
                      "isLValue": true,
                      "isPure": false,
                      "lValueRequested": true,
                      "nodeType": "IndexAccess",
                      "src": "7221:36:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "arguments": [
                        {
                          "argumentTypes": null,
                          "id": 361,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": true,
                          "lValueRequested": false,
                          "nodeType": "UnaryOperation",
                          "operator": "-",
                          "prefix": true,
                          "src": "7266:2:1",
                          "subExpression": {
                            "argumentTypes": null,
                            "hexValue": "31",
                            "id": 360,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": true,
                            "kind": "number",
                            "lValueRequested": false,
                            "nodeType": "Literal",
                            "src": "7267:1:1",
                            "subdenomination": null,
                            "typeDescriptions": {
                              "typeIdentifier": "t_rational_1_by_1",
                              "typeString": "int_const 1"
                            },
                            "value": "1"
                          },
                          "typeDescriptions": {
                            "typeIdentifier": "t_rational_minus_1_by_1",
                            "typeString": "int_const -1"
                          }
                        }
                      ],
                      "expression": {
                        "argumentTypes": [
                          {
                            "typeIdentifier": "t_rational_minus_1_by_1",
                            "typeString": "int_const -1"
                          }
                        ],
                        "id": 359,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": true,
                        "lValueRequested": false,
                        "nodeType": "ElementaryTypeNameExpression",
                        "src": "7258:7:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_type$_t_uint256_$",
                          "typeString": "type(uint256)"
                        },
                        "typeName": "uint256"
                      },
                      "id": 362,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": true,
                      "kind": "typeConversion",
                      "lValueRequested": false,
                      "names": [],
                      "nodeType": "FunctionCall",
                      "src": "7258:11:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "src": "7221:48:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "id": 364,
                  "nodeType": "ExpressionStatement",
                  "src": "7221:48:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "hexValue": "74727565",
                    "id": 365,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": true,
                    "kind": "bool",
                    "lValueRequested": false,
                    "nodeType": "Literal",
                    "src": "7287:4:1",
                    "subdenomination": null,
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    },
                    "value": "true"
                  },
                  "functionReturnParameters": 328,
                  "id": 366,
                  "nodeType": "Return",
                  "src": "7280:11:1"
                }
              ]
            },
            "documentation": null,
            "id": 368,
            "implemented": true,
            "kind": "function",
            "modifiers": [],
            "name": "cancelSubscription",
            "nodeType": "FunctionDefinition",
            "parameters": {
              "id": 325,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 312,
                  "name": "from",
                  "nodeType": "VariableDeclaration",
                  "scope": 368,
                  "src": "6230:12:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 311,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "6230:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 314,
                  "name": "to",
                  "nodeType": "VariableDeclaration",
                  "scope": 368,
                  "src": "6269:10:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 313,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "6269:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 316,
                  "name": "tokenAddress",
                  "nodeType": "VariableDeclaration",
                  "scope": 368,
                  "src": "6305:20:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 315,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "6305:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 318,
                  "name": "tokenAmount",
                  "nodeType": "VariableDeclaration",
                  "scope": 368,
                  "src": "6377:19:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 317,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "6377:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 320,
                  "name": "periodSeconds",
                  "nodeType": "VariableDeclaration",
                  "scope": 368,
                  "src": "6447:21:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 319,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "6447:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 322,
                  "name": "gasPrice",
                  "nodeType": "VariableDeclaration",
                  "scope": 368,
                  "src": "6519:16:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 321,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "6519:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 324,
                  "name": "signature",
                  "nodeType": "VariableDeclaration",
                  "scope": 368,
                  "src": "6603:22:1",
                  "stateVariable": false,
                  "storageLocation": "memory",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bytes_memory_ptr",
                    "typeString": "bytes"
                  },
                  "typeName": {
                    "id": 323,
                    "name": "bytes",
                    "nodeType": "ElementaryTypeName",
                    "src": "6603:5:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes_storage_ptr",
                      "typeString": "bytes"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "6220:461:1"
            },
            "returnParameters": {
              "id": 328,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 327,
                  "name": "success",
                  "nodeType": "VariableDeclaration",
                  "scope": 368,
                  "src": "6714:12:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bool",
                    "typeString": "bool"
                  },
                  "typeName": {
                    "id": 326,
                    "name": "bool",
                    "nodeType": "ElementaryTypeName",
                    "src": "6714:4:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "6713:14:1"
            },
            "scope": 560,
            "src": "6193:1105:1",
            "stateMutability": "nonpayable",
            "superFunction": null,
            "visibility": "public"
          },
          {
            "body": {
              "id": 558,
              "nodeType": "Block",
              "src": "7996:2924:1",
              "statements": [
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        "id": 391,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "expression": {
                            "argumentTypes": null,
                            "id": 388,
                            "name": "msg",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 1236,
                            "src": "8014:3:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_magic_message",
                              "typeString": "msg"
                            }
                          },
                          "id": 389,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "memberName": "sender",
                          "nodeType": "MemberAccess",
                          "referencedDeclaration": null,
                          "src": "8014:10:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_address_payable",
                            "typeString": "address payable"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "==",
                        "rightExpression": {
                          "argumentTypes": null,
                          "id": 390,
                          "name": "relayer",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 71,
                          "src": "8028:7:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          }
                        },
                        "src": "8014:21:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      ],
                      "id": 387,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1239,
                      "src": "8006:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$returns$__$",
                        "typeString": "function (bool) pure"
                      }
                    },
                    "id": 392,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "8006:30:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 393,
                  "nodeType": "ExpressionStatement",
                  "src": "8006:30:1"
                },
                {
                  "assignments": [
                    395
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 395,
                      "name": "subscriptionHash",
                      "nodeType": "VariableDeclaration",
                      "scope": 558,
                      "src": "8196:24:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_bytes32",
                        "typeString": "bytes32"
                      },
                      "typeName": {
                        "id": 394,
                        "name": "bytes32",
                        "nodeType": "ElementaryTypeName",
                        "src": "8196:7:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 404,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 397,
                        "name": "from",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 370,
                        "src": "8256:4:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 398,
                        "name": "to",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 372,
                        "src": "8262:2:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 399,
                        "name": "tokenAddress",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 374,
                        "src": "8266:12:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 400,
                        "name": "tokenAmount",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 376,
                        "src": "8280:11:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 401,
                        "name": "periodSeconds",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 378,
                        "src": "8293:13:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 402,
                        "name": "gasPrice",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 380,
                        "src": "8308:8:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      ],
                      "id": 396,
                      "name": "getSubscriptionHash",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 204,
                      "src": "8223:19:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_internal_view$_t_address_$_t_address_$_t_address_$_t_uint256_$_t_uint256_$_t_uint256_$returns$_t_bytes32_$",
                        "typeString": "function (address,address,address,uint256,uint256,uint256) view returns (bytes32)"
                      }
                    },
                    "id": 403,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "8223:103:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes32",
                      "typeString": "bytes32"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "8196:130:1"
                },
                {
                  "assignments": [
                    406
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 406,
                      "name": "signer",
                      "nodeType": "VariableDeclaration",
                      "scope": 558,
                      "src": "8336:14:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      },
                      "typeName": {
                        "id": 405,
                        "name": "address",
                        "nodeType": "ElementaryTypeName",
                        "src": "8336:7:1",
                        "stateMutability": "nonpayable",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 411,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 408,
                        "name": "subscriptionHash",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 395,
                        "src": "8375:16:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 409,
                        "name": "signature",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 382,
                        "src": "8393:9:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        },
                        {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      ],
                      "id": 407,
                      "name": "getSubscriptionSigner",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 221,
                      "src": "8353:21:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_internal_pure$_t_bytes32_$_t_bytes_memory_ptr_$returns$_t_address_$",
                        "typeString": "function (bytes32,bytes memory) pure returns (address)"
                      }
                    },
                    "id": 410,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "8353:50:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "8336:67:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        "id": 415,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "id": 413,
                          "name": "signer",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 406,
                          "src": "8460:6:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "==",
                        "rightExpression": {
                          "argumentTypes": null,
                          "id": 414,
                          "name": "from",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 370,
                          "src": "8470:4:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          }
                        },
                        "src": "8460:14:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "hexValue": "496e76616c6964205369676e6174757265",
                        "id": 416,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": true,
                        "kind": "string",
                        "lValueRequested": false,
                        "nodeType": "Literal",
                        "src": "8476:19:1",
                        "subdenomination": null,
                        "typeDescriptions": {
                          "typeIdentifier": "t_stringliteral_98abf41928333e3fb96f450e411f323711f90894815c0b92e5e7c34ae876605a",
                          "typeString": "literal_string \"Invalid Signature\""
                        },
                        "value": "Invalid Signature"
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        {
                          "typeIdentifier": "t_stringliteral_98abf41928333e3fb96f450e411f323711f90894815c0b92e5e7c34ae876605a",
                          "typeString": "literal_string \"Invalid Signature\""
                        }
                      ],
                      "id": 412,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1240,
                      "src": "8452:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$_t_string_memory_ptr_$returns$__$",
                        "typeString": "function (bool,string memory) pure"
                      }
                    },
                    "id": 417,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "8452:44:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 418,
                  "nodeType": "ExpressionStatement",
                  "src": "8452:44:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        "id": 425,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "expression": {
                            "argumentTypes": null,
                            "id": 420,
                            "name": "block",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 1226,
                            "src": "8588:5:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_magic_block",
                              "typeString": "block"
                            }
                          },
                          "id": 421,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "memberName": "timestamp",
                          "nodeType": "MemberAccess",
                          "referencedDeclaration": null,
                          "src": "8588:15:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": ">=",
                        "rightExpression": {
                          "argumentTypes": null,
                          "baseExpression": {
                            "argumentTypes": null,
                            "id": 422,
                            "name": "nextValidTimestamp",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 144,
                            "src": "8607:18:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_mapping$_t_bytes32_$_t_uint256_$",
                              "typeString": "mapping(bytes32 => uint256)"
                            }
                          },
                          "id": 424,
                          "indexExpression": {
                            "argumentTypes": null,
                            "id": 423,
                            "name": "subscriptionHash",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 395,
                            "src": "8626:16:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_bytes32",
                              "typeString": "bytes32"
                            }
                          },
                          "isConstant": false,
                          "isLValue": true,
                          "isPure": false,
                          "lValueRequested": false,
                          "nodeType": "IndexAccess",
                          "src": "8607:36:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        },
                        "src": "8588:55:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "hexValue": "537562736372697074696f6e206973206e6f74207265616479",
                        "id": 426,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": true,
                        "kind": "string",
                        "lValueRequested": false,
                        "nodeType": "Literal",
                        "src": "8657:27:1",
                        "subdenomination": null,
                        "typeDescriptions": {
                          "typeIdentifier": "t_stringliteral_06451f6f57a39e3bee27389eef645fbe7a0fd302c8667e4917572d784cd6c690",
                          "typeString": "literal_string \"Subscription is not ready\""
                        },
                        "value": "Subscription is not ready"
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        {
                          "typeIdentifier": "t_stringliteral_06451f6f57a39e3bee27389eef645fbe7a0fd302c8667e4917572d784cd6c690",
                          "typeString": "literal_string \"Subscription is not ready\""
                        }
                      ],
                      "id": 419,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1240,
                      "src": "8567:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$_t_string_memory_ptr_$returns$__$",
                        "typeString": "function (bool,string memory) pure"
                      }
                    },
                    "id": 427,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "8567:127:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 428,
                  "nodeType": "ExpressionStatement",
                  "src": "8567:127:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        "id": 438,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          },
                          "id": 434,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 430,
                            "name": "requiredToAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 73,
                            "src": "8819:17:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "arguments": [
                              {
                                "argumentTypes": null,
                                "hexValue": "30",
                                "id": 432,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": true,
                                "kind": "number",
                                "lValueRequested": false,
                                "nodeType": "Literal",
                                "src": "8848:1:1",
                                "subdenomination": null,
                                "typeDescriptions": {
                                  "typeIdentifier": "t_rational_0_by_1",
                                  "typeString": "int_const 0"
                                },
                                "value": "0"
                              }
                            ],
                            "expression": {
                              "argumentTypes": [
                                {
                                  "typeIdentifier": "t_rational_0_by_1",
                                  "typeString": "int_const 0"
                                }
                              ],
                              "id": 431,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": true,
                              "lValueRequested": false,
                              "nodeType": "ElementaryTypeNameExpression",
                              "src": "8840:7:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_type$_t_address_$",
                                "typeString": "type(address)"
                              },
                              "typeName": "address"
                            },
                            "id": 433,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": true,
                            "kind": "typeConversion",
                            "lValueRequested": false,
                            "names": [],
                            "nodeType": "FunctionCall",
                            "src": "8840:10:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address_payable",
                              "typeString": "address payable"
                            }
                          },
                          "src": "8819:31:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "||",
                        "rightExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          },
                          "id": 437,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 435,
                            "name": "to",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 372,
                            "src": "8854:2:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "id": 436,
                            "name": "requiredToAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 73,
                            "src": "8860:17:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          "src": "8854:23:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "src": "8819:58:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      ],
                      "id": 429,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1239,
                      "src": "8810:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$returns$__$",
                        "typeString": "function (bool) pure"
                      }
                    },
                    "id": 439,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "8810:69:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 440,
                  "nodeType": "ExpressionStatement",
                  "src": "8810:69:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        "id": 450,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          },
                          "id": 446,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 442,
                            "name": "requiredTokenAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 75,
                            "src": "8898:20:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "arguments": [
                              {
                                "argumentTypes": null,
                                "hexValue": "30",
                                "id": 444,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": true,
                                "kind": "number",
                                "lValueRequested": false,
                                "nodeType": "Literal",
                                "src": "8930:1:1",
                                "subdenomination": null,
                                "typeDescriptions": {
                                  "typeIdentifier": "t_rational_0_by_1",
                                  "typeString": "int_const 0"
                                },
                                "value": "0"
                              }
                            ],
                            "expression": {
                              "argumentTypes": [
                                {
                                  "typeIdentifier": "t_rational_0_by_1",
                                  "typeString": "int_const 0"
                                }
                              ],
                              "id": 443,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": true,
                              "lValueRequested": false,
                              "nodeType": "ElementaryTypeNameExpression",
                              "src": "8922:7:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_type$_t_address_$",
                                "typeString": "type(address)"
                              },
                              "typeName": "address"
                            },
                            "id": 445,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": true,
                            "kind": "typeConversion",
                            "lValueRequested": false,
                            "names": [],
                            "nodeType": "FunctionCall",
                            "src": "8922:10:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address_payable",
                              "typeString": "address payable"
                            }
                          },
                          "src": "8898:34:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "||",
                        "rightExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          },
                          "id": 449,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 447,
                            "name": "tokenAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 374,
                            "src": "8936:12:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "id": 448,
                            "name": "requiredTokenAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 75,
                            "src": "8952:20:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          "src": "8936:36:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "src": "8898:74:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      ],
                      "id": 441,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1239,
                      "src": "8889:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$returns$__$",
                        "typeString": "function (bool) pure"
                      }
                    },
                    "id": 451,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "8889:85:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 452,
                  "nodeType": "ExpressionStatement",
                  "src": "8889:85:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        "id": 460,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          },
                          "id": 456,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 454,
                            "name": "requiredTokenAmount",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 77,
                            "src": "8993:19:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "hexValue": "30",
                            "id": 455,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": true,
                            "kind": "number",
                            "lValueRequested": false,
                            "nodeType": "Literal",
                            "src": "9016:1:1",
                            "subdenomination": null,
                            "typeDescriptions": {
                              "typeIdentifier": "t_rational_0_by_1",
                              "typeString": "int_const 0"
                            },
                            "value": "0"
                          },
                          "src": "8993:24:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "||",
                        "rightExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          },
                          "id": 459,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 457,
                            "name": "tokenAmount",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 376,
                            "src": "9021:11:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "id": 458,
                            "name": "requiredTokenAmount",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 77,
                            "src": "9036:19:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "src": "9021:34:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "src": "8993:62:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      ],
                      "id": 453,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1239,
                      "src": "8984:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$returns$__$",
                        "typeString": "function (bool) pure"
                      }
                    },
                    "id": 461,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "8984:73:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 462,
                  "nodeType": "ExpressionStatement",
                  "src": "8984:73:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        "id": 470,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          },
                          "id": 466,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 464,
                            "name": "requiredPeriodSeconds",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 79,
                            "src": "9076:21:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "hexValue": "30",
                            "id": 465,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": true,
                            "kind": "number",
                            "lValueRequested": false,
                            "nodeType": "Literal",
                            "src": "9101:1:1",
                            "subdenomination": null,
                            "typeDescriptions": {
                              "typeIdentifier": "t_rational_0_by_1",
                              "typeString": "int_const 0"
                            },
                            "value": "0"
                          },
                          "src": "9076:26:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "||",
                        "rightExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          },
                          "id": 469,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 467,
                            "name": "periodSeconds",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 378,
                            "src": "9106:13:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "id": 468,
                            "name": "requiredPeriodSeconds",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 79,
                            "src": "9123:21:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "src": "9106:38:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "src": "9076:68:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      ],
                      "id": 463,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1239,
                      "src": "9067:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$returns$__$",
                        "typeString": "function (bool) pure"
                      }
                    },
                    "id": 471,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "9067:79:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 472,
                  "nodeType": "ExpressionStatement",
                  "src": "9067:79:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        "id": 480,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          },
                          "id": 476,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 474,
                            "name": "requiredGasPrice",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 81,
                            "src": "9165:16:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "hexValue": "30",
                            "id": 475,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": true,
                            "kind": "number",
                            "lValueRequested": false,
                            "nodeType": "Literal",
                            "src": "9185:1:1",
                            "subdenomination": null,
                            "typeDescriptions": {
                              "typeIdentifier": "t_rational_0_by_1",
                              "typeString": "int_const 0"
                            },
                            "value": "0"
                          },
                          "src": "9165:21:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "||",
                        "rightExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          },
                          "id": 479,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 477,
                            "name": "gasPrice",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 380,
                            "src": "9190:8:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "id": 478,
                            "name": "requiredGasPrice",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 81,
                            "src": "9202:16:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "src": "9190:28:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "src": "9165:53:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      ],
                      "id": 473,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1239,
                      "src": "9156:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$returns$__$",
                        "typeString": "function (bool) pure"
                      }
                    },
                    "id": 481,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "9156:64:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 482,
                  "nodeType": "ExpressionStatement",
                  "src": "9156:64:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 491,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "baseExpression": {
                        "argumentTypes": null,
                        "id": 483,
                        "name": "nextValidTimestamp",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 144,
                        "src": "9310:18:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_mapping$_t_bytes32_$_t_uint256_$",
                          "typeString": "mapping(bytes32 => uint256)"
                        }
                      },
                      "id": 485,
                      "indexExpression": {
                        "argumentTypes": null,
                        "id": 484,
                        "name": "subscriptionHash",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 395,
                        "src": "9329:16:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      "isConstant": false,
                      "isLValue": true,
                      "isPure": false,
                      "lValueRequested": true,
                      "nodeType": "IndexAccess",
                      "src": "9310:36:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "arguments": [
                        {
                          "argumentTypes": null,
                          "id": 489,
                          "name": "periodSeconds",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 378,
                          "src": "9369:13:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        }
                      ],
                      "expression": {
                        "argumentTypes": [
                          {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        ],
                        "expression": {
                          "argumentTypes": null,
                          "expression": {
                            "argumentTypes": null,
                            "id": 486,
                            "name": "block",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 1226,
                            "src": "9349:5:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_magic_block",
                              "typeString": "block"
                            }
                          },
                          "id": 487,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "memberName": "timestamp",
                          "nodeType": "MemberAccess",
                          "referencedDeclaration": null,
                          "src": "9349:15:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        },
                        "id": 488,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "memberName": "add",
                        "nodeType": "MemberAccess",
                        "referencedDeclaration": 748,
                        "src": "9349:19:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_function_internal_pure$_t_uint256_$_t_uint256_$returns$_t_uint256_$bound_to$_t_uint256_$",
                          "typeString": "function (uint256,uint256) pure returns (uint256)"
                        }
                      },
                      "id": 490,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": false,
                      "kind": "functionCall",
                      "lValueRequested": false,
                      "names": [],
                      "nodeType": "FunctionCall",
                      "src": "9349:34:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "src": "9310:73:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "id": 492,
                  "nodeType": "ExpressionStatement",
                  "src": "9310:73:1"
                },
                {
                  "assignments": [
                    494
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 494,
                      "name": "startingBalance",
                      "nodeType": "VariableDeclaration",
                      "scope": 558,
                      "src": "9469:23:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      },
                      "typeName": {
                        "id": 493,
                        "name": "uint256",
                        "nodeType": "ElementaryTypeName",
                        "src": "9469:7:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 501,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 499,
                        "name": "to",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 372,
                        "src": "9525:2:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      ],
                      "expression": {
                        "argumentTypes": null,
                        "arguments": [
                          {
                            "argumentTypes": null,
                            "id": 496,
                            "name": "tokenAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 374,
                            "src": "9501:12:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          }
                        ],
                        "expression": {
                          "argumentTypes": [
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          ],
                          "id": 495,
                          "name": "ERC20",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 1152,
                          "src": "9495:5:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_type$_t_contract$_ERC20_$1152_$",
                            "typeString": "type(contract ERC20)"
                          }
                        },
                        "id": 497,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "kind": "typeConversion",
                        "lValueRequested": false,
                        "names": [],
                        "nodeType": "FunctionCall",
                        "src": "9495:19:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_contract$_ERC20_$1152",
                          "typeString": "contract ERC20"
                        }
                      },
                      "id": 498,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": false,
                      "lValueRequested": false,
                      "memberName": "balanceOf",
                      "nodeType": "MemberAccess",
                      "referencedDeclaration": 810,
                      "src": "9495:29:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_external_view$_t_address_$returns$_t_uint256_$",
                        "typeString": "function (address) view external returns (uint256)"
                      }
                    },
                    "id": 500,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "9495:33:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "9469:59:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "arguments": [
                          {
                            "argumentTypes": null,
                            "id": 507,
                            "name": "from",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 370,
                            "src": "9590:4:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "id": 508,
                            "name": "to",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 372,
                            "src": "9595:2:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "id": 509,
                            "name": "tokenAmount",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 376,
                            "src": "9598:11:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          }
                        ],
                        "expression": {
                          "argumentTypes": [
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            },
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            },
                            {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          ],
                          "expression": {
                            "argumentTypes": null,
                            "arguments": [
                              {
                                "argumentTypes": null,
                                "id": 504,
                                "name": "tokenAddress",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 374,
                                "src": "9563:12:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_address",
                                  "typeString": "address"
                                }
                              }
                            ],
                            "expression": {
                              "argumentTypes": [
                                {
                                  "typeIdentifier": "t_address",
                                  "typeString": "address"
                                }
                              ],
                              "id": 503,
                              "name": "ERC20",
                              "nodeType": "Identifier",
                              "overloadedDeclarations": [],
                              "referencedDeclaration": 1152,
                              "src": "9557:5:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_type$_t_contract$_ERC20_$1152_$",
                                "typeString": "type(contract ERC20)"
                              }
                            },
                            "id": 505,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": false,
                            "kind": "typeConversion",
                            "lValueRequested": false,
                            "names": [],
                            "nodeType": "FunctionCall",
                            "src": "9557:19:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_contract$_ERC20_$1152",
                              "typeString": "contract ERC20"
                            }
                          },
                          "id": 506,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "memberName": "transferFrom",
                          "nodeType": "MemberAccess",
                          "referencedDeclaration": 899,
                          "src": "9557:32:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_function_external_nonpayable$_t_address_$_t_address_$_t_uint256_$returns$_t_bool_$",
                            "typeString": "function (address,address,uint256) external returns (bool)"
                          }
                        },
                        "id": 510,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "kind": "functionCall",
                        "lValueRequested": false,
                        "names": [],
                        "nodeType": "FunctionCall",
                        "src": "9557:53:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "hexValue": "5472616e73666572204661696c6564",
                        "id": 511,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": true,
                        "kind": "string",
                        "lValueRequested": false,
                        "nodeType": "Literal",
                        "src": "9622:17:1",
                        "subdenomination": null,
                        "typeDescriptions": {
                          "typeIdentifier": "t_stringliteral_c5acabcb762867cdbcf367c30c495273eabea012d93b81d74177ab1ef966623f",
                          "typeString": "literal_string \"Transfer Failed\""
                        },
                        "value": "Transfer Failed"
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        {
                          "typeIdentifier": "t_stringliteral_c5acabcb762867cdbcf367c30c495273eabea012d93b81d74177ab1ef966623f",
                          "typeString": "literal_string \"Transfer Failed\""
                        }
                      ],
                      "id": 502,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1240,
                      "src": "9538:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$_t_string_memory_ptr_$returns$__$",
                        "typeString": "function (bool,string memory) pure"
                      }
                    },
                    "id": 512,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "9538:111:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 513,
                  "nodeType": "ExpressionStatement",
                  "src": "9538:111:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        "id": 525,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "components": [
                            {
                              "argumentTypes": null,
                              "commonType": {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256"
                              },
                              "id": 517,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": false,
                              "lValueRequested": false,
                              "leftExpression": {
                                "argumentTypes": null,
                                "id": 515,
                                "name": "startingBalance",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 494,
                                "src": "9679:15:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_uint256",
                                  "typeString": "uint256"
                                }
                              },
                              "nodeType": "BinaryOperation",
                              "operator": "+",
                              "rightExpression": {
                                "argumentTypes": null,
                                "id": 516,
                                "name": "tokenAmount",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 376,
                                "src": "9695:11:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_uint256",
                                  "typeString": "uint256"
                                }
                              },
                              "src": "9679:27:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256"
                              }
                            }
                          ],
                          "id": 518,
                          "isConstant": false,
                          "isInlineArray": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "nodeType": "TupleExpression",
                          "src": "9678:29:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "==",
                        "rightExpression": {
                          "argumentTypes": null,
                          "arguments": [
                            {
                              "argumentTypes": null,
                              "id": 523,
                              "name": "to",
                              "nodeType": "Identifier",
                              "overloadedDeclarations": [],
                              "referencedDeclaration": 372,
                              "src": "9741:2:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_address",
                                "typeString": "address"
                              }
                            }
                          ],
                          "expression": {
                            "argumentTypes": [
                              {
                                "typeIdentifier": "t_address",
                                "typeString": "address"
                              }
                            ],
                            "expression": {
                              "argumentTypes": null,
                              "arguments": [
                                {
                                  "argumentTypes": null,
                                  "id": 520,
                                  "name": "tokenAddress",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 374,
                                  "src": "9717:12:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_address",
                                    "typeString": "address"
                                  }
                                }
                              ],
                              "expression": {
                                "argumentTypes": [
                                  {
                                    "typeIdentifier": "t_address",
                                    "typeString": "address"
                                  }
                                ],
                                "id": 519,
                                "name": "ERC20",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 1152,
                                "src": "9711:5:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_type$_t_contract$_ERC20_$1152_$",
                                  "typeString": "type(contract ERC20)"
                                }
                              },
                              "id": 521,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": false,
                              "kind": "typeConversion",
                              "lValueRequested": false,
                              "names": [],
                              "nodeType": "FunctionCall",
                              "src": "9711:19:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_contract$_ERC20_$1152",
                                "typeString": "contract ERC20"
                              }
                            },
                            "id": 522,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": false,
                            "lValueRequested": false,
                            "memberName": "balanceOf",
                            "nodeType": "MemberAccess",
                            "referencedDeclaration": 810,
                            "src": "9711:29:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_function_external_view$_t_address_$returns$_t_uint256_$",
                              "typeString": "function (address) view external returns (uint256)"
                            }
                          },
                          "id": 524,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "kind": "functionCall",
                          "lValueRequested": false,
                          "names": [],
                          "nodeType": "FunctionCall",
                          "src": "9711:33:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        },
                        "src": "9678:66:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "hexValue": "437261707079204552433230206973206120626164206b697474792e",
                        "id": 526,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": true,
                        "kind": "string",
                        "lValueRequested": false,
                        "nodeType": "Literal",
                        "src": "9756:30:1",
                        "subdenomination": null,
                        "typeDescriptions": {
                          "typeIdentifier": "t_stringliteral_029ffbbaf13c4f3c926d750ec214cf79eff7ac3e72a55ff6f0f5dd1e456a4c5c",
                          "typeString": "literal_string \"Crappy ERC20 is a bad kitty.\""
                        },
                        "value": "Crappy ERC20 is a bad kitty."
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        {
                          "typeIdentifier": "t_stringliteral_029ffbbaf13c4f3c926d750ec214cf79eff7ac3e72a55ff6f0f5dd1e456a4c5c",
                          "typeString": "literal_string \"Crappy ERC20 is a bad kitty.\""
                        }
                      ],
                      "id": 514,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1240,
                      "src": "9659:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$_t_string_memory_ptr_$returns$__$",
                        "typeString": "function (bool,string memory) pure"
                      }
                    },
                    "id": 527,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "9659:137:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 528,
                  "nodeType": "ExpressionStatement",
                  "src": "9659:137:1"
                },
                {
                  "eventCall": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 530,
                        "name": "from",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 370,
                        "src": "9845:4:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 531,
                        "name": "to",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 372,
                        "src": "9851:2:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 532,
                        "name": "tokenAddress",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 374,
                        "src": "9855:12:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 533,
                        "name": "tokenAmount",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 376,
                        "src": "9869:11:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 534,
                        "name": "periodSeconds",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 378,
                        "src": "9882:13:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 535,
                        "name": "gasPrice",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 380,
                        "src": "9897:8:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      ],
                      "id": 529,
                      "name": "ExecuteSubscription",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 140,
                      "src": "9812:19:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_event_nonpayable$_t_address_$_t_address_$_t_address_$_t_uint256_$_t_uint256_$_t_uint256_$returns$__$",
                        "typeString": "function (address,address,address,uint256,uint256,uint256)"
                      }
                    },
                    "id": 536,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "9812:103:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 537,
                  "nodeType": "EmitStatement",
                  "src": "9807:108:1"
                },
                {
                  "condition": {
                    "argumentTypes": null,
                    "commonType": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    },
                    "id": 540,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftExpression": {
                      "argumentTypes": null,
                      "id": 538,
                      "name": "gasPrice",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 380,
                      "src": "10135:8:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "nodeType": "BinaryOperation",
                    "operator": ">",
                    "rightExpression": {
                      "argumentTypes": null,
                      "hexValue": "30",
                      "id": 539,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": true,
                      "kind": "number",
                      "lValueRequested": false,
                      "nodeType": "Literal",
                      "src": "10146:1:1",
                      "subdenomination": null,
                      "typeDescriptions": {
                        "typeIdentifier": "t_rational_0_by_1",
                        "typeString": "int_const 0"
                      },
                      "value": "0"
                    },
                    "src": "10135:12:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    }
                  },
                  "falseBody": null,
                  "id": 555,
                  "nodeType": "IfStatement",
                  "src": "10131:761:1",
                  "trueBody": {
                    "id": 554,
                    "nodeType": "Block",
                    "src": "10149:743:1",
                    "statements": [
                      {
                        "expression": {
                          "argumentTypes": null,
                          "arguments": [
                            {
                              "argumentTypes": null,
                              "arguments": [
                                {
                                  "argumentTypes": null,
                                  "id": 546,
                                  "name": "from",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 370,
                                  "src": "10787:4:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_address",
                                    "typeString": "address"
                                  }
                                },
                                {
                                  "argumentTypes": null,
                                  "expression": {
                                    "argumentTypes": null,
                                    "id": 547,
                                    "name": "msg",
                                    "nodeType": "Identifier",
                                    "overloadedDeclarations": [],
                                    "referencedDeclaration": 1236,
                                    "src": "10793:3:1",
                                    "typeDescriptions": {
                                      "typeIdentifier": "t_magic_message",
                                      "typeString": "msg"
                                    }
                                  },
                                  "id": 548,
                                  "isConstant": false,
                                  "isLValue": false,
                                  "isPure": false,
                                  "lValueRequested": false,
                                  "memberName": "sender",
                                  "nodeType": "MemberAccess",
                                  "referencedDeclaration": null,
                                  "src": "10793:10:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_address_payable",
                                    "typeString": "address payable"
                                  }
                                },
                                {
                                  "argumentTypes": null,
                                  "id": 549,
                                  "name": "gasPrice",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 380,
                                  "src": "10805:8:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_uint256",
                                    "typeString": "uint256"
                                  }
                                }
                              ],
                              "expression": {
                                "argumentTypes": [
                                  {
                                    "typeIdentifier": "t_address",
                                    "typeString": "address"
                                  },
                                  {
                                    "typeIdentifier": "t_address_payable",
                                    "typeString": "address payable"
                                  },
                                  {
                                    "typeIdentifier": "t_uint256",
                                    "typeString": "uint256"
                                  }
                                ],
                                "expression": {
                                  "argumentTypes": null,
                                  "arguments": [
                                    {
                                      "argumentTypes": null,
                                      "id": 543,
                                      "name": "tokenAddress",
                                      "nodeType": "Identifier",
                                      "overloadedDeclarations": [],
                                      "referencedDeclaration": 374,
                                      "src": "10760:12:1",
                                      "typeDescriptions": {
                                        "typeIdentifier": "t_address",
                                        "typeString": "address"
                                      }
                                    }
                                  ],
                                  "expression": {
                                    "argumentTypes": [
                                      {
                                        "typeIdentifier": "t_address",
                                        "typeString": "address"
                                      }
                                    ],
                                    "id": 542,
                                    "name": "ERC20",
                                    "nodeType": "Identifier",
                                    "overloadedDeclarations": [],
                                    "referencedDeclaration": 1152,
                                    "src": "10754:5:1",
                                    "typeDescriptions": {
                                      "typeIdentifier": "t_type$_t_contract$_ERC20_$1152_$",
                                      "typeString": "type(contract ERC20)"
                                    }
                                  },
                                  "id": 544,
                                  "isConstant": false,
                                  "isLValue": false,
                                  "isPure": false,
                                  "kind": "typeConversion",
                                  "lValueRequested": false,
                                  "names": [],
                                  "nodeType": "FunctionCall",
                                  "src": "10754:19:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_contract$_ERC20_$1152",
                                    "typeString": "contract ERC20"
                                  }
                                },
                                "id": 545,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": false,
                                "lValueRequested": false,
                                "memberName": "transferFrom",
                                "nodeType": "MemberAccess",
                                "referencedDeclaration": 899,
                                "src": "10754:32:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_function_external_nonpayable$_t_address_$_t_address_$_t_uint256_$returns$_t_bool_$",
                                  "typeString": "function (address,address,uint256) external returns (bool)"
                                }
                              },
                              "id": 550,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": false,
                              "kind": "functionCall",
                              "lValueRequested": false,
                              "names": [],
                              "nodeType": "FunctionCall",
                              "src": "10754:60:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_bool",
                                "typeString": "bool"
                              }
                            },
                            {
                              "argumentTypes": null,
                              "hexValue": "4661696c656420746f20706179206761732061732066726f6d206163636f756e74",
                              "id": 551,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": true,
                              "kind": "string",
                              "lValueRequested": false,
                              "nodeType": "Literal",
                              "src": "10832:35:1",
                              "subdenomination": null,
                              "typeDescriptions": {
                                "typeIdentifier": "t_stringliteral_14793e3e3905a30586d2b24e3ad0438f041907f0cf302e37f5d900c5e9ac3e25",
                                "typeString": "literal_string \"Failed to pay gas as from account\""
                              },
                              "value": "Failed to pay gas as from account"
                            }
                          ],
                          "expression": {
                            "argumentTypes": [
                              {
                                "typeIdentifier": "t_bool",
                                "typeString": "bool"
                              },
                              {
                                "typeIdentifier": "t_stringliteral_14793e3e3905a30586d2b24e3ad0438f041907f0cf302e37f5d900c5e9ac3e25",
                                "typeString": "literal_string \"Failed to pay gas as from account\""
                              }
                            ],
                            "id": 541,
                            "name": "require",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [
                              1239,
                              1240
                            ],
                            "referencedDeclaration": 1240,
                            "src": "10729:7:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_function_require_pure$_t_bool_$_t_string_memory_ptr_$returns$__$",
                              "typeString": "function (bool,string memory) pure"
                            }
                          },
                          "id": 552,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "kind": "functionCall",
                          "lValueRequested": false,
                          "names": [],
                          "nodeType": "FunctionCall",
                          "src": "10729:152:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_tuple$__$",
                            "typeString": "tuple()"
                          }
                        },
                        "id": 553,
                        "nodeType": "ExpressionStatement",
                        "src": "10729:152:1"
                      }
                    ]
                  }
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "hexValue": "74727565",
                    "id": 556,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": true,
                    "kind": "bool",
                    "lValueRequested": false,
                    "nodeType": "Literal",
                    "src": "10909:4:1",
                    "subdenomination": null,
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    },
                    "value": "true"
                  },
                  "functionReturnParameters": 386,
                  "id": 557,
                  "nodeType": "Return",
                  "src": "10902:11:1"
                }
              ]
            },
            "documentation": null,
            "id": 559,
            "implemented": true,
            "kind": "function",
            "modifiers": [],
            "name": "executeSubscription",
            "nodeType": "FunctionDefinition",
            "parameters": {
              "id": 383,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 370,
                  "name": "from",
                  "nodeType": "VariableDeclaration",
                  "scope": 559,
                  "src": "7494:12:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 369,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "7494:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 372,
                  "name": "to",
                  "nodeType": "VariableDeclaration",
                  "scope": 559,
                  "src": "7533:10:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 371,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "7533:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 374,
                  "name": "tokenAddress",
                  "nodeType": "VariableDeclaration",
                  "scope": 559,
                  "src": "7569:20:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 373,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "7569:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 376,
                  "name": "tokenAmount",
                  "nodeType": "VariableDeclaration",
                  "scope": 559,
                  "src": "7641:19:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 375,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "7641:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 378,
                  "name": "periodSeconds",
                  "nodeType": "VariableDeclaration",
                  "scope": 559,
                  "src": "7711:21:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 377,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "7711:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 380,
                  "name": "gasPrice",
                  "nodeType": "VariableDeclaration",
                  "scope": 559,
                  "src": "7783:16:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 379,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "7783:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 382,
                  "name": "signature",
                  "nodeType": "VariableDeclaration",
                  "scope": 559,
                  "src": "7867:22:1",
                  "stateVariable": false,
                  "storageLocation": "memory",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bytes_memory_ptr",
                    "typeString": "bytes"
                  },
                  "typeName": {
                    "id": 381,
                    "name": "bytes",
                    "nodeType": "ElementaryTypeName",
                    "src": "7867:5:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes_storage_ptr",
                      "typeString": "bytes"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "7484:461:1"
            },
            "returnParameters": {
              "id": 386,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 385,
                  "name": "success",
                  "nodeType": "VariableDeclaration",
                  "scope": 559,
                  "src": "7978:12:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bool",
                    "typeString": "bool"
                  },
                  "typeName": {
                    "id": 384,
                    "name": "bool",
                    "nodeType": "ElementaryTypeName",
                    "src": "7978:4:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "7977:14:1"
            },
            "scope": 560,
            "src": "7456:3464:1",
            "stateMutability": "nonpayable",
            "superFunction": null,
            "visibility": "public"
          }
        ],
        "scope": 561,
        "src": "1096:9826:1"
      }
    ],
    "src": "0:10923:1"
  },
  "legacyAST": {
    "absolutePath": "/Users/danlipert/gitcoin/grants1337/contracts/Subscription.sol",
    "exportedSymbols": {
      "Subscription": [
        560
      ]
    },
    "id": 561,
    "nodeType": "SourceUnit",
    "nodes": [
      {
        "id": 58,
        "literals": [
          "solidity",
          "^",
          "0.5",
          ".2"
        ],
        "nodeType": "PragmaDirective",
        "src": "0:23:1"
      },
      {
        "absolutePath": "openzeppelin-solidity/contracts/cryptography/ECDSA.sol",
        "file": "openzeppelin-solidity/contracts/cryptography/ECDSA.sol",
        "id": 59,
        "nodeType": "ImportDirective",
        "scope": 561,
        "sourceUnit": 642,
        "src": "905:64:1",
        "symbolAliases": [],
        "unitAlias": ""
      },
      {
        "absolutePath": "openzeppelin-solidity/contracts/math/SafeMath.sol",
        "file": "openzeppelin-solidity/contracts/math/SafeMath.sol",
        "id": 60,
        "nodeType": "ImportDirective",
        "scope": 561,
        "sourceUnit": 770,
        "src": "970:59:1",
        "symbolAliases": [],
        "unitAlias": ""
      },
      {
        "absolutePath": "openzeppelin-solidity/contracts/token/ERC20/ERC20.sol",
        "file": "openzeppelin-solidity/contracts/token/ERC20/ERC20.sol",
        "id": 61,
        "nodeType": "ImportDirective",
        "scope": 561,
        "sourceUnit": 1153,
        "src": "1030:63:1",
        "symbolAliases": [],
        "unitAlias": ""
      },
      {
        "baseContracts": [],
        "contractDependencies": [],
        "contractKind": "contract",
        "documentation": null,
        "fullyImplemented": true,
        "id": 560,
        "linearizedBaseContracts": [
          560
        ],
        "name": "Subscription",
        "nodeType": "ContractDefinition",
        "nodes": [
          {
            "id": 64,
            "libraryName": {
              "contractScope": null,
              "id": 62,
              "name": "ECDSA",
              "nodeType": "UserDefinedTypeName",
              "referencedDeclaration": 641,
              "src": "1130:5:1",
              "typeDescriptions": {
                "typeIdentifier": "t_contract$_ECDSA_$641",
                "typeString": "library ECDSA"
              }
            },
            "nodeType": "UsingForDirective",
            "src": "1124:24:1",
            "typeName": {
              "id": 63,
              "name": "bytes32",
              "nodeType": "ElementaryTypeName",
              "src": "1140:7:1",
              "typeDescriptions": {
                "typeIdentifier": "t_bytes32",
                "typeString": "bytes32"
              }
            }
          },
          {
            "id": 67,
            "libraryName": {
              "contractScope": null,
              "id": 65,
              "name": "SafeMath",
              "nodeType": "UserDefinedTypeName",
              "referencedDeclaration": 769,
              "src": "1159:8:1",
              "typeDescriptions": {
                "typeIdentifier": "t_contract$_SafeMath_$769",
                "typeString": "library SafeMath"
              }
            },
            "nodeType": "UsingForDirective",
            "src": "1153:27:1",
            "typeName": {
              "id": 66,
              "name": "uint256",
              "nodeType": "ElementaryTypeName",
              "src": "1172:7:1",
              "typeDescriptions": {
                "typeIdentifier": "t_uint256",
                "typeString": "uint256"
              }
            }
          },
          {
            "constant": false,
            "id": 69,
            "name": "author",
            "nodeType": "VariableDeclaration",
            "scope": 560,
            "src": "1217:21:1",
            "stateVariable": true,
            "storageLocation": "default",
            "typeDescriptions": {
              "typeIdentifier": "t_address",
              "typeString": "address"
            },
            "typeName": {
              "id": 68,
              "name": "address",
              "nodeType": "ElementaryTypeName",
              "src": "1217:7:1",
              "stateMutability": "nonpayable",
              "typeDescriptions": {
                "typeIdentifier": "t_address",
                "typeString": "address"
              }
            },
            "value": null,
            "visibility": "public"
          },
          {
            "constant": false,
            "id": 71,
            "name": "relayer",
            "nodeType": "VariableDeclaration",
            "scope": 560,
            "src": "1285:22:1",
            "stateVariable": true,
            "storageLocation": "default",
            "typeDescriptions": {
              "typeIdentifier": "t_address",
              "typeString": "address"
            },
            "typeName": {
              "id": 70,
              "name": "address",
              "nodeType": "ElementaryTypeName",
              "src": "1285:7:1",
              "stateMutability": "nonpayable",
              "typeDescriptions": {
                "typeIdentifier": "t_address",
                "typeString": "address"
              }
            },
            "value": null,
            "visibility": "public"
          },
          {
            "constant": false,
            "id": 73,
            "name": "requiredToAddress",
            "nodeType": "VariableDeclaration",
            "scope": 560,
            "src": "1467:32:1",
            "stateVariable": true,
            "storageLocation": "default",
            "typeDescriptions": {
              "typeIdentifier": "t_address",
              "typeString": "address"
            },
            "typeName": {
              "id": 72,
              "name": "address",
              "nodeType": "ElementaryTypeName",
              "src": "1467:7:1",
              "stateMutability": "nonpayable",
              "typeDescriptions": {
                "typeIdentifier": "t_address",
                "typeString": "address"
              }
            },
            "value": null,
            "visibility": "public"
          },
          {
            "constant": false,
            "id": 75,
            "name": "requiredTokenAddress",
            "nodeType": "VariableDeclaration",
            "scope": 560,
            "src": "1505:35:1",
            "stateVariable": true,
            "storageLocation": "default",
            "typeDescriptions": {
              "typeIdentifier": "t_address",
              "typeString": "address"
            },
            "typeName": {
              "id": 74,
              "name": "address",
              "nodeType": "ElementaryTypeName",
              "src": "1505:7:1",
              "stateMutability": "nonpayable",
              "typeDescriptions": {
                "typeIdentifier": "t_address",
                "typeString": "address"
              }
            },
            "value": null,
            "visibility": "public"
          },
          {
            "constant": false,
            "id": 77,
            "name": "requiredTokenAmount",
            "nodeType": "VariableDeclaration",
            "scope": 560,
            "src": "1546:34:1",
            "stateVariable": true,
            "storageLocation": "default",
            "typeDescriptions": {
              "typeIdentifier": "t_uint256",
              "typeString": "uint256"
            },
            "typeName": {
              "id": 76,
              "name": "uint256",
              "nodeType": "ElementaryTypeName",
              "src": "1546:7:1",
              "typeDescriptions": {
                "typeIdentifier": "t_uint256",
                "typeString": "uint256"
              }
            },
            "value": null,
            "visibility": "public"
          },
          {
            "constant": false,
            "id": 79,
            "name": "requiredPeriodSeconds",
            "nodeType": "VariableDeclaration",
            "scope": 560,
            "src": "1586:36:1",
            "stateVariable": true,
            "storageLocation": "default",
            "typeDescriptions": {
              "typeIdentifier": "t_uint256",
              "typeString": "uint256"
            },
            "typeName": {
              "id": 78,
              "name": "uint256",
              "nodeType": "ElementaryTypeName",
              "src": "1586:7:1",
              "typeDescriptions": {
                "typeIdentifier": "t_uint256",
                "typeString": "uint256"
              }
            },
            "value": null,
            "visibility": "public"
          },
          {
            "constant": false,
            "id": 81,
            "name": "requiredGasPrice",
            "nodeType": "VariableDeclaration",
            "scope": 560,
            "src": "1628:31:1",
            "stateVariable": true,
            "storageLocation": "default",
            "typeDescriptions": {
              "typeIdentifier": "t_uint256",
              "typeString": "uint256"
            },
            "typeName": {
              "id": 80,
              "name": "uint256",
              "nodeType": "ElementaryTypeName",
              "src": "1628:7:1",
              "typeDescriptions": {
                "typeIdentifier": "t_uint256",
                "typeString": "uint256"
              }
            },
            "value": null,
            "visibility": "public"
          },
          {
            "body": {
              "id": 125,
              "nodeType": "Block",
              "src": "1865:266:1",
              "statements": [
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 98,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "id": 96,
                      "name": "requiredToAddress",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 73,
                      "src": "1875:17:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "id": 97,
                      "name": "_toAddress",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 83,
                      "src": "1893:10:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      }
                    },
                    "src": "1875:28:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "id": 99,
                  "nodeType": "ExpressionStatement",
                  "src": "1875:28:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 102,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "id": 100,
                      "name": "requiredTokenAddress",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 75,
                      "src": "1913:20:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "id": 101,
                      "name": "_tokenAddress",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 85,
                      "src": "1934:13:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      }
                    },
                    "src": "1913:34:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "id": 103,
                  "nodeType": "ExpressionStatement",
                  "src": "1913:34:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 106,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "id": 104,
                      "name": "requiredTokenAmount",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 77,
                      "src": "1957:19:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "id": 105,
                      "name": "_tokenAmount",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 87,
                      "src": "1977:12:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "src": "1957:32:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "id": 107,
                  "nodeType": "ExpressionStatement",
                  "src": "1957:32:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 110,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "id": 108,
                      "name": "requiredPeriodSeconds",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 79,
                      "src": "1999:21:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "id": 109,
                      "name": "_periodSeconds",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 89,
                      "src": "2021:14:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "src": "1999:36:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "id": 111,
                  "nodeType": "ExpressionStatement",
                  "src": "1999:36:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 114,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "id": 112,
                      "name": "requiredGasPrice",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 81,
                      "src": "2045:16:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "id": 113,
                      "name": "_gasPrice",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 91,
                      "src": "2062:9:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "src": "2045:26:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "id": 115,
                  "nodeType": "ExpressionStatement",
                  "src": "2045:26:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 119,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "id": 116,
                      "name": "author",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 69,
                      "src": "2081:6:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "expression": {
                        "argumentTypes": null,
                        "id": 117,
                        "name": "msg",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 1236,
                        "src": "2088:3:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_magic_message",
                          "typeString": "msg"
                        }
                      },
                      "id": 118,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": false,
                      "lValueRequested": false,
                      "memberName": "sender",
                      "nodeType": "MemberAccess",
                      "referencedDeclaration": null,
                      "src": "2088:10:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address_payable",
                        "typeString": "address payable"
                      }
                    },
                    "src": "2081:17:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "id": 120,
                  "nodeType": "ExpressionStatement",
                  "src": "2081:17:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 123,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "id": 121,
                      "name": "relayer",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 71,
                      "src": "2108:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "id": 122,
                      "name": "_relayer",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 93,
                      "src": "2116:8:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      }
                    },
                    "src": "2108:16:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "id": 124,
                  "nodeType": "ExpressionStatement",
                  "src": "2108:16:1"
                }
              ]
            },
            "documentation": null,
            "id": 126,
            "implemented": true,
            "kind": "constructor",
            "modifiers": [],
            "name": "",
            "nodeType": "FunctionDefinition",
            "parameters": {
              "id": 94,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 83,
                  "name": "_toAddress",
                  "nodeType": "VariableDeclaration",
                  "scope": 126,
                  "src": "1687:18:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 82,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "1687:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 85,
                  "name": "_tokenAddress",
                  "nodeType": "VariableDeclaration",
                  "scope": 126,
                  "src": "1715:21:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 84,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "1715:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 87,
                  "name": "_tokenAmount",
                  "nodeType": "VariableDeclaration",
                  "scope": 126,
                  "src": "1746:20:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 86,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "1746:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 89,
                  "name": "_periodSeconds",
                  "nodeType": "VariableDeclaration",
                  "scope": 126,
                  "src": "1776:22:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 88,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "1776:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 91,
                  "name": "_gasPrice",
                  "nodeType": "VariableDeclaration",
                  "scope": 126,
                  "src": "1808:17:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 90,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "1808:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 93,
                  "name": "_relayer",
                  "nodeType": "VariableDeclaration",
                  "scope": 126,
                  "src": "1835:16:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 92,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "1835:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "1677:180:1"
            },
            "returnParameters": {
              "id": 95,
              "nodeType": "ParameterList",
              "parameters": [],
              "src": "1865:0:1"
            },
            "scope": 560,
            "src": "1666:465:1",
            "stateMutability": "nonpayable",
            "superFunction": null,
            "visibility": "public"
          },
          {
            "anonymous": false,
            "documentation": null,
            "id": 140,
            "name": "ExecuteSubscription",
            "nodeType": "EventDefinition",
            "parameters": {
              "id": 139,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 128,
                  "indexed": true,
                  "name": "from",
                  "nodeType": "VariableDeclaration",
                  "scope": 140,
                  "src": "2172:20:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 127,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "2172:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 130,
                  "indexed": true,
                  "name": "to",
                  "nodeType": "VariableDeclaration",
                  "scope": 140,
                  "src": "2219:18:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 129,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "2219:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 132,
                  "indexed": false,
                  "name": "tokenAddress",
                  "nodeType": "VariableDeclaration",
                  "scope": 140,
                  "src": "2263:20:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 131,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "2263:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 134,
                  "indexed": false,
                  "name": "tokenAmount",
                  "nodeType": "VariableDeclaration",
                  "scope": 140,
                  "src": "2335:19:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 133,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "2335:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 136,
                  "indexed": false,
                  "name": "periodSeconds",
                  "nodeType": "VariableDeclaration",
                  "scope": 140,
                  "src": "2405:21:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 135,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "2405:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 138,
                  "indexed": false,
                  "name": "gasPrice",
                  "nodeType": "VariableDeclaration",
                  "scope": 140,
                  "src": "2477:16:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 137,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "2477:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "2162:388:1"
            },
            "src": "2137:414:1"
          },
          {
            "constant": false,
            "id": 144,
            "name": "nextValidTimestamp",
            "nodeType": "VariableDeclaration",
            "scope": 560,
            "src": "2741:53:1",
            "stateVariable": true,
            "storageLocation": "default",
            "typeDescriptions": {
              "typeIdentifier": "t_mapping$_t_bytes32_$_t_uint256_$",
              "typeString": "mapping(bytes32 => uint256)"
            },
            "typeName": {
              "id": 143,
              "keyType": {
                "id": 141,
                "name": "bytes32",
                "nodeType": "ElementaryTypeName",
                "src": "2749:7:1",
                "typeDescriptions": {
                  "typeIdentifier": "t_bytes32",
                  "typeString": "bytes32"
                }
              },
              "nodeType": "Mapping",
              "src": "2741:27:1",
              "typeDescriptions": {
                "typeIdentifier": "t_mapping$_t_bytes32_$_t_uint256_$",
                "typeString": "mapping(bytes32 => uint256)"
              },
              "valueType": {
                "id": 142,
                "name": "uint256",
                "nodeType": "ElementaryTypeName",
                "src": "2760:7:1",
                "typeDescriptions": {
                  "typeIdentifier": "t_uint256",
                  "typeString": "uint256"
                }
              }
            },
            "value": null,
            "visibility": "public"
          },
          {
            "body": {
              "id": 164,
              "nodeType": "Block",
              "src": "3198:130:1",
              "statements": [
                {
                  "expression": {
                    "argumentTypes": null,
                    "components": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        "id": 161,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "expression": {
                            "argumentTypes": null,
                            "id": 153,
                            "name": "block",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 1226,
                            "src": "3216:5:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_magic_block",
                              "typeString": "block"
                            }
                          },
                          "id": 154,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "memberName": "timestamp",
                          "nodeType": "MemberAccess",
                          "referencedDeclaration": null,
                          "src": "3216:15:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "<=",
                        "rightExpression": {
                          "argumentTypes": null,
                          "arguments": [
                            {
                              "argumentTypes": null,
                              "id": 159,
                              "name": "gracePeriodSeconds",
                              "nodeType": "Identifier",
                              "overloadedDeclarations": [],
                              "referencedDeclaration": 148,
                              "src": "3292:18:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256"
                              }
                            }
                          ],
                          "expression": {
                            "argumentTypes": [
                              {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256"
                              }
                            ],
                            "expression": {
                              "argumentTypes": null,
                              "baseExpression": {
                                "argumentTypes": null,
                                "id": 155,
                                "name": "nextValidTimestamp",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 144,
                                "src": "3251:18:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_mapping$_t_bytes32_$_t_uint256_$",
                                  "typeString": "mapping(bytes32 => uint256)"
                                }
                              },
                              "id": 157,
                              "indexExpression": {
                                "argumentTypes": null,
                                "id": 156,
                                "name": "subscriptionHash",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 146,
                                "src": "3270:16:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_bytes32",
                                  "typeString": "bytes32"
                                }
                              },
                              "isConstant": false,
                              "isLValue": true,
                              "isPure": false,
                              "lValueRequested": false,
                              "nodeType": "IndexAccess",
                              "src": "3251:36:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256"
                              }
                            },
                            "id": 158,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": false,
                            "lValueRequested": false,
                            "memberName": "add",
                            "nodeType": "MemberAccess",
                            "referencedDeclaration": 748,
                            "src": "3251:40:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_function_internal_pure$_t_uint256_$_t_uint256_$returns$_t_uint256_$bound_to$_t_uint256_$",
                              "typeString": "function (uint256,uint256) pure returns (uint256)"
                            }
                          },
                          "id": 160,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "kind": "functionCall",
                          "lValueRequested": false,
                          "names": [],
                          "nodeType": "FunctionCall",
                          "src": "3251:60:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        },
                        "src": "3216:95:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      }
                    ],
                    "id": 162,
                    "isConstant": false,
                    "isInlineArray": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "nodeType": "TupleExpression",
                    "src": "3215:106:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    }
                  },
                  "functionReturnParameters": 152,
                  "id": 163,
                  "nodeType": "Return",
                  "src": "3208:113:1"
                }
              ]
            },
            "documentation": null,
            "id": 165,
            "implemented": true,
            "kind": "function",
            "modifiers": [],
            "name": "isSubscriptionActive",
            "nodeType": "FunctionDefinition",
            "parameters": {
              "id": 149,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 146,
                  "name": "subscriptionHash",
                  "nodeType": "VariableDeclaration",
                  "scope": 165,
                  "src": "3074:24:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bytes32",
                    "typeString": "bytes32"
                  },
                  "typeName": {
                    "id": 145,
                    "name": "bytes32",
                    "nodeType": "ElementaryTypeName",
                    "src": "3074:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes32",
                      "typeString": "bytes32"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 148,
                  "name": "gracePeriodSeconds",
                  "nodeType": "VariableDeclaration",
                  "scope": 165,
                  "src": "3108:26:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 147,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "3108:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "3064:76:1"
            },
            "returnParameters": {
              "id": 152,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 151,
                  "name": "",
                  "nodeType": "VariableDeclaration",
                  "scope": 165,
                  "src": "3188:4:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bool",
                    "typeString": "bool"
                  },
                  "typeName": {
                    "id": 150,
                    "name": "bool",
                    "nodeType": "ElementaryTypeName",
                    "src": "3188:4:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "3187:6:1"
            },
            "scope": 560,
            "src": "3035:293:1",
            "stateMutability": "view",
            "superFunction": null,
            "visibility": "external"
          },
          {
            "body": {
              "id": 203,
              "nodeType": "Block",
              "src": "3950:316:1",
              "statements": [
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "arguments": [
                          {
                            "argumentTypes": null,
                            "arguments": [
                              {
                                "argumentTypes": null,
                                "hexValue": "30783139",
                                "id": 186,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": true,
                                "kind": "number",
                                "lValueRequested": false,
                                "nodeType": "Literal",
                                "src": "4029:4:1",
                                "subdenomination": null,
                                "typeDescriptions": {
                                  "typeIdentifier": "t_rational_25_by_1",
                                  "typeString": "int_const 25"
                                },
                                "value": "0x19"
                              }
                            ],
                            "expression": {
                              "argumentTypes": [
                                {
                                  "typeIdentifier": "t_rational_25_by_1",
                                  "typeString": "int_const 25"
                                }
                              ],
                              "id": 185,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": true,
                              "lValueRequested": false,
                              "nodeType": "ElementaryTypeNameExpression",
                              "src": "4024:4:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_type$_t_bytes1_$",
                                "typeString": "type(bytes1)"
                              },
                              "typeName": "byte"
                            },
                            "id": 187,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": true,
                            "kind": "typeConversion",
                            "lValueRequested": false,
                            "names": [],
                            "nodeType": "FunctionCall",
                            "src": "4024:10:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_bytes1",
                              "typeString": "bytes1"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "arguments": [
                              {
                                "argumentTypes": null,
                                "hexValue": "30",
                                "id": 189,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": true,
                                "kind": "number",
                                "lValueRequested": false,
                                "nodeType": "Literal",
                                "src": "4057:1:1",
                                "subdenomination": null,
                                "typeDescriptions": {
                                  "typeIdentifier": "t_rational_0_by_1",
                                  "typeString": "int_const 0"
                                },
                                "value": "0"
                              }
                            ],
                            "expression": {
                              "argumentTypes": [
                                {
                                  "typeIdentifier": "t_rational_0_by_1",
                                  "typeString": "int_const 0"
                                }
                              ],
                              "id": 188,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": true,
                              "lValueRequested": false,
                              "nodeType": "ElementaryTypeNameExpression",
                              "src": "4052:4:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_type$_t_bytes1_$",
                                "typeString": "type(bytes1)"
                              },
                              "typeName": "byte"
                            },
                            "id": 190,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": true,
                            "kind": "typeConversion",
                            "lValueRequested": false,
                            "names": [],
                            "nodeType": "FunctionCall",
                            "src": "4052:7:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_bytes1",
                              "typeString": "bytes1"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "arguments": [
                              {
                                "argumentTypes": null,
                                "id": 192,
                                "name": "this",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 1259,
                                "src": "4085:4:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_contract$_Subscription_$560",
                                  "typeString": "contract Subscription"
                                }
                              }
                            ],
                            "expression": {
                              "argumentTypes": [
                                {
                                  "typeIdentifier": "t_contract$_Subscription_$560",
                                  "typeString": "contract Subscription"
                                }
                              ],
                              "id": 191,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": true,
                              "lValueRequested": false,
                              "nodeType": "ElementaryTypeNameExpression",
                              "src": "4077:7:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_type$_t_address_$",
                                "typeString": "type(address)"
                              },
                              "typeName": "address"
                            },
                            "id": 193,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": false,
                            "kind": "typeConversion",
                            "lValueRequested": false,
                            "names": [],
                            "nodeType": "FunctionCall",
                            "src": "4077:13:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "id": 194,
                            "name": "from",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 167,
                            "src": "4108:4:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "id": 195,
                            "name": "to",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 169,
                            "src": "4130:2:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "id": 196,
                            "name": "tokenAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 171,
                            "src": "4150:12:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "id": 197,
                            "name": "tokenAmount",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 173,
                            "src": "4180:11:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "id": 198,
                            "name": "periodSeconds",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 175,
                            "src": "4209:13:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "id": 199,
                            "name": "gasPrice",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 177,
                            "src": "4240:8:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          }
                        ],
                        "expression": {
                          "argumentTypes": [
                            {
                              "typeIdentifier": "t_bytes1",
                              "typeString": "bytes1"
                            },
                            {
                              "typeIdentifier": "t_bytes1",
                              "typeString": "bytes1"
                            },
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            },
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            },
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            },
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            },
                            {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            },
                            {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            },
                            {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          ],
                          "expression": {
                            "argumentTypes": null,
                            "id": 183,
                            "name": "abi",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 1223,
                            "src": "3990:3:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_magic_abi",
                              "typeString": "abi"
                            }
                          },
                          "id": 184,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": true,
                          "lValueRequested": false,
                          "memberName": "encodePacked",
                          "nodeType": "MemberAccess",
                          "referencedDeclaration": null,
                          "src": "3990:16:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_function_abiencodepacked_pure$__$returns$_t_bytes_memory_ptr_$",
                            "typeString": "function () pure returns (bytes memory)"
                          }
                        },
                        "id": 200,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "kind": "functionCall",
                        "lValueRequested": false,
                        "names": [],
                        "nodeType": "FunctionCall",
                        "src": "3990:268:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      ],
                      "id": 182,
                      "name": "keccak256",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 1230,
                      "src": "3967:9:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_keccak256_pure$_t_bytes_memory_ptr_$returns$_t_bytes32_$",
                        "typeString": "function (bytes memory) pure returns (bytes32)"
                      }
                    },
                    "id": 201,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "3967:292:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes32",
                      "typeString": "bytes32"
                    }
                  },
                  "functionReturnParameters": 181,
                  "id": 202,
                  "nodeType": "Return",
                  "src": "3960:299:1"
                }
              ]
            },
            "documentation": null,
            "id": 204,
            "implemented": true,
            "kind": "function",
            "modifiers": [],
            "name": "getSubscriptionHash",
            "nodeType": "FunctionDefinition",
            "parameters": {
              "id": 178,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 167,
                  "name": "from",
                  "nodeType": "VariableDeclaration",
                  "scope": 204,
                  "src": "3522:12:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 166,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "3522:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 169,
                  "name": "to",
                  "nodeType": "VariableDeclaration",
                  "scope": 204,
                  "src": "3561:10:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 168,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "3561:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 171,
                  "name": "tokenAddress",
                  "nodeType": "VariableDeclaration",
                  "scope": 204,
                  "src": "3597:20:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 170,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "3597:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 173,
                  "name": "tokenAmount",
                  "nodeType": "VariableDeclaration",
                  "scope": 204,
                  "src": "3669:19:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 172,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "3669:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 175,
                  "name": "periodSeconds",
                  "nodeType": "VariableDeclaration",
                  "scope": 204,
                  "src": "3739:21:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 174,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "3739:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 177,
                  "name": "gasPrice",
                  "nodeType": "VariableDeclaration",
                  "scope": 204,
                  "src": "3811:16:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 176,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "3811:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "3512:379:1"
            },
            "returnParameters": {
              "id": 181,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 180,
                  "name": "",
                  "nodeType": "VariableDeclaration",
                  "scope": 204,
                  "src": "3937:7:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bytes32",
                    "typeString": "bytes32"
                  },
                  "typeName": {
                    "id": 179,
                    "name": "bytes32",
                    "nodeType": "ElementaryTypeName",
                    "src": "3937:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes32",
                      "typeString": "bytes32"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "3936:9:1"
            },
            "scope": 560,
            "src": "3484:782:1",
            "stateMutability": "view",
            "superFunction": null,
            "visibility": "public"
          },
          {
            "body": {
              "id": 220,
              "nodeType": "Block",
              "src": "4561:84:1",
              "statements": [
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 217,
                        "name": "signature",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 208,
                        "src": "4628:9:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      ],
                      "expression": {
                        "argumentTypes": null,
                        "arguments": [],
                        "expression": {
                          "argumentTypes": [],
                          "expression": {
                            "argumentTypes": null,
                            "id": 213,
                            "name": "subscriptionHash",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 206,
                            "src": "4578:16:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_bytes32",
                              "typeString": "bytes32"
                            }
                          },
                          "id": 214,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "memberName": "toEthSignedMessageHash",
                          "nodeType": "MemberAccess",
                          "referencedDeclaration": 640,
                          "src": "4578:39:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_function_internal_pure$_t_bytes32_$returns$_t_bytes32_$bound_to$_t_bytes32_$",
                            "typeString": "function (bytes32) pure returns (bytes32)"
                          }
                        },
                        "id": 215,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "kind": "functionCall",
                        "lValueRequested": false,
                        "names": [],
                        "nodeType": "FunctionCall",
                        "src": "4578:41:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      "id": 216,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": false,
                      "lValueRequested": false,
                      "memberName": "recover",
                      "nodeType": "MemberAccess",
                      "referencedDeclaration": 624,
                      "src": "4578:49:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_internal_pure$_t_bytes32_$_t_bytes_memory_ptr_$returns$_t_address_$bound_to$_t_bytes32_$",
                        "typeString": "function (bytes32,bytes memory) pure returns (address)"
                      }
                    },
                    "id": 218,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "4578:60:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "functionReturnParameters": 212,
                  "id": 219,
                  "nodeType": "Return",
                  "src": "4571:67:1"
                }
              ]
            },
            "documentation": null,
            "id": 221,
            "implemented": true,
            "kind": "function",
            "modifiers": [],
            "name": "getSubscriptionSigner",
            "nodeType": "FunctionDefinition",
            "parameters": {
              "id": 209,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 206,
                  "name": "subscriptionHash",
                  "nodeType": "VariableDeclaration",
                  "scope": 221,
                  "src": "4367:24:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bytes32",
                    "typeString": "bytes32"
                  },
                  "typeName": {
                    "id": 205,
                    "name": "bytes32",
                    "nodeType": "ElementaryTypeName",
                    "src": "4367:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes32",
                      "typeString": "bytes32"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 208,
                  "name": "signature",
                  "nodeType": "VariableDeclaration",
                  "scope": 221,
                  "src": "4424:22:1",
                  "stateVariable": false,
                  "storageLocation": "memory",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bytes_memory_ptr",
                    "typeString": "bytes"
                  },
                  "typeName": {
                    "id": 207,
                    "name": "bytes",
                    "nodeType": "ElementaryTypeName",
                    "src": "4424:5:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes_storage_ptr",
                      "typeString": "bytes"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "4357:145:1"
            },
            "returnParameters": {
              "id": 212,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 211,
                  "name": "",
                  "nodeType": "VariableDeclaration",
                  "scope": 221,
                  "src": "4548:7:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 210,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "4548:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "4547:9:1"
            },
            "scope": 560,
            "src": "4327:318:1",
            "stateMutability": "pure",
            "superFunction": null,
            "visibility": "public"
          },
          {
            "body": {
              "id": 309,
              "nodeType": "Block",
              "src": "5314:625:1",
              "statements": [
                {
                  "assignments": [
                    241
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 241,
                      "name": "subscriptionHash",
                      "nodeType": "VariableDeclaration",
                      "scope": 309,
                      "src": "5324:24:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_bytes32",
                        "typeString": "bytes32"
                      },
                      "typeName": {
                        "id": 240,
                        "name": "bytes32",
                        "nodeType": "ElementaryTypeName",
                        "src": "5324:7:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 250,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 243,
                        "name": "from",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 223,
                        "src": "5384:4:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 244,
                        "name": "to",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 225,
                        "src": "5390:2:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 245,
                        "name": "tokenAddress",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 227,
                        "src": "5394:12:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 246,
                        "name": "tokenAmount",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 229,
                        "src": "5408:11:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 247,
                        "name": "periodSeconds",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 231,
                        "src": "5421:13:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 248,
                        "name": "gasPrice",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 233,
                        "src": "5436:8:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      ],
                      "id": 242,
                      "name": "getSubscriptionHash",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 204,
                      "src": "5351:19:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_internal_view$_t_address_$_t_address_$_t_address_$_t_uint256_$_t_uint256_$_t_uint256_$returns$_t_bytes32_$",
                        "typeString": "function (address,address,address,uint256,uint256,uint256) view returns (bytes32)"
                      }
                    },
                    "id": 249,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "5351:103:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes32",
                      "typeString": "bytes32"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "5324:130:1"
                },
                {
                  "assignments": [
                    252
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 252,
                      "name": "signer",
                      "nodeType": "VariableDeclaration",
                      "scope": 309,
                      "src": "5464:14:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      },
                      "typeName": {
                        "id": 251,
                        "name": "address",
                        "nodeType": "ElementaryTypeName",
                        "src": "5464:7:1",
                        "stateMutability": "nonpayable",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 257,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 254,
                        "name": "subscriptionHash",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 241,
                        "src": "5503:16:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 255,
                        "name": "signature",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 235,
                        "src": "5521:9:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        },
                        {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      ],
                      "id": 253,
                      "name": "getSubscriptionSigner",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 221,
                      "src": "5481:21:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_internal_pure$_t_bytes32_$_t_bytes_memory_ptr_$returns$_t_address_$",
                        "typeString": "function (bytes32,bytes memory) pure returns (address)"
                      }
                    },
                    "id": 256,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "5481:50:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "5464:67:1"
                },
                {
                  "assignments": [
                    259
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 259,
                      "name": "allowance",
                      "nodeType": "VariableDeclaration",
                      "scope": 309,
                      "src": "5541:17:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      },
                      "typeName": {
                        "id": 258,
                        "name": "uint256",
                        "nodeType": "ElementaryTypeName",
                        "src": "5541:7:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 269,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 264,
                        "name": "from",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 223,
                        "src": "5591:4:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "arguments": [
                          {
                            "argumentTypes": null,
                            "id": 266,
                            "name": "this",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 1259,
                            "src": "5605:4:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_contract$_Subscription_$560",
                              "typeString": "contract Subscription"
                            }
                          }
                        ],
                        "expression": {
                          "argumentTypes": [
                            {
                              "typeIdentifier": "t_contract$_Subscription_$560",
                              "typeString": "contract Subscription"
                            }
                          ],
                          "id": 265,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": true,
                          "lValueRequested": false,
                          "nodeType": "ElementaryTypeNameExpression",
                          "src": "5597:7:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_type$_t_address_$",
                            "typeString": "type(address)"
                          },
                          "typeName": "address"
                        },
                        "id": 267,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "kind": "typeConversion",
                        "lValueRequested": false,
                        "names": [],
                        "nodeType": "FunctionCall",
                        "src": "5597:13:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      ],
                      "expression": {
                        "argumentTypes": null,
                        "arguments": [
                          {
                            "argumentTypes": null,
                            "id": 261,
                            "name": "tokenAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 227,
                            "src": "5567:12:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          }
                        ],
                        "expression": {
                          "argumentTypes": [
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          ],
                          "id": 260,
                          "name": "ERC20",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 1152,
                          "src": "5561:5:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_type$_t_contract$_ERC20_$1152_$",
                            "typeString": "type(contract ERC20)"
                          }
                        },
                        "id": 262,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "kind": "typeConversion",
                        "lValueRequested": false,
                        "names": [],
                        "nodeType": "FunctionCall",
                        "src": "5561:19:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_contract$_ERC20_$1152",
                          "typeString": "contract ERC20"
                        }
                      },
                      "id": 263,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": false,
                      "lValueRequested": false,
                      "memberName": "allowance",
                      "nodeType": "MemberAccess",
                      "referencedDeclaration": 826,
                      "src": "5561:29:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_external_view$_t_address_$_t_address_$returns$_t_uint256_$",
                        "typeString": "function (address,address) view external returns (uint256)"
                      }
                    },
                    "id": 268,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "5561:50:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "5541:70:1"
                },
                {
                  "assignments": [
                    271
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 271,
                      "name": "balance",
                      "nodeType": "VariableDeclaration",
                      "scope": 309,
                      "src": "5621:15:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      },
                      "typeName": {
                        "id": 270,
                        "name": "uint256",
                        "nodeType": "ElementaryTypeName",
                        "src": "5621:7:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 278,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 276,
                        "name": "from",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 223,
                        "src": "5669:4:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      ],
                      "expression": {
                        "argumentTypes": null,
                        "arguments": [
                          {
                            "argumentTypes": null,
                            "id": 273,
                            "name": "tokenAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 227,
                            "src": "5645:12:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          }
                        ],
                        "expression": {
                          "argumentTypes": [
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          ],
                          "id": 272,
                          "name": "ERC20",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 1152,
                          "src": "5639:5:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_type$_t_contract$_ERC20_$1152_$",
                            "typeString": "type(contract ERC20)"
                          }
                        },
                        "id": 274,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "kind": "typeConversion",
                        "lValueRequested": false,
                        "names": [],
                        "nodeType": "FunctionCall",
                        "src": "5639:19:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_contract$_ERC20_$1152",
                          "typeString": "contract ERC20"
                        }
                      },
                      "id": 275,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": false,
                      "lValueRequested": false,
                      "memberName": "balanceOf",
                      "nodeType": "MemberAccess",
                      "referencedDeclaration": 810,
                      "src": "5639:29:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_external_view$_t_address_$returns$_t_uint256_$",
                        "typeString": "function (address) view external returns (uint256)"
                      }
                    },
                    "id": 277,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "5639:35:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "5621:53:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "components": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        "id": 306,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          },
                          "id": 299,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "commonType": {
                              "typeIdentifier": "t_bool",
                              "typeString": "bool"
                            },
                            "id": 292,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": false,
                            "lValueRequested": false,
                            "leftExpression": {
                              "argumentTypes": null,
                              "commonType": {
                                "typeIdentifier": "t_bool",
                                "typeString": "bool"
                              },
                              "id": 285,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": false,
                              "lValueRequested": false,
                              "leftExpression": {
                                "argumentTypes": null,
                                "commonType": {
                                  "typeIdentifier": "t_address",
                                  "typeString": "address"
                                },
                                "id": 281,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": false,
                                "lValueRequested": false,
                                "leftExpression": {
                                  "argumentTypes": null,
                                  "id": 279,
                                  "name": "signer",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 252,
                                  "src": "5705:6:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_address",
                                    "typeString": "address"
                                  }
                                },
                                "nodeType": "BinaryOperation",
                                "operator": "==",
                                "rightExpression": {
                                  "argumentTypes": null,
                                  "id": 280,
                                  "name": "from",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 223,
                                  "src": "5715:4:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_address",
                                    "typeString": "address"
                                  }
                                },
                                "src": "5705:14:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_bool",
                                  "typeString": "bool"
                                }
                              },
                              "nodeType": "BinaryOperation",
                              "operator": "&&",
                              "rightExpression": {
                                "argumentTypes": null,
                                "commonType": {
                                  "typeIdentifier": "t_address",
                                  "typeString": "address"
                                },
                                "id": 284,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": false,
                                "lValueRequested": false,
                                "leftExpression": {
                                  "argumentTypes": null,
                                  "id": 282,
                                  "name": "from",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 223,
                                  "src": "5735:4:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_address",
                                    "typeString": "address"
                                  }
                                },
                                "nodeType": "BinaryOperation",
                                "operator": "!=",
                                "rightExpression": {
                                  "argumentTypes": null,
                                  "id": 283,
                                  "name": "to",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 225,
                                  "src": "5743:2:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_address",
                                    "typeString": "address"
                                  }
                                },
                                "src": "5735:10:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_bool",
                                  "typeString": "bool"
                                }
                              },
                              "src": "5705:40:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_bool",
                                "typeString": "bool"
                              }
                            },
                            "nodeType": "BinaryOperation",
                            "operator": "&&",
                            "rightExpression": {
                              "argumentTypes": null,
                              "commonType": {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256"
                              },
                              "id": 291,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": false,
                              "lValueRequested": false,
                              "leftExpression": {
                                "argumentTypes": null,
                                "expression": {
                                  "argumentTypes": null,
                                  "id": 286,
                                  "name": "block",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 1226,
                                  "src": "5761:5:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_magic_block",
                                    "typeString": "block"
                                  }
                                },
                                "id": 287,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": false,
                                "lValueRequested": false,
                                "memberName": "timestamp",
                                "nodeType": "MemberAccess",
                                "referencedDeclaration": null,
                                "src": "5761:15:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_uint256",
                                  "typeString": "uint256"
                                }
                              },
                              "nodeType": "BinaryOperation",
                              "operator": ">=",
                              "rightExpression": {
                                "argumentTypes": null,
                                "baseExpression": {
                                  "argumentTypes": null,
                                  "id": 288,
                                  "name": "nextValidTimestamp",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 144,
                                  "src": "5780:18:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_mapping$_t_bytes32_$_t_uint256_$",
                                    "typeString": "mapping(bytes32 => uint256)"
                                  }
                                },
                                "id": 290,
                                "indexExpression": {
                                  "argumentTypes": null,
                                  "id": 289,
                                  "name": "subscriptionHash",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 241,
                                  "src": "5799:16:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_bytes32",
                                    "typeString": "bytes32"
                                  }
                                },
                                "isConstant": false,
                                "isLValue": true,
                                "isPure": false,
                                "lValueRequested": false,
                                "nodeType": "IndexAccess",
                                "src": "5780:36:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_uint256",
                                  "typeString": "uint256"
                                }
                              },
                              "src": "5761:55:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_bool",
                                "typeString": "bool"
                              }
                            },
                            "src": "5705:111:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_bool",
                              "typeString": "bool"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "&&",
                          "rightExpression": {
                            "argumentTypes": null,
                            "commonType": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            },
                            "id": 298,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": false,
                            "lValueRequested": false,
                            "leftExpression": {
                              "argumentTypes": null,
                              "id": 293,
                              "name": "allowance",
                              "nodeType": "Identifier",
                              "overloadedDeclarations": [],
                              "referencedDeclaration": 259,
                              "src": "5832:9:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256"
                              }
                            },
                            "nodeType": "BinaryOperation",
                            "operator": ">=",
                            "rightExpression": {
                              "argumentTypes": null,
                              "arguments": [
                                {
                                  "argumentTypes": null,
                                  "id": 296,
                                  "name": "gasPrice",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 233,
                                  "src": "5861:8:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_uint256",
                                    "typeString": "uint256"
                                  }
                                }
                              ],
                              "expression": {
                                "argumentTypes": [
                                  {
                                    "typeIdentifier": "t_uint256",
                                    "typeString": "uint256"
                                  }
                                ],
                                "expression": {
                                  "argumentTypes": null,
                                  "id": 294,
                                  "name": "tokenAmount",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 229,
                                  "src": "5845:11:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_uint256",
                                    "typeString": "uint256"
                                  }
                                },
                                "id": 295,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": false,
                                "lValueRequested": false,
                                "memberName": "add",
                                "nodeType": "MemberAccess",
                                "referencedDeclaration": 748,
                                "src": "5845:15:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_function_internal_pure$_t_uint256_$_t_uint256_$returns$_t_uint256_$bound_to$_t_uint256_$",
                                  "typeString": "function (uint256,uint256) pure returns (uint256)"
                                }
                              },
                              "id": 297,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": false,
                              "kind": "functionCall",
                              "lValueRequested": false,
                              "names": [],
                              "nodeType": "FunctionCall",
                              "src": "5845:25:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256"
                              }
                            },
                            "src": "5832:38:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_bool",
                              "typeString": "bool"
                            }
                          },
                          "src": "5705:165:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "&&",
                        "rightExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          },
                          "id": 305,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 300,
                            "name": "balance",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 271,
                            "src": "5886:7:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": ">=",
                          "rightExpression": {
                            "argumentTypes": null,
                            "arguments": [
                              {
                                "argumentTypes": null,
                                "id": 303,
                                "name": "gasPrice",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 233,
                                "src": "5913:8:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_uint256",
                                  "typeString": "uint256"
                                }
                              }
                            ],
                            "expression": {
                              "argumentTypes": [
                                {
                                  "typeIdentifier": "t_uint256",
                                  "typeString": "uint256"
                                }
                              ],
                              "expression": {
                                "argumentTypes": null,
                                "id": 301,
                                "name": "tokenAmount",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 229,
                                "src": "5897:11:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_uint256",
                                  "typeString": "uint256"
                                }
                              },
                              "id": 302,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": false,
                              "lValueRequested": false,
                              "memberName": "add",
                              "nodeType": "MemberAccess",
                              "referencedDeclaration": 748,
                              "src": "5897:15:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_function_internal_pure$_t_uint256_$_t_uint256_$returns$_t_uint256_$bound_to$_t_uint256_$",
                                "typeString": "function (uint256,uint256) pure returns (uint256)"
                              }
                            },
                            "id": 304,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": false,
                            "kind": "functionCall",
                            "lValueRequested": false,
                            "names": [],
                            "nodeType": "FunctionCall",
                            "src": "5897:25:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "src": "5886:36:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "src": "5705:217:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      }
                    ],
                    "id": 307,
                    "isConstant": false,
                    "isInlineArray": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "nodeType": "TupleExpression",
                    "src": "5691:241:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    }
                  },
                  "functionReturnParameters": 239,
                  "id": 308,
                  "nodeType": "Return",
                  "src": "5684:248:1"
                }
              ]
            },
            "documentation": null,
            "id": 310,
            "implemented": true,
            "kind": "function",
            "modifiers": [],
            "name": "isSubscriptionReady",
            "nodeType": "FunctionDefinition",
            "parameters": {
              "id": 236,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 223,
                  "name": "from",
                  "nodeType": "VariableDeclaration",
                  "scope": 310,
                  "src": "4806:12:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 222,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "4806:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 225,
                  "name": "to",
                  "nodeType": "VariableDeclaration",
                  "scope": 310,
                  "src": "4845:10:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 224,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "4845:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 227,
                  "name": "tokenAddress",
                  "nodeType": "VariableDeclaration",
                  "scope": 310,
                  "src": "4881:20:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 226,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "4881:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 229,
                  "name": "tokenAmount",
                  "nodeType": "VariableDeclaration",
                  "scope": 310,
                  "src": "4953:19:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 228,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "4953:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 231,
                  "name": "periodSeconds",
                  "nodeType": "VariableDeclaration",
                  "scope": 310,
                  "src": "5023:21:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 230,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "5023:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 233,
                  "name": "gasPrice",
                  "nodeType": "VariableDeclaration",
                  "scope": 310,
                  "src": "5095:16:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 232,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "5095:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 235,
                  "name": "signature",
                  "nodeType": "VariableDeclaration",
                  "scope": 310,
                  "src": "5180:22:1",
                  "stateVariable": false,
                  "storageLocation": "memory",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bytes_memory_ptr",
                    "typeString": "bytes"
                  },
                  "typeName": {
                    "id": 234,
                    "name": "bytes",
                    "nodeType": "ElementaryTypeName",
                    "src": "5180:5:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes_storage_ptr",
                      "typeString": "bytes"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "4796:462:1"
            },
            "returnParameters": {
              "id": 239,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 238,
                  "name": "",
                  "nodeType": "VariableDeclaration",
                  "scope": 310,
                  "src": "5304:4:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bool",
                    "typeString": "bool"
                  },
                  "typeName": {
                    "id": 237,
                    "name": "bool",
                    "nodeType": "ElementaryTypeName",
                    "src": "5304:4:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "5303:6:1"
            },
            "scope": 560,
            "src": "4768:1171:1",
            "stateMutability": "view",
            "superFunction": null,
            "visibility": "public"
          },
          {
            "body": {
              "id": 367,
              "nodeType": "Block",
              "src": "6732:566:1",
              "statements": [
                {
                  "assignments": [
                    330
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 330,
                      "name": "subscriptionHash",
                      "nodeType": "VariableDeclaration",
                      "scope": 367,
                      "src": "6742:24:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_bytes32",
                        "typeString": "bytes32"
                      },
                      "typeName": {
                        "id": 329,
                        "name": "bytes32",
                        "nodeType": "ElementaryTypeName",
                        "src": "6742:7:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 339,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 332,
                        "name": "from",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 312,
                        "src": "6802:4:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 333,
                        "name": "to",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 314,
                        "src": "6808:2:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 334,
                        "name": "tokenAddress",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 316,
                        "src": "6812:12:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 335,
                        "name": "tokenAmount",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 318,
                        "src": "6826:11:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 336,
                        "name": "periodSeconds",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 320,
                        "src": "6839:13:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 337,
                        "name": "gasPrice",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 322,
                        "src": "6854:8:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      ],
                      "id": 331,
                      "name": "getSubscriptionHash",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 204,
                      "src": "6769:19:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_internal_view$_t_address_$_t_address_$_t_address_$_t_uint256_$_t_uint256_$_t_uint256_$returns$_t_bytes32_$",
                        "typeString": "function (address,address,address,uint256,uint256,uint256) view returns (bytes32)"
                      }
                    },
                    "id": 338,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "6769:103:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes32",
                      "typeString": "bytes32"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "6742:130:1"
                },
                {
                  "assignments": [
                    341
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 341,
                      "name": "signer",
                      "nodeType": "VariableDeclaration",
                      "scope": 367,
                      "src": "6882:14:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      },
                      "typeName": {
                        "id": 340,
                        "name": "address",
                        "nodeType": "ElementaryTypeName",
                        "src": "6882:7:1",
                        "stateMutability": "nonpayable",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 348,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 346,
                        "name": "signature",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 324,
                        "src": "6949:9:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      ],
                      "expression": {
                        "argumentTypes": null,
                        "arguments": [],
                        "expression": {
                          "argumentTypes": [],
                          "expression": {
                            "argumentTypes": null,
                            "id": 342,
                            "name": "subscriptionHash",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 330,
                            "src": "6899:16:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_bytes32",
                              "typeString": "bytes32"
                            }
                          },
                          "id": 343,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "memberName": "toEthSignedMessageHash",
                          "nodeType": "MemberAccess",
                          "referencedDeclaration": 640,
                          "src": "6899:39:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_function_internal_pure$_t_bytes32_$returns$_t_bytes32_$bound_to$_t_bytes32_$",
                            "typeString": "function (bytes32) pure returns (bytes32)"
                          }
                        },
                        "id": 344,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "kind": "functionCall",
                        "lValueRequested": false,
                        "names": [],
                        "nodeType": "FunctionCall",
                        "src": "6899:41:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      "id": 345,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": false,
                      "lValueRequested": false,
                      "memberName": "recover",
                      "nodeType": "MemberAccess",
                      "referencedDeclaration": 624,
                      "src": "6899:49:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_internal_pure$_t_bytes32_$_t_bytes_memory_ptr_$returns$_t_address_$bound_to$_t_bytes32_$",
                        "typeString": "function (bytes32,bytes memory) pure returns (address)"
                      }
                    },
                    "id": 347,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "6899:60:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "6882:77:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        "id": 352,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "id": 350,
                          "name": "signer",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 341,
                          "src": "7016:6:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "==",
                        "rightExpression": {
                          "argumentTypes": null,
                          "id": 351,
                          "name": "from",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 312,
                          "src": "7026:4:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          }
                        },
                        "src": "7016:14:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "hexValue": "496e76616c6964205369676e617475726520666f7220737562736372697074696f6e2063616e63656c6c6174696f6e",
                        "id": 353,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": true,
                        "kind": "string",
                        "lValueRequested": false,
                        "nodeType": "Literal",
                        "src": "7032:49:1",
                        "subdenomination": null,
                        "typeDescriptions": {
                          "typeIdentifier": "t_stringliteral_20f3baa67ddd296dfb8b9e0ec971696cfd8630a4bebb38617aeef0cee76fac0b",
                          "typeString": "literal_string \"Invalid Signature for subscription cancellation\""
                        },
                        "value": "Invalid Signature for subscription cancellation"
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        {
                          "typeIdentifier": "t_stringliteral_20f3baa67ddd296dfb8b9e0ec971696cfd8630a4bebb38617aeef0cee76fac0b",
                          "typeString": "literal_string \"Invalid Signature for subscription cancellation\""
                        }
                      ],
                      "id": 349,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1240,
                      "src": "7008:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$_t_string_memory_ptr_$returns$__$",
                        "typeString": "function (bool,string memory) pure"
                      }
                    },
                    "id": 354,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "7008:74:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 355,
                  "nodeType": "ExpressionStatement",
                  "src": "7008:74:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 363,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "baseExpression": {
                        "argumentTypes": null,
                        "id": 356,
                        "name": "nextValidTimestamp",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 144,
                        "src": "7221:18:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_mapping$_t_bytes32_$_t_uint256_$",
                          "typeString": "mapping(bytes32 => uint256)"
                        }
                      },
                      "id": 358,
                      "indexExpression": {
                        "argumentTypes": null,
                        "id": 357,
                        "name": "subscriptionHash",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 330,
                        "src": "7240:16:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      "isConstant": false,
                      "isLValue": true,
                      "isPure": false,
                      "lValueRequested": true,
                      "nodeType": "IndexAccess",
                      "src": "7221:36:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "arguments": [
                        {
                          "argumentTypes": null,
                          "id": 361,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": true,
                          "lValueRequested": false,
                          "nodeType": "UnaryOperation",
                          "operator": "-",
                          "prefix": true,
                          "src": "7266:2:1",
                          "subExpression": {
                            "argumentTypes": null,
                            "hexValue": "31",
                            "id": 360,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": true,
                            "kind": "number",
                            "lValueRequested": false,
                            "nodeType": "Literal",
                            "src": "7267:1:1",
                            "subdenomination": null,
                            "typeDescriptions": {
                              "typeIdentifier": "t_rational_1_by_1",
                              "typeString": "int_const 1"
                            },
                            "value": "1"
                          },
                          "typeDescriptions": {
                            "typeIdentifier": "t_rational_minus_1_by_1",
                            "typeString": "int_const -1"
                          }
                        }
                      ],
                      "expression": {
                        "argumentTypes": [
                          {
                            "typeIdentifier": "t_rational_minus_1_by_1",
                            "typeString": "int_const -1"
                          }
                        ],
                        "id": 359,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": true,
                        "lValueRequested": false,
                        "nodeType": "ElementaryTypeNameExpression",
                        "src": "7258:7:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_type$_t_uint256_$",
                          "typeString": "type(uint256)"
                        },
                        "typeName": "uint256"
                      },
                      "id": 362,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": true,
                      "kind": "typeConversion",
                      "lValueRequested": false,
                      "names": [],
                      "nodeType": "FunctionCall",
                      "src": "7258:11:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "src": "7221:48:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "id": 364,
                  "nodeType": "ExpressionStatement",
                  "src": "7221:48:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "hexValue": "74727565",
                    "id": 365,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": true,
                    "kind": "bool",
                    "lValueRequested": false,
                    "nodeType": "Literal",
                    "src": "7287:4:1",
                    "subdenomination": null,
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    },
                    "value": "true"
                  },
                  "functionReturnParameters": 328,
                  "id": 366,
                  "nodeType": "Return",
                  "src": "7280:11:1"
                }
              ]
            },
            "documentation": null,
            "id": 368,
            "implemented": true,
            "kind": "function",
            "modifiers": [],
            "name": "cancelSubscription",
            "nodeType": "FunctionDefinition",
            "parameters": {
              "id": 325,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 312,
                  "name": "from",
                  "nodeType": "VariableDeclaration",
                  "scope": 368,
                  "src": "6230:12:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 311,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "6230:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 314,
                  "name": "to",
                  "nodeType": "VariableDeclaration",
                  "scope": 368,
                  "src": "6269:10:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 313,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "6269:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 316,
                  "name": "tokenAddress",
                  "nodeType": "VariableDeclaration",
                  "scope": 368,
                  "src": "6305:20:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 315,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "6305:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 318,
                  "name": "tokenAmount",
                  "nodeType": "VariableDeclaration",
                  "scope": 368,
                  "src": "6377:19:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 317,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "6377:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 320,
                  "name": "periodSeconds",
                  "nodeType": "VariableDeclaration",
                  "scope": 368,
                  "src": "6447:21:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 319,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "6447:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 322,
                  "name": "gasPrice",
                  "nodeType": "VariableDeclaration",
                  "scope": 368,
                  "src": "6519:16:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 321,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "6519:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 324,
                  "name": "signature",
                  "nodeType": "VariableDeclaration",
                  "scope": 368,
                  "src": "6603:22:1",
                  "stateVariable": false,
                  "storageLocation": "memory",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bytes_memory_ptr",
                    "typeString": "bytes"
                  },
                  "typeName": {
                    "id": 323,
                    "name": "bytes",
                    "nodeType": "ElementaryTypeName",
                    "src": "6603:5:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes_storage_ptr",
                      "typeString": "bytes"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "6220:461:1"
            },
            "returnParameters": {
              "id": 328,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 327,
                  "name": "success",
                  "nodeType": "VariableDeclaration",
                  "scope": 368,
                  "src": "6714:12:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bool",
                    "typeString": "bool"
                  },
                  "typeName": {
                    "id": 326,
                    "name": "bool",
                    "nodeType": "ElementaryTypeName",
                    "src": "6714:4:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "6713:14:1"
            },
            "scope": 560,
            "src": "6193:1105:1",
            "stateMutability": "nonpayable",
            "superFunction": null,
            "visibility": "public"
          },
          {
            "body": {
              "id": 558,
              "nodeType": "Block",
              "src": "7996:2924:1",
              "statements": [
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        "id": 391,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "expression": {
                            "argumentTypes": null,
                            "id": 388,
                            "name": "msg",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 1236,
                            "src": "8014:3:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_magic_message",
                              "typeString": "msg"
                            }
                          },
                          "id": 389,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "memberName": "sender",
                          "nodeType": "MemberAccess",
                          "referencedDeclaration": null,
                          "src": "8014:10:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_address_payable",
                            "typeString": "address payable"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "==",
                        "rightExpression": {
                          "argumentTypes": null,
                          "id": 390,
                          "name": "relayer",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 71,
                          "src": "8028:7:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          }
                        },
                        "src": "8014:21:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      ],
                      "id": 387,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1239,
                      "src": "8006:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$returns$__$",
                        "typeString": "function (bool) pure"
                      }
                    },
                    "id": 392,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "8006:30:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 393,
                  "nodeType": "ExpressionStatement",
                  "src": "8006:30:1"
                },
                {
                  "assignments": [
                    395
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 395,
                      "name": "subscriptionHash",
                      "nodeType": "VariableDeclaration",
                      "scope": 558,
                      "src": "8196:24:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_bytes32",
                        "typeString": "bytes32"
                      },
                      "typeName": {
                        "id": 394,
                        "name": "bytes32",
                        "nodeType": "ElementaryTypeName",
                        "src": "8196:7:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 404,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 397,
                        "name": "from",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 370,
                        "src": "8256:4:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 398,
                        "name": "to",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 372,
                        "src": "8262:2:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 399,
                        "name": "tokenAddress",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 374,
                        "src": "8266:12:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 400,
                        "name": "tokenAmount",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 376,
                        "src": "8280:11:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 401,
                        "name": "periodSeconds",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 378,
                        "src": "8293:13:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 402,
                        "name": "gasPrice",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 380,
                        "src": "8308:8:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      ],
                      "id": 396,
                      "name": "getSubscriptionHash",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 204,
                      "src": "8223:19:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_internal_view$_t_address_$_t_address_$_t_address_$_t_uint256_$_t_uint256_$_t_uint256_$returns$_t_bytes32_$",
                        "typeString": "function (address,address,address,uint256,uint256,uint256) view returns (bytes32)"
                      }
                    },
                    "id": 403,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "8223:103:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes32",
                      "typeString": "bytes32"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "8196:130:1"
                },
                {
                  "assignments": [
                    406
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 406,
                      "name": "signer",
                      "nodeType": "VariableDeclaration",
                      "scope": 558,
                      "src": "8336:14:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_address",
                        "typeString": "address"
                      },
                      "typeName": {
                        "id": 405,
                        "name": "address",
                        "nodeType": "ElementaryTypeName",
                        "src": "8336:7:1",
                        "stateMutability": "nonpayable",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 411,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 408,
                        "name": "subscriptionHash",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 395,
                        "src": "8375:16:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 409,
                        "name": "signature",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 382,
                        "src": "8393:9:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        },
                        {
                          "typeIdentifier": "t_bytes_memory_ptr",
                          "typeString": "bytes memory"
                        }
                      ],
                      "id": 407,
                      "name": "getSubscriptionSigner",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 221,
                      "src": "8353:21:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_internal_pure$_t_bytes32_$_t_bytes_memory_ptr_$returns$_t_address_$",
                        "typeString": "function (bytes32,bytes memory) pure returns (address)"
                      }
                    },
                    "id": 410,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "8353:50:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "8336:67:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        "id": 415,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "id": 413,
                          "name": "signer",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 406,
                          "src": "8460:6:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "==",
                        "rightExpression": {
                          "argumentTypes": null,
                          "id": 414,
                          "name": "from",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 370,
                          "src": "8470:4:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          }
                        },
                        "src": "8460:14:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "hexValue": "496e76616c6964205369676e6174757265",
                        "id": 416,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": true,
                        "kind": "string",
                        "lValueRequested": false,
                        "nodeType": "Literal",
                        "src": "8476:19:1",
                        "subdenomination": null,
                        "typeDescriptions": {
                          "typeIdentifier": "t_stringliteral_98abf41928333e3fb96f450e411f323711f90894815c0b92e5e7c34ae876605a",
                          "typeString": "literal_string \"Invalid Signature\""
                        },
                        "value": "Invalid Signature"
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        {
                          "typeIdentifier": "t_stringliteral_98abf41928333e3fb96f450e411f323711f90894815c0b92e5e7c34ae876605a",
                          "typeString": "literal_string \"Invalid Signature\""
                        }
                      ],
                      "id": 412,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1240,
                      "src": "8452:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$_t_string_memory_ptr_$returns$__$",
                        "typeString": "function (bool,string memory) pure"
                      }
                    },
                    "id": 417,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "8452:44:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 418,
                  "nodeType": "ExpressionStatement",
                  "src": "8452:44:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        "id": 425,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "expression": {
                            "argumentTypes": null,
                            "id": 420,
                            "name": "block",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 1226,
                            "src": "8588:5:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_magic_block",
                              "typeString": "block"
                            }
                          },
                          "id": 421,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "memberName": "timestamp",
                          "nodeType": "MemberAccess",
                          "referencedDeclaration": null,
                          "src": "8588:15:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": ">=",
                        "rightExpression": {
                          "argumentTypes": null,
                          "baseExpression": {
                            "argumentTypes": null,
                            "id": 422,
                            "name": "nextValidTimestamp",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 144,
                            "src": "8607:18:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_mapping$_t_bytes32_$_t_uint256_$",
                              "typeString": "mapping(bytes32 => uint256)"
                            }
                          },
                          "id": 424,
                          "indexExpression": {
                            "argumentTypes": null,
                            "id": 423,
                            "name": "subscriptionHash",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 395,
                            "src": "8626:16:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_bytes32",
                              "typeString": "bytes32"
                            }
                          },
                          "isConstant": false,
                          "isLValue": true,
                          "isPure": false,
                          "lValueRequested": false,
                          "nodeType": "IndexAccess",
                          "src": "8607:36:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        },
                        "src": "8588:55:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "hexValue": "537562736372697074696f6e206973206e6f74207265616479",
                        "id": 426,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": true,
                        "kind": "string",
                        "lValueRequested": false,
                        "nodeType": "Literal",
                        "src": "8657:27:1",
                        "subdenomination": null,
                        "typeDescriptions": {
                          "typeIdentifier": "t_stringliteral_06451f6f57a39e3bee27389eef645fbe7a0fd302c8667e4917572d784cd6c690",
                          "typeString": "literal_string \"Subscription is not ready\""
                        },
                        "value": "Subscription is not ready"
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        {
                          "typeIdentifier": "t_stringliteral_06451f6f57a39e3bee27389eef645fbe7a0fd302c8667e4917572d784cd6c690",
                          "typeString": "literal_string \"Subscription is not ready\""
                        }
                      ],
                      "id": 419,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1240,
                      "src": "8567:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$_t_string_memory_ptr_$returns$__$",
                        "typeString": "function (bool,string memory) pure"
                      }
                    },
                    "id": 427,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "8567:127:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 428,
                  "nodeType": "ExpressionStatement",
                  "src": "8567:127:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        "id": 438,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          },
                          "id": 434,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 430,
                            "name": "requiredToAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 73,
                            "src": "8819:17:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "arguments": [
                              {
                                "argumentTypes": null,
                                "hexValue": "30",
                                "id": 432,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": true,
                                "kind": "number",
                                "lValueRequested": false,
                                "nodeType": "Literal",
                                "src": "8848:1:1",
                                "subdenomination": null,
                                "typeDescriptions": {
                                  "typeIdentifier": "t_rational_0_by_1",
                                  "typeString": "int_const 0"
                                },
                                "value": "0"
                              }
                            ],
                            "expression": {
                              "argumentTypes": [
                                {
                                  "typeIdentifier": "t_rational_0_by_1",
                                  "typeString": "int_const 0"
                                }
                              ],
                              "id": 431,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": true,
                              "lValueRequested": false,
                              "nodeType": "ElementaryTypeNameExpression",
                              "src": "8840:7:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_type$_t_address_$",
                                "typeString": "type(address)"
                              },
                              "typeName": "address"
                            },
                            "id": 433,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": true,
                            "kind": "typeConversion",
                            "lValueRequested": false,
                            "names": [],
                            "nodeType": "FunctionCall",
                            "src": "8840:10:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address_payable",
                              "typeString": "address payable"
                            }
                          },
                          "src": "8819:31:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "||",
                        "rightExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          },
                          "id": 437,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 435,
                            "name": "to",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 372,
                            "src": "8854:2:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "id": 436,
                            "name": "requiredToAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 73,
                            "src": "8860:17:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          "src": "8854:23:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "src": "8819:58:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      ],
                      "id": 429,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1239,
                      "src": "8810:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$returns$__$",
                        "typeString": "function (bool) pure"
                      }
                    },
                    "id": 439,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "8810:69:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 440,
                  "nodeType": "ExpressionStatement",
                  "src": "8810:69:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        "id": 450,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          },
                          "id": 446,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 442,
                            "name": "requiredTokenAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 75,
                            "src": "8898:20:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "arguments": [
                              {
                                "argumentTypes": null,
                                "hexValue": "30",
                                "id": 444,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": true,
                                "kind": "number",
                                "lValueRequested": false,
                                "nodeType": "Literal",
                                "src": "8930:1:1",
                                "subdenomination": null,
                                "typeDescriptions": {
                                  "typeIdentifier": "t_rational_0_by_1",
                                  "typeString": "int_const 0"
                                },
                                "value": "0"
                              }
                            ],
                            "expression": {
                              "argumentTypes": [
                                {
                                  "typeIdentifier": "t_rational_0_by_1",
                                  "typeString": "int_const 0"
                                }
                              ],
                              "id": 443,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": true,
                              "lValueRequested": false,
                              "nodeType": "ElementaryTypeNameExpression",
                              "src": "8922:7:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_type$_t_address_$",
                                "typeString": "type(address)"
                              },
                              "typeName": "address"
                            },
                            "id": 445,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": true,
                            "kind": "typeConversion",
                            "lValueRequested": false,
                            "names": [],
                            "nodeType": "FunctionCall",
                            "src": "8922:10:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address_payable",
                              "typeString": "address payable"
                            }
                          },
                          "src": "8898:34:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "||",
                        "rightExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_address",
                            "typeString": "address"
                          },
                          "id": 449,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 447,
                            "name": "tokenAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 374,
                            "src": "8936:12:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "id": 448,
                            "name": "requiredTokenAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 75,
                            "src": "8952:20:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          "src": "8936:36:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "src": "8898:74:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      ],
                      "id": 441,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1239,
                      "src": "8889:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$returns$__$",
                        "typeString": "function (bool) pure"
                      }
                    },
                    "id": 451,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "8889:85:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 452,
                  "nodeType": "ExpressionStatement",
                  "src": "8889:85:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        "id": 460,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          },
                          "id": 456,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 454,
                            "name": "requiredTokenAmount",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 77,
                            "src": "8993:19:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "hexValue": "30",
                            "id": 455,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": true,
                            "kind": "number",
                            "lValueRequested": false,
                            "nodeType": "Literal",
                            "src": "9016:1:1",
                            "subdenomination": null,
                            "typeDescriptions": {
                              "typeIdentifier": "t_rational_0_by_1",
                              "typeString": "int_const 0"
                            },
                            "value": "0"
                          },
                          "src": "8993:24:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "||",
                        "rightExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          },
                          "id": 459,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 457,
                            "name": "tokenAmount",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 376,
                            "src": "9021:11:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "id": 458,
                            "name": "requiredTokenAmount",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 77,
                            "src": "9036:19:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "src": "9021:34:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "src": "8993:62:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      ],
                      "id": 453,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1239,
                      "src": "8984:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$returns$__$",
                        "typeString": "function (bool) pure"
                      }
                    },
                    "id": 461,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "8984:73:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 462,
                  "nodeType": "ExpressionStatement",
                  "src": "8984:73:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        "id": 470,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          },
                          "id": 466,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 464,
                            "name": "requiredPeriodSeconds",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 79,
                            "src": "9076:21:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "hexValue": "30",
                            "id": 465,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": true,
                            "kind": "number",
                            "lValueRequested": false,
                            "nodeType": "Literal",
                            "src": "9101:1:1",
                            "subdenomination": null,
                            "typeDescriptions": {
                              "typeIdentifier": "t_rational_0_by_1",
                              "typeString": "int_const 0"
                            },
                            "value": "0"
                          },
                          "src": "9076:26:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "||",
                        "rightExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          },
                          "id": 469,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 467,
                            "name": "periodSeconds",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 378,
                            "src": "9106:13:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "id": 468,
                            "name": "requiredPeriodSeconds",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 79,
                            "src": "9123:21:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "src": "9106:38:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "src": "9076:68:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      ],
                      "id": 463,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1239,
                      "src": "9067:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$returns$__$",
                        "typeString": "function (bool) pure"
                      }
                    },
                    "id": 471,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "9067:79:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 472,
                  "nodeType": "ExpressionStatement",
                  "src": "9067:79:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        "id": 480,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          },
                          "id": 476,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 474,
                            "name": "requiredGasPrice",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 81,
                            "src": "9165:16:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "hexValue": "30",
                            "id": 475,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": true,
                            "kind": "number",
                            "lValueRequested": false,
                            "nodeType": "Literal",
                            "src": "9185:1:1",
                            "subdenomination": null,
                            "typeDescriptions": {
                              "typeIdentifier": "t_rational_0_by_1",
                              "typeString": "int_const 0"
                            },
                            "value": "0"
                          },
                          "src": "9165:21:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "||",
                        "rightExpression": {
                          "argumentTypes": null,
                          "commonType": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          },
                          "id": 479,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "leftExpression": {
                            "argumentTypes": null,
                            "id": 477,
                            "name": "gasPrice",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 380,
                            "src": "9190:8:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "nodeType": "BinaryOperation",
                          "operator": "==",
                          "rightExpression": {
                            "argumentTypes": null,
                            "id": 478,
                            "name": "requiredGasPrice",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 81,
                            "src": "9202:16:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          },
                          "src": "9190:28:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_bool",
                            "typeString": "bool"
                          }
                        },
                        "src": "9165:53:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      ],
                      "id": 473,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1239,
                      "src": "9156:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$returns$__$",
                        "typeString": "function (bool) pure"
                      }
                    },
                    "id": 481,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "9156:64:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 482,
                  "nodeType": "ExpressionStatement",
                  "src": "9156:64:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "id": 491,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftHandSide": {
                      "argumentTypes": null,
                      "baseExpression": {
                        "argumentTypes": null,
                        "id": 483,
                        "name": "nextValidTimestamp",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 144,
                        "src": "9310:18:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_mapping$_t_bytes32_$_t_uint256_$",
                          "typeString": "mapping(bytes32 => uint256)"
                        }
                      },
                      "id": 485,
                      "indexExpression": {
                        "argumentTypes": null,
                        "id": 484,
                        "name": "subscriptionHash",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 395,
                        "src": "9329:16:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bytes32",
                          "typeString": "bytes32"
                        }
                      },
                      "isConstant": false,
                      "isLValue": true,
                      "isPure": false,
                      "lValueRequested": true,
                      "nodeType": "IndexAccess",
                      "src": "9310:36:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "nodeType": "Assignment",
                    "operator": "=",
                    "rightHandSide": {
                      "argumentTypes": null,
                      "arguments": [
                        {
                          "argumentTypes": null,
                          "id": 489,
                          "name": "periodSeconds",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 378,
                          "src": "9369:13:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        }
                      ],
                      "expression": {
                        "argumentTypes": [
                          {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        ],
                        "expression": {
                          "argumentTypes": null,
                          "expression": {
                            "argumentTypes": null,
                            "id": 486,
                            "name": "block",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 1226,
                            "src": "9349:5:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_magic_block",
                              "typeString": "block"
                            }
                          },
                          "id": 487,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "memberName": "timestamp",
                          "nodeType": "MemberAccess",
                          "referencedDeclaration": null,
                          "src": "9349:15:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        },
                        "id": 488,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "memberName": "add",
                        "nodeType": "MemberAccess",
                        "referencedDeclaration": 748,
                        "src": "9349:19:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_function_internal_pure$_t_uint256_$_t_uint256_$returns$_t_uint256_$bound_to$_t_uint256_$",
                          "typeString": "function (uint256,uint256) pure returns (uint256)"
                        }
                      },
                      "id": 490,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": false,
                      "kind": "functionCall",
                      "lValueRequested": false,
                      "names": [],
                      "nodeType": "FunctionCall",
                      "src": "9349:34:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "src": "9310:73:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "id": 492,
                  "nodeType": "ExpressionStatement",
                  "src": "9310:73:1"
                },
                {
                  "assignments": [
                    494
                  ],
                  "declarations": [
                    {
                      "constant": false,
                      "id": 494,
                      "name": "startingBalance",
                      "nodeType": "VariableDeclaration",
                      "scope": 558,
                      "src": "9469:23:1",
                      "stateVariable": false,
                      "storageLocation": "default",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      },
                      "typeName": {
                        "id": 493,
                        "name": "uint256",
                        "nodeType": "ElementaryTypeName",
                        "src": "9469:7:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      "value": null,
                      "visibility": "internal"
                    }
                  ],
                  "id": 501,
                  "initialValue": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 499,
                        "name": "to",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 372,
                        "src": "9525:2:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      ],
                      "expression": {
                        "argumentTypes": null,
                        "arguments": [
                          {
                            "argumentTypes": null,
                            "id": 496,
                            "name": "tokenAddress",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 374,
                            "src": "9501:12:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          }
                        ],
                        "expression": {
                          "argumentTypes": [
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          ],
                          "id": 495,
                          "name": "ERC20",
                          "nodeType": "Identifier",
                          "overloadedDeclarations": [],
                          "referencedDeclaration": 1152,
                          "src": "9495:5:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_type$_t_contract$_ERC20_$1152_$",
                            "typeString": "type(contract ERC20)"
                          }
                        },
                        "id": 497,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "kind": "typeConversion",
                        "lValueRequested": false,
                        "names": [],
                        "nodeType": "FunctionCall",
                        "src": "9495:19:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_contract$_ERC20_$1152",
                          "typeString": "contract ERC20"
                        }
                      },
                      "id": 498,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": false,
                      "lValueRequested": false,
                      "memberName": "balanceOf",
                      "nodeType": "MemberAccess",
                      "referencedDeclaration": 810,
                      "src": "9495:29:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_external_view$_t_address_$returns$_t_uint256_$",
                        "typeString": "function (address) view external returns (uint256)"
                      }
                    },
                    "id": 500,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "9495:33:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "nodeType": "VariableDeclarationStatement",
                  "src": "9469:59:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "arguments": [
                          {
                            "argumentTypes": null,
                            "id": 507,
                            "name": "from",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 370,
                            "src": "9590:4:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "id": 508,
                            "name": "to",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 372,
                            "src": "9595:2:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            }
                          },
                          {
                            "argumentTypes": null,
                            "id": 509,
                            "name": "tokenAmount",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [],
                            "referencedDeclaration": 376,
                            "src": "9598:11:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          }
                        ],
                        "expression": {
                          "argumentTypes": [
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            },
                            {
                              "typeIdentifier": "t_address",
                              "typeString": "address"
                            },
                            {
                              "typeIdentifier": "t_uint256",
                              "typeString": "uint256"
                            }
                          ],
                          "expression": {
                            "argumentTypes": null,
                            "arguments": [
                              {
                                "argumentTypes": null,
                                "id": 504,
                                "name": "tokenAddress",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 374,
                                "src": "9563:12:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_address",
                                  "typeString": "address"
                                }
                              }
                            ],
                            "expression": {
                              "argumentTypes": [
                                {
                                  "typeIdentifier": "t_address",
                                  "typeString": "address"
                                }
                              ],
                              "id": 503,
                              "name": "ERC20",
                              "nodeType": "Identifier",
                              "overloadedDeclarations": [],
                              "referencedDeclaration": 1152,
                              "src": "9557:5:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_type$_t_contract$_ERC20_$1152_$",
                                "typeString": "type(contract ERC20)"
                              }
                            },
                            "id": 505,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": false,
                            "kind": "typeConversion",
                            "lValueRequested": false,
                            "names": [],
                            "nodeType": "FunctionCall",
                            "src": "9557:19:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_contract$_ERC20_$1152",
                              "typeString": "contract ERC20"
                            }
                          },
                          "id": 506,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "memberName": "transferFrom",
                          "nodeType": "MemberAccess",
                          "referencedDeclaration": 899,
                          "src": "9557:32:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_function_external_nonpayable$_t_address_$_t_address_$_t_uint256_$returns$_t_bool_$",
                            "typeString": "function (address,address,uint256) external returns (bool)"
                          }
                        },
                        "id": 510,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "kind": "functionCall",
                        "lValueRequested": false,
                        "names": [],
                        "nodeType": "FunctionCall",
                        "src": "9557:53:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "hexValue": "5472616e73666572204661696c6564",
                        "id": 511,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": true,
                        "kind": "string",
                        "lValueRequested": false,
                        "nodeType": "Literal",
                        "src": "9622:17:1",
                        "subdenomination": null,
                        "typeDescriptions": {
                          "typeIdentifier": "t_stringliteral_c5acabcb762867cdbcf367c30c495273eabea012d93b81d74177ab1ef966623f",
                          "typeString": "literal_string \"Transfer Failed\""
                        },
                        "value": "Transfer Failed"
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        {
                          "typeIdentifier": "t_stringliteral_c5acabcb762867cdbcf367c30c495273eabea012d93b81d74177ab1ef966623f",
                          "typeString": "literal_string \"Transfer Failed\""
                        }
                      ],
                      "id": 502,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1240,
                      "src": "9538:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$_t_string_memory_ptr_$returns$__$",
                        "typeString": "function (bool,string memory) pure"
                      }
                    },
                    "id": 512,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "9538:111:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 513,
                  "nodeType": "ExpressionStatement",
                  "src": "9538:111:1"
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "commonType": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        "id": 525,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": false,
                        "lValueRequested": false,
                        "leftExpression": {
                          "argumentTypes": null,
                          "components": [
                            {
                              "argumentTypes": null,
                              "commonType": {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256"
                              },
                              "id": 517,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": false,
                              "lValueRequested": false,
                              "leftExpression": {
                                "argumentTypes": null,
                                "id": 515,
                                "name": "startingBalance",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 494,
                                "src": "9679:15:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_uint256",
                                  "typeString": "uint256"
                                }
                              },
                              "nodeType": "BinaryOperation",
                              "operator": "+",
                              "rightExpression": {
                                "argumentTypes": null,
                                "id": 516,
                                "name": "tokenAmount",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 376,
                                "src": "9695:11:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_uint256",
                                  "typeString": "uint256"
                                }
                              },
                              "src": "9679:27:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_uint256",
                                "typeString": "uint256"
                              }
                            }
                          ],
                          "id": 518,
                          "isConstant": false,
                          "isInlineArray": false,
                          "isLValue": false,
                          "isPure": false,
                          "lValueRequested": false,
                          "nodeType": "TupleExpression",
                          "src": "9678:29:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        },
                        "nodeType": "BinaryOperation",
                        "operator": "==",
                        "rightExpression": {
                          "argumentTypes": null,
                          "arguments": [
                            {
                              "argumentTypes": null,
                              "id": 523,
                              "name": "to",
                              "nodeType": "Identifier",
                              "overloadedDeclarations": [],
                              "referencedDeclaration": 372,
                              "src": "9741:2:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_address",
                                "typeString": "address"
                              }
                            }
                          ],
                          "expression": {
                            "argumentTypes": [
                              {
                                "typeIdentifier": "t_address",
                                "typeString": "address"
                              }
                            ],
                            "expression": {
                              "argumentTypes": null,
                              "arguments": [
                                {
                                  "argumentTypes": null,
                                  "id": 520,
                                  "name": "tokenAddress",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 374,
                                  "src": "9717:12:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_address",
                                    "typeString": "address"
                                  }
                                }
                              ],
                              "expression": {
                                "argumentTypes": [
                                  {
                                    "typeIdentifier": "t_address",
                                    "typeString": "address"
                                  }
                                ],
                                "id": 519,
                                "name": "ERC20",
                                "nodeType": "Identifier",
                                "overloadedDeclarations": [],
                                "referencedDeclaration": 1152,
                                "src": "9711:5:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_type$_t_contract$_ERC20_$1152_$",
                                  "typeString": "type(contract ERC20)"
                                }
                              },
                              "id": 521,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": false,
                              "kind": "typeConversion",
                              "lValueRequested": false,
                              "names": [],
                              "nodeType": "FunctionCall",
                              "src": "9711:19:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_contract$_ERC20_$1152",
                                "typeString": "contract ERC20"
                              }
                            },
                            "id": 522,
                            "isConstant": false,
                            "isLValue": false,
                            "isPure": false,
                            "lValueRequested": false,
                            "memberName": "balanceOf",
                            "nodeType": "MemberAccess",
                            "referencedDeclaration": 810,
                            "src": "9711:29:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_function_external_view$_t_address_$returns$_t_uint256_$",
                              "typeString": "function (address) view external returns (uint256)"
                            }
                          },
                          "id": 524,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "kind": "functionCall",
                          "lValueRequested": false,
                          "names": [],
                          "nodeType": "FunctionCall",
                          "src": "9711:33:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_uint256",
                            "typeString": "uint256"
                          }
                        },
                        "src": "9678:66:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "hexValue": "437261707079204552433230206973206120626164206b697474792e",
                        "id": 526,
                        "isConstant": false,
                        "isLValue": false,
                        "isPure": true,
                        "kind": "string",
                        "lValueRequested": false,
                        "nodeType": "Literal",
                        "src": "9756:30:1",
                        "subdenomination": null,
                        "typeDescriptions": {
                          "typeIdentifier": "t_stringliteral_029ffbbaf13c4f3c926d750ec214cf79eff7ac3e72a55ff6f0f5dd1e456a4c5c",
                          "typeString": "literal_string \"Crappy ERC20 is a bad kitty.\""
                        },
                        "value": "Crappy ERC20 is a bad kitty."
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_bool",
                          "typeString": "bool"
                        },
                        {
                          "typeIdentifier": "t_stringliteral_029ffbbaf13c4f3c926d750ec214cf79eff7ac3e72a55ff6f0f5dd1e456a4c5c",
                          "typeString": "literal_string \"Crappy ERC20 is a bad kitty.\""
                        }
                      ],
                      "id": 514,
                      "name": "require",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [
                        1239,
                        1240
                      ],
                      "referencedDeclaration": 1240,
                      "src": "9659:7:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_require_pure$_t_bool_$_t_string_memory_ptr_$returns$__$",
                        "typeString": "function (bool,string memory) pure"
                      }
                    },
                    "id": 527,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "9659:137:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 528,
                  "nodeType": "ExpressionStatement",
                  "src": "9659:137:1"
                },
                {
                  "eventCall": {
                    "argumentTypes": null,
                    "arguments": [
                      {
                        "argumentTypes": null,
                        "id": 530,
                        "name": "from",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 370,
                        "src": "9845:4:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 531,
                        "name": "to",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 372,
                        "src": "9851:2:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 532,
                        "name": "tokenAddress",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 374,
                        "src": "9855:12:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 533,
                        "name": "tokenAmount",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 376,
                        "src": "9869:11:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 534,
                        "name": "periodSeconds",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 378,
                        "src": "9882:13:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      },
                      {
                        "argumentTypes": null,
                        "id": 535,
                        "name": "gasPrice",
                        "nodeType": "Identifier",
                        "overloadedDeclarations": [],
                        "referencedDeclaration": 380,
                        "src": "9897:8:1",
                        "typeDescriptions": {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      }
                    ],
                    "expression": {
                      "argumentTypes": [
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_address",
                          "typeString": "address"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        },
                        {
                          "typeIdentifier": "t_uint256",
                          "typeString": "uint256"
                        }
                      ],
                      "id": 529,
                      "name": "ExecuteSubscription",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 140,
                      "src": "9812:19:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_function_event_nonpayable$_t_address_$_t_address_$_t_address_$_t_uint256_$_t_uint256_$_t_uint256_$returns$__$",
                        "typeString": "function (address,address,address,uint256,uint256,uint256)"
                      }
                    },
                    "id": 536,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "kind": "functionCall",
                    "lValueRequested": false,
                    "names": [],
                    "nodeType": "FunctionCall",
                    "src": "9812:103:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_tuple$__$",
                      "typeString": "tuple()"
                    }
                  },
                  "id": 537,
                  "nodeType": "EmitStatement",
                  "src": "9807:108:1"
                },
                {
                  "condition": {
                    "argumentTypes": null,
                    "commonType": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    },
                    "id": 540,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": false,
                    "lValueRequested": false,
                    "leftExpression": {
                      "argumentTypes": null,
                      "id": 538,
                      "name": "gasPrice",
                      "nodeType": "Identifier",
                      "overloadedDeclarations": [],
                      "referencedDeclaration": 380,
                      "src": "10135:8:1",
                      "typeDescriptions": {
                        "typeIdentifier": "t_uint256",
                        "typeString": "uint256"
                      }
                    },
                    "nodeType": "BinaryOperation",
                    "operator": ">",
                    "rightExpression": {
                      "argumentTypes": null,
                      "hexValue": "30",
                      "id": 539,
                      "isConstant": false,
                      "isLValue": false,
                      "isPure": true,
                      "kind": "number",
                      "lValueRequested": false,
                      "nodeType": "Literal",
                      "src": "10146:1:1",
                      "subdenomination": null,
                      "typeDescriptions": {
                        "typeIdentifier": "t_rational_0_by_1",
                        "typeString": "int_const 0"
                      },
                      "value": "0"
                    },
                    "src": "10135:12:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    }
                  },
                  "falseBody": null,
                  "id": 555,
                  "nodeType": "IfStatement",
                  "src": "10131:761:1",
                  "trueBody": {
                    "id": 554,
                    "nodeType": "Block",
                    "src": "10149:743:1",
                    "statements": [
                      {
                        "expression": {
                          "argumentTypes": null,
                          "arguments": [
                            {
                              "argumentTypes": null,
                              "arguments": [
                                {
                                  "argumentTypes": null,
                                  "id": 546,
                                  "name": "from",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 370,
                                  "src": "10787:4:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_address",
                                    "typeString": "address"
                                  }
                                },
                                {
                                  "argumentTypes": null,
                                  "expression": {
                                    "argumentTypes": null,
                                    "id": 547,
                                    "name": "msg",
                                    "nodeType": "Identifier",
                                    "overloadedDeclarations": [],
                                    "referencedDeclaration": 1236,
                                    "src": "10793:3:1",
                                    "typeDescriptions": {
                                      "typeIdentifier": "t_magic_message",
                                      "typeString": "msg"
                                    }
                                  },
                                  "id": 548,
                                  "isConstant": false,
                                  "isLValue": false,
                                  "isPure": false,
                                  "lValueRequested": false,
                                  "memberName": "sender",
                                  "nodeType": "MemberAccess",
                                  "referencedDeclaration": null,
                                  "src": "10793:10:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_address_payable",
                                    "typeString": "address payable"
                                  }
                                },
                                {
                                  "argumentTypes": null,
                                  "id": 549,
                                  "name": "gasPrice",
                                  "nodeType": "Identifier",
                                  "overloadedDeclarations": [],
                                  "referencedDeclaration": 380,
                                  "src": "10805:8:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_uint256",
                                    "typeString": "uint256"
                                  }
                                }
                              ],
                              "expression": {
                                "argumentTypes": [
                                  {
                                    "typeIdentifier": "t_address",
                                    "typeString": "address"
                                  },
                                  {
                                    "typeIdentifier": "t_address_payable",
                                    "typeString": "address payable"
                                  },
                                  {
                                    "typeIdentifier": "t_uint256",
                                    "typeString": "uint256"
                                  }
                                ],
                                "expression": {
                                  "argumentTypes": null,
                                  "arguments": [
                                    {
                                      "argumentTypes": null,
                                      "id": 543,
                                      "name": "tokenAddress",
                                      "nodeType": "Identifier",
                                      "overloadedDeclarations": [],
                                      "referencedDeclaration": 374,
                                      "src": "10760:12:1",
                                      "typeDescriptions": {
                                        "typeIdentifier": "t_address",
                                        "typeString": "address"
                                      }
                                    }
                                  ],
                                  "expression": {
                                    "argumentTypes": [
                                      {
                                        "typeIdentifier": "t_address",
                                        "typeString": "address"
                                      }
                                    ],
                                    "id": 542,
                                    "name": "ERC20",
                                    "nodeType": "Identifier",
                                    "overloadedDeclarations": [],
                                    "referencedDeclaration": 1152,
                                    "src": "10754:5:1",
                                    "typeDescriptions": {
                                      "typeIdentifier": "t_type$_t_contract$_ERC20_$1152_$",
                                      "typeString": "type(contract ERC20)"
                                    }
                                  },
                                  "id": 544,
                                  "isConstant": false,
                                  "isLValue": false,
                                  "isPure": false,
                                  "kind": "typeConversion",
                                  "lValueRequested": false,
                                  "names": [],
                                  "nodeType": "FunctionCall",
                                  "src": "10754:19:1",
                                  "typeDescriptions": {
                                    "typeIdentifier": "t_contract$_ERC20_$1152",
                                    "typeString": "contract ERC20"
                                  }
                                },
                                "id": 545,
                                "isConstant": false,
                                "isLValue": false,
                                "isPure": false,
                                "lValueRequested": false,
                                "memberName": "transferFrom",
                                "nodeType": "MemberAccess",
                                "referencedDeclaration": 899,
                                "src": "10754:32:1",
                                "typeDescriptions": {
                                  "typeIdentifier": "t_function_external_nonpayable$_t_address_$_t_address_$_t_uint256_$returns$_t_bool_$",
                                  "typeString": "function (address,address,uint256) external returns (bool)"
                                }
                              },
                              "id": 550,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": false,
                              "kind": "functionCall",
                              "lValueRequested": false,
                              "names": [],
                              "nodeType": "FunctionCall",
                              "src": "10754:60:1",
                              "typeDescriptions": {
                                "typeIdentifier": "t_bool",
                                "typeString": "bool"
                              }
                            },
                            {
                              "argumentTypes": null,
                              "hexValue": "4661696c656420746f20706179206761732061732066726f6d206163636f756e74",
                              "id": 551,
                              "isConstant": false,
                              "isLValue": false,
                              "isPure": true,
                              "kind": "string",
                              "lValueRequested": false,
                              "nodeType": "Literal",
                              "src": "10832:35:1",
                              "subdenomination": null,
                              "typeDescriptions": {
                                "typeIdentifier": "t_stringliteral_14793e3e3905a30586d2b24e3ad0438f041907f0cf302e37f5d900c5e9ac3e25",
                                "typeString": "literal_string \"Failed to pay gas as from account\""
                              },
                              "value": "Failed to pay gas as from account"
                            }
                          ],
                          "expression": {
                            "argumentTypes": [
                              {
                                "typeIdentifier": "t_bool",
                                "typeString": "bool"
                              },
                              {
                                "typeIdentifier": "t_stringliteral_14793e3e3905a30586d2b24e3ad0438f041907f0cf302e37f5d900c5e9ac3e25",
                                "typeString": "literal_string \"Failed to pay gas as from account\""
                              }
                            ],
                            "id": 541,
                            "name": "require",
                            "nodeType": "Identifier",
                            "overloadedDeclarations": [
                              1239,
                              1240
                            ],
                            "referencedDeclaration": 1240,
                            "src": "10729:7:1",
                            "typeDescriptions": {
                              "typeIdentifier": "t_function_require_pure$_t_bool_$_t_string_memory_ptr_$returns$__$",
                              "typeString": "function (bool,string memory) pure"
                            }
                          },
                          "id": 552,
                          "isConstant": false,
                          "isLValue": false,
                          "isPure": false,
                          "kind": "functionCall",
                          "lValueRequested": false,
                          "names": [],
                          "nodeType": "FunctionCall",
                          "src": "10729:152:1",
                          "typeDescriptions": {
                            "typeIdentifier": "t_tuple$__$",
                            "typeString": "tuple()"
                          }
                        },
                        "id": 553,
                        "nodeType": "ExpressionStatement",
                        "src": "10729:152:1"
                      }
                    ]
                  }
                },
                {
                  "expression": {
                    "argumentTypes": null,
                    "hexValue": "74727565",
                    "id": 556,
                    "isConstant": false,
                    "isLValue": false,
                    "isPure": true,
                    "kind": "bool",
                    "lValueRequested": false,
                    "nodeType": "Literal",
                    "src": "10909:4:1",
                    "subdenomination": null,
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    },
                    "value": "true"
                  },
                  "functionReturnParameters": 386,
                  "id": 557,
                  "nodeType": "Return",
                  "src": "10902:11:1"
                }
              ]
            },
            "documentation": null,
            "id": 559,
            "implemented": true,
            "kind": "function",
            "modifiers": [],
            "name": "executeSubscription",
            "nodeType": "FunctionDefinition",
            "parameters": {
              "id": 383,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 370,
                  "name": "from",
                  "nodeType": "VariableDeclaration",
                  "scope": 559,
                  "src": "7494:12:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 369,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "7494:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 372,
                  "name": "to",
                  "nodeType": "VariableDeclaration",
                  "scope": 559,
                  "src": "7533:10:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 371,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "7533:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 374,
                  "name": "tokenAddress",
                  "nodeType": "VariableDeclaration",
                  "scope": 559,
                  "src": "7569:20:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_address",
                    "typeString": "address"
                  },
                  "typeName": {
                    "id": 373,
                    "name": "address",
                    "nodeType": "ElementaryTypeName",
                    "src": "7569:7:1",
                    "stateMutability": "nonpayable",
                    "typeDescriptions": {
                      "typeIdentifier": "t_address",
                      "typeString": "address"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 376,
                  "name": "tokenAmount",
                  "nodeType": "VariableDeclaration",
                  "scope": 559,
                  "src": "7641:19:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 375,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "7641:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 378,
                  "name": "periodSeconds",
                  "nodeType": "VariableDeclaration",
                  "scope": 559,
                  "src": "7711:21:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 377,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "7711:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 380,
                  "name": "gasPrice",
                  "nodeType": "VariableDeclaration",
                  "scope": 559,
                  "src": "7783:16:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_uint256",
                    "typeString": "uint256"
                  },
                  "typeName": {
                    "id": 379,
                    "name": "uint256",
                    "nodeType": "ElementaryTypeName",
                    "src": "7783:7:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_uint256",
                      "typeString": "uint256"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                },
                {
                  "constant": false,
                  "id": 382,
                  "name": "signature",
                  "nodeType": "VariableDeclaration",
                  "scope": 559,
                  "src": "7867:22:1",
                  "stateVariable": false,
                  "storageLocation": "memory",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bytes_memory_ptr",
                    "typeString": "bytes"
                  },
                  "typeName": {
                    "id": 381,
                    "name": "bytes",
                    "nodeType": "ElementaryTypeName",
                    "src": "7867:5:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bytes_storage_ptr",
                      "typeString": "bytes"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "7484:461:1"
            },
            "returnParameters": {
              "id": 386,
              "nodeType": "ParameterList",
              "parameters": [
                {
                  "constant": false,
                  "id": 385,
                  "name": "success",
                  "nodeType": "VariableDeclaration",
                  "scope": 559,
                  "src": "7978:12:1",
                  "stateVariable": false,
                  "storageLocation": "default",
                  "typeDescriptions": {
                    "typeIdentifier": "t_bool",
                    "typeString": "bool"
                  },
                  "typeName": {
                    "id": 384,
                    "name": "bool",
                    "nodeType": "ElementaryTypeName",
                    "src": "7978:4:1",
                    "typeDescriptions": {
                      "typeIdentifier": "t_bool",
                      "typeString": "bool"
                    }
                  },
                  "value": null,
                  "visibility": "internal"
                }
              ],
              "src": "7977:14:1"
            },
            "scope": 560,
            "src": "7456:3464:1",
            "stateMutability": "nonpayable",
            "superFunction": null,
            "visibility": "public"
          }
        ],
        "scope": 561,
        "src": "1096:9826:1"
      }
    ],
    "src": "0:10923:1"
  },
  "compiler": {
    "name": "solc",
    "version": "0.5.2+commit.1df8f40c.Emscripten.clang"
  },
  "networks": {},
  "schemaVersion": "3.0.6",
  "updatedAt": "2019-04-18T12:13:40.098Z",
  "devdoc": {
    "methods": {}
  },
  "userdoc": {
    "methods": {}
  }
}
