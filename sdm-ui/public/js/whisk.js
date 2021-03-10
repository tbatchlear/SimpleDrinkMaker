//<!--Function to shopping cart button (View shopping list)-->
function viewList() {
  whisk.queue.push(function () {
    whisk.listeners.addClickListener(
      "whisk-shopping-list",
      "shoppingList.viewList"
    );
  });
}
//<!--Function to add one or more ingredients to shopping list-->
function addIngredients(ingr) {
  if (Array.isArray(ingr)) {
    whisk.queue.push(function () {
      whisk.shoppingList.addProductsToList({
        products: ingr,
      });
    });
  } else {
    whisk.queue.push(function () {
      whisk.shoppingList.addProductsToList({
        products: [ingr],
      });
    });
  }
}
