import React from "react";

import "./sideNavMenu.scss";

const NavGroup = (props) => {
  const { href, pageType, noCustom, text, children } = props;

  let page = pageType;
  if (noCustom && pageType === "custom") page = "browse";
  const url = href ? href : `/mycabinet/${page}`;

  return (
    <div className="list-group">
      <a href={url}>
        <p>{text}</p>
      </a>
      {children}
    </div>
  );
};

export default NavGroup;
