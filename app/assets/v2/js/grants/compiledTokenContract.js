let compiledToken = {
  'contractName': 'WasteCoin',
  'abi': [
    {
      'constant': true,
      'inputs': [],
      'name': 'mintingFinished',
      'outputs': [
        {
          'name': '',
          'type': 'bool'
        }
      ],
      'payable': false,
      'stateMutability': 'view',
      'type': 'function'
    },
    {
      'constant': true,
      'inputs': [],
      'name': 'name',
      'outputs': [
        {
          'name': '',
          'type': 'string'
        }
      ],
      'payable': false,
      'stateMutability': 'view',
      'type': 'function'
    },
    {
      'constant': false,
      'inputs': [
        {
          'name': 'spender',
          'type': 'address'
        },
        {
          'name': 'value',
          'type': 'uint256'
        }
      ],
      'name': 'approve',
      'outputs': [
        {
          'name': '',
          'type': 'bool'
        }
      ],
      'payable': false,
      'stateMutability': 'nonpayable',
      'type': 'function'
    },
    {
      'constant': true,
      'inputs': [],
      'name': 'totalSupply',
      'outputs': [
        {
          'name': '',
          'type': 'uint256'
        }
      ],
      'payable': false,
      'stateMutability': 'view',
      'type': 'function'
    },
    {
      'constant': false,
      'inputs': [
        {
          'name': 'from',
          'type': 'address'
        },
        {
          'name': 'to',
          'type': 'address'
        },
        {
          'name': 'value',
          'type': 'uint256'
        }
      ],
      'name': 'transferFrom',
      'outputs': [
        {
          'name': '',
          'type': 'bool'
        }
      ],
      'payable': false,
      'stateMutability': 'nonpayable',
      'type': 'function'
    },
    {
      'constant': true,
      'inputs': [],
      'name': 'decimals',
      'outputs': [
        {
          'name': '',
          'type': 'uint8'
        }
      ],
      'payable': false,
      'stateMutability': 'view',
      'type': 'function'
    },
    {
      'constant': false,
      'inputs': [
        {
          'name': 'spender',
          'type': 'address'
        },
        {
          'name': 'addedValue',
          'type': 'uint256'
        }
      ],
      'name': 'increaseAllowance',
      'outputs': [
        {
          'name': '',
          'type': 'bool'
        }
      ],
      'payable': false,
      'stateMutability': 'nonpayable',
      'type': 'function'
    },
    {
      'constant': false,
      'inputs': [
        {
          'name': 'to',
          'type': 'address'
        },
        {
          'name': 'amount',
          'type': 'uint256'
        }
      ],
      'name': 'mint',
      'outputs': [
        {
          'name': '',
          'type': 'bool'
        }
      ],
      'payable': false,
      'stateMutability': 'nonpayable',
      'type': 'function'
    },
    {
      'constant': true,
      'inputs': [
        {
          'name': 'owner',
          'type': 'address'
        }
      ],
      'name': 'balanceOf',
      'outputs': [
        {
          'name': '',
          'type': 'uint256'
        }
      ],
      'payable': false,
      'stateMutability': 'view',
      'type': 'function'
    },
    {
      'constant': false,
      'inputs': [],
      'name': 'finishMinting',
      'outputs': [
        {
          'name': '',
          'type': 'bool'
        }
      ],
      'payable': false,
      'stateMutability': 'nonpayable',
      'type': 'function'
    },
    {
      'constant': true,
      'inputs': [],
      'name': 'symbol',
      'outputs': [
        {
          'name': '',
          'type': 'string'
        }
      ],
      'payable': false,
      'stateMutability': 'view',
      'type': 'function'
    },
    {
      'constant': false,
      'inputs': [
        {
          'name': 'account',
          'type': 'address'
        }
      ],
      'name': 'addMinter',
      'outputs': [],
      'payable': false,
      'stateMutability': 'nonpayable',
      'type': 'function'
    },
    {
      'constant': false,
      'inputs': [],
      'name': 'renounceMinter',
      'outputs': [],
      'payable': false,
      'stateMutability': 'nonpayable',
      'type': 'function'
    },
    {
      'constant': false,
      'inputs': [
        {
          'name': 'spender',
          'type': 'address'
        },
        {
          'name': 'subtractedValue',
          'type': 'uint256'
        }
      ],
      'name': 'decreaseAllowance',
      'outputs': [
        {
          'name': '',
          'type': 'bool'
        }
      ],
      'payable': false,
      'stateMutability': 'nonpayable',
      'type': 'function'
    },
    {
      'constant': false,
      'inputs': [
        {
          'name': 'to',
          'type': 'address'
        },
        {
          'name': 'value',
          'type': 'uint256'
        }
      ],
      'name': 'transfer',
      'outputs': [
        {
          'name': '',
          'type': 'bool'
        }
      ],
      'payable': false,
      'stateMutability': 'nonpayable',
      'type': 'function'
    },
    {
      'constant': true,
      'inputs': [
        {
          'name': 'account',
          'type': 'address'
        }
      ],
      'name': 'isMinter',
      'outputs': [
        {
          'name': '',
          'type': 'bool'
        }
      ],
      'payable': false,
      'stateMutability': 'view',
      'type': 'function'
    },
    {
      'constant': true,
      'inputs': [
        {
          'name': 'owner',
          'type': 'address'
        },
        {
          'name': 'spender',
          'type': 'address'
        }
      ],
      'name': 'allowance',
      'outputs': [
        {
          'name': '',
          'type': 'uint256'
        }
      ],
      'payable': false,
      'stateMutability': 'view',
      'type': 'function'
    },
    {
      'inputs': [],
      'payable': false,
      'stateMutability': 'nonpayable',
      'type': 'constructor'
    },
    {
      'anonymous': false,
      'inputs': [],
      'name': 'MintingFinished',
      'type': 'event'
    },
    {
      'anonymous': false,
      'inputs': [
        {
          'indexed': true,
          'name': 'account',
          'type': 'address'
        }
      ],
      'name': 'MinterAdded',
      'type': 'event'
    },
    {
      'anonymous': false,
      'inputs': [
        {
          'indexed': true,
          'name': 'account',
          'type': 'address'
        }
      ],
      'name': 'MinterRemoved',
      'type': 'event'
    },
    {
      'anonymous': false,
      'inputs': [
        {
          'indexed': true,
          'name': 'from',
          'type': 'address'
        },
        {
          'indexed': true,
          'name': 'to',
          'type': 'address'
        },
        {
          'indexed': false,
          'name': 'value',
          'type': 'uint256'
        }
      ],
      'name': 'Transfer',
      'type': 'event'
    },
    {
      'anonymous': false,
      'inputs': [
        {
          'indexed': true,
          'name': 'owner',
          'type': 'address'
        },
        {
          'indexed': true,
          'name': 'spender',
          'type': 'address'
        },
        {
          'indexed': false,
          'name': 'value',
          'type': 'uint256'
        }
      ],
      'name': 'Approval',
      'type': 'event'
    }
  ],
  'bytecode': '0x60806040526000600460006101000a81548160ff0219169083151502179055506040805190810160405280600981526020017f5761737465436f696e0000000000000000000000000000000000000000000000815250600590805190602001906200006c929190620001aa565b506040805190810160405280600281526020017f574300000000000000000000000000000000000000000000000000000000000081525060069080519060200190620000ba929190620001aa565b506012600760006101000a81548160ff021916908360ff160217905550348015620000e457600080fd5b50620001093360036200010f640100000000026200176d179091906401000000009004565b62000259565b600073ffffffffffffffffffffffffffffffffffffffff168173ffffffffffffffffffffffffffffffffffffffff16141515156200014c57600080fd5b60018260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060006101000a81548160ff0219169083151502179055505050565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f10620001ed57805160ff19168380011785556200021e565b828001600101855582156200021e579182015b828111156200021d57825182559160200191906001019062000200565b5b5090506200022d919062000231565b5090565b6200025691905b808211156200025257600081600090555060010162000238565b5090565b90565b61196180620002696000396000f3006080604052600436106100f1576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806305d2035b146100f657806306fdde0314610125578063095ea7b3146101b557806318160ddd1461021a57806323b872dd14610245578063313ce567146102ca57806339509351146102fb57806340c10f191461036057806370a08231146103c55780637d64bcb41461041c57806395d89b411461044b578063983b2d56146104db578063986502751461051e578063a457c2d714610535578063a9059cbb1461059a578063aa271e1a146105ff578063dd62ed3e1461065a575b600080fd5b34801561010257600080fd5b5061010b6106d1565b604051808215151515815260200191505060405180910390f35b34801561013157600080fd5b5061013a6106e8565b6040518080602001828103825283818151815260200191508051906020019080838360005b8381101561017a57808201518184015260208101905061015f565b50505050905090810190601f1680156101a75780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b3480156101c157600080fd5b50610200600480360381019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919080359060200190929190505050610786565b604051808215151515815260200191505060405180910390f35b34801561022657600080fd5b5061022f6108b3565b6040518082815260200191505060405180910390f35b34801561025157600080fd5b506102b0600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291905050506108bd565b604051808215151515815260200191505060405180910390f35b3480156102d657600080fd5b506102df610c78565b604051808260ff1660ff16815260200191505060405180910390f35b34801561030757600080fd5b50610346600480360381019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919080359060200190929190505050610c8b565b604051808215151515815260200191505060405180910390f35b34801561036c57600080fd5b506103ab600480360381019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919080359060200190929190505050610ec2565b604051808215151515815260200191505060405180910390f35b3480156103d157600080fd5b50610406600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050610f08565b6040518082815260200191505060405180910390f35b34801561042857600080fd5b50610431610f50565b604051808215151515815260200191505060405180910390f35b34801561045757600080fd5b50610460610fd0565b6040518080602001828103825283818151815260200191508051906020019080838360005b838110156104a0578082015181840152602081019050610485565b50505050905090810190601f1680156104cd5780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b3480156104e757600080fd5b5061051c600480360381019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919050505061106e565b005b34801561052a57600080fd5b506105336110dc565b005b34801561054157600080fd5b50610580600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291905050506110f2565b604051808215151515815260200191505060405180910390f35b3480156105a657600080fd5b506105e5600480360381019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919080359060200190929190505050611329565b604051808215151515815260200191505060405180910390f35b34801561060b57600080fd5b50610640600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050611549565b604051808215151515815260200191505060405180910390f35b34801561066657600080fd5b506106bb600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050611566565b6040518082815260200191505060405180910390f35b6000600460009054906101000a900460ff16905090565b60058054600181600116156101000203166002900480601f01602080910402602001604051908101604052809291908181526020018280546001816001161561010002031660029004801561077e5780601f106107535761010080835404028352916020019161077e565b820191906000526020600020905b81548152906001019060200180831161076157829003601f168201915b505050505081565b60008073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff16141515156107c357600080fd5b81600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925846040518082815260200191505060405180910390a36001905092915050565b6000600254905090565b60008060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054821115151561090c57600080fd5b600160008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054821115151561099757600080fd5b600073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff16141515156109d357600080fd5b610a24826000808773ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020546115ed90919063ffffffff16565b6000808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550610ab7826000808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205461160e90919063ffffffff16565b6000808573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550610b8882600160008773ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020546115ed90919063ffffffff16565b600160008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff168473ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040518082815260200191505060405180910390a3600190509392505050565b600760009054906101000a900460ff1681565b60008073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff1614151515610cc857600080fd5b610d5782600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205461160e90919063ffffffff16565b600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008773ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020546040518082815260200191505060405180910390a36001905092915050565b6000610ecd33611549565b1515610ed857600080fd5b600460009054906101000a900460ff16151515610ef457600080fd5b610efe838361162f565b6001905092915050565b60008060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020549050919050565b6000610f5b33611549565b1515610f6657600080fd5b600460009054906101000a900460ff16151515610f8257600080fd5b6001600460006101000a81548160ff0219169083151502179055507fb828d9b5c78095deeeeff2eca2e5d4fe046ce3feb4c99702624a3fd384ad2dbc60405160405180910390a16001905090565b60068054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156110665780601f1061103b57610100808354040283529160200191611066565b820191906000526020600020905b81548152906001019060200180831161104957829003601f168201915b505050505081565b61107733611549565b151561108257600080fd5b61109681600361176d90919063ffffffff16565b8073ffffffffffffffffffffffffffffffffffffffff167f6ae172837ea30b801fbfcdd4108aa1d5bf8ff775444fd70256b44e6bf3dfc3f660405160405180910390a250565b6110f033600361180790919063ffffffff16565b565b60008073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff161415151561112f57600080fd5b6111be82600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020546115ed90919063ffffffff16565b600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008773ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020546040518082815260200191505060405180910390a36001905092915050565b60008060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054821115151561137857600080fd5b600073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff16141515156113b457600080fd5b611405826000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020546115ed90919063ffffffff16565b6000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550611498826000808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205461160e90919063ffffffff16565b6000808573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040518082815260200191505060405180910390a36001905092915050565b600061155f8260036118a190919063ffffffff16565b9050919050565b6000600160008473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054905092915050565b6000808383111515156115ff57600080fd5b82840390508091505092915050565b600080828401905083811015151561162557600080fd5b8091505092915050565b60008273ffffffffffffffffffffffffffffffffffffffff161415151561165557600080fd5b61166a8160025461160e90919063ffffffff16565b6002819055506116c1816000808573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205461160e90919063ffffffff16565b6000808473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508173ffffffffffffffffffffffffffffffffffffffff16600073ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef836040518082815260200191505060405180910390a35050565b600073ffffffffffffffffffffffffffffffffffffffff168173ffffffffffffffffffffffffffffffffffffffff16141515156117a957600080fd5b60018260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060006101000a81548160ff0219169083151502179055505050565b600073ffffffffffffffffffffffffffffffffffffffff168173ffffffffffffffffffffffffffffffffffffffff161415151561184357600080fd5b60008260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060006101000a81548160ff0219169083151502179055505050565b60008073ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff16141515156118de57600080fd5b8260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060009054906101000a900460ff169050929150505600a165627a7a723058209df5d9d7cf4753564308cec607ec0a368993aa77994d6b794abd121be544ac3c0029',
  'deployedBytecode': '0x6080604052600436106100f1576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806305d2035b146100f657806306fdde0314610125578063095ea7b3146101b557806318160ddd1461021a57806323b872dd14610245578063313ce567146102ca57806339509351146102fb57806340c10f191461036057806370a08231146103c55780637d64bcb41461041c57806395d89b411461044b578063983b2d56146104db578063986502751461051e578063a457c2d714610535578063a9059cbb1461059a578063aa271e1a146105ff578063dd62ed3e1461065a575b600080fd5b34801561010257600080fd5b5061010b6106d1565b604051808215151515815260200191505060405180910390f35b34801561013157600080fd5b5061013a6106e8565b6040518080602001828103825283818151815260200191508051906020019080838360005b8381101561017a57808201518184015260208101905061015f565b50505050905090810190601f1680156101a75780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b3480156101c157600080fd5b50610200600480360381019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919080359060200190929190505050610786565b604051808215151515815260200191505060405180910390f35b34801561022657600080fd5b5061022f6108b3565b6040518082815260200191505060405180910390f35b34801561025157600080fd5b506102b0600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291905050506108bd565b604051808215151515815260200191505060405180910390f35b3480156102d657600080fd5b506102df610c78565b604051808260ff1660ff16815260200191505060405180910390f35b34801561030757600080fd5b50610346600480360381019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919080359060200190929190505050610c8b565b604051808215151515815260200191505060405180910390f35b34801561036c57600080fd5b506103ab600480360381019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919080359060200190929190505050610ec2565b604051808215151515815260200191505060405180910390f35b3480156103d157600080fd5b50610406600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050610f08565b6040518082815260200191505060405180910390f35b34801561042857600080fd5b50610431610f50565b604051808215151515815260200191505060405180910390f35b34801561045757600080fd5b50610460610fd0565b6040518080602001828103825283818151815260200191508051906020019080838360005b838110156104a0578082015181840152602081019050610485565b50505050905090810190601f1680156104cd5780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b3480156104e757600080fd5b5061051c600480360381019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919050505061106e565b005b34801561052a57600080fd5b506105336110dc565b005b34801561054157600080fd5b50610580600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803590602001909291905050506110f2565b604051808215151515815260200191505060405180910390f35b3480156105a657600080fd5b506105e5600480360381019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919080359060200190929190505050611329565b604051808215151515815260200191505060405180910390f35b34801561060b57600080fd5b50610640600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050611549565b604051808215151515815260200191505060405180910390f35b34801561066657600080fd5b506106bb600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050611566565b6040518082815260200191505060405180910390f35b6000600460009054906101000a900460ff16905090565b60058054600181600116156101000203166002900480601f01602080910402602001604051908101604052809291908181526020018280546001816001161561010002031660029004801561077e5780601f106107535761010080835404028352916020019161077e565b820191906000526020600020905b81548152906001019060200180831161076157829003601f168201915b505050505081565b60008073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff16141515156107c357600080fd5b81600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925846040518082815260200191505060405180910390a36001905092915050565b6000600254905090565b60008060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054821115151561090c57600080fd5b600160008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054821115151561099757600080fd5b600073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff16141515156109d357600080fd5b610a24826000808773ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020546115ed90919063ffffffff16565b6000808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550610ab7826000808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205461160e90919063ffffffff16565b6000808573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550610b8882600160008773ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020546115ed90919063ffffffff16565b600160008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff168473ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040518082815260200191505060405180910390a3600190509392505050565b600760009054906101000a900460ff1681565b60008073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff1614151515610cc857600080fd5b610d5782600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205461160e90919063ffffffff16565b600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008773ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020546040518082815260200191505060405180910390a36001905092915050565b6000610ecd33611549565b1515610ed857600080fd5b600460009054906101000a900460ff16151515610ef457600080fd5b610efe838361162f565b6001905092915050565b60008060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020549050919050565b6000610f5b33611549565b1515610f6657600080fd5b600460009054906101000a900460ff16151515610f8257600080fd5b6001600460006101000a81548160ff0219169083151502179055507fb828d9b5c78095deeeeff2eca2e5d4fe046ce3feb4c99702624a3fd384ad2dbc60405160405180910390a16001905090565b60068054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156110665780601f1061103b57610100808354040283529160200191611066565b820191906000526020600020905b81548152906001019060200180831161104957829003601f168201915b505050505081565b61107733611549565b151561108257600080fd5b61109681600361176d90919063ffffffff16565b8073ffffffffffffffffffffffffffffffffffffffff167f6ae172837ea30b801fbfcdd4108aa1d5bf8ff775444fd70256b44e6bf3dfc3f660405160405180910390a250565b6110f033600361180790919063ffffffff16565b565b60008073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff161415151561112f57600080fd5b6111be82600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020546115ed90919063ffffffff16565b600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925600160003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008773ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020546040518082815260200191505060405180910390a36001905092915050565b60008060003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054821115151561137857600080fd5b600073ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff16141515156113b457600080fd5b611405826000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020546115ed90919063ffffffff16565b6000803373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002081905550611498826000808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205461160e90919063ffffffff16565b6000808573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508273ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef846040518082815260200191505060405180910390a36001905092915050565b600061155f8260036118a190919063ffffffff16565b9050919050565b6000600160008473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002054905092915050565b6000808383111515156115ff57600080fd5b82840390508091505092915050565b600080828401905083811015151561162557600080fd5b8091505092915050565b60008273ffffffffffffffffffffffffffffffffffffffff161415151561165557600080fd5b61166a8160025461160e90919063ffffffff16565b6002819055506116c1816000808573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000205461160e90919063ffffffff16565b6000808473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020819055508173ffffffffffffffffffffffffffffffffffffffff16600073ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef836040518082815260200191505060405180910390a35050565b600073ffffffffffffffffffffffffffffffffffffffff168173ffffffffffffffffffffffffffffffffffffffff16141515156117a957600080fd5b60018260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060006101000a81548160ff0219169083151502179055505050565b600073ffffffffffffffffffffffffffffffffffffffff168173ffffffffffffffffffffffffffffffffffffffff161415151561184357600080fd5b60008260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060006101000a81548160ff0219169083151502179055505050565b60008073ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff16141515156118de57600080fd5b8260000160008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060009054906101000a900460ff169050929150505600a165627a7a723058209df5d9d7cf4753564308cec607ec0a368993aa77994d6b794abd121be544ac3c0029',
  'sourceMap': '146:166:1:-;;;262:5:8;230:37;;;;;;;;;;;;;;;;;;;;187:32:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:::i;:::-;;223:27;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:::i;:::-;;278:2;254:26;;;;;;;;;;;;;;;;;;;;285:24;8:9:-1;5:2;;;30:1;27;20:12;5:2;285:24:1;259:23:3;271:10;259:7;:11;;;;;;:23;;;;;:::i;:::-;146:166:1;;245:132:2;336:1;317:21;;:7;:21;;;;309:30;;;;;;;;368:4;345;:11;;:20;357:7;345:20;;;;;;;;;;;;;;;;:27;;;;;;;;;;;;;;;;;;245:132;;:::o;146:166:1:-;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:::i;:::-;;;:::o;:::-;;;;;;;;;;;;;;;;;;;;;;;;;;;:::o;:::-;;;;;;;',
  'deployedSourceMap': '146:166:1:-;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;415:87:8;;8:9:-1;5:2;;;30:1;27;20:12;5:2;415:87:8;;;;;;;;;;;;;;;;;;;;;;;;;;;187:32:1;;8:9:-1;5:2;;;30:1;27;20:12;5:2;187:32:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;23:1:-1;8:100;33:3;30:1;27:10;8:100;;;99:1;94:3;90:11;84:18;80:1;75:3;71:11;64:39;52:2;49:1;45:10;40:15;;8:100;;;12:14;187:32:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;2574:220:7;;8:9:-1;5:2;;;30:1;27;20:12;5:2;2574:220:7;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;641:83;;8:9:-1;5:2;;;30:1;27;20:12;5:2;641:83:7;;;;;;;;;;;;;;;;;;;;;;;3066:458;;8:9:-1;5:2;;;30:1;27;20:12;5:2;3066:458:7;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;254:26:1;;8:9:-1;5:2;;;30:1;27;20:12;5:2;254:26:1;;;;;;;;;;;;;;;;;;;;;;;;;;;3975:330:7;;8:9:-1;5:2;;;30:1;27;20:12;5:2;3975:330:7;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;736:176:8;;8:9:-1;5:2;;;30:1;27;20:12;5:2;736:176:8;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;925:98:7;;8:9:-1;5:2;;;30:1;27;20:12;5:2;925:98:7;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;1026:181:8;;8:9:-1;5:2;;;30:1;27;20:12;5:2;1026:181:8;;;;;;;;;;;;;;;;;;;;;;;;;;;223:27:1;;8:9:-1;5:2;;;30:1;27;20:12;5:2;223:27:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;23:1:-1;8:100;33:3;30:1;27:10;8:100;;;99:1;94:3;90:11;84:18;80:1;75:3;71:11;64:39;52:2;49:1;45:10;40:15;;8:100;;;12:14;223:27:1;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;468:116:3;;8:9:-1;5:2;;;30:1;27;20:12;5:2;468:116:3;;;;;;;;;;;;;;;;;;;;;;;;;;;;588:70;;8:9:-1;5:2;;;30:1;27;20:12;5:2;588:70:3;;;;;;4761:340:7;;8:9:-1;5:2;;;30:1;27;20:12;5:2;4761:340:7;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;1642:316;;8:9:-1;5:2;;;30:1;27;20:12;5:2;1642:316:7;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;364:100:3;;8:9:-1;5:2;;;30:1;27;20:12;5:2;364:100:3;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;1340:150:7;;8:9:-1;5:2;;;30:1;27;20:12;5:2;1340:150:7;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;415:87:8;462:4;481:16;;;;;;;;;;;474:23;;415:87;:::o;187:32:1:-;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:::o;2574:220:7:-;2639:4;2678:1;2659:21;;:7;:21;;;;2651:30;;;;;;;;2720:5;2688:8;:20;2697:10;2688:20;;;;;;;;;;;;;;;:29;2709:7;2688:29;;;;;;;;;;;;;;;:37;;;;2757:7;2736:36;;2745:10;2736:36;;;2766:5;2736:36;;;;;;;;;;;;;;;;;;2785:4;2778:11;;2574:220;;;;:::o;641:83::-;685:7;707:12;;700:19;;641:83;:::o;3066:458::-;3169:4;3200:9;:15;3210:4;3200:15;;;;;;;;;;;;;;;;3191:5;:24;;3183:33;;;;;;;;3239:8;:14;3248:4;3239:14;;;;;;;;;;;;;;;:26;3254:10;3239:26;;;;;;;;;;;;;;;;3230:5;:35;;3222:44;;;;;;;;3294:1;3280:16;;:2;:16;;;;3272:25;;;;;;;;3322:26;3342:5;3322:9;:15;3332:4;3322:15;;;;;;;;;;;;;;;;:19;;:26;;;;:::i;:::-;3304:9;:15;3314:4;3304:15;;;;;;;;;;;;;;;:44;;;;3370:24;3388:5;3370:9;:13;3380:2;3370:13;;;;;;;;;;;;;;;;:17;;:24;;;;:::i;:::-;3354:9;:13;3364:2;3354:13;;;;;;;;;;;;;;;:40;;;;3429:37;3460:5;3429:8;:14;3438:4;3429:14;;;;;;;;;;;;;;;:26;3444:10;3429:26;;;;;;;;;;;;;;;;:30;;:37;;;;:::i;:::-;3400:8;:14;3409:4;3400:14;;;;;;;;;;;;;;;:26;3415:10;3400:26;;;;;;;;;;;;;;;:66;;;;3492:2;3477:25;;3486:4;3477:25;;;3496:5;3477:25;;;;;;;;;;;;;;;;;;3515:4;3508:11;;3066:458;;;;;:::o;254:26:1:-;;;;;;;;;;;;;:::o;3975:330:7:-;4075:4;4116:1;4097:21;;:7;:21;;;;4089:30;;;;;;;;4166:45;4200:10;4166:8;:20;4175:10;4166:20;;;;;;;;;;;;;;;:29;4187:7;4166:29;;;;;;;;;;;;;;;;:33;;:45;;;;:::i;:::-;4126:8;:20;4135:10;4126:20;;;;;;;;;;;;;;;:29;4147:7;4126:29;;;;;;;;;;;;;;;:86;;;;4244:7;4223:60;;4232:10;4223:60;;;4253:8;:20;4262:10;4253:20;;;;;;;;;;;;;;;:29;4274:7;4253:29;;;;;;;;;;;;;;;;4223:60;;;;;;;;;;;;;;;;;;4296:4;4289:11;;3975:330;;;;:::o;736:176:8:-;859:4;327:20:3;336:10;327:8;:20::i;:::-;319:29;;;;;;;;324:16:8;;;;;;;;;;;323:17;315:26;;;;;;;;873:17;879:2;883:6;873:5;:17::i;:::-;903:4;896:11;;736:176;;;;:::o;925:98:7:-;980:7;1002:9;:16;1012:5;1002:16;;;;;;;;;;;;;;;;995:23;;925:98;;;:::o;1026:181:8:-;1120:4;327:20:3;336:10;327:8;:20::i;:::-;319:29;;;;;;;;324:16:8;;;;;;;;;;;323:17;315:26;;;;;;;;1153:4;1134:16;;:23;;;;;;;;;;;;;;;;;;1168:17;;;;;;;;;;1198:4;1191:11;;1026:181;:::o;223:27:1:-;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;:::o;468:116:3:-;327:20;336:10;327:8;:20::i;:::-;319:29;;;;;;;;528:20;540:7;528;:11;;:20;;;;:::i;:::-;571:7;559:20;;;;;;;;;;;;468:116;:::o;588:70::-;627:26;642:10;627:7;:14;;:26;;;;:::i;:::-;588:70::o;4761:340:7:-;4866:4;4907:1;4888:21;;:7;:21;;;;4880:30;;;;;;;;4957:50;4991:15;4957:8;:20;4966:10;4957:20;;;;;;;;;;;;;;;:29;4978:7;4957:29;;;;;;;;;;;;;;;;:33;;:50;;;;:::i;:::-;4917:8;:20;4926:10;4917:20;;;;;;;;;;;;;;;:29;4938:7;4917:29;;;;;;;;;;;;;;;:91;;;;5040:7;5019:60;;5028:10;5019:60;;;5049:8;:20;5058:10;5049:20;;;;;;;;;;;;;;;:29;5070:7;5049:29;;;;;;;;;;;;;;;;5019:60;;;;;;;;;;;;;;;;;;5092:4;5085:11;;4761:340;;;;:::o;1642:316::-;1703:4;1732:9;:21;1742:10;1732:21;;;;;;;;;;;;;;;;1723:5;:30;;1715:39;;;;;;;;1782:1;1768:16;;:2;:16;;;;1760:25;;;;;;;;1816:32;1842:5;1816:9;:21;1826:10;1816:21;;;;;;;;;;;;;;;;:25;;:32;;;;:::i;:::-;1792:9;:21;1802:10;1792:21;;;;;;;;;;;;;;;:56;;;;1870:24;1888:5;1870:9;:13;1880:2;1870:13;;;;;;;;;;;;;;;;:17;;:24;;;;:::i;:::-;1854:9;:13;1864:2;1854:13;;;;;;;;;;;;;;;:40;;;;1926:2;1905:31;;1914:10;1905:31;;;1930:5;1905:31;;;;;;;;;;;;;;;;;;1949:4;1942:11;;1642:316;;;;:::o;364:100:3:-;420:4;439:20;451:7;439;:11;;:20;;;;:::i;:::-;432:27;;364:100;;;:::o;1340:150:7:-;1437:7;1461:8;:15;1470:5;1461:15;;;;;;;;;;;;;;;:24;1477:7;1461:24;;;;;;;;;;;;;;;;1454:31;;1340:150;;;;:::o;1079:131:5:-;1137:7;1173:9;1165:1;1160;:6;;1152:15;;;;;;;;1189:1;1185;:5;1173:17;;1204:1;1197:8;;1079:131;;;;;:::o;1273:::-;1331:7;1346:9;1362:1;1358;:5;1346:17;;1382:1;1377;:6;;1369:15;;;;;;;;1398:1;1391:8;;1273:131;;;;;:::o;5429:239:7:-;5511:1;5500:7;:12;;;;5492:21;;;;;;;;5534:24;5551:6;5534:12;;:16;;:24;;;;:::i;:::-;5519:12;:39;;;;5585:30;5608:6;5585:9;:18;5595:7;5585:18;;;;;;;;;;;;;;;;:22;;:30;;;;:::i;:::-;5564:9;:18;5574:7;5564:18;;;;;;;;;;;;;;;:51;;;;5647:7;5626:37;;5643:1;5626:37;;;5656:6;5626:37;;;;;;;;;;;;;;;;;;5429:239;;:::o;245:132:2:-;336:1;317:21;;:7;:21;;;;309:30;;;;;;;;368:4;345;:11;;:20;357:7;345:20;;;;;;;;;;;;;;;;:27;;;;;;;;;;;;;;;;;;245:132;;:::o;443:136::-;537:1;518:21;;:7;:21;;;;510:30;;;;;;;;569:5;546:4;:11;;:20;558:7;546:20;;;;;;;;;;;;;;;;:28;;;;;;;;;;;;;;;;;;443:136;;:::o;657:166::-;741:4;782:1;763:21;;:7;:21;;;;755:30;;;;;;;;798:4;:11;;:20;810:7;798:20;;;;;;;;;;;;;;;;;;;;;;;;;791:27;;657:166;;;;:::o',
  'source': 'pragma solidity ^0.4.24;\n\n/*\n  TEST token for tokensubscription.com\n */\n\nimport "openzeppelin-solidity/contracts/token/ERC20/ERC20Mintable.sol";\n\ncontract WasteCoin is ERC20Mintable {\n\n  string public name = "WasteCoin";\n  string public symbol = "WC";\n  uint8 public decimals = 18;\n\n  constructor() public { }\n\n}\n',
  'sourcePath': '/Users/kevinseagraves/Desktop/gitcoin/grants1337/contracts/WasteCoin.sol',
  'ast': {
    'absolutePath': '/Users/kevinseagraves/Desktop/gitcoin/grants1337/contracts/WasteCoin.sol',
    'exportedSymbols': {
      'WasteCoin': [
        507
      ]
    },
    'id': 508,
    'nodeType': 'SourceUnit',
    'nodes': [
      {
        'id': 490,
        'literals': [
          'solidity',
          '^',
          '0.4',
          '.24'
        ],
        'nodeType': 'PragmaDirective',
        'src': '0:24:1'
      },
      {
        'absolutePath': 'openzeppelin-solidity/contracts/token/ERC20/ERC20Mintable.sol',
        'file': 'openzeppelin-solidity/contracts/token/ERC20/ERC20Mintable.sol',
        'id': 491,
        'nodeType': 'ImportDirective',
        'scope': 508,
        'sourceUnit': 1536,
        'src': '73:71:1',
        'symbolAliases': [],
        'unitAlias': ''
      },
      {
        'baseContracts': [
          {
            'arguments': null,
            'baseName': {
              'contractScope': null,
              'id': 492,
              'name': 'ERC20Mintable',
              'nodeType': 'UserDefinedTypeName',
              'referencedDeclaration': 1535,
              'src': '168:13:1',
              'typeDescriptions': {
                'typeIdentifier': 't_contract$_ERC20Mintable_$1535',
                'typeString': 'contract ERC20Mintable'
              }
            },
            'id': 493,
            'nodeType': 'InheritanceSpecifier',
            'src': '168:13:1'
          }
        ],
        'contractDependencies': [
          683,
          1464,
          1535,
          1604
        ],
        'contractKind': 'contract',
        'documentation': null,
        'fullyImplemented': true,
        'id': 507,
        'linearizedBaseContracts': [
          507,
          1535,
          683,
          1464,
          1604
        ],
        'name': 'WasteCoin',
        'nodeType': 'ContractDefinition',
        'nodes': [
          {
            'constant': false,
            'id': 496,
            'name': 'name',
            'nodeType': 'VariableDeclaration',
            'scope': 507,
            'src': '187:32:1',
            'stateVariable': true,
            'storageLocation': 'default',
            'typeDescriptions': {
              'typeIdentifier': 't_string_storage',
              'typeString': 'string'
            },
            'typeName': {
              'id': 494,
              'name': 'string',
              'nodeType': 'ElementaryTypeName',
              'src': '187:6:1',
              'typeDescriptions': {
                'typeIdentifier': 't_string_storage_ptr',
                'typeString': 'string'
              }
            },
            'value': {
              'argumentTypes': null,
              'hexValue': '5761737465436f696e',
              'id': 495,
              'isConstant': false,
              'isLValue': false,
              'isPure': true,
              'kind': 'string',
              'lValueRequested': false,
              'nodeType': 'Literal',
              'src': '208:11:1',
              'subdenomination': null,
              'typeDescriptions': {
                'typeIdentifier': 't_stringliteral_e15addeb8e1b976e6201e59eff80fcbb9b94daef3a4622a66b70a882a7895345',
                'typeString': 'literal_string "WasteCoin"'
              },
              'value': 'WasteCoin'
            },
            'visibility': 'public'
          },
          {
            'constant': false,
            'id': 499,
            'name': 'symbol',
            'nodeType': 'VariableDeclaration',
            'scope': 507,
            'src': '223:27:1',
            'stateVariable': true,
            'storageLocation': 'default',
            'typeDescriptions': {
              'typeIdentifier': 't_string_storage',
              'typeString': 'string'
            },
            'typeName': {
              'id': 497,
              'name': 'string',
              'nodeType': 'ElementaryTypeName',
              'src': '223:6:1',
              'typeDescriptions': {
                'typeIdentifier': 't_string_storage_ptr',
                'typeString': 'string'
              }
            },
            'value': {
              'argumentTypes': null,
              'hexValue': '5743',
              'id': 498,
              'isConstant': false,
              'isLValue': false,
              'isPure': true,
              'kind': 'string',
              'lValueRequested': false,
              'nodeType': 'Literal',
              'src': '246:4:1',
              'subdenomination': null,
              'typeDescriptions': {
                'typeIdentifier': 't_stringliteral_1c2da66a392f0d4dcaf751e793f79945c04bfa4304c166e6f9da4a0722b3da26',
                'typeString': 'literal_string "WC"'
              },
              'value': 'WC'
            },
            'visibility': 'public'
          },
          {
            'constant': false,
            'id': 502,
            'name': 'decimals',
            'nodeType': 'VariableDeclaration',
            'scope': 507,
            'src': '254:26:1',
            'stateVariable': true,
            'storageLocation': 'default',
            'typeDescriptions': {
              'typeIdentifier': 't_uint8',
              'typeString': 'uint8'
            },
            'typeName': {
              'id': 500,
              'name': 'uint8',
              'nodeType': 'ElementaryTypeName',
              'src': '254:5:1',
              'typeDescriptions': {
                'typeIdentifier': 't_uint8',
                'typeString': 'uint8'
              }
            },
            'value': {
              'argumentTypes': null,
              'hexValue': '3138',
              'id': 501,
              'isConstant': false,
              'isLValue': false,
              'isPure': true,
              'kind': 'number',
              'lValueRequested': false,
              'nodeType': 'Literal',
              'src': '278:2:1',
              'subdenomination': null,
              'typeDescriptions': {
                'typeIdentifier': 't_rational_18_by_1',
                'typeString': 'int_const 18'
              },
              'value': '18'
            },
            'visibility': 'public'
          },
          {
            'body': {
              'id': 505,
              'nodeType': 'Block',
              'src': '306:3:1',
              'statements': []
            },
            'documentation': null,
            'id': 506,
            'implemented': true,
            'isConstructor': true,
            'isDeclaredConst': false,
            'modifiers': [],
            'name': '',
            'nodeType': 'FunctionDefinition',
            'parameters': {
              'id': 503,
              'nodeType': 'ParameterList',
              'parameters': [],
              'src': '296:2:1'
            },
            'payable': false,
            'returnParameters': {
              'id': 504,
              'nodeType': 'ParameterList',
              'parameters': [],
              'src': '306:0:1'
            },
            'scope': 507,
            'src': '285:24:1',
            'stateMutability': 'nonpayable',
            'superFunction': null,
            'visibility': 'public'
          }
        ],
        'scope': 508,
        'src': '146:166:1'
      }
    ],
    'src': '0:313:1'
  },
  'legacyAST': {
    'absolutePath': '/Users/kevinseagraves/Desktop/gitcoin/grants1337/contracts/WasteCoin.sol',
    'exportedSymbols': {
      'WasteCoin': [
        507
      ]
    },
    'id': 508,
    'nodeType': 'SourceUnit',
    'nodes': [
      {
        'id': 490,
        'literals': [
          'solidity',
          '^',
          '0.4',
          '.24'
        ],
        'nodeType': 'PragmaDirective',
        'src': '0:24:1'
      },
      {
        'absolutePath': 'openzeppelin-solidity/contracts/token/ERC20/ERC20Mintable.sol',
        'file': 'openzeppelin-solidity/contracts/token/ERC20/ERC20Mintable.sol',
        'id': 491,
        'nodeType': 'ImportDirective',
        'scope': 508,
        'sourceUnit': 1536,
        'src': '73:71:1',
        'symbolAliases': [],
        'unitAlias': ''
      },
      {
        'baseContracts': [
          {
            'arguments': null,
            'baseName': {
              'contractScope': null,
              'id': 492,
              'name': 'ERC20Mintable',
              'nodeType': 'UserDefinedTypeName',
              'referencedDeclaration': 1535,
              'src': '168:13:1',
              'typeDescriptions': {
                'typeIdentifier': 't_contract$_ERC20Mintable_$1535',
                'typeString': 'contract ERC20Mintable'
              }
            },
            'id': 493,
            'nodeType': 'InheritanceSpecifier',
            'src': '168:13:1'
          }
        ],
        'contractDependencies': [
          683,
          1464,
          1535,
          1604
        ],
        'contractKind': 'contract',
        'documentation': null,
        'fullyImplemented': true,
        'id': 507,
        'linearizedBaseContracts': [
          507,
          1535,
          683,
          1464,
          1604
        ],
        'name': 'WasteCoin',
        'nodeType': 'ContractDefinition',
        'nodes': [
          {
            'constant': false,
            'id': 496,
            'name': 'name',
            'nodeType': 'VariableDeclaration',
            'scope': 507,
            'src': '187:32:1',
            'stateVariable': true,
            'storageLocation': 'default',
            'typeDescriptions': {
              'typeIdentifier': 't_string_storage',
              'typeString': 'string'
            },
            'typeName': {
              'id': 494,
              'name': 'string',
              'nodeType': 'ElementaryTypeName',
              'src': '187:6:1',
              'typeDescriptions': {
                'typeIdentifier': 't_string_storage_ptr',
                'typeString': 'string'
              }
            },
            'value': {
              'argumentTypes': null,
              'hexValue': '5761737465436f696e',
              'id': 495,
              'isConstant': false,
              'isLValue': false,
              'isPure': true,
              'kind': 'string',
              'lValueRequested': false,
              'nodeType': 'Literal',
              'src': '208:11:1',
              'subdenomination': null,
              'typeDescriptions': {
                'typeIdentifier': 't_stringliteral_e15addeb8e1b976e6201e59eff80fcbb9b94daef3a4622a66b70a882a7895345',
                'typeString': 'literal_string "WasteCoin"'
              },
              'value': 'WasteCoin'
            },
            'visibility': 'public'
          },
          {
            'constant': false,
            'id': 499,
            'name': 'symbol',
            'nodeType': 'VariableDeclaration',
            'scope': 507,
            'src': '223:27:1',
            'stateVariable': true,
            'storageLocation': 'default',
            'typeDescriptions': {
              'typeIdentifier': 't_string_storage',
              'typeString': 'string'
            },
            'typeName': {
              'id': 497,
              'name': 'string',
              'nodeType': 'ElementaryTypeName',
              'src': '223:6:1',
              'typeDescriptions': {
                'typeIdentifier': 't_string_storage_ptr',
                'typeString': 'string'
              }
            },
            'value': {
              'argumentTypes': null,
              'hexValue': '5743',
              'id': 498,
              'isConstant': false,
              'isLValue': false,
              'isPure': true,
              'kind': 'string',
              'lValueRequested': false,
              'nodeType': 'Literal',
              'src': '246:4:1',
              'subdenomination': null,
              'typeDescriptions': {
                'typeIdentifier': 't_stringliteral_1c2da66a392f0d4dcaf751e793f79945c04bfa4304c166e6f9da4a0722b3da26',
                'typeString': 'literal_string "WC"'
              },
              'value': 'WC'
            },
            'visibility': 'public'
          },
          {
            'constant': false,
            'id': 502,
            'name': 'decimals',
            'nodeType': 'VariableDeclaration',
            'scope': 507,
            'src': '254:26:1',
            'stateVariable': true,
            'storageLocation': 'default',
            'typeDescriptions': {
              'typeIdentifier': 't_uint8',
              'typeString': 'uint8'
            },
            'typeName': {
              'id': 500,
              'name': 'uint8',
              'nodeType': 'ElementaryTypeName',
              'src': '254:5:1',
              'typeDescriptions': {
                'typeIdentifier': 't_uint8',
                'typeString': 'uint8'
              }
            },
            'value': {
              'argumentTypes': null,
              'hexValue': '3138',
              'id': 501,
              'isConstant': false,
              'isLValue': false,
              'isPure': true,
              'kind': 'number',
              'lValueRequested': false,
              'nodeType': 'Literal',
              'src': '278:2:1',
              'subdenomination': null,
              'typeDescriptions': {
                'typeIdentifier': 't_rational_18_by_1',
                'typeString': 'int_const 18'
              },
              'value': '18'
            },
            'visibility': 'public'
          },
          {
            'body': {
              'id': 505,
              'nodeType': 'Block',
              'src': '306:3:1',
              'statements': []
            },
            'documentation': null,
            'id': 506,
            'implemented': true,
            'isConstructor': true,
            'isDeclaredConst': false,
            'modifiers': [],
            'name': '',
            'nodeType': 'FunctionDefinition',
            'parameters': {
              'id': 503,
              'nodeType': 'ParameterList',
              'parameters': [],
              'src': '296:2:1'
            },
            'payable': false,
            'returnParameters': {
              'id': 504,
              'nodeType': 'ParameterList',
              'parameters': [],
              'src': '306:0:1'
            },
            'scope': 507,
            'src': '285:24:1',
            'stateMutability': 'nonpayable',
            'superFunction': null,
            'visibility': 'public'
          }
        ],
        'scope': 508,
        'src': '146:166:1'
      }
    ],
    'src': '0:313:1'
  },
  'compiler': {
    'name': 'solc',
    'version': '0.4.24+commit.e67f0147.Emscripten.clang'
  },
  'networks': {},
  'schemaVersion': '2.0.0',
  'updatedAt': '2018-10-02T22:00:23.641Z'
};
