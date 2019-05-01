import React from "react";
import {connect} from "react-redux";
import {Button, Col, Form, FormGroup, Input, Label, Row} from "reactstrap";
import {createSession} from "../../actions";


class SessionChat extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      text: 'test',
      canSubmit: true
    };
  }

  handleTextChange = (event) => {
    this.setState({text: event.target.value});
  };

  handleSubmit = (event) => {
    // this.setState({canSubmit: false}
    // )
    // this.props.dispatch(createSession({
    //   title: this.state.title,
    //   description: this.state.description
    // }, this.props.history))
  };


  render() {
    return (
      <div>
        <h2>Chat</h2>
        <Form onSubmit={this.handleSubmit}>
          <FormGroup>
            <Label for="description">Description</Label>
            <Input type="textarea" value="show messages"/>
          </FormGroup>
          <FormGroup>
            <Label for="title">Title</Label>
            <Input type="text" value={this.state.text} onChange={this.handleTextChange()}
                   placeholder=""/>
          </FormGroup>

          <Button color="primary" disabled={!this.state.canSubmit} onClick={this.handleSubmit}>Submit</Button>

        </Form>
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
)(SessionChat);
