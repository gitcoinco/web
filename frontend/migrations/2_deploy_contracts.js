var PaymentChannels = artifacts.require("PaymentChannels");

module.exports = function (deployer, network, accounts) {
  deployer.deploy(PaymentChannels)
    .then(function () {
      return PaymentChannels.new();
    }).then(async function (instance) {
    }
  );
};
