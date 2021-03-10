import React from "react";

import "./burger.scss";
import palette from "../../theme/palette.scss";

const Burger = (props) => {
  const { open, setOpen } = props;

  let stylesChild1 = open
    ? { transform: "rotate(45deg)", background: palette.primaryDarker }
    : { transform: "rotate(0)", background: palette.primary };

  let stylesChild2 = open
    ? {
        opacity: "0",
        transform: "translateX(20px)",
        background: palette.primaryDarker,
      }
    : {
        opacity: "1",
        transform: "translateX(0)",
        background: palette.primary,
      };

  let stylesChild3 = open
    ? { transform: "rotate(-45deg)", background: palette.primaryDarker }
    : { transform: "rotate(0)", background: palette.primary };

  return (
    <button className="burger-btn" onClick={() => setOpen(!open)}>
      <div style={stylesChild1} />
      <div style={stylesChild2} />
      <div style={stylesChild3} />
    </button>
  );
};

export default Burger;
