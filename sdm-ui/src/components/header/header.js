import React from "react";
import Logo from "../../assets/images/CabinetLogo.png";

import "./header.scss";

const Header = (props) => {
  let { sticky } = props;
  let viewable = "show slide-in";

  const toggleVisibility = (sticky) => {
    if (sticky) {
      viewable = "hide slide-out";
    }
  };

  toggleVisibility(sticky);

  return (
    <div id="header" className={viewable}>
      <span className="span-bold">Simple</span>
      <span className="span-thin">Drink</span>
      <img className="logo" src={Logo} alt="App Logo" />
      <span className="span-after">Maker</span>
    </div>
  );
};

export default Header;
