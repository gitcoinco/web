const Web3 = require('web3');
const PaymentChannels = artifacts.require("PaymentChannels");
const ethutils = require('ethereumjs-util');


// let tryCatch = require("./exceptions.js").tryCatch;
// let errTypes = require("./exceptions.js").errTypes;

const web3 = new Web3(Web3.givenProvider || "ws://localhost:8545");
const aliceMainAccount = web3.eth.accounts.privateKeyToAccount(
  '0x91938cb45eb51f9480246b3c88d82ff6a830f3328d3237997d8bb0210c07cb24');
const aliceDelegateAccount = web3.eth.accounts.privateKeyToAccount(
  '0xae6ae8e5ccbfb04590405997ee2d52d2b330726137b875053c36d94e974d162f');
const bobMainAccount = web3.eth.accounts.privateKeyToAccount(
  '0x5973cac7b1b9aa4cb30bc9f0cab1066a14b3c9537f9161051131a928182dc099');
const bobDelegateAccount = web3.eth.accounts.privateKeyToAccount(
  '0xc88b703fb08cbea894b6aeff5a544fb92e78a18e19814cd85da83b71f772aa6c');


console.log('Alice main: ' + aliceMainAccount.address);
console.log('Alice delegate: ' + aliceDelegateAccount.address);
console.log('Bob main: ' + bobMainAccount.address);
console.log('Bob delegate: ' + bobDelegateAccount.address);

contract("PaymentChannels", (accounts) => {
  it("test_start_session", async () => {
    // start the session as the host
    const contract = await PaymentChannels.deployed();
    let value = 1 * 10 ** 18;


    let bobHash = web3.utils.sha3('join');
    let bobSig = web3.eth.accounts.sign(
      bobHash,
      bobDelegateAccount.privateKey
    );

    let aliceBalance_0 = await web3.eth.getBalance(aliceMainAccount.address);
    let bobBalance_0 = await web3.eth.getBalance(bobMainAccount.address);

    let createRes = await contract.createChannel(
      aliceDelegateAccount.address,
      bobMainAccount.address,
      bobDelegateAccount.address,
      [bobSig.v, bobSig.r, bobSig.s],
      1000,
      {from: aliceMainAccount.address, value: value}
    );

    let aliceBalance_1 = await web3.eth.getBalance(aliceMainAccount.address);
    let bobBalance_1 = await web3.eth.getBalance(bobMainAccount.address);

    let channelID = createRes.logs[0].args.id;
    console.log(channelID)

    let stringBytes = web3.utils.hexToBytes(web3.utils.toHex('close_channel'));
    let stringBytesPadded = ethutils.setLengthRight(stringBytes, 32);
    let channelIdBytes = web3.utils.hexToBytes(web3.utils.toHex(channelID));
    let channelIdBytesPadded = ethutils.setLengthRight(channelIdBytes, 32);

    let aliceHash = web3.utils.soliditySha3(
      web3.utils.bytesToHex(channelIdBytesPadded),
      web3.utils.bytesToHex(stringBytesPadded),
      web3.utils.toBN(value),
    );

    let aliceSig = web3.eth.accounts.sign(
      aliceHash,
      aliceDelegateAccount.privateKey
    )

    let closeRes = await contract.closeChannel(
      channelID,
      web3.utils.toBN(value),
      [aliceSig.v, aliceSig.r, aliceSig.s],
      {from: bobMainAccount.address}
    )

    let aliceBalance_2 = await web3.eth.getBalance(aliceMainAccount.address);
    let bobBalance_2 = await web3.eth.getBalance(bobMainAccount.address);

    const createGasUsed = web3.utils.toBN(createRes.receipt.gasUsed);
    const createTx = await web3.eth.getTransaction(createRes.tx);
    const createGasPrice = web3.utils.toBN(createTx.gasPrice);
    const createGasCost = createGasPrice.mul(createGasUsed);

    const closeGasUsed = web3.utils.toBN(closeRes.receipt.gasUsed);
    const closeTx = await web3.eth.getTransaction(closeRes.tx);
    const closeGasPrice = web3.utils.toBN(closeTx.gasPrice);
    const closeGasCost = closeGasUsed.mul(closeGasPrice);

    if (closeRes.logs[3].args[0] === closeRes.logs[0].args[0]) {
      console.log('works')
    }

    assert.equal(web3.utils.toBN(aliceBalance_0).sub(createGasCost).sub(web3.utils.toBN(value)).toString(), aliceBalance_2)
    assert.equal(web3.utils.toBN(bobBalance_0).sub(closeGasCost).add(web3.utils.toBN(value)).toString(), bobBalance_2)

    // assert.equal(res.logs[0].args.sender, player1MainAccount.address)


    // let sig = web3.eth.accounts.sign(
    //   getDelegationHash(player1MainAccount.address, web3),
    //   player1BurnerAccount.privateKey
    // );
    // let delegateResult = await gameContract.delegate(
    //   player1BurnerAccount.address, sig.v, sig.r, sig.s
    // );
    //
    // let mainAddress = await gameContract.delegates(player1BurnerAccount.address);
    // assert.equal(mainAddress, player1MainAccount.address);
    //
    // // now remove the delegation
    // await gameContract.undelegate(player1BurnerAccount.address);
    // let zeroAddress = await gameContract.delegates(player1BurnerAccount.address);
    // assert.equal(zeroAddress, '0x0000000000000000000000000000000000000000');

  });


});
