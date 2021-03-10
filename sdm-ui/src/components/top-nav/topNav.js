import React from "react";
import { Burger } from "../../components";
import cart from "../../assets/images/Cart.png";
import account from "../../assets/images/Account.png";

//CSS
import "./topNav.scss";

const TopNav = (props) => {
  const { toggleMenuHandler, open, user, sticky } = props;

  const logout = () => {
    localStorage.removeItem("token");
    window.location.href("/");
  };
  return (
    <div className="mainMenu">
      <div
        className="mainNav"
        style={sticky ? { position: "fixed" } : { position: "sticky" }}
      >
        <Burger open={open} setOpen={toggleMenuHandler}></Burger>
        <div className="centerMenu">
          <li className="hnav-item">
            <a
              className="hnav-item"
              href="/mycabinet/browse"
              title="Add Ingredients"
            >
              My Cabinet
            </a>
          </li>
          <li className="hnav-item">
            <a className="hnav-item" href="/recipes/all" title="View Recipes">
              Recipes
            </a>
          </li>
        </div>
        <div className="rightMenu">
          <li className="hnav-item">Welcome, {user ? user : "USER"}</li>
          <li className="hnav-item">
            <a
              className="hnav-item"
              id="whisk-shopping-list"
              title="Shopping List"
              href="#"
            >
              <img src={cart} alt="shopping cart" height="30px" />
            </a>
            {window.viewList()}
          </li>
          <li className="hnav-item">
            <a href="/" onClick={logout} title="Log Out">
              <img src={account} alt="account" height="30px" />
            </a>
          </li>
        </div>
      </div>
    </div>
  );
};

export default TopNav;
