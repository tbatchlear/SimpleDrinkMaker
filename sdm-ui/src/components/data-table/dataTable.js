import React, { Component } from "react";
import MUIDatable from "mui-datatables";
import { AddCart, AddCustom, Delete, Favorite, Quantity } from "./icons";
import {
  allIngredientsRequest,
  allUserIngredientsRequest,
  updateIngredientRequest,
  addCustomIngredientRequest,
  deleteIngredientRequest,
} from "../../util/API";

class DataTable extends Component {
  state = {
    allIngredients: [],
    customIngredients: [],
    defaultIngredients: [],
    customUserIngredients: [],
    defaultUserIngredients: [],
    allUserIngredients: [],
    pageType: this.props.pageType,
    search: this.props.search,
  };

  async componentDidMount() {
    if (this.state.pageType === "browse") {
      let userIngredients = await allUserIngredientsRequest();
      const allUserIngredients = userIngredients.default.concat(
        userIngredients.custom
      );
      this.setState({
        defaultUserIngredients: userIngredients.default,
        customUserIngredients: userIngredients.custom,
        allUserIngredients: allUserIngredients,
      });
    } else {
      let ingredients = await allIngredientsRequest();
      const allIngredients = ingredients.default.concat(ingredients.custom);
      this.setState({
        customIngredients: ingredients.custom,
        defaultIngredients: ingredients.default,
        allIngredients: allIngredients,
      });
    }
  }

  updateIngredient = (ingredient) => {
    if (ingredient.quantity < 0) {
      ingredient.quantity = 0;
      return;
    }
    this.setState({
      allIngredients: this.state.allIngredients,
    });
    updateIngredientRequest(
      ingredient.name,
      ingredient.favorite,
      ingredient.quantity
    );
  };

  addCustomIngredient = async () => {
    const name = prompt("Enter a Custom Ingredient Name");
    const type = prompt("Enter the Type of Ingredient");
    let response = await addCustomIngredientRequest(name, type);
    if (response.message) {
      let ingredients = await allUserIngredientsRequest();
      this.setState({
        customIngredients: ingredients.custom,
      });
    } else if (response.error) alert(response.error);
  };

  deleteIngredient = async (remove) => {
    let tempCustomIngredients = this.state.customIngredients.filter((keep) => {
      return keep.name !== remove.name;
    });
    let tempUserIngredients = this.state.allUserIngredients.filter((keep) => {
      return keep.name !== remove.name;
    });
    this.setState({
      customIngredients: tempCustomIngredients,
      allUserIngredients: tempUserIngredients,
    });
    deleteIngredientRequest(remove.name);
  };

  preserveSearch = (search) => {
    this.setState({
      search: search,
    });
  };

  getTableData = () => {
    const customIngredient = () => {
      return AddCustom(this.addCustomIngredient);
    };

    const {
      allIngredients,
      allUserIngredients,
      customIngredients,
      pageType,
    } = this.state;

    let delaySearch = null;
    let data = {
      title: "Manage All Supported Ingredients",
      columns: ["Ingredient", "Type", "Quantity", "Favorite"],
      options: {
        filter: false,
        download: false,
        print: false,
        responsive: "scroll",
        selectableRows: "none",
        customToolbar: null,
        searchText: this.state.search ? this.state.search : "",
        onTableChange: (action, tableState) => {
          if (action === "search") {
            if (delaySearch) clearTimeout(delaySearch);
            delaySearch = setTimeout(() => {
              this.preserveSearch(tableState.searchText);
            }, 500);
          }
        },
      },
      data: [],
    };
    let source = "";
    switch (pageType) {
      case "manage":
        source = allIngredients;
        break;
      case "browse":
        data.title = "Browse Ingredients in Cabinet";
        data.columns.push("Delete", "Add to Cart");
        source = allUserIngredients;
        break;
      case "custom":
        data.title = "Custom Ingredients";
        data.columns.push("Delete");
        source = customIngredients;
        data.options.customToolbar = customIngredient;
        break;
      default:
        source = allIngredients;
    }
    data.data = source.map((ingredient) => {
      return [
        ingredient.name,
        ingredient.type,
        Quantity(ingredient, this.updateIngredient),
        Favorite(ingredient, this.updateIngredient),
        Delete(ingredient, pageType, this.deleteIngredient),
        AddCart(ingredient, pageType),
      ];
    });
    return data;
  };

  render() {
    const { title, options, columns, data } = this.getTableData();
    return (
      <MUIDatable
        title={title}
        options={options}
        columns={columns}
        data={data}
      />
    );
  }
}

export default DataTable;
