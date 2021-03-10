// This file handles the UI when forgetting the Password
import React, { Component } from "react";
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import TextField from "@material-ui/core/TextField";
import Button from "@material-ui/core/Button";
import { Link } from "react-router-dom";

import { passwordLinkRequest } from "../../util/API";
import "./forgotPass.scss";

class forgotPass extends Component {
  constructor() {
    super();
    this.state = {
      loginId: "",
      response: "",
    };
  }
  /**
   * Request when forgetting password
   *
   * @param event
   * @public
   */
  handleSubmit = async (event) => {
    event.preventDefault();
    const userData = {
      loginId: this.state.loginId,
    };
    let status = await passwordLinkRequest(userData);
    if (status.message) {
      this.setState({
        response: status.message,
      });
    }
  };

  handleChange = (event) => {
    this.setState({
      loginId: event.target.value,
    });
  };

  render() {
    return (
      <Grid container className="container">
        <Grid item sm />
        <Grid item sm style={{ marginTop: 200 }}>
          <Typography variant="h2">Account recovery</Typography>
          <form noValidate onSubmit={this.handleSubmit}>
            <TextField
              id="loginId"
              name="loginId"
              type="loginId"
              label="Enter your username or email address"
              value={this.state.loginId}
              variant="outlined"
              onChange={this.handleChange}
              fullWidth
            />
            <Button
              type="submit"
              variant="contained"
              color="primary"
              style={{ marginTop: 10 }}
            >
              Send
            </Button>
            <small>
              Return to <Link to="/">Log In</Link>
            </small>
          </form>
          <div className="reset-sent">
            <small>{this.state.response}</small>
          </div>
        </Grid>
        <Grid item sm />
      </Grid>
    );
  }
}

export default forgotPass;
