# This file sets up all the individual backend endpoints that will
# be supported by the SDM application. It contains routes designed
# to provide API access to be consumed by the SDM frontend.
from functools import wraps
from flask import render_template, url_for, jsonify, request, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from flask_mail import Message
from sdm_server import app, db, mail
from sdm_server.models import User
from sdm_server.validators import *

@app.route('/')
def index():
    """
    The default index route.

    This route simply returns a JSON representation of the other
    supported routes/endpoints. It is intended for development use
    and will likely be removed before moving to production.
    Returns
    -------
    json : JSON
        A JSON representation of the backend supported endpoints.
    """
    return jsonify({"message": "Please reference API documentation to view supported endpoints"}), 200

@app.route('/api/login', methods=['POST'])
@cross_origin(origin='localhost')
def login():
    """
    This endpoint provides authentication for a registered user. A JSONWebToken is returned for a valid login request.
    Parameters
    ----------
    userData : JSON Request Body
        A properly formatted JSON object containing the user's 
        username or email and user's password. The userData object
        should be sent as the request body of an HTTP/POST.
    Returns
    -------
    json : JSON
        A JSON object containing a JSON Web Token for succesful logins
        or an error message for failed logins.
    """
    request_body = request.get_json()
    request_login_id = request_body.get('loginId')
    request_password = request_body.get('password')
    
    user = validate_request(loginId=request_login_id, password=request_password)
    if not user:
        return jsonify({"message": "Invalid username or password"}), 401

    token = generate_token(user, request_password)
    if token:
        return jsonify({"token": token.decode('UTF-8')}), 200

    return jsonify({"message": "Invalid username or password"}), 401

@app.route('/api/register', methods=['POST'])
@cross_origin(origin='localhost')
def register():
    """
    This endpoint provides functioanlity to register a new user.
    Parameters
    ----------
    userData : JSON Request Body
        A properly formatted JSON object containing a username, email,
        and password. The userData object should be sent as the request
        body of an HTTP/POST request.
    Returns
    -------
    json : JSON
        A JSON object containing a success message or an error message depending
        on if the new user was registered.
    """
    request_body = request.get_json()
    username = request_body.get('username')
    password = request_body.get('password')
    email = request_body.get('email')

    if entry_is_null(username, password, email):
        return jsonify({"message": "'username, password, email' are required parameters."}), 400
    if user_exists(username, email):
        return jsonify({"error": "User or email already registered. Please login instead."}), 403

    add_new_user(username, password, email)

    return jsonify({"message": "New user created."}), 200

@app.route('/api/forgot-password', methods=['POST'])
@cross_origin(origin='localhost')
def send_reset_link():
    """
    This endpoint provides functionality to request a password-reset link.
    Parameters
    ----------
    userLogin : JSON Request Body
        A properly formatted JSON object containing a username or email.
        The userLogin object should be sent as the request body of an
        HTTP/POST request.
    Returns
    -------
    json : JSON
        A JSON object containing an e-mail sent message.
    """
    request_body = request.get_json()
    request_login_id = request_body.get('loginId')
    try:
        # An error can be thrown if AWS rejects the request to send
        # the email through its service.
        send_reset_email(request_login_id)
    except:
        # If an error does occur, the application should still display a success message.
        pass
    return jsonify({"message": "An email has been sent with instructions to reset your password."}), 200

@app.route('/api/forgot-password/<token>', methods=['POST'])
@cross_origin(origin='localhost')
def reset_user_password(token):
    """
    This endpoint provides the ability to reset a password after a reset-link is received.
    Parameters
    ----------
    token : JSON Web Signature token
        A generated token sent as a URL parameter of an HTTP/POST request.
    newPassword : JSON Request Body
        A properly formatted JSON object containing the requested new password.
        The newPassword object should be sent as the request body of an HTTP/POST
        request.
    Returns
    -------
    json : JSON
        A JSON object containing either an error or success message.
    """
    reset_password = request.get_json().get("newPassword")
    reset = validate_and_reset(reset_password, token)
    if reset:
        return jsonify({"message": reset}), 200
    return jsonify({"error": "The reset password link is expired. Please try again."}), 400

@app.route('/api/authenticate', methods=['POST'])
@cross_origin(origin='localhost')
@login_required
def authenticate(user):
    """
    This endpoint provides the initial serverside validation of JSONWebTokens
    submitted for authenticated backend access. The Authorization header must be
    set and contain the user's JWT. The user instance is implicitly passed in by 
    the @login_required decorator after a JWT is succesffully decoded.
    Parameters
    ----------
    token : JSONWebToken
        A JSONWebToken sent in the Authorization header.
    Returns
    -------
    user : JSON
        A JSON formatted message containing the username of the authenticated
        user that the supplied token belongs to.
    """
    return jsonify({"user": user.username}), 200

