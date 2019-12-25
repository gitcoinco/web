# -*- coding: utf-8 -*-
"""Define the Grant ABI.

Copyright (C) 2018 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
abi_v1 = [{'constant': True,
  'inputs': [],
  'name': 'requiredGasPrice',
  'outputs': [{'name': '', 'type': 'uint256'}],
  'payable': False,
  'stateMutability': 'view',
  'type': 'function'},
 {'constant': True,
  'inputs': [],
  'name': 'requiredTokenAmount',
  'outputs': [{'name': '', 'type': 'uint256'}],
  'payable': False,
  'stateMutability': 'view',
  'type': 'function'},
 {'constant': True,
  'inputs': [],
  'name': 'requiredToAddress',
  'outputs': [{'name': '', 'type': 'address'}],
  'payable': False,
  'stateMutability': 'view',
  'type': 'function'},
 {'constant': True,
  'inputs': [],
  'name': 'requiredPeriodSeconds',
  'outputs': [{'name': '', 'type': 'uint256'}],
  'payable': False,
  'stateMutability': 'view',
  'type': 'function'},
 {'constant': True,
  'inputs': [],
  'name': 'requiredTokenAddress',
  'outputs': [{'name': '', 'type': 'address'}],
  'payable': False,
  'stateMutability': 'view',
  'type': 'function'},
 {'constant': True,
  'inputs': [],
  'name': 'relayer',
  'outputs': [{'name': '', 'type': 'address'}],
  'payable': False,
  'stateMutability': 'view',
  'type': 'function'},
 {'constant': True,
  'inputs': [{'name': '', 'type': 'address'}],
  'name': 'extraNonce',
  'outputs': [{'name': '', 'type': 'uint256'}],
  'payable': False,
  'stateMutability': 'view',
  'type': 'function'},
 {'constant': True,
  'inputs': [],
  'name': 'author',
  'outputs': [{'name': '', 'type': 'address'}],
  'payable': False,
  'stateMutability': 'view',
  'type': 'function'},
 {'constant': True,
  'inputs': [{'name': '', 'type': 'bytes32'}],
  'name': 'nextValidTimestamp',
  'outputs': [{'name': '', 'type': 'uint256'}],
  'payable': False,
  'stateMutability': 'view',
  'type': 'function'},
 {'inputs': [{'name': '_toAddress', 'type': 'address'},
             {'name': '_tokenAddress', 'type': 'address'},
             {'name': '_tokenAmount', 'type': 'uint256'},
             {'name': '_periodSeconds', 'type': 'uint256'},
             {'name': '_gasPrice', 'type': 'uint256'},
             {'name': '_version', 'type': 'uint8'},
             {'name': '_relayer', 'type': 'address'}],
  'payable': False,
  'stateMutability': 'nonpayable',
  'type': 'constructor'},
 {'payable': True, 'stateMutability': 'payable', 'type': 'fallback'},
 {'anonymous': False,
  'inputs': [{'indexed': True, 'name': 'from', 'type': 'address'},
             {'indexed': True, 'name': 'to', 'type': 'address'},
             {'indexed': False, 'name': 'tokenAddress', 'type': 'address'},
             {'indexed': False, 'name': 'tokenAmount', 'type': 'uint256'},
             {'indexed': False, 'name': 'periodSeconds', 'type': 'uint256'},
             {'indexed': False, 'name': 'gasPrice', 'type': 'uint256'},
             {'indexed': False, 'name': 'nonce', 'type': 'uint256'}],
  'name': 'ExecuteSubscription',
  'type': 'event'},
 {'anonymous': False,
  'inputs': [{'indexed': True, 'name': 'from', 'type': 'address'},
             {'indexed': True, 'name': 'to', 'type': 'address'},
             {'indexed': False, 'name': 'tokenAddress', 'type': 'address'},
             {'indexed': False, 'name': 'tokenAmount', 'type': 'uint256'},
             {'indexed': False, 'name': 'periodSeconds', 'type': 'uint256'},
             {'indexed': False, 'name': 'gasPrice', 'type': 'uint256'},
             {'indexed': False, 'name': 'nonce', 'type': 'uint256'}],
  'name': 'CancelSubscription',
  'type': 'event'},
 {'constant': True,
  'inputs': [{'name': 'subscriptionHash', 'type': 'bytes32'},
             {'name': 'gracePeriodSeconds', 'type': 'uint256'}],
  'name': 'isSubscriptionActive',
  'outputs': [{'name': '', 'type': 'bool'}],
  'payable': False,
  'stateMutability': 'view',
  'type': 'function'},
 {'constant': True,
  'inputs': [{'name': 'from', 'type': 'address'},
             {'name': 'to', 'type': 'address'},
             {'name': 'tokenAddress', 'type': 'address'},
             {'name': 'tokenAmount', 'type': 'uint256'},
             {'name': 'periodSeconds', 'type': 'uint256'},
             {'name': 'gasPrice', 'type': 'uint256'},
             {'name': 'nonce', 'type': 'uint256'}],
  'name': 'getSubscriptionHash',
  'outputs': [{'name': '', 'type': 'bytes32'}],
  'payable': False,
  'stateMutability': 'view',
  'type': 'function'},
 {'constant': True,
  'inputs': [{'name': 'subscriptionHash', 'type': 'bytes32'},
             {'name': 'signature', 'type': 'bytes'}],
  'name': 'getSubscriptionSigner',
  'outputs': [{'name': '', 'type': 'address'}],
  'payable': False,
  'stateMutability': 'pure',
  'type': 'function'},
 {'constant': True,
  'inputs': [{'name': 'from', 'type': 'address'},
             {'name': 'to', 'type': 'address'},
             {'name': 'tokenAddress', 'type': 'address'},
             {'name': 'tokenAmount', 'type': 'uint256'},
             {'name': 'periodSeconds', 'type': 'uint256'},
             {'name': 'gasPrice', 'type': 'uint256'},
             {'name': 'nonce', 'type': 'uint256'},
             {'name': 'signature', 'type': 'bytes'}],
  'name': 'isSubscriptionReady',
  'outputs': [{'name': '', 'type': 'bool'}],
  'payable': False,
  'stateMutability': 'view',
  'type': 'function'},
 {'constant': False,
  'inputs': [{'name': 'from', 'type': 'address'},
             {'name': 'to', 'type': 'address'},
             {'name': 'tokenAddress', 'type': 'address'},
             {'name': 'tokenAmount', 'type': 'uint256'},
             {'name': 'periodSeconds', 'type': 'uint256'},
             {'name': 'gasPrice', 'type': 'uint256'},
             {'name': 'nonce', 'type': 'uint256'},
             {'name': 'signature', 'type': 'bytes'}],
  'name': 'cancelSubscription',
  'outputs': [{'name': 'success', 'type': 'bool'}],
  'payable': False,
  'stateMutability': 'nonpayable',
  'type': 'function'},
 {'constant': False,
  'inputs': [{'name': 'from', 'type': 'address'},
             {'name': 'to', 'type': 'address'},
             {'name': 'tokenAddress', 'type': 'address'},
             {'name': 'tokenAmount', 'type': 'uint256'},
             {'name': 'periodSeconds', 'type': 'uint256'},
             {'name': 'gasPrice', 'type': 'uint256'},
             {'name': 'nonce', 'type': 'uint256'},
             {'name': 'signature', 'type': 'bytes'}],
  'name': 'executeSubscription',
  'outputs': [{'name': 'success', 'type': 'bool'}],
  'payable': False,
  'stateMutability': 'nonpayable',
  'type': 'function'},
 {'constant': False,
  'inputs': [],
  'name': 'endContract',
  'outputs': [],
  'payable': False,
  'stateMutability': 'nonpayable',
  'type': 'function'}]


abi_v0 = [{
    "constant": True,
    "inputs": [],
    "name": "requiredGasPrice",
    "outputs": [{
        "name": "",
        "type": "uint256"
    }],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
},  {
    "constant": True,
    "inputs": [],
    "name": "requiredTokenAmount",
    "outputs": [{
        "name": "",
        "type": "uint256"
    }],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
},  {
    "constant": True,
    "inputs": [],
    "name": "requiredToAddress",
    "outputs": [{
      "name": "",
      "type": "address"
    }],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
},  {
    "constant": True,
    "inputs": [],
    "name": "requiredPeriodSeconds",
    "outputs": [{
        "name": "",
        "type": "uint256"
    }],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
},  {
    "constant": True,
    "inputs": [],
    "name": "requiredTokenAddress",
    "outputs": [{
        "name": "",
        "type": "address"
    }],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
},  {
    "constant": True,
    "inputs": [],
    "name": "owner",
    "outputs": [{
        "name": "",
        "type": "address"
    }],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
},  {
    "constant": True,
    "inputs": [],
    "name": "contractVersion",
    "outputs": [{
        "name": "",
        "type": "uint8"
    }],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
},  {
    "constant": True,
    "inputs": [{
        "name": "",
        "type": "address"
    }],
    "name": "extraNonce",
    "outputs": [{
        "name": "",
        "type": "uint256"
    }],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
},  {
    "constant": True,
    "inputs": [{
        "name": "",
        "type": "bytes32"
    }],
    "name": "nextValidTimestamp",
    "outputs": [{
        "name": "",
        "type": "uint256"
    }],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
},  {
    "inputs": [{
        "name": "_toAddress",
        "type": "address"
    },  {
        "name": "_tokenAddress",
        "type": "address"
    },  {
        "name": "_tokenAmount",
        "type": "uint256"
    },  {
        "name": "_periodSeconds",
        "type": "uint256"
    },  {
        "name": "_gasPrice",
        "type": "uint256"
    },  {
        "name": "_version",
        "type": "uint8"
    }],
    "payable": False,
    "stateMutability": "nonpayable",
    "type": "constructor"
},  {
    "payable": True,
    "stateMutability": "payable",
    "type": "fallback"
},  {
    "anonymous": False,
    "inputs": [{
        "indexed": True,
        "name": "from",
        "type": "address"
    },  {
        "indexed": True,
        "name": "to",
        "type": "address"
    },  {
        "indexed": False,
        "name": "tokenAddress",
        "type": "address"
    },  {
        "indexed": False,
        "name": "tokenAmount",
        "type": "uint256"
    },  {
        "indexed": False,
        "name": "periodSeconds",
        "type": "uint256"
    },  {
        "indexed": False,
        "name": "gasPrice",
        "type": "uint256"
    },  {
        "indexed": False,
        "name": "nonce",
        "type": "uint256"
    }],
    "name": "ExecuteSubscription",
    "type": "event"
},  {
    "anonymous": False,
    "inputs": [{
        "indexed": True,
        "name": "from",
        "type": "address"
    },  {
        "indexed": True,
        "name": "to",
        "type": "address"
    },  {
        "indexed": False,
        "name": "tokenAddress",
        "type": "address"
    },  {
        "indexed": False,
        "name": "tokenAmount",
        "type": "uint256"
    },  {
        "indexed": False,
        "name": "periodSeconds",
        "type": "uint256"
    },  {
        "indexed": False,
        "name": "gasPrice",
        "type": "uint256"
    },  {
        "indexed": False,
        "name": "nonce",
        "type": "uint256"
    }],
    "name": "CancelSubscription",
    "type": "event"
},  {
    "anonymous": False,
    "inputs": [{
        "indexed": False,
        "name": "oldOwner",
        "type": "address"
    },  {
        "indexed": False,
        "name": "newOwner",
        "type": "address"
    }],
    "name": "ownershipChanged",
    "type": "event"
},  {
    "constant": False,
    "inputs": [{
        "name": "_newOwner",
        "type": "address"
    }],
    "name": "changeOwnership",
    "outputs": [],
    "payable": False,
    "stateMutability": "nonpayable",
    "type": "function"
},  {
    "constant": True,
    "inputs": [{
        "name": "subscriptionHash",
        "type": "bytes32"
    },  {
        "name": "gracePeriodSeconds",
        "type": "uint256"
    }],
    "name": "isSubscriptionActive",
    "outputs": [{
        "name": "",
        "type": "bool"
    }],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
},  {
    "constant": True,
    "inputs": [{
        "name": "from",
        "type": "address"
    },  {
        "name": "to",
        "type": "address"
    },  {
        "name": "tokenAddress",
        "type": "address"
    },  {
        "name": "tokenAmount",
        "type": "uint256"
    },  {
        "name": "periodSeconds",
        "type": "uint256"
    },  {
        "name": "gasPrice",
        "type": "uint256"
    },  {
        "name": "nonce",
        "type": "uint256"
    }],
    "name": "getSubscriptionHash",
    "outputs": [{
        "name": "",
        "type": "bytes32"
    }],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
},    {
    "constant": True,
    "inputs": [{
        "name": "subscriptionHash",
        "type": "bytes32"
    },  {
        "name": "signature",
        "type": "bytes"
    }],
    "name": "getSubscriptionSigner",
    "outputs": [{
        "name": "",
        "type": "address"
    }],
    "payable": False,
    "stateMutability": "pure",
    "type": "function"
},  {
    "constant": True,
    "inputs": [{
        "name": "from",
        "type": "address"
    },  {
        "name": "to",
        "type": "address"
    },  {
        "name": "tokenAddress",
        "type": "address"
    },  {
        "name": "tokenAmount",
        "type": "uint256"
    },  {
        "name": "periodSeconds",
        "type": "uint256"
    },  {
        "name": "gasPrice",
        "type": "uint256"
    },  {
        "name": "nonce",
        "type": "uint256"
    },  {
        "name": "signature",
        "type": "bytes"
    }],
    "name": "isSubscriptionReady",
    "outputs": [{
        "name": "",
        "type": "bool"
    }],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
},  {
    "constant": False,
    "inputs": [{
        "name": "from",
        "type": "address"
    },  {
        "name": "to",
        "type": "address"
    },  {
        "name": "tokenAddress",
        "type": "address"
    },  {
        "name": "tokenAmount",
        "type": "uint256"
    },  {
        "name": "periodSeconds",
        "type": "uint256"
    },  {
        "name": "gasPrice",
        "type": "uint256"
    },  {
        "name": "nonce",
        "type": "uint256"
    },  {
        "name": "signature",
        "type": "bytes"
    }],
    "name": "cancelSubscription",
    "outputs": [{
        "name": "success",
        "type": "bool"
    }],
    "payable": False,
    "stateMutability": "nonpayable",
    "type": "function"
},  {
    "constant": False,
    "inputs": [{
        "name": "from",
        "type": "address"
    },  {
        "name": "to",
        "type": "address"
    },  {
        "name": "tokenAddress",
        "type": "address"
    },  {
        "name": "tokenAmount",
        "type": "uint256"
    },  {
        "name": "periodSeconds",
        "type": "uint256"
    },  {
        "name": "gasPrice",
        "type": "uint256"
    },  {
        "name": "nonce",
        "type": "uint256"
    },  {
        "name": "signature",
        "type": "bytes"
    }],
    "name": "executeSubscription",
    "outputs": [{
        "name": "success",
        "type": "bool"
    }],
    "payable": False,
    "stateMutability": "nonpayable",
    "type": "function"
},  {
    "constant": False,
    "inputs": [],
    "name": "endContract",
    "outputs": [],
    "payable": False,
    "stateMutability": "nonpayable",
    "type": "function"
}]
