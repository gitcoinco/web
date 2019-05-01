import React from "react";
import {connect} from "react-redux";
import JoinRequests from "./joinRequests";
import {Web3Consumer} from "web3-react";

class OpenSession extends React.Component {
  // Waiting for people to join, and for host to accept
  render() {
    let session = this.props.session;
    let user = this.props.user;

    return (
      <div>
        <Web3Consumer>
          {context =>
            <JoinRequests
              joinRequests={session.interests}
              user={user}
              onAcceptJoinRequest={this.props.onAcceptJoinRequest}
              isOwner={user.id === session.requested_by.id}
              web3Context={context}
            />
          }
        </Web3Consumer>
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
)(OpenSession);
