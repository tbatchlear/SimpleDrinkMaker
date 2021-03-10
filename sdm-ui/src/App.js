import React, { Component } from "react";
import {
  BrowserRouter as Router,
  Route,
  Switch,
  Redirect,
} from "react-router-dom";
import { ThemeProvider as MuiThemeProvider } from "@material-ui/core/styles";
import createMuiTheme from "@material-ui/core/styles/createMuiTheme";
import themeObject from "./util/theme";
//import jwtDecode from "jwt-decode";

import "./App.css";
import login from "./pages/login/login";
import signUp from "./pages/signUp/signUp";
import forgotPass from "./pages/forgotPass/forgotPass";
import resetPass from "./pages/forgotPass/resetPass";
import MyCabinet from "./pages/myCabinet/myCabinet";
import Recipes from "./pages/recipes/recipes";
import PrivateRoute from "./util/privateRoute";
const theme = createMuiTheme(themeObject);

const handleRedirection = (props) =>
  localStorage.getItem("token") ? (
    <PrivateRoute component={MyCabinet} />
  ) : (
    <Redirect to="/" />
  );

class App extends Component {
  render() {
    return (
      <MuiThemeProvider theme={theme}>
        <Router>
          <div className="container">
            <Switch>
              <Route exact path="/" component={login} />
              <Route exact path="/signup" component={signUp} />
              <Route exact path="/forgot-password" component={forgotPass} />
              <Route exact path="/reset-pass/:token" component={resetPass} />
              <PrivateRoute path="/mycabinet/" component={MyCabinet} />
              <PrivateRoute path="/recipes/" component={Recipes} />
              <Route render={handleRedirection} />
            </Switch>
          </div>
        </Router>
      </MuiThemeProvider>
    );
  }
}

export default App;
