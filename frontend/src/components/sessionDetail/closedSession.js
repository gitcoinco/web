import React from "react";
import {Button} from "reactstrap";
import {connect} from "react-redux";
import {fundsClaimed, getContract} from "../../actions";
import BN from "bn.js";

class ClosedSession extends React.Component {
  handleClaimFunds = () => {
    console.log('claim tx...');

    let signature = this.props.session.signature;
    let r = signature.substr(0, 66);
    let s = '0x' + signature.substr(66, 64);
    let v = '0x' + signature.substr(130, 2);

    let web3 = this.props.web3Context.library;

    let contract = getContract(this.props.web3Context);
    contract.methods.closeChannel(
      this.props.session.channel_id,
      String(this.props.session.value), // TODO should be BN
      // web3.utils.toBN(this.props.session.value),
      [v, r, s]
    ).send({
      from: this.props.web3Context.account,
      gas: '300000', // https://github.com/trufflesuite/ganache-core/issues/26
    }).on('transactionHash', (hash) => {
      console.log('hash: ' + hash)
    }).on('confirmation', (confirmationNumber, receipt) => {
      this.props.dispatch(fundsClaimed(this.props.session.id, receipt.transactionHash))
    }).on('receipt', (receipt) => {
      console.log('receipt')
    });

  };

  render() {
    console.log('closed')
    console.log(this.props.web3Context)
    let child = <p>Host message... can expire channel if other party doesn't claim in x hours</p>;
    if (this.props.user.id === this.props.session.requested_by.id) {
      child = <p>Host message... can expire channel if other party doesn't claim in x hours</p>;
    } else {
      child = <Button onClick={this.handleClaimFunds} color="primary">Claim funds</Button>
    }
    let claimTxLink;
    if (this.props.session.claim_tx_hash !== null) {
      claimTxLink = <p><a
        href={"https://rinkeby.etherscan.io/tx/" + this.props.session.claim_tx_hash}>
        Claimed</a></p>
      child = <p></p>
    }
    return (
      <div>
        {child}
        {claimTxLink}

        Value: {this.props.session.value / 10 ** 18}
      </div>
    );
  }
}

const mapStateToProps = state => {
  return {
    session: state.data.session,
    user: state.data.user
  };
};

export default connect(
  mapStateToProps,
  null
)(ClosedSession);
