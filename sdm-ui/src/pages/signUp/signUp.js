import React, { Component } from "react";
import { Link } from "react-router-dom";

// MUI Stuff
//import Alert from "@material-ui/lab/Alert";
import {
  //Snackbar,
  TextField,
  Typography,
  Grid,
  Button,
} from "@material-ui/core";

import "./signUp.scss";
import { registerRequest } from "../../util/API";

class signUp extends Component {
  constructor() {
    super();
    // state
    this.state = {
      username: null,
      email: null,
      password: null,
      confirmPassword: null,
      error: null,
      response: "",
    };
  }
  /**
   * Clicking to register a new account
   *
   * @param event
   * @public
   */
  handleSubmit = async (event) => {
    event.preventDefault();
    const newUserData = {
      username: this.state.username,
      email: this.state.email,
      password: this.state.password,
      confirmPassword: this.state.confirmPassword,
    };
    let status = await registerRequest(newUserData);
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
          <Typography variant="h2">Sign Up</Typography>
          <form onSubmit={this.handleSubmit}>
            <TextField
              id="username"
              name="username"
              type="username"
              label="Username"
              value={this.state.username || ""}
              fullWidth
              variant="outlined"
              onChange={this.handleChange}
              error={this.state.username === ""}
              helperText={
                this.state.username === "" ? "Please enter a username" : " "
              }
              required
            />
            <TextField
              id="email"
              name="email"
              type="email"
              label="Email"
              value={this.state.email || ""}
              fullWidth
              variant="outlined"
              onChange={this.handleChange}
              error={this.state.email === ""}
              helperText={
                this.state.email === "" ? "Please enter an email" : " "
              }
              required
            />
            <TextField
              id="password"
              name="password"
              type="password"
              label="Password"
              value={this.state.password || ""}
              fullWidth
              variant="outlined"
              onChange={this.handleChange}
              error={this.state.password === ""}
              helperText={
                this.state.password === "" ? "Please enter a password" : " "
              }
              required
            />
            <TextField
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              label="Confirm Password"
              value={this.state.confirmPassword || ""}
              fullWidth
              variant="outlined"
              onChange={this.handleChange}
              error={
                this.state.confirmPassword === "" ||
                this.state.confirmPassword !== this.state.password
              }
              helperText={
                this.state.confirmPassword !== this.state.password
                  ? "Passwords dont match"
                  : " "
              }
              required
            />
            <div className="sign-up">
              <Button type="submit" variant="contained" color="primary">
                Sign Up
              </Button>
              <small>
                Already have an account? <Link to="/">Log In</Link> /{" "}
                <Link to="/forgot-password">Forgot Password</Link>
              </small>
            </div>
            <div style={{ marginTop: 10 }}>
              <small style={{ color: "red" }}>{this.state.response}</small>
            </div>
          </form>
        </Grid>
        <Grid item sm />
      </Grid>
    );
  }
}

export default signUp;
