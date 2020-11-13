var _selectedAccount = '0x8ff5c070e1f9bc771fc65132086e6e220bcfd989';
var _tokenAddress = '0x6b175474e89094c44da98b954eedeac495271d0f';// DAI
const _token_contract = new web3.eth.Contract(token_abi, _tokenAddress);
const _to = bounty_address();

_token_contract.methods.allowance(_selectedAccount, _to).call({from: selectedAccount}, (error, result) => {
if (error || Number(result) == 0) {
  isTokenAuthed = false;
}
console.log(result)
});

