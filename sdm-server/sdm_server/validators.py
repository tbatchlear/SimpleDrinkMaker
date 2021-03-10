# This file provides general utility and validation methods.
# Its primary purpose is to validate the data received by API
# endpoints to ensure that requests are properly formatted
# and contain all expected parameters and objects.
from sdm_server import app, db, mail
from sdm_server.models import *
from functools import wraps
from flask import request, jsonify
from flask_mail import Message
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
from operator import itemgetter
import jwt
import uuid

def entry_is_null(*args):
    """
    Verifies that each passed in parameter contains data that is not None.
    Parameters
    ----------
    *args : *args
        A variable number of parameters that should be checked.
    Returns
    -------
    True/False : boolean
        Returns True if ANY parameter is None or False otherwise.
    """
    for entry in args:
        if entry is None:
            return True
    return False

def validate_request(**kwargs):
    """
    Checks that data received by an endpoint contains a username/email and password, and then returns the assocaited user.
    Parameters
    ----------
    **kwargs : **kwargs
        Keyword arguments that must contain a loginId and a password.
    Returns
    -------
    user : User or None
        The User associated with the passed in loginId or None if the loginId does
        not exist or the **kwargs did not contain a password.
    """
    login_id = kwargs.get('loginId')
    user = None
    if not login_id:
        return None
    if 'password' not in kwargs:
        return None
    # loginId can be either a username or e-mail address. Both fields are unique to 1 user.
    user = User.query.filter((User.username==login_id) | (User.email==login_id)).first()
    return user

def user_exists(check_user, check_email):
    """
    Checks if the database already contains the supplied username or email address.
    Parameters
    ----------
    check_user : str
        The username to search for in the database.
    check_email : str
        The email address to search for in the database.
    Returns
    -------
    True/False : boolean
        Returns True if the user exists and False otherwise.
    """
    user = User.query.filter((User.username==check_user) | (User.email==check_email)).first()
    return user is not None

