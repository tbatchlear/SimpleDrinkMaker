// This file handles the UI when resetting the Password

import React, { Component } from "react";

import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import TextField from "@material-ui/core/TextField";
import Button from "@material-ui/core/Button";

import { passwordResetRequest } from "../../util/API";

import "./forgotPass.scss";

class resetPass extends Component {
  constructor() {
    super();
    this.state = {
      newPassword: "",
      confirmPassword: "",
      response: "",
    };
  }

  /**
   * Request when resetting password
   *
   * @param event
   * @public
   */
  handleSubmit = async (event) => {
    event.preventDefault();
    const userData = {
      newPassword: this.state.newPassword,
      token: this.props.match.params.token,
    };
    let status = await passwordResetRequest(userData);
    if (status.error) {
      this.setState({
        response: status.error,
      });
    }
  };

  handleChange = (event) => {
    this.setState({
      [event.target.name]: event.target.value,
    });
  };

  render() {
    return (
      <Grid container className="container">
        <Grid item sm />
        <Grid item sm style={{ marginTop: 200 }}>
          <Typography variant="h2">Reset Password</Typography>
          <form noValidate onSubmit={this.handleSubmit}>
            <TextField
              id="newPassword"
              name="newPassword"
              type="password"
              label="Enter new password"
              value={this.state.newPassword}
              variant="outlined"
              onChange={this.handleChange}
              fullWidth
            />
            <TextField
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              label="Confirm new password"
              value={this.state.confirmPassword}
              variant="outlined"
              style={{ marginTop: 10 }}
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
          </form>
          <div className="reset-fail">
            <small>{this.state.response}</small>
          </div>
        </Grid>
        <Grid item sm />
      </Grid>
    );
  }
}

export default resetPass;
