import React, { Component } from "react";
import GridList from "@material-ui/core/GridList";
import GridListTile from "@material-ui/core/GridListTile";
import RecipeCard from "../../components/card/card";
import { allRecipesRequest, filteredRecipesRequest, partialRecipesRequest } from "../../util/API";
import icon from "../../assets/images/SmoothieIcon.png";

import "./gridlist.scss";

class RecipeGridList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      recipes: [],
      pageType: this.props.pageType,
    };
  }
  returnRecipes = async () => {};

  async componentDidMount() {
    let resp = [];
    if (this.state.pageType === "filter") resp = await filteredRecipesRequest();
    else if (this.state.pageType === "partial") resp = await partialRecipesRequest();
    else resp = await allRecipesRequest();

    this.setState({ recipes: resp });
  }

  render() {
    if (this.state.recipes.length == 0 && (this.state.pageType === "filter" || this.state.pageType === "partial")) {
      return (
        <h1
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          Not enough ingredients to make any recipes. Add ingredients to your
          cabinet.
        </h1>
      );
    }
    return (
      <GridList
        cellHeight="auto"
        cols="auto"
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        {this.state.recipes.map((resp) => (
          <GridListTile>
            <RecipeCard
              name={resp.name}
              imgsrc={icon}
              instructions={resp.instructions}
              ingredients={resp.ingredients}
            />
          </GridListTile>
        ))}
      </GridList>
    );
  }
}

export default RecipeGridList;
