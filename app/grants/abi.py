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
abi_v0 = [{
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
      "name": "_version",
      "type": "uint8"
    }
  ],
  "payable": false,
  "stateMutability": "nonpayable",
  "type": "constructor"
},
{
  "payable": true,
  "stateMutability": "payable",
  "type": "fallback"
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
  "name": "CancelSubscription",
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
},
{
  "constant": false,
  "inputs": [],
  "name": "endContract",
  "outputs": [],
  "payable": false,
  "stateMutability": "nonpayable",
  "type": "function"
}]
