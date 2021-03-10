import React from "react";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemText from "@material-ui/core/ListItemText";

import { $primaryDarker, $lighter } from "../../theme/palette";

function ShoppingListItems() {
  return (
    <List
      style={{
        margin: "auto",
        color: $primaryDarker,
        backgroundColor: $lighter,
        width: "50%",
      }}
    >
      <ListItem button>
        <ListItemText primary="Ingredient 1" />
      </ListItem>
      <ListItem button>
        <ListItemText primary="Ingredient 2" />
      </ListItem>
    </List>
  );
}

export default ShoppingListItems;