@app.route('/api/all-ingredients', methods=['GET'])
@cross_origin(origin='localhost')
@login_required
def get_all_ingredients(user):
    """
    This endpoint returns all ingredients stored in the database.
    The Authorization header must be set and must contain the user's 
    JWT. The user instance is implicitly passed in by the 
    @login_required decorator after a JWT is succesffully decoded.
    Parameters
    ----------
    token : JSONWebToken
        A JSONWebToken sent in the Authorization header.
    Returns
    -------
    ingredients : JSON
        A JSON formatted listing of all database ingredients.
    """
    ingredients = get_all_database_ingredients(user)
    return jsonify({"ingredients": ingredients}), 200

@app.route('/api/all-ingredients', methods=['PATCH'])
@cross_origin(origin='localhost')
@login_required
def update_ingredient(user):
    """
    This endpoint updates the quantity and favorite column in the database
    for a specific ingredient.The Authorization header must be set and must 
    contain the user's JWT. The user instance is implicitly passed in by the 
    @login_required decorator after a JWT is succesffully decoded.
    Parameters
    ----------
    token : JSONWebToken
        A JSONWebToken sent in the Authorization header.
    name : str
        The name of the ingredient to update. Sent as a JSON object in
        the request body.
    quantitiy : int
        The quantity of the ingredient. Sent as a JSON object in
        the request body.
    isFavorite : str
        'True' if the ingredient is a favorite, 'False' otherwise. Sent as a
        JSON object in the request body.
    Returns
    -------
    error : JSON
        A JSON formatted error message is required parameters are missing.
    message : JSON
        A JSON formatted success message if the update was successful. 
    """
    name = request.get_json().get('name')
    quantity = request.get_json().get('quantity')
    is_favorite = request.get_json().get('isFavorite')

    if(entry_is_null(name, quantity, is_favorite)):
        return jsonify({"error": "Provide name, quantity and isFavorite"}), 401
    update_database_ingredients(user, name, quantity, is_favorite)
    return jsonify({"message": "Ok"}), 200

@app.route('/api/custom-ingredients', methods=['GET'])
@cross_origin(origin='localhost')
@login_required
def get_all_custom_ingredients(user):
    """
    This endpoint returns all of the User's custom ingredients stored in the database.
    The Authorization header must be set and must contain the user's 
    JWT. The user instance is implicitly passed in by the 
    @login_required decorator after a JWT is succesffully decoded.
    Parameters
    ----------
    token : JSONWebToken
        A JSONWebToken sent in the Authorization header.
    Returns
    -------
    ingredients : JSON
        A JSON formatted listing of all custom ingredients associated to the 
        User instance.
    """
    ingredients = get_all_database_custom_ingredients(user)
    return jsonify({"ingredients": ingredients}), 200

@app.route('/api/custom-ingredients', methods=['POST'])
@cross_origin(origin='localhost')
@login_required
def create_custom_ingredient(user):
    """
    This endpoint creates a new custom ingredient by extracting the
    JSON object sent in the request body. The created custom ingredient
    is then associated to the User. If the custom ingredient already exists
    in the database it will simply be associated to the User.The Authorization 
    header must be set and must contain the user's JWT. The user instance is 
    implicitly passed in by the @login_required decorator after a JWT is succesffully decoded.
    Parameters
    ----------
    token : JSONWebToken
        A JSONWebToken sent in the Authorization header.
    name : JSON
        The name of the custom ingredient to add to the database, sent
        in the request body.
    type : JSON
        The type of the custom ingredient to add to the database, sent 
        in the request body.
    Returns
    -------
    message : JSON
        A JSON formatted success message.
    error : JSON
        A JSON formatted error message.
    """
    name = request.get_json().get('name')
    typeof = request.get_json().get('type')
    if (entry_is_null(name, typeof)):
        return jsonify({"error": "'name' and 'type' are required parameters."}), 401
    status = insert_custom_ingredient(user, name, typeof)
    return status

@app.route('/api/custom-ingredients', methods=['DELETE'])
@cross_origin(origin='localhost')
@login_required
def delete_custom(user):
    """
    This endpoint deletes a custom ingredient from the database.
    The name of the ingredient to delete must be sent as a JSON
    object in the request body. If the ingredient does not exist
    in the database no action is taken. The Authorization header 
    must be set and must contain the user's JWT. The user instance 
    is implicitly passed in by the @login_required decorator after 
    a JWT is succesffully decoded.
    Parameters
    ----------
    token : JSONWebToken
        A JSONWebToken sent in the Authorization header.
    name : JSON
        A JSON formatted name of the ingredient to delete.
    Returns
    -------
    message : JSON
        A JSON formatted success message.
    error : JSON
        A JSON formatted error message.
    """
    name = request.get_json().get('name')

    if (entry_is_null(name)):
        return jsonify({"error": "'name' is a required parameter."}), 401
    delete_custom_ingredient(user, name)
    return jsonify({'message': 'Ok'}), 200

