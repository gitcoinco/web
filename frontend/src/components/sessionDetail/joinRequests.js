import React from "react";
import {Button, Col, Row} from "reactstrap";
import {connect} from "react-redux";
import {acceptJoinRequest, cancelJoinRequest, sendJoinRequest} from "../../actions";


class JoinRequests extends React.Component {

  constructor(props) {
    super(props);

    let joinRequestSent = false;
    props.joinRequests.map((request, index) => {
      if (props.user.id === request.profile.id) {
        joinRequestSent = true
      }
    });

    this.state = {
      joinRequestSent: joinRequestSent,
    };
  }

  handleAcceptJoinRequest = (joinRequest) => {
    this.props.dispatch(acceptJoinRequest(joinRequest))
  };

  handleCancelJoinRequest = (joinRequest) => {
    this.props.dispatch(cancelJoinRequest(joinRequest))
  };

  handleSendJoinRequest = () => {
    // this.setState({joinRequestSent: true})

    console.log(this.props);

    let msg = this.props.web3Context.library.utils.sha3('join');
    let sig = this.props.web3Context.library.eth.accounts.sign(msg, this.props.delegateAccount.privateKey);

    let joinRequest = {
      session_id: this.props.session.id,
      signature: sig.signature,
      main_address: this.props.web3Context.account,
      delegate_address: this.props.delegateAccount.address
    };
    this.props.dispatch(sendJoinRequest(joinRequest))

  };

  render() {
    let joinRequests = this.props.joinRequests.map((request, index) => {
      return <Row key={request.id} className="border m-3">
        <Col>
          <img className="rounded-circle img-thumbnail" width={64} src={request.profile.avatar_url}/>
        </Col>
        <Col className="my-auto">
          <p>
          {request.profile.handle}
          </p>
        </Col>
        <Col className="my-auto">
          {this.props.isOwner === true &&
          <Button color="gc-blue" className="my-auto"
                  onClick={this.handleAcceptJoinRequest.bind(this, request)}>Accept</Button>
          }
          {this.props.user.id === request.profile.id &&
          <Button color="gc-blue"
                  onClick={this.handleCancelJoinRequest.bind(this, request)}>Cancel</Button>
          }
        </Col>
      </Row>
    });
    return <div>

      <h2>Offers</h2>
      {this.props.isOwner === false && <p>
        <Button className="btn-gc-blue"
                disabled={this.state.joinRequestSent}
                onClick={this.handleSendJoinRequest.bind(this)}>Offer Expertise</Button>
      </p>}
      {joinRequests.length === 0 && <p>No offers yet</p>}
      {joinRequests.length > 0 && <>{joinRequests}</>}
    </div>
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
)(JoinRequests);
