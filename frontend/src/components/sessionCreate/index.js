import React from "react";
import {Button, Col, Form, FormGroup, FormText, Input, Label, Row} from "reactstrap";
import {connect} from "react-redux";
import {acceptJoinRequest, cancelJoinRequest, createSession, sendJoinRequest} from "../../actions";
import Container from "reactstrap/es/Container";


class SessionCreate extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      title: '',
      description: '',
      canSubmit: true
    };
  }

  handleTitleChange = (event) => {
    this.setState({title: event.target.value});
  };

  handleDescriptionChange = (event) => {
    this.setState({description: event.target.value});
  };

  handleSubmit = (event) => {
    this.setState({canSubmit: false}
    )
    this.props.dispatch(createSession({
      title: this.state.title,
      description: this.state.description
    }, this.props.history))
  };

  render() {
    console.log('cre')
    console.log(this.props)
    return (<Container>
        <Row>
          <Col md="6" className="pt-3">
            <h3>Find an Expert</h3>
            <Form onSubmit={this.handleSubmit}>
              <FormGroup>
                <Label for="title">Title</Label>
                <FormText color="muted">
                  What kind of help are you looking for?
                </FormText>
                <Input type="text" value={this.state.title} onChange={this.handleTitleChange}
                       placeholder="Help me, Obi-Wan Kenobi. You're my only hope."/>
              </FormGroup>
              <FormGroup>
                <Label for="description">Details</Label>
                <Input type="textarea" value={this.state.description} rows="5"
                       onChange={this.handleDescriptionChange}
                       placeholder="So, my planet got blown up and I'm trying to find some guidance on mounting
                       a rebel alliance in the face of superior enemy technology. Can anyone help?"
                />
                <FormText color="muted">

                </FormText>
              </FormGroup>
              <Button className="btn-gc-blue"
                      disabled={!this.state.canSubmit}
                      onClick={this.handleSubmit}>Submit</Button>
            </Form>
          </Col>
        </Row>
      </Container>
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
)(SessionCreate);
