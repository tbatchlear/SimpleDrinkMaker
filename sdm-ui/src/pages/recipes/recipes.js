import React, { Component } from "react";
import {
  TopNav,
  Header,
  SideNav,
  NavGroup,
  NavItem,
  RecipeGridList,
} from "../../components";
import { throttle } from "lodash";

import "./recipes.scss";

class Recipes extends Component {
  constructor(props) {
    super(props);
    this.state = {
      menuOpen: false,
      isSticky: false,
      user: this.props.user,
    };

    this.setSticky = (isSticky) => {
      this.setState(() => ({
        isSticky,
      }));
    };

    this.handleClick = () => {
      this.setState((state) => ({
        menuOpen: !state.menuOpen,
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
    const pageType = this.props.location.pathname.split("/recipes/")[1];
    return (
      <div>
        <Header sticky={this.state.isSticky}></Header>
        <TopNav
          open={this.state.menuOpen}
          sticky={this.state.isSticky}
          user={this.state.user}
          toggleMenuHandler={this.handleClick}
        ></TopNav>
        <SideNav open={this.state.menuOpen}>
          <NavGroup href="/recipes/all" text="All Recipes">
            <NavItem></NavItem>
          </NavGroup>
          <NavGroup href="/recipes/filter" text="Filtered by Cabinet">
            <NavItem></NavItem>
          </NavGroup>
          <NavGroup href="/recipes/partial" text="Filtered by Partial Match to Cabinet">
            <NavItem></NavItem>
          </NavGroup>
        </SideNav>
        <div className="recipeGrid">
          <RecipeGridList pageType={pageType} />
        </div>
      </div>
    );
  }
}

export default Recipes;
