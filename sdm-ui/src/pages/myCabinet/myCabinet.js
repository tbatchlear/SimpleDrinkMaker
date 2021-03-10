import React, { Component } from "react";
import throttle from "lodash";
import {
  Breadcrumb,
  DataTable,
  TopNav,
  Header,
  SideNav,
  NavGroup,
  NavItem,
} from "../../components";

import "./myCabinet.scss";

class LayoutPage extends Component {
  constructor(props) {
    super(props);
    this.state = {
      menuOpen: false,
      isSticky: false,
      user: this.props.user,
    };

    this.handleClick = () => {
      this.setState(() => ({
        menuOpen: !this.state.menuOpen,
      }));
    };

    this.setSticky = (isSticky, opacity) => {
      this.setState(() => ({
        isSticky,
        opacity,
      }));
    };

    this.handleScroll = () => {
      if (window.pageYOffset > 10) return this.setSticky(true);
      this.setSticky(false);
    };
  }

  componentDidMount() {
    window.addEventListener("scroll", throttle(this.handleScroll, 75));
  }

  componentWillUnmount() {
    window.removeEventListener("scroll", this.handleScroll);
  }

  render() {
    const { menuOpen, isSticky } = this.state;
    const pageType = this.props.location.pathname.split("/mycabinet/")[1];
    const search = this.props.location.search.split("=")[1];

    return (
      <div>
        <div>
          <Header sticky={isSticky}></Header>
          <TopNav
            open={menuOpen}
            sticky={isSticky}
            toggleMenuHandler={this.handleClick}
            user={this.state.user}
          ></TopNav>
        </div>
        <SideNav open={menuOpen}>
          <Breadcrumb></Breadcrumb>
          <NavGroup pageType={pageType} noCustom={true} text="All Ingredients">
            <NavItem pageType={pageType} noCustom={true} term="fruit">
              Fruits
            </NavItem>
            <NavItem pageType={pageType} noCustom={true} term="vegetable">
              Vegetables
            </NavItem>
            <NavItem pageType={pageType} noCustom={true} term="liquid">
              Liquids
            </NavItem>
            <NavItem pageType={pageType} noCustom={true} term="yogurt">
              Yogurts / Thickeners
            </NavItem>
            <NavItem pageType={pageType} noCustom={true} term="other">
              Other
            </NavItem>
          </NavGroup>
          <NavGroup pageType="custom" text="Custom">
            <NavItem pageType="custom" term="fruit">
              Fruits
            </NavItem>
            <NavItem pageType="custom" term="vegetable">
              Vegetables
            </NavItem>
            <NavItem pageType="custom" term="liquid">
              Liquids
            </NavItem>
            <NavItem pageType="custom" term="yogurt">
              Yogurts / Thickeners
            </NavItem>
            <NavItem pageType={pageType} term="other">
              Other
            </NavItem>
          </NavGroup>
        </SideNav>
        <div className={"content-wrapper"}>
          <DataTable pageType={pageType} search={search} />
        </div>
      </div>
    );
  }
}

export default LayoutPage;
