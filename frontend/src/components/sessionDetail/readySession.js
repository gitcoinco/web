import React from "react";
import {connect} from "react-redux";
import {Button, Col, FormGroup, FormText, Input, Label} from "reactstrap";
import {getContract, startSession, startSessionConfirmed} from "../../actions";
import {Web3Consumer} from "web3-react";
import Slider from 'react-rangeslider'


class HostControls extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      value: '1'
    }
  }

  // Host has selected an expert. Host should start the session by funding the channel
  startSession = () => {

    let accepted = this.props.session.accepted_interest;
    let r = accepted.signature.substr(0, 66);
    let s = '0x' + accepted.signature.substr(66, 64);
    let v = '0x' + accepted.signature.substr(130, 2);

    console.log(this.props.delegateAccount.address,
      accepted.main_address,
      accepted.delegate_address)
    console.log(v, r, s);
    console.log(this.props.web3Context.account);

    let contract = getContract(this.props.web3Context);
    contract.methods.createChannel(
      this.props.delegateAccount.address,
      accepted.main_address,
      accepted.delegate_address,
      [v, r, s],
      1000
    ).send({
      from: this.props.web3Context.account,
      gas: '300000', // https://github.com/trufflesuite/ganache-core/issues/26
      value: 1 * 10 ** 18
    }).on('transactionHash', (hash) => {
      console.log('hash: ' + hash)
    }).on('confirmation', (confirmationNumber, receipt) => {
      console.log('confirmed');
      console.log(receipt);
      this.props.dispatch(startSessionConfirmed(
        this.props.session.id,
        receipt.transactionHash,
        receipt.events.ChannelOpened.returnValues.id
      ));

    }).on('receipt', (receipt) => {
      console.log('receipt')
      console.log(receipt)
    });

  };

  handleValueChange = (event) => {
    this.setState({value: event.target.value})
  };

  render() {
    console.log('ctrl')
    // console.log(this.props);
    return (
      <div className="my-auto">
        <FormGroup>
          {/*TODO DRY*/}
          <div className="float-right">
            <img className="rounded-circle img-thumbnail"
                 width={64} src={this.props.session.accepted_interest.profile.avatar_url}/>
          </div>
          <h2 className="pb-4">Session with {this.props.session.accepted_interest.profile.handle}</h2>
          <hr/>
          <Label>Deposit amount</Label>
          <FormText color="muted">
            Deposit funds for the session. Unspent funds will be returned at the end.
          </FormText>
          <Input type="number" value={this.state.value} onChange={this.handleValueChange}
                 placeholder="Deposit amount"/>
        </FormGroup>
        <Button color="gc-blue" className="mb-3"
                onClick={this.startSession.bind(this)}>Start Session</Button>
        {/*show slider for how much to lock into channel based on expert's rate*/}

      </div>
    );
  }
}

class GuestControls extends React.Component {
  render() {
    return (
      <div>
        <div className="float-right">
          <img className="rounded-circle img-thumbnail"
               width={64} src={this.props.session.accepted_interest.profile.avatar_url}/>
        </div>
        <h2 className="pb-4">Session with {this.props.session.accepted_interest.profile.handle}</h2>
        <hr/>
        Waiting for {this.props.session.requested_by.handle} to start the session
      </div>
    );
  }
}


class ReadySession extends React.Component {

  render() {
    // let session = this.props.session;
    // let user = this.props.user;

    let controls;
    if (this.props.user.id === this.props.session.requested_by.id) {
      controls =
        <Web3Consumer>
          {context =>
            <HostControls
              user={this.props.user}
              session={this.props.session}
              dispatch={this.props.dispatch}
              contract={this.props.contract}
              web3Context={context}
              delegateAccount={this.props.delegateAccount}
            />
          }
        </Web3Consumer>

    } else {
      // TODO should check user is guest, and not just 'not owner'
      controls = <GuestControls
        user={this.props.user}
        session={this.props.session}
        dispatch={this.props.dispatch}
      />
    }
    return (
      <div>
        {controls}
      </div>
    );
  }
}

const mapStateToProps = state => {
  return {
    session: state.data.session,
    user: state.data.user,
    delegateAccount: state.data.delegateAccount

  };
};

export default connect(
  mapStateToProps,
  null
)(ReadySession);
