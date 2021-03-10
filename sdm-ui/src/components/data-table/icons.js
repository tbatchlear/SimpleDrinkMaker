import React from "react";
import AddShoppingCartIcon from "@material-ui/icons/AddShoppingCart";
import FavoriteIcon from "@material-ui/icons/Favorite";
import FavoriteBorderIcon from "@material-ui/icons/FavoriteBorder";
import DeleteIcon from "@material-ui/icons/Delete";
import IconButton from "@material-ui/core/IconButton";
import Tooltip from "@material-ui/core/Tooltip";
import AddIcon from "@material-ui/icons/Add";
import { Input } from "@material-ui/core";

export const Delete = (ingredient, pageType, handler) => {
  if (pageType === "browse" || pageType === "custom") {
    return (
      <a
        href="/#"
        style={{ color: "grey" }}
        onClick={(event) => {
          event.preventDefault();
          handler(ingredient);
        }}
      >
        <DeleteIcon />
      </a>
    );
  }
};

export const Quantity = (ingredient, updater) => {
  return (
    <Input
      value={ingredient.quantity}
      type="number"
      onChange={(event) => {
        ingredient.quantity = event.target.value;
        updater(ingredient);
      }}
    />
  );
};

export const Favorite = (ingredient, updater) => {
  return (
    <a
      style={{ color: "red" }}
      href="/#"
      onClick={(event) => {
        event.preventDefault();
        ingredient.favorite =
          ingredient.favorite === "False" ? "True" : "False";
        updater(ingredient);
      }}
    >
      {ingredient.favorite === "True" ? (
        <FavoriteIcon />
      ) : (
        <FavoriteBorderIcon />
      )}
    </a>
  );
};

export const AddCustom = (callback) => {
  return (
    <Tooltip title={"Add Custom Ingredient"}>
      <IconButton onClick={callback}>
        <AddIcon />
      </IconButton>
    </Tooltip>
  );
};

export const AddCart = (ingredient, pageType) => {
  if (pageType === "browse") {
    return (
      <Tooltip title={"Add Ingrdient to Shopping List"}>
        <IconButton
          onClick={() =>
            window.addIngredients(`${ingredient.quantity} ${ingredient.name}`)
          }
        >
          <AddShoppingCartIcon />
        </IconButton>
      </Tooltip>
    );
  }
};
