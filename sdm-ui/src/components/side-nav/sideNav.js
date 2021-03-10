import React from "react";

import "./sideNavMenu.scss";

const SideNav = (props) => {
  const { open, children } = props;
  let viewable = open ? "main-menu show" : "main-menu hide";
  return (
    <div className={viewable}>
      <ul>{children}</ul>
    </div>
  );
};

export default SideNav;
