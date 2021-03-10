import React from "react";

import "./breadcrumb.scss";

class Breadcrumb extends React.PureComponent {
  render() {
    return (
      <ul className="breadcrumb-ul">
        <li className="breadcrumb-li">
          <a href="/mycabinet/browse">Browse</a>
        </li>
        <li className="breadcrumb-li">
          <a href="/mycabinet/manage">Manage</a>
        </li>
      </ul>
    );
  }
}

export default Breadcrumb;
