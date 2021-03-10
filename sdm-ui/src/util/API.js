import jwtDecode from "jwt-decode";

// Backend URL
const backendUrl = "http://127.0.0.1:5000/api/";
// Headers
const requestHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Content-Type": "application/json",
};
const authHeaders = (token) => {
  return {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
};

const request = async (endpoint, verb, requestBody) => {
  let url = backendUrl + endpoint;
  let response = await fetch(url, {
    method: verb,
    headers: requestHeaders,
    body: requestBody,
  });
  return response.json();
};

const authenticatedRequest = async (endpoint, verb, requestBody) => {
  let url = backendUrl + endpoint;
  let token = getToken();
  let response = await fetch(url, {
    method: verb,
    headers: authHeaders(token),
    body: requestBody,
  });
  return response.json();
};

export const authenticate = async () => {
  if (tokenIsValid()) {
    let data = await authenticatedRequest("authenticate", "POST", "");
    return data.user ? data.user : false;
  }
};

/**
 * Check if token exists
 *
 * @public
 */
const tokenIsValid = () => {
  let token = localStorage.getItem("token");
  if (token) {
    try {
      jwtDecode(token);
      return token;
    } catch (InvalidTokenError) {
      return false;
    }
  }
  return false;
};

const getToken = () => {
  return localStorage.getItem("token");
};

/**
 * Request to login
 *
 * @param requestBody
 * @public
 */
export const loginRequest = async (requestBody) => {
  let jsonParams = JSON.stringify({
    loginId: requestBody.loginId,
    password: requestBody.password,
  });
  let data = await request("login", "POST", jsonParams);
  if (data.token) {
    localStorage.setItem("token", data.token);
    window.location.href = "/mycabinet/browse";
    return { "success": "" };
  } else {
    return data;
  }
};

/**
 * Request to Register a new account
 *
 * @param requestBody
 * @public
 */
export const registerRequest = async (requestBody) => {
  let jsonParams = JSON.stringify({
    username: requestBody.username,
    password: requestBody.password,
    email: requestBody.email,
  });
  let data = await request("register", "POST", jsonParams);
  if (data.error) {
    return data;
  } else {
    window.location.href = "/";
    return data;
  }
};

/**
 * Request when forgetting password
 *
 * @param requestBody
 * @public
 */

export const passwordLinkRequest = async (requestBody) => {
  let jsonParams = JSON.stringify({
    loginId: requestBody.loginId,
  });
  let data = await request("forgot-password", "POST", jsonParams);
  return data;
};

/**
 * Request when resetting password
 *
 * @param requestBody
 * @public
 */
export const passwordResetRequest = async (requestBody) => {
  let url = "forgot-password/" + requestBody.token;
  let jsonParams = JSON.stringify({
    newPassword: requestBody.newPassword,
  });
  let data = await request(url, "POST", jsonParams);
  if (data.error) {
    return data;
  } else {
    window.location.href = "/";
  }
};

export const allIngredientsRequest = async () => {
  if (tokenIsValid()) {
    let response = await authenticatedRequest("all-ingredients", "GET");
    if (response.ingredients) {
      return response.ingredients;
    }
  }
};

export const allUserIngredientsRequest = async () => {
  if (tokenIsValid()) {
    let response = await authenticatedRequest("user-ingredients", "GET");
    if (response.ingredients) {
      return response.ingredients;
    }
  }
};

export const addCustomIngredientRequest = async (name, type) => {
  if (tokenIsValid()) {
    let body = JSON.stringify({
      name: name,
      type: type,
    });
    let response = await authenticatedRequest(
      "custom-ingredients",
      "POST",
      body
    );
    return response;
  }
};

export const getCustomIngredientsRequest = async () => {
  if (tokenIsValid()) {
    let response = await authenticatedRequest("custom-ingredients", "GET");
    return response;
  }
};

export const deleteIngredientRequest = async (name) => {
  if (tokenIsValid()) {
    const custom = JSON.stringify({
      name: name,
    });
    await authenticatedRequest("custom-ingredients", "DELETE", custom);

    const nonCustom = JSON.stringify({
      ingredients: [name],
    });
    await authenticatedRequest("user-ingredients", "DELETE", nonCustom);
  }
};

/**
 * Authenticated request for all recipes in the database
 *
 * @public
 */
export const allRecipesRequest = async () => {
  if (tokenIsValid()) {
    let response = await authenticatedRequest("all-recipes", "GET");
    if (response.recipes) {
      return response.recipes;
    }
  }
};

export const filteredRecipesRequest = async () => {
  if (tokenIsValid()) {
    let response = await authenticatedRequest("filtered-recipes", "GET");
    if (response.recipes) {
      return response.recipes;
    }
  }
};

export const partialRecipesRequest = async () => {
  if (tokenIsValid()) {
    let response = await authenticatedRequest("partial-filter", "GET");
    if (response.recipes) {
      return response.recipes;
    }
  }
};

export const updateIngredientRequest = (name, favorite, quantity) => {
  if (tokenIsValid()) {
    let body = JSON.stringify({
      name: name,
      quantity: quantity,
      isFavorite: favorite,
    });
    authenticatedRequest("all-ingredients", "PATCH", body);
  }
};