def generate_token(user, password):
    """
    Checks if the correct password was supplied and generates a JSON Web Token
    Parameters
    ----------
    user : User
        The User object that contains the password to check against.
    password : str
        A password string that will be validated against the database's password hash.
    Returns
    -------
    token : JSONWebToken or None
        An encoded JSON Web Token if the password was correct, or None if the password was incorrect.
    """
    token = None
    if(check_password_hash(user.password, password)):
        token = jwt.encode({'sub': user.user_uuid, 'exp': datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def add_new_user(username, password, email):
    """
    Adds adds a new entry in the User table in the database.

    This method takes in a username, password, and email as parameters. It will
    use the plaintext password to generate a SHA256 password hash that will be 
    stored in the database. The plaintext password is discarded. The method will
    also generate a UUIDv4 string to store in the database entry as well.
    Parameters
    ----------
    username : str
        The username of the User to add to the database.
    password : str
        The plaintext password of the User that will be hashed and
        added to the database.
    email : str
        The email address of the User to add to the database.
    """
    hashed_pass = generate_password_hash(password, method='sha256')
    user_uuid = str(uuid.uuid4())
    user = User(username=username, password=hashed_pass, email=email, user_uuid=user_uuid)
    db.session.add(user)
    db.session.commit()

def send_reset_email(login_id):
    """
    Emails a password-reset link containing a JSON Web Signature token.
    Parameters
    ----------
    loginId : str
        The username or email address of the User requesting a password-reset link.
    """
    user = User.query.filter((User.username==login_id) | (User.email==login_id)).first()
    if user:
        message = get_email_body(user)   
        mail.send(message)

def get_email_body(user):
    """
    Generates a password reset e-mail containing a JSON Web Signature token and user message.
    Parameters
    ----------
    user : User
        The User requesting a password reset.
    Returns
    -------
    message : Message
        A Message object that contains the formatted e-mail subject, sender, recipient, and body.
    """
    message = Message("Reset Password", sender='do-not-reply@simpledrinkmaker.com', recipients=[user.email])
    body = ("Hello {0}!\n\nWe received a request to reset your password."
            "Please click the link below to reset your password:\n\n"
            "http://localhost:3000/reset-pass/{1}\n\n"
            "If you did not initiate this request then you do not need to take any action and your password will not be reset.\n\n"
            "Please do not reply to this e-mail as this mailbox is not monitored.".format(user.username, user.get_reset_token()))
    message.body = body
    return message

def validate_and_reset(new_pass,token):
    """
    Resets a User's password after the User clicks on a generated reset link.

    This method expects a new password and a JSON Web Signature token. The
    token will be decoded to extract a User UUID from the database. If the
    token is properly decoded, then a User object will be returned from the 
    database and the password can be set to the new password.
    Parameters
    ----------
    new_pass : str
        The new plaintext password that will be hashed and stored in the database.
    token : JSONWebSignature
        The JSON Web Signature token that will be decoded to extract a User UUID.
    Returns
    -------
    message : str or None
        Returns a success message if successful or None otherwise.
    """
    user = User.verify_reset_token(token)
    if user:
        hashed_pass = generate_password_hash(new_pass, method='sha256')
        user.password = hashed_pass
        db.session.commit()
        return "Your password was reset."
    return None

def get_all_database_ingredients(user):
    """
    This method queries the database for Ingredients and Custom_Ingredients and
    returns a dictionary containing lists of all database ingredients. The lists
    are sorted alphabetically.
    Parameters
    ----------
    user : User
        The User instance to retrieve custom ingredients from.
    Returns
    -------
    ingredients : dict
        A dictionary containing lists of all database ingredients, sorted alphabetically.
        The two primary keys are 'default' and 'custom'
    """
    ingredients = {}

    custom_ingredients = []
    default_ingredients = []
    for default_ingredient in Ingredients.query.all():
        # User's cabinet ingredients will be added afterwards, so avoid
        # duplicating the entries by only adding the ingredients not in the cabinet.
        if(default_ingredient not in user.ingredients):
            ingredient = {}
            ingredient['name'] =  default_ingredient.name.capitalize()
            ingredient['type'] = default_ingredient.ingredient_type.capitalize()
            ingredient['quantity'] = 0
            ingredient['favorite'] = "False"
            default_ingredients.append(ingredient)
    
    user_cabinet = get_all_user_ingredients(user)
    if(user_cabinet.get('default')):
        default_ingredients.extend(user_cabinet.get('default'))
    if(user_cabinet.get('custom')):
        custom_ingredients.extend(user_cabinet.get('custom'))
    
    ingredients['default'] = sorted(default_ingredients, key=itemgetter('name'))
    ingredients['custom'] = sorted(custom_ingredients, key=itemgetter('name'))
    return ingredients

def get_all_database_custom_ingredients(user):
    """
    This method queries the Custom_Ingredients database table and
    returns a list of dictionaries of all custom ingredients that
    are associated to a User.
    Parameters
    ----------
    user : User
        The User instance to retrieve custom ingredients from.
    Returns
    -------
    ingredients : List
        A List of Dictionaries of all Custom Ingredients, sorted alphabetically.
    """
    ingredients = []
    for custom_ingredient in user.custom_ingredients:
        ingredient = {}
        ingredient['name'] = custom_ingredient.name.capitalize()
        ingredient['type'] = custom_ingredient.ingredient_type.capitalize()
        ingredients.append(ingredient)
    return sorted(ingredients, key=itemgetter('name'))
        
def update_database_ingredients(user, name, quantity, isFavorite):
    """
    This method updates the quantity and favorite flag of the ingredient
    matching 'name'. The method searches for 'name' in Ingredients (default)
    and Custom_Ingredients, updating the quantity and favorite as appropriate. The
    ingredient will be automatically added to the User's cabinet when the quantity
    is increased above 0.
    Parameters
    ----------
    user : User
        The User instance to associate ingredient quantity and favorite with.
    name : str
        The name of the ingredient to update.
    quantity : int
        The quantity to update the ingredient with.
    isFavorite : str
        'True' if the ingredient is a favorite, 'False' otherwise.
    """
    is_favorite = isFavorite != 'False'
    ingredient = Ingredients.query.filter_by(name=name.lower()).first()
    # If the ingredient is not found, it is not a default ingredient and
    # the user's custom ingredients should be updated instead.
    if(not ingredient):
        update_custom_database_ingredients(user, name, quantity, isFavorite)
    else:
        # If the user has previously updated the ingredient quantity or favorite, there
        # will be an existing relationship setup to track the association. Update the
        # association with new values.
        existing_ingredient = user.quantities.filter_by(owned_ingredient=ingredient).first()
        if(existing_ingredient):
            existing_ingredient.quantity = quantity
            existing_ingredient.favorite = is_favorite
            db.session.commit()
        # Otherwise, create the quantity and favorite association and assign the values
        # that were passed in to the method.
        else:
            update = Inventory(quantity=quantity, favorite=is_favorite)
            update.owned_ingredient = ingredient
            user.quantities.append(update)
            db.session.commit()
        # Finally, add the ingredient to the user's cabinet.
        add_ingredients(user, [ingredient.name])   

def update_custom_database_ingredients(user, name, quantity, isFavorite):
    """
    This method updates the quantity and favorite flags of a user's Custom Ingredients.
    Parameters
    ----------
    user : User
        The User instance that owns the custom ingredient.
    name : str
        The name of the custom ingredient.
    quantity : int
        The update quantity of the custom ingredient.
    isFavorite : str
        'True' if the custom ingredient is a favorite, 'False' otherwise.
    """
    # Custom ingredients are only associated directly with User instances.
    # The custom ingredient must have previously been created, otherwise no
    # action will be taken by this method.
    ingredient = user.custom_ingredients.filter_by(name=name.lower()).first()
    if(ingredient):
        ingredient.quantity = quantity
        ingredient.is_favorite = isFavorite != 'False'
        db.session.commit()
    
def get_all_database_recipes():
    """
    This method queries the database for Recipes and returns
    the query result sorted alphabetically.
    Returns
    -------
    recipes : List
        A List of Dictionaries containing all database recipes, sorted alphabetically.
    """
    output = []
    for recipe in Recipe.query.all():
        recipes = {}
        recipes['name'] = recipe.name
        recipes['instructions'] = recipe.instructions
        recipes['ingredients'] = []
        for ingredient in recipe.ingredients.all():
            recipes['ingredients'].append(ingredient.name.capitalize())
        output.append(recipes)
    return sorted(output, key=itemgetter('name'))

def get_all_filtered_database_recipes(user):
    '''
    This method queries the database for Recipes with Ingredients
    that match the User's current Ingredients. Every Ingredient required
    by the Recipe must be present in the User's Ingredients list.
    Parameters
    ----------
    user : User
        The User instance.
    Returns
    -------
    recipes : List
        A List of dictionaries containing all filtered Recipes, sorted alphabetically.
    '''
    output = []
    for recipe in Recipe.query.all():
        required_ingredients = set(recipe.ingredients.all())
        user_ingredients = user.ingredients.all()
        recipes = {}
        # Check if the Recipe's required ingredients are a subset of the
        # ingredients in a User's cabinet. If True, every ingredient
        # required by the Recipe is stored in the User's cabinet.
        if(required_ingredients.issubset(user_ingredients)):
            recipes['name'] = recipe.name
            recipes['instructions'] = recipe.instructions
            recipes['ingredients'] = []
            for ingredient in required_ingredients:
                recipes['ingredients'].append(ingredient.name.capitalize())
            output.append(recipes)
    return sorted(output, key=itemgetter('name'))
        
def get_all_partial_match_recipes(user):
    '''
    This method queries the database for Recipes with Ingredients
    that partially match the User's current Ingredients.  At least one
    of the Ingredients required to make the the Recipe must be present 
    in the User's Ingredients list.
    Parameters
    ----------
    user : User
        The User instance.
    Returns
    -------
    recipes : List
        A List containing all filtered Recipes, sorted alphabetically.
    '''
    output = []
    for recipe in Recipe.query.all():
        required_ingredients = recipe.ingredients.all()
        user_ingredients = set(user.ingredients.all())
        recipes = {}
        # Check if at least 1 ingredient required by the Recipe is
        # stored in the User's cabinet.
        if(not user_ingredients.isdisjoint(required_ingredients)):
            recipes['name'] = recipe.name
            recipes['instructions'] = recipe.instructions
            recipes['ingredients'] = []
            for ingredient in required_ingredients:
                recipes['ingredients'].append(ingredient.name.capitalize())
            output.append(recipes)
    return sorted(output, key=itemgetter('name'))

def get_all_user_ingredients(user):
    """
    This function queries the passed in User instance and returns
    all ingredients that are associated to the User in the database.
    Parameters
    ----------
    user : User
        The User instance to query for ingredients.
    Returns
    -------
    ingredients : Dictionary
        A Dictionary containing the User's ingredients, sorted alphabetically.
    """
    ingredients = {}
    if(len(user.ingredients.all()) == 0 and len(user.custom_ingredients.all()) == 0):
        ingredients['default'] = []
        ingredients['custom'] = []
        return ingredients
    
    default_ingredients = []
    for ingredient in user.ingredients:
        current_ingredient = {}
        inventory = user.quantities.filter_by(owned_ingredient=ingredient).first()
        current_ingredient['name'] = ingredient.name.capitalize()
        current_ingredient['type'] = ingredient.ingredient_type.capitalize()
        current_ingredient['quantity'] = inventory.quantity
        current_ingredient['favorite'] = str(inventory.favorite)
        default_ingredients.append(current_ingredient)

    custom_ingredients = []
    for ingredient in user.custom_ingredients:
        current_ingredient = {}
        current_ingredient['name'] = ingredient.name.capitalize()
        current_ingredient['type'] = ingredient.ingredient_type.capitalize()
        current_ingredient['quantity'] = ingredient.quantity
        current_ingredient['favorite'] = str(ingredient.is_favorite)
        custom_ingredients.append(current_ingredient)
    
    ingredients['default'] = sorted(default_ingredients, key=itemgetter('name'))
    ingredients['custom'] = sorted(custom_ingredients, key=itemgetter('name'))
    return ingredients

def add_ingredients(user, ingredients):
    """
    This function associates the passed-in List of Ingredients to
    the passed in User instance. Each Ingredient in the List of
    Ingredients must be valid and exist in the database, or it will
    not be associated to the User instance.
    Parameters
    ----------
    user : User
        The User instance to add Ingredients to.
    ingredients : List
        A List of Ingredients to add to the User.
        Each Ingredient must exist in the database already.
    Returns
    -------
    message : str
        A String success message listing the Ingredients that were added or
        None otherwise.
    """
    if (len(ingredients) == 0):
        return None
    for ingredient in ingredients:
        user_ingredient = Ingredients.query.filter_by(name=ingredient.lower()).first()
        if (user_ingredient and user_ingredient not in user.ingredients):
            user.ingredients.append(user_ingredient)
    db.session.commit()
    return "Added {} to user cabinet.".format(', '.join(ingredients))

def delete_ingredients(user, ingredients):
    """
    This function deletes the passed-in List of Ingredients from
    the passed in User instance. Each Ingredient in the List of
    Ingredients must be valid and exist in the database, or it will
    not be deleted from the User instance.
    Parameters
    ----------
    user : User
        The User instance to delete Ingredients from.
    ingredients : List
        A List of Ingredients to delete from the User.
        Each Ingredient must exist in the database already.
    Returns
    -------
    message : str
        A String success message listing the Ingredients that were deleted or
        None otherwise.
    """
    if(len(ingredients) == 0):
        return None
    for ingredient in ingredients:
        user_ingredient = Ingredients.query.filter_by(name=ingredient.lower()).first()
        if(user_ingredient and user_ingredient in user.ingredients):
            user.ingredients.remove(user_ingredient)
    db.session.commit()
    return "Removed {} from user cabinet.".format(', '.join(ingredients))

def insert_custom_ingredient(user, name, typeof):
    """
    This method creates a Custom Ingredient and associates it to the 
    passed in User instance. If the Custom Ingredient is already associated to
    the User instance, then no action is taken and a JSON success message is returned.
    Parameters
    ----------
    user : User
        The User instance to associate Custom Ingredient to.
    name : str
        The name of the Custom Ingredient
    typeof : str
        The type of the Custom Ingredient.
    Returns
    -------
    message : JSON
        A JSON formatted success message.
    error : JSON
        A JSON formatted error message.
    """
    custom_ingredient = user.custom_ingredients.filter_by(name=name.lower()).first()
    default_ingredient = Ingredients.query.filter_by(name=name.lower()).first()
    # If the Custom Ingredient is already associated to the User, take no action.
    if(custom_ingredient):
        return jsonify({"message": "'{}' already exists.".format(name)}), 200
    # If the Custom Ingredient matches the name of a default Ingredient, return an error.
    if(default_ingredient):
        return jsonify({"error":"{} is a default ingredient and can not be added as a custom ingredient.".format(name)}), 401
    else:
        user.custom_ingredients.append(Custom_Ingredients(name=name.lower(), ingredient_type=typeof, quantity=0, is_favorite=False))
        db.session.commit()
        return jsonify({"message": "Added ingredient '{}' of type '{}'".format(name, typeof)}), 200

def delete_custom_ingredient(user, name):
    """
    This method deletes the custom ingredient matching 'name' from the 
    database, and removes it from the user's cabinet.
    Parameters
    ----------
    user : User
        The User instance to delete custom ingredients from.
    name : str
        The name of the custom ingredient to delete.
    """
    ingredient = user.custom_ingredients.filter_by(name=name.lower()).first()
    db_ingredient = None
    if(ingredient):
        user.custom_ingredients.remove(ingredient)
        # Find the custom ingredient by id, because other users can create 
        # custom ingredients with the same name.
        db_ingredient = Custom_Ingredients.query.filter_by(id=ingredient.id).first()
    # If the custom ingredient exists in the database, remove it by id.
    if(db_ingredient):
        db.session.delete(db_ingredient)
    db.session.commit()

def login_required(f):
    """
    This function serves as a decorator intended to validate requests
    for access to protected endpoints. The function checks for the
    Authorization header to be set, extracts the bearer JWT token that is 
    set in the header, and attempts to decode it. If the token is successfully
    decoded, then the database is queried for the User instance, and the User
    instance is passed in to the decorated function. Otherwise an error message
    is returned.
    Parameters
    ----------
    token : JSONWebToken
        A JSONWebToken that must be sent in the Authorization header.
    Returns
    -------
    message : JSON
        A fail message, sent whenever the token can not be decoded or validated,
        or if the token was not associated to a User in the database.
    user : User
        The User that was associated to the JSONWebToken.
    """
    @wraps(f)
    def _verify(*args, **kwargs):
        headers = request.headers.get('Authorization', '').split()
        invalid = {"message": "Invalid authentication token. Please log in and try again."}
        if (len(headers) != 2):
            return jsonify(invalid), 401
        try:
            token = headers[1]
            user_uuid = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['sub']
            user = User.query.filter_by(user_uuid=user_uuid).first()
            if not user:
                return jsonify(invalid), 401
            return f(user, *args, **kwargs)
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            return jsonify(invalid), 401
    return _verify