@app.route('/api/user-ingredients', methods=['GET'])
@cross_origin(origin='localhost')
@login_required
def get_user_ingredients(user):
    """
    This endpoint returns all ingredients that a user has added
    to the user's cabinet. The Authorization header must be set 
    and must contain the user's JWT. The user instance is implicitly 
    passed in by the @login_required decorator after a JWT is succesffully decoded.
    Parameters
    ----------
    token : JSONWebToken
        A JSONWebToken sent in the Authorization header.
    Returns
    -------
    ingredients : JSON
        A JSON formatted listing of the user's ingredients.
    """
    ingredients = get_all_user_ingredients(user)
    return jsonify({"ingredients": ingredients}), 200

@app.route('/api/user-ingredients', methods=['POST'])
@cross_origin(origin='localhost')
@login_required
def add_user_ingredients(user):
    """
    This endpoint provides functionality to add ingredients to a
    User's cabinet. A JSON formatted list of ingredients must be sent
    in the request body. The Authorization header must be set and must 
    contain the user's JWT. The user instance is implicitly passed in by 
    the @login_required decorator after a JWT is succesffully decoded.
    Parameters
    ----------
    token : JSONWebToken
        A JSONWebToken sent in the Authorization header.
    ingredients : JSON
        A JSON formatted list of ingredients to add to a User's cabinet.
        The ingredients should be sent in the request body.
    Returns
    -------
    message : JSON
        A success message, listing all ingredients that were added.
        Or a fail message, specifying no valid ingredients were sent.
    """
    ingredients = request.get_json().get('ingredients', '')
    message = add_ingredients(user, ingredients)
    if message:
        return jsonify({"message": message}), 200
    return jsonify({"message": "No valid ingredients"}), 400

@app.route('/api/user-ingredients', methods=['DELETE'])
@cross_origin(origin='loclahost')
@login_required
def delete_user_ingredients(user):
    """
    This endpoint provides functionality to delete ingredients from a
    User's cabinet. A JSON formatted list of ingredients to delete must
    be sent in the request body. The Authorization header must be set and
    must contain the user's JWT. The user instance is implicitly passed in
    by the @login_required decorator after a JWT is successfully decoded.
    Parameters
    ----------
    token : JSONWebToken
        A JSONWebToken sent in the Authorization header.
    ingredients : JSON
        A JSON formatted list of ingredients to delete.
    Returns
    -------
    message : JSON
        A success message, listing all ingredients that were deleted.
        Or a fail message, specifying no valid ingredients were sent.
    """
    ingredients = request.get_json().get('ingredients', '')
    message = delete_ingredients(user, ingredients)
    if message:
        return jsonify({"message": message}), 200
    return jsonify({"message": "No valid ingredients"}), 400

@app.route('/api/all-recipes', methods=['GET'])
@cross_origin(origin='localhost')
@login_required
def get_all_recipes(user):
    """
    This endpoint returns all recipes stored in the database.
    The Authorization header must be set and must contain the user's 
    JWT. The user instance is implicitly passed in by the 
    @login_required decorator after a JWT is succesffully decoded.
    Parameters
    ----------
    token : JSONWebToken
        A JSONWebToken sent in the Authorization header.
    Returns
    -------
    recipes : JSON
        A JSON formatted listing of all database recipes.
    """
    recipes = get_all_database_recipes()
    return jsonify({"recipes": recipes}), 200

@app.route('/api/filtered-recipes', methods=['GET'])
@cross_origin(origin='localhost')
@login_required
def get_filtered_recipes(user):
    """
    This endpoint returns all Recipes stored in the database,
    filtered by ingredients that are present in the User's cabinet.
    Only Recipes that the User could currently make with the Ingredients
    in the cabinet are returned. The Authorization header must be set
    and contain the user's JWT. The user instance is implicitly passed in
    by the @login_required decorator after a JWT is successfully decoded.
    Parameters
    ----------
    token : JSONWebToken
        A JSONWebToken setn in the Authorization header.
    Returns
    -------
    recipes : JSON
        A JSON formatted listing of filtered database recipes.
    """
    recipes = get_all_filtered_database_recipes(user)
    return jsonify({"recipes": recipes}), 200

@app.route('/api/partial-filter', methods=['GET'])
@cross_origin(origin='localhost')
@login_required
def get_partial_filter(user):
    """
    This endpoint returns all Recipes stored in the database,
    filtered by a partial match on ingredients present in the User's
    cabinet. Only Recipes that match some of the User's ingredients
    will be returned. The Authorization header must be set and contain
    the user's JWT. The user instance is implicitly passed in by the
    @logi_required decorator after a JWT is successfully decoded.
    Paramters
    ---------
    token : JSONWebToken
        A JSONWebToken sent in the Authorization header.
    Returns
    -------
    recipes : JSON
        A JSON formatted listing of filtered database recipes.
    """
    recipes = get_all_partial_match_recipes(user)
    return jsonify({"recipes": recipes}), 200
