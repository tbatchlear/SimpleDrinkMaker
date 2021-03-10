import React from "react";
import "./sideNavMenu.scss";

const NavItem = (props) => {
  const { children, pageType, noCustom, term, href } = props;

  let page = pageType;
  if (noCustom && pageType === "custom") page = "browse";
  const url = href ? href : `/mycabinet/${page}?search=${term}`;

  return (
    <li className="list-item">
      <a href={url}>{children}</a>
    </li>
  );
};

export default NavItem;
