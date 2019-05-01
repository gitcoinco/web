import React from "react";
import {Button, FormGroup} from "reactstrap";
import {connect} from "react-redux";
import {endSession} from "../../actions";

class ActiveSession extends React.Component {
  endSession = () => {
    // this.props.endSession()
    this.props.channelManager.closeChannel()
    this.props.dispatch(endSession(this.props.session.id))
  };

  render() {
    return (
      <div>
        {/*TODO DRY*/}
        <div className="float-right">
          <img className="rounded-circle img-thumbnail"
               width={64} src={this.props.session.accepted_interest.profile.avatar_url}/>
        </div>
        <h2 className="pb-4">Session with {this.props.session.accepted_interest.profile.handle}</h2>
        <hr/>

        Value: {Number(this.props.session.value / 10 ** 18).toFixed(4)}
        <br /><br />
        <Button className="mb-3"
          onClick={this.endSession} color="danger">End Session</Button>

      </div>
    );
  }
}

const mapStateToProps = state => {
  return {
    session: state.data.session,
    user: state.data.user,
    channelManager: state.data.channelManager,
  };
};

export default connect(
  mapStateToProps,
  null
)(ActiveSession);
