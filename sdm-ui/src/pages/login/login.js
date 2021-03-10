// This file handles the UI to login into the Dashboard
import React, { Component } from "react";
import { Link } from "react-router-dom";

// MUI Stuff
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import TextField from "@material-ui/core/TextField";
import Button from "@material-ui/core/Button";

import { loginRequest } from "../../util/API";
import "./login.scss";

class login extends Component {
  constructor() {
    super();
    this.state = {
      loginId: "",
      password: "",
      response: "",
    };
  }
  /**
   * Request when logging in
   *
   * @param event
   * @public
   */
  handleSubmit = async (event) => {
    event.preventDefault();
    const userData = {
      loginId: this.state.loginId,
      password: this.state.password,
    };
    // hitting the login endpoint
    let status = await loginRequest(userData);
    if (status.message) {
      this.setState({
        response: status.message,
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
          <Typography variant="h2">Login</Typography>
          <form noValidate onSubmit={this.handleSubmit}>
            <TextField
              id="loginId"
              name="loginId"
              type="loginId"
              label="Username or Email"
              variant="outlined"
              value={this.state.loginId}
              onChange={this.handleChange}
              fullWidth
              style={{ marginTop: 10 }}
            />
            <TextField
              id="password"
              name="password"
              type="password"
              label="Password"
              variant="outlined"
              value={this.state.password}
              onChange={this.handleChange}
              fullWidth
              style={{ marginTop: 10 }}
            />
            <div className="sign-up">
              <Button type="submit" variant="contained" color="primary">
                Login
              </Button>
              <small>
                Don't have an account? <Link to="/signup">Sign up</Link> /{" "}
                <Link to="/forgot-password">Forgot Password</Link>
              </small>
            </div>
            <div className="login-error">
              <small>{this.state.response}</small>
            </div>
          </form>
        </Grid>
        <Grid item sm />
      </Grid>
    );
  }
}

export default login;
