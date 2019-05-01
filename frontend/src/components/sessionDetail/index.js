import React from 'react';
import {Button, Col, Container, Row} from "reactstrap";
import Websocket from "react-websocket";

import {STATUS_ACTIVE, STATUS_CLOSED, STATUS_OPEN, STATUS_READY} from "../../constants";
import {PaymentChannelManager} from "../../paymentChannel";
import {connect} from "react-redux";
import {endSession, initApp, initWeb3, requestSessionTicket, sendSessionTicket} from "../../actions";
import {SESSION_UPDATE_RECEIVED} from "../../actions/types";
import OpenSession from './openSession'
import ReadySession from './readySession'
import ClosedSession from './closedSession'
import ActiveSession from './activeSession'
import SessionChat from './sessionChat'
import {useWeb3Context, Web3Consumer} from "web3-react";


class SessionDetail extends React.Component {

  constructor(props) {
    super(props);

    // let context = useWeb3Context();
    // console.log('c')
    // console.log(context);


    this.state = {
      websocketConnected: false,
      // TODO better fix - give each message a timestamp and ignore updates that have been processed
      ignoreSessionUpdates: false // workaround for bug with session going back into active state
    };
  }

  onChannelTimeout = () => {
    console.log('app timeout')
  };

  handleRequestSessionTicket = (ticketRequest) => {
    this.props.dispatch(requestSessionTicket(ticketRequest))
  };

  // endSession = () => {
  //   // TODO this could be removed if I made the channel manager available to thunks
  //   this.channelManager.closeChannel();
  //   this.props.dispatch(endSession(this.props.session.id))
  // };

  componentDidMount() {
    const sessionId = this.props.match.params.id; // TODO get from router params
    console.log('session ' + sessionId)

    let channelManager = new PaymentChannelManager(
      sessionId,
      this.onChannelTimeout,
      this.handleRequestSessionTicket
    );

    this.props.dispatch(initApp(sessionId, channelManager));
    // this.props.dispatch(initWeb3(this.props.web3Context));

    this.props.web3Context.setFirstValidConnector(['MetaMask']).then((res) => {
      console.log('init')
      console.log(this.props.web3Context)
      console.log(res)
    })

  }

  handleWebsocketMessage(data) {
    // handle websocket actions
    let result = JSON.parse(data);

    console.log('websocket received')
    console.log(result)

    switch (result.type) {
      case "session_update":
        // this.setState({session: result.data});
        // if (!this.state.ignoreSessionUpdates) {
          this.props.dispatch({type: SESSION_UPDATE_RECEIVED, data: result.data});
        // }
        break;

      case "ticket_request":
        let ticket = this.props.channelManager.ticketRequestReceived(
          result.data, this.props.web3Context.library, this.props.delegateAccount.privateKey
        );
        this.props.dispatch(sendSessionTicket(ticket))
        break;

      case "send_ticket":
        this.props.channelManager.ticketReceived(result.data);
        // TODO Send ticket receipt message here to confirm delivery
        break;

      case "session_started":

        if (this.props.session.status === STATUS_CLOSED) {
          console.log('not restarting closed session')
          return;
        }

        let isPayer = (this.props.user.id === result.data.session.requested_by.id);
        console.log('starting payment flow - isPayer: ' + isPayer);
        this.props.channelManager.openChannel(
          result.data.session.channel_id,
          isPayer
        );
        this.props.dispatch({type: SESSION_UPDATE_RECEIVED, data: result.data.session});
        break;

      case "session_ended":
        console.log('stopping payment flow')
        this.props.channelManager.closeChannel();
        this.setState({ignoreSessionUpdates: true})

        this.props.dispatch({type: SESSION_UPDATE_RECEIVED, data: result.data.session});
        break;
      default:
        return
    }
  }

  onOpen(data) {
    this.setState({websocketConnected: true})
  }

  render() {
    console.log(this.state);
    console.log('app')
    // console.log(this.props.web3Context);


    if (this.props.session === undefined) {
      return <div>Loading...</div>
    }

    let child;

    switch (this.props.session.status) {
      case STATUS_OPEN:
        child = <OpenSession/>
        break;
      case STATUS_READY:
        child = <ReadySession/>
        break;
      case STATUS_ACTIVE:
        child = <ActiveSession/>;
        break;
      case STATUS_CLOSED:
        child = <Web3Consumer>
          {context =>
            <ClosedSession
              web3Context={context}
            />
          }
        </Web3Consumer>
        ;
        break;
      default:
        child = <p>Unknown state</p>
    }

    return <div className="App">

      <Websocket url={'ws://localhost/ws/experts/sessions/' + this.props.match.params.id + '/'}
                 onMessage={this.handleWebsocketMessage.bind(this)}
                 onOpen={this.onOpen.bind(this)}
      />
      {this.state.websocketConnected || <p>Connecting...</p>}
      {this.props.user !== undefined && <Container>
        <Row>
          <Col md="5" className="border pt-1 m-3">
            <div className="float-right">
              <img className="rounded-circle img-thumbnail"
                   width={64} src={this.props.session.requested_by.avatar_url}/>
            </div>
            <h2 className="pb-4">{this.props.session.title}</h2>
            <hr/>
            <p style={{"whiteSpace": "pre-line"}}>{this.props.session.description}</p>
          </Col>
          <Col md="5" className="border pt-1 m-3">{child}</Col>
        </Row>
      </Container>}
    </div>
  }
}


const mapStateToProps = state => {
  return {
    session: state.data.session,
    user: state.data.user,
    channelManager: state.data.channelManager,
    delegateAccount: state.data.delegateAccount
  };
};

export default connect(
  mapStateToProps,
  null
)(SessionDetail);
