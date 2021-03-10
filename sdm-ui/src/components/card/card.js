import React, { Component } from "react";
import Card from "@material-ui/core/Card";
import CardHeader from "@material-ui/core/CardHeader";
import CardMedia from "@material-ui/core/CardMedia";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import CardActions from "@material-ui/core/CardActions";
import IconButton from "@material-ui/core/IconButton";
import Tooltip from "@material-ui/core/Tooltip";
import AddShoppingCartIcon from "@material-ui/icons/AddShoppingCart";

import "./card.scss";

class RecipeCard extends Component {
  constructor(props) {
    super(props);
    this.state = {
      name: this.props.name,
      imgsrc: this.props.imgsrc,
      instructions: this.props.instructions,
      ingredients: this.props.ingredients,
    };
  }
  render() {
    return (
      <Card className="card">
        <CardHeader title={this.props.name} />
        <CardMedia className="image" image={this.props.imgsrc} />
        <CardContent>
          <Typography variant="body1" color="textPrimary">
            Recipe Instructions
          </Typography>
          <Typography variant="body2" color="textSecondary" component="p">
            {this.props.instructions}
          </Typography>
          <Typography variant="body1" color="textPrimary">
            Required Ingredients
          </Typography>
          <Typography variant="body2" color="textSecondary" component="p">
            {this.state.ingredients
              .map((ingr) => <span>{ingr}</span>)
              .reduce((prev, curr) => [prev, ", ", curr])}
            .
          </Typography>
        </CardContent>
        <CardActions className="actions">
          <Tooltip title={"Add Ingredients to Shopping List"}>
            <IconButton
              onClick={() => window.addIngredients(this.state.ingredients)}
            >
              <AddShoppingCartIcon />
            </IconButton>
          </Tooltip>
        </CardActions>
      </Card>
    );
  }
}

export default RecipeCard;
