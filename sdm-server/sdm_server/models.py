# This file defines the database representations used by Flask SQLAlchemy to create
# database tables and fields. Each class defined below represents a database table
# and each class member represents a field in that database table.
from sdm_server import db, app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class User(db.Model):
    '''
    The User class defines the ORM model that is translated by SQLAlchemy into
    the appropriate database structure to maintain users. The model defines the 
    following schema:
    
    id : primary_key, This field is automatically set and does not need to be
    manually specified or adjusted.

    user_uuid : String(50), The UUID of the user. Generated when a new user is created.

    username : String(50), The username specified when a new user is created.

    password : String(80), The SHA256 hash of the user's password.

    email : String(50), The user's email address specified when a new user is created.

    quantities : QueryObject, The quantities of an Ingredient and favorite status of an
    Ingredient. This column is implicitly generated by SQLAlchemy to setup the
    User -> Inventory -> Ingredient relationship.
    '''
    id = db.Column(db.Integer, primary_key=True)
    user_uuid = db.Column(db.String(50), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    quantities = db.relationship("Inventory", lazy="dynamic")

    def get_reset_token(self, expires=1800):
        """
        Generate a password reset token.

        This method generate's a TimedJSONWebSignatureSerializer token
        using the application's configured SECRET_KEY, the user UUID and,
        a default expiration timer of 30 minutes. The resulting token is emailed
        and used to validate a password change request.

        Parameters
        ----------
        expires : int
            An optional parameter to specify expiration time in seconds.

        Returns
        -------
        TimedJSONWebSignatureSerializer
            A generated JSON Web Signature token that will be validated to authenticate a user.
        """
        token = Serializer(app.config['SECRET_KEY'], expires)
        return token.dumps({'user_uuid': self.user_uuid}).decode('UTF-8')

    @staticmethod
    def verify_reset_token(check_token):
        """
        Verify a password reset token.

        This method takes a TimedJSONWebSignatureSerializer token and 
        attempts to extract a user UUID using the application's configured
        SECRET_KEY. If a valid UUID is decoded, then the supplied token was
        valid and the user is authenticated.

        Parameters
        ----------
        checkToken : TimedJSONWebSignatureSerializer
            The JSON Web Signature token to validate

        Returns
        -------
        User
            The User object associated to the JSON Web Signature token, or None if the token is invalid.
        """
        token = Serializer(app.config['SECRET_KEY'])
        try:
            uuid = token.loads(check_token)['user_uuid']
        except:
            return None
        return User.query.filter_by(user_uuid=uuid).first()

#recipe_ingredients is an intermediary table that tracks relationships between Ingredient and Recipe.
#It is automatically populated and should not be directly modified.
recipe_ingredients = db.Table('recipe_ingredients',
                     db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
                     db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredients.id')))

#user_ingredients is an intermediary table that tracks relationships between Ingredient and User.
#It is automaticallly populated and should not be directly modified.
user_ingredients = db.Table('user_ingredients',
                   db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                   db.Column('ingredient_id', db.Integer, db.ForeignKey('ingredients.id')))

#custom_user_ingredients is an intermediary table that tracks relationships between Custom_Ingredients and
#User. It is automatically populated and should not be directly modified.
custom_user_ingredients = db.Table('custom_user_ingredients',
                   db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                   db.Column('ingredient_id', db.Integer, db.ForeignKey('custom_ingredients.id')))


class Recipe (db.Model):
    '''
    The Recipe class defines the ORM model that is translated by SQLAlchemy into
    the appropriate database structure to maintain recipes. The model defines 
    the following schema:
    
    id : primary_key, This field is automatically set and does not need to be
    manually set or adjusted.
        
    name : String(50), The name of an individual ingredient.

    instructions : Text, The instructions that document how the Recipe is made.

    ingredients : QueryObject, The Ingredients that the Recipe requires. This
    column is implicitly generated by SQLAlchemy to setup the Recipe -> Ingredients
    relationship.
    '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
		
class Ingredients(db.Model):
    '''
    The Ingredients class defines the ORM model that is translated by SQLAlchemy into
    the appropriate database structure to maintain ingredients. The model defines 
    the following schema:

    id : primary_key, This field is automatically set and does not need to be
    manually set or adjusted.
        
    name : String(50), The name of an individual ingredient.

    used_in : QueryObject, The Recipes that use this Ingredient. This column is
    implicitly generated by SQLAlchemy to setup the Ingredients -> Recipe relationship.

    owned_by : QueryObject, The Users that own this Ingredient. This column is
    implicitly generated by SQLAlchemy to setup the Ingredient -> User relationship.
    '''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    ingredient_type = db.Column(db.String(50), unique=False, nullable=False)
    quantity = db.Column(db.Integer, unique=False, nullable=False)
    is_favorite = db.Column(db.Boolean, nullable=False, default=False)
    used_in = db.relationship('Recipe', secondary=recipe_ingredients, backref=db.backref('ingredients', lazy='dynamic'))
    owned_by = db.relationship('User', secondary=user_ingredients, backref=db.backref('ingredients', lazy='dynamic'))

class Custom_Ingredients(db.Model):
    '''
    The Custom_Ingredients class defines the ORM model that is translated by SQLAlchemy into
    the appropriate database structure to maintain custom ingredients. The model defines 
    the following schema:

    id : primary_key, This field is automatically set and does not need to be
    manually set or adjusted.

    name : String(50), The name of an individual ingredient.

    ingredient_type : String(50), The type of an individual ingredient.

    quantity : Integer, The amount of an individual ingredient.

    is_favorite : Boolean, True if the ingredient is a favorite, False otherwise.

    owned_by : QueryObject, the User that owns this Custom Ingredient. This column is
    implicitly generated by SQLAlchemy to setup the Custom_Ingredient -> User relationship.
    '''
    __tablename__ = "custom_ingredients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False, nullable=False)
    ingredient_type = db.Column(db.String(50), unique=False, nullable=False)
    quantity = db.Column(db.Integer, unique=False, nullable=False)
    is_favorite = db.Column(db.Boolean, nullable=False, default=False)
    owned_by = db.relationship('User', secondary=custom_user_ingredients, backref=db.backref('custom_ingredients', lazy='dynamic'))

class Inventory(db.Model):
    '''
    The Inventory class defines the ORM Model that is used translated by SQLALchemy into
    the appropriate database structure to maintain individual User quantities, and favorites
    for Ingredients. This model enables quantities and favorites to be User-specific, instead
    of database/application wide. The following schema is defined:

    user : ForeignKey, The User instance that should be associated to an Ingredient.

    ingredient : ForeignKey, The Ingredient instance that should be associated to a User.

    quantity : Integer, The quantity of the Ingredient instance.

    favorite : Boolean, True if the Ingredient instance is a favorite, False otherwise.

    owned_ingredient : QueryObject, A list of Ingredient instances associated to the User instance.
    '''
    user = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    ingredient = db.Column(db.Integer, db.ForeignKey('ingredients.id'), primary_key=True)
    quantity = db.Column(db.Integer, unique=False, nullable=False)
    favorite = db.Column(db.Boolean, unique=False, nullable=False)
    owned_ingredient = db.relationship("Ingredients")