import React from "react";
import { Route, Redirect } from "react-router-dom";
import { authenticate } from "./API";

class PrivateRoute extends React.Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      isAuthenticated: false,
      isLoading: true,
      user: null,
    };
  }

  /*
  Validate the token stored in local storage against the backend API, to make sure it 
  is actually valid. 
  */
  async componentDidMount() {
    let authUser = await authenticate();
    if (authUser) {
      this.setState({
        isAuthenticated: true,
        isLoading: false,
        user: authUser,
      });
    } else {
      this.setState({
        isAuthenticated: false,
        isLoading: false,
        user: null,
      });
    }
  }

  render() {
    if (this.state.isLoading) {
      return null;
    } else {
      if (this.state.isAuthenticated) {
        return (
          <Route
            render={(props, ...rest) => (
              <this.props.component
                user={this.state.user}
                {...props}
                {...rest}
              />
            )}
          />
        );
      } else {
        return (
          <Redirect
            to={{ pathname: "/", state: { from: this.props.location } }}
          />
        );
      }
    }
  }
}

export default PrivateRoute;
