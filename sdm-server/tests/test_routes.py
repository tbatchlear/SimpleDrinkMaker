import unittest
import csv
import json
from sdm_server import app, db
from sdm_server.models import *


class TestRoutes(unittest.TestCase):
    '''
    Module for running unittests on current supported frontend routes.
    This module performs tests on the expected operations and requests
    each route is expected to receive. Responses are checked to make
    sure they are in line with expectations.
    '''
    @classmethod
    def setUpClass(cls):
        cls.ingredients = []
        cls.recipes = []
        with open('ingredients.csv', newline='') as f:
            reader = csv.reader(f, delimiter=',')
            for line in reader:
                if line not in cls.ingredients:
                    cls.ingredients.append([line[0], line[1], line[2], line[3]])

        with open('Recipes.csv', newline='') as f:
            reader = csv.reader(f, delimiter=';')
            for line in reader:
                if line not in cls.recipes:
                    cls.recipes.append([line[0], line[1]])

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../tests/test.db'
        app.config['SECRET_KEY'] = 'Not A Good Key'
        db.create_all()

        for ingredient in TestRoutes.ingredients:
            ing = Ingredients(name=ingredient[0].lower(), ingredient_type=ingredient[1].lower(), quantity=ingredient[2], is_favorite=eval(ingredient[3]))
            db.session.add(ing)
        for recipe in TestRoutes.recipes:
            rec = Recipe(name=recipe[0], instructions=recipe[1])
            db.session.add(rec)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_login(self):
        invalid_message = "Invalid username or password"

        print("\n>Running test for User account does not exist.")
        post_data = {'loginId':'fake', 'password': 'fake'}
        response = self.client.post('/api/login', data=json.dumps(post_data), content_type='application/json')
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

        print(">Running test for incorrect User password.")
        self.register_user({"username": "test", "password": "test", "email": "test"})
        post_data = {'loginId': 'test', 'password': 'badpass'}
        response = self.client.post('/api/login', data=json.dumps(post_data), content_type='application/json')
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

        print(">Running test for token response after correct login.")
        post_data['password'] = 'test'
        response = self.client.post('/api/login', data=json.dumps(post_data), content_type='application/json')
        response_token = response.get_json().get('token')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response_token)

    def test_register(self):
        missing_params = "'username, password, email' are required parameters."
        user_exists = "User or email already registered. Please login instead."

        print("\n>Running test for missing email at User registration.")
        response = self.register_user({'username':'test', 'password': 'test'})
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(missing_params, response_message)

        print(">Running test for missing username at User registration.")
        response = self.register_user({'email':'test', 'password': 'test'})
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(missing_params, response_message)

        print(">Running test for missing password at User registration.")
        response = self.register_user({'username':'test', 'email': 'test'})
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(missing_params, response_message)

        print(">Running test for missing all parameters at User registration.")
        response = self.register_user({})
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(missing_params, response_message)

        print(">Running test for successful User registration.")
        response = self.register_user({'username':'test', 'password': 'test', 'email': 'test'})
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 200)
        self.assertEqual("New user created.", response_message)

        print(">Running test for duplicate username registration.")
        response = self.register_user({'username':'test', 'password': 'test', 'email': 'not_in_db'})
        response_message = response.get_json().get('error')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(user_exists, response_message)

        print(">Running test for duplicate email registration.")
        response = self.register_user({'username':'not_in_db', 'password': 'test', 'email': 'test'})
        response_message = response.get_json().get('error')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(user_exists, response_message)

    def test_send_password_email(self):
        message = "An email has been sent with instructions to reset your password."

        print("\n>Running test for invalid username/email specified.")
        post_data = {'loginId':'notReal'}
        response = self.client.post('/api/forgot-password', data=json.dumps(post_data), content_type='application/json')
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(message, response_message)

        #This block requires valid SMTP credentials. It will fail without the AWS user/pass.
        #print(">Running test for valid username/email specified")
        #post_data={'loginId':'newUser'}
        #self.register_user({"username": "newUser", "password": "test", "email": "admin@simpledrinkmaker.com"})
        #response = self.client.post('/api/forgot-password', data=json.dumps(post_data), content_type='application/json')
        #response_message = response.get_json().get('message')
        #self.assertEqual(response.status_code, 200)
        #self.assertEqual(message, response_message)

    def test_reset_password(self):
        success_message = "Your password was reset."
        fail_message = "The reset password link is expired. Please try again."
        response = self.register_user({"username": "test", "password": "test", "email": "test"})

        print("\n>Running test for malformed token sent.")
        post_data = {"newPassword":"newpass"}
        response = self.client.post('/api/forgot-password/bad_token', data=json.dumps(post_data), content_type='application/json')
        response_message = response.get_json().get('error')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(fail_message, response_message)

        print(">Running test for expired token sent.")
        post_data = {"newPassword": "newpass"}
        token = self.get_test_user_token('test', -1)
        response = self.client.post('/api/forgot-password/' + token, data=json.dumps(post_data), content_type='application/json')
        response_message = response.get_json().get('error')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(fail_message, response_message)

        print(">Running test for successful password reset.")
        post_data = {"newPassword":"newpass"}
        token = self.get_test_user_token('test', 18000)
        response = self.client.post('/api/forgot-password/' + token, data=json.dumps(post_data), content_type='application/json')
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(success_message, response_message)

    def test_authenticate(self):
        invalid_message = "Invalid authentication token. Please log in and try again."

        print("\n>Running test for successful authentication.")
        header = self.get_authorization_header_token("user", "pass", "email")
        response = self.client.post('/api/authenticate', headers=header)
        user = response.get_json().get('user')
        self.assertEqual(response.status_code, 200)
        self.assertEqual('user', user)

        print(">Running test for missing header.")
        response = self.client.post('/api/authenticate')
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

        print(">Running test for invalid token.")
        header['Authorization'] = 'Bearer fake_token'
        response = self.client.post('/api/authenticate', headers=header)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

    def test_get_all_ingredients(self):
        invalid_message = "Invalid authentication token. Please log in and try again."

        print("\n>Running test for successful retrieval of database ingredients.")
        header = self.get_authorization_header_token("user", "pass", "email")
        response = self.client.get('/api/all-ingredients', headers=header)
        response_message = response.get_json().get('ingredients')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response_message) > 0)
        self.assertTrue(isinstance(response_message, dict))

        print(">Running test for missing header.")
        response = self.client.get('/api/all-ingredients')
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

        print(">Running test for invalid token.")
        header['Authorization'] = 'Bearer fake_token'
        response = self.client.get('/api/all-ingredients', headers=header)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

    def test_get_user_ingredients(self):
        invalid_message = "Invalid authentication token. Please log in and try again."

        print("\n>Running test for no ingredients in cabinet.")
        header = self.get_authorization_header_token("user", "pass", "email")
        response = self.client.get('/api/user-ingredients', headers=header)
        response_message = response.get_json().get('ingredients')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_message, dict))

        ingredient = {'name': "Apple", 'quantity': 1, 'isFavorite': False}
        self.add_ingredients_to_user(header, ingredient)

        print(">Running test for successful ingredient retrieval from cabinet.")
        response = self.client.get('/api/user-ingredients', headers=header)
        response_message = response.get_json().get('ingredients')
        self.assertEqual(response.status_code, 200)
        for item in response_message['default']:
            self.assertTrue(ingredient['name'] in item['name'])

        print(">Running test for missing header")
        response = self.client.get('/api/user-ingredients')
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

        print(">Running test for invalid token")
        header['Authorization'] = 'Bearer fake_token'
        response = self.client.get('/api/user-ingredients', headers=header)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

    def test_add_user_ingredients(self):
        header = self.get_authorization_header_token("user", "pass", "email")
        ingredients = {'name': "Banana", 'quantity': 1, 'isFavorite': False}
        ingredient_message = "Ok"
        missing_ingredients = "Provide name, quantity and isFavorite"
        invalid_message = "Invalid authentication token. Please log in and try again."

        print("\n>Running test for successful add ingredients to cabinet.")
        response = self.add_ingredients_to_user(header, ingredients)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ingredient_message, response_message)

        print(">Running test for duplicate add ingredients to cabinet.")
        response = self.add_ingredients_to_user(header, ingredients)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ingredient_message, response_message)
        response = self.add_ingredients_to_user(header, ingredients)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ingredient_message, response_message)

        print(">Running test for missing ingredients to add to cabinet.")
        ingredients = {}
        response = self.add_ingredients_to_user(header, ingredients)
        response_message = response.get_json().get('error')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(missing_ingredients, response_message)

        print(">Running test for missing header")
        response = self.client.post('/api/user-ingredients')
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

        print(">Running test for invalid token")
        header['Authorization'] = 'Bearer fake_token'
        response = self.client.post('/api/user-ingredients', headers=header)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

    def test_delete_user_ingredients(self):
        header = self.get_authorization_header_token("user", "pass", "email")
        ingredients = {"ingredients": ["Apple", "Avocado", "Banana"]}
        delete_ingredients = {"ingredients": ["Apple"]}
        delete_message = "Removed {} from user cabinet.".format(', '.join(delete_ingredients['ingredients']))
        invalid_message = "Invalid authentication token. Please log in and try again."
        missing_ingredients = "No valid ingredients"

        print("\n>Running test for delete user ingredients from cabinet.")
        self.add_ingredients_to_user(header, ingredients)
        response = self.delete_ingredients_from_user(header, delete_ingredients)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(delete_message, response_message)

        print(">Running test for duplicate delete user ingredients from cabinet.")
        self.add_ingredients_to_user(header, ingredients)
        response = self.delete_ingredients_from_user(header, delete_ingredients)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(delete_message, response_message)
        response = self.delete_ingredients_from_user(header, delete_ingredients)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(delete_message, response_message)

        print(">Running test for missing ingredients to delete cabinet.")
        ingredients['ingredients'] = ""
        response = self.delete_ingredients_from_user(header, ingredients)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(missing_ingredients, response_message)

        print(">Running test for duplicate add and delete user ingredients from cabinet.")
        self.add_ingredients_to_user(header, ingredients)
        self.add_ingredients_to_user(header, ingredients)
        response = self.delete_ingredients_from_user(header, delete_ingredients)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(delete_message, response_message)
        response = self.delete_ingredients_from_user(header, delete_ingredients)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(delete_message, response_message)

        print(">Running test for missing header")
        response = self.client.delete('/api/user-ingredients')
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

        print(">Running test for invalid token")
        header['Authorization'] = 'Bearer fake_token'
        response = self.client.delete('/api/user-ingredients', headers=header)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

    def test_add_user_custom_ingredients(self):
        header = self.get_authorization_header_token("user", "pass", "email")
        custom_ingredients = {'name': "Juicy", 'type': "Liquid"}
        custom_ingredient_message = "Added ingredient '{}' of type '{}'".format(custom_ingredients['name'], custom_ingredients['type'])
        custom_ingredient_exists = "'{}' already exists.".format(custom_ingredients['name'])
        custom_matches_default_ingredient = "{} is a default ingredient and can not be added as a custom ingredient.".format("Apple")
        missing_custom_ingredients = "'name' and 'type' are required parameters."
        invalid_message = "Invalid authentication token. Please log in and try again."

        print("\n>Running test for successful add custom ingredients to cabinet.")
        response = self.add_custom_ingredients_to_user(header, custom_ingredients)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(custom_ingredient_message, response_message)

        print(">Running test for duplicate add custom ingredients to cabinet.")
        response = self.add_custom_ingredients_to_user(header, custom_ingredients)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(custom_ingredient_exists, response_message)

        print(">Running test for add custom ingredients that match default ingredients to cabinet.")
        custom_ingredients = {'name': "Apple", 'type': "Fruit"}
        response = self.add_custom_ingredients_to_user(header, custom_ingredients)
        response_message = response.get_json().get('error')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(custom_matches_default_ingredient, response_message)

        print(">Running test for missing custom ingredients to add to cabinet.")
        custom_ingredients = {}
        response = self.add_custom_ingredients_to_user(header, custom_ingredients)
        response_message = response.get_json().get('error')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(missing_custom_ingredients, response_message)

        print(">Running test for missing header")
        response = self.client.post('/api/custom-ingredients')
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

        print(">Running test for invalid token")
        header['Authorization'] = 'Bearer fake_token'
        response = self.client.post('/api/custom-ingredients', headers=header)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

    def test_get_user_custom_ingredients(self):
        header = self.get_authorization_header_token("user", "pass", "email")
        custom_ingredients = {'name': "Juicy", 'type': "Liquid"}
        invalid_message = "Invalid authentication token. Please log in and try again."

        print("\n>Running test for no custom ingredients in cabinet.")
        response = self.client.get('/api/custom-ingredients', headers=header)
        response_message = response.get_json().get('ingredients')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_message, list))

        self.add_custom_ingredients_to_user(header, custom_ingredients)

        print(">Running test for successful custom ingredient retrieval from cabinet.")
        response = self.client.get('/api/custom-ingredients', headers=header)
        response_message = response.get_json().get('ingredients')
        self.assertEqual(response.status_code, 200)
        for item in response_message:
            self.assertTrue(custom_ingredients['name'] in item['name'])

        print(">Running test for missing header")
        response = self.client.get('/api/custom-ingredients')
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

        print(">Running test for invalid token")
        header['Authorization'] = 'Bearer fake_token'
        response = self.client.get('/api/custom-ingredients', headers=header)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

    def test_delete_user_custom_ingredients(self):
        header = self.get_authorization_header_token("user", "pass", "email")
        custom_ingredients = {'name': "Juicy", 'type': "Liquid"}
        custom_ingredient_message = "Ok"
        missing_custom_ingredients = "'name' is a required parameter."
        invalid_message = "Invalid authentication token. Please log in and try again."

        print("\n>Running test for successful delete custom ingredients from cabinet.")
        response = self.delete_custom_ingredients_from_user(header, custom_ingredients)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(custom_ingredient_message, response_message)

        print(">Running test for missing custom ingredients to delete from cabinet.")
        custom_ingredients = {}
        response = self.delete_custom_ingredients_from_user(header, custom_ingredients)
        response_message = response.get_json().get('error')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(missing_custom_ingredients, response_message)

        print(">Running test for missing header")
        response = self.client.delete('/api/custom-ingredients')
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

        print(">Running test for invalid token")
        header['Authorization'] = 'Bearer fake_token'
        response = self.client.delete('/api/custom-ingredients', headers=header)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

    def test_get_recipes(self):
        header = self.get_authorization_header_token("user", "pass", "email")
        all_recipe_first = "Acai-Peanut Protein"
        invalid_message = "Invalid authentication token. Please log in and try again."

        print("\n>Running test for get all recipes")
        response = self.client.get('/api/all-recipes', headers=header)
        response_message = response.get_json().get('recipes')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response_message, list))
        self.assertTrue(all_recipe_first in response_message[0]['name'])

        print(">Running test for missing header")
        response = self.client.get('/api/all-recipes')
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

        print(">Running test for invalid token")
        header['Authorization'] = 'Bearer fake_token'
        response = self.client.get('/api/all-recipes', headers=header)
        response_message = response.get_json().get('message')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(invalid_message, response_message)

    def test_database_consistency(self):
        header1 = self.get_authorization_header_token("user1", "pass", "email1")
        header2 = self.get_authorization_header_token("user2", "pass", "email2")
        ingredients = [{'name': "Banana", 'quantity': 1, 'isFavorite': False},
                       {'name': "Apple", 'quantity': 1, 'isFavorite': False}]
        ingredient_message = "Ok"
        delete_ingredients = {"ingredients": ["Banana"]}
        delete_message = "Removed {} from user cabinet.".format(', '.join(delete_ingredients['ingredients']))

        print("\n>Running test for adding same ingredients to multiple users.")
        for ingredient in ingredients:
            response1 = self.add_ingredients_to_user(header1, ingredient)
            response2 = self.add_ingredients_to_user(header2, ingredient)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response1.get_json().get('message'), response2.get_json().get('message'))

        print(">Manually checking that database entries contain the same ingredients for users.")
        user1 = User.query.filter_by(username='user1').first()
        user2 = User.query.filter_by(username='user2').first()
        ingredients_user1 = [ingredient.name for ingredient in user1.ingredients.all()]
        ingredients_user2 = [ingredient.name for ingredient in user2.ingredients.all()]
        self.assertTrue(sorted(ingredients_user1) == sorted(ingredients_user2))

        print(">Deleting an ingredient from one user.")
        response = self.delete_ingredients_from_user(header2, delete_ingredients)
        response_message = response.get_json().get('message')
        self.assertEqual(response_message, delete_message.format(', '.join(delete_ingredients['ingredients'])))
        self.assertTrue(response.status_code, 200)

        print(">Checking API reflects ingredient deletion from one user.")
        response1 = self.client.get('/api/user-ingredients', headers=header1)
        response2 = self.client.get('/api/user-ingredients', headers=header2)
        response_message1 = response1.get_json().get('ingredients')
        response_message2 = response2.get_json().get('ingredients')
        self.assertFalse(response_message1['default'] == response_message2['default'])

        print(">Manually checking database entries correctly reflect deletion.")
        user1 = User.query.filter_by(username='user1').first()
        user2 = User.query.filter_by(username='user2').first()
        ingredients_user1 = [ingredient.name for ingredient in user1.ingredients.all()]
        ingredients_user2 = [ingredient.name for ingredient in user2.ingredients.all()]
        self.assertTrue(sorted(ingredients_user1) != sorted(ingredients_user2))

        print(">Manually checking that deleting user ingredients did not corrupt Ingredients table.")
        banana = Ingredients.query.filter_by(name='banana').first()
        apple = Ingredients.query.filter_by(name='apple').first()
        self.assertTrue(banana != None)
        self.assertTrue(len(banana.owned_by) == 1)
        self.assertTrue(apple != None)
        self.assertTrue(len(apple.owned_by) == 2)

    def get_test_user_token(self, username, expires):
        user = User.query.filter_by(username=username).first()
        return user.get_reset_token(expires)

    def get_authorization_header_token(self, username, password, email):
        self.register_user({"username": username, "password": password, "email": email})
        login_data = {"loginId": username, "password": password}
        response = self.client.post('/api/login', data=json.dumps(login_data), content_type='application/json')
        token = response.get_json().get('token')
        return {"Authorization": "Bearer " + token}

    def register_user(self, data):
        return self.client.post('/api/register', data=json.dumps(data), content_type='application/json')

    def add_ingredients_to_user(self, header, ingredients):
        return self.client.patch('/api/all-ingredients',
                               data=json.dumps(ingredients),
                               headers=header,
                               content_type='application/json')

    def add_custom_ingredients_to_user(self, header, ingredients):
        return self.client.post('/api/custom-ingredients',
                               data=json.dumps(ingredients),
                               headers=header,
                               content_type='application/json')

    def delete_ingredients_from_user(self, header, ingredients):
        return self.client.delete('/api/user-ingredients',
                               data=json.dumps(ingredients),
                               headers=header,
                               content_type='application/json')

    def delete_custom_ingredients_from_user(self, header, ingredients):
        return self.client.delete('/api/custom-ingredients',
                               data=json.dumps(ingredients),
                               headers=header,
                               content_type='application/json')

if __name__ == '__main__':
    unittest.main(verbosity=2)
