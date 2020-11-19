# basic tests for the functionality of the api

import os 
import unittest

from application import app, db, User, url_for

class Config(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		# configurations
		app.config["TESTING"] = True
		app.config["DEBUG"] = False
		app.config["MONGODB_SETTINGS"] = {
			"host": "mongomock://localhost",
		}
		app.config["SECRET_KEY"] = "JEJ78623YBEEHKUK21"


class UserModelTests(Config):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.uche = User(username="uclw", password_hash="blablabla")
		cls.uche.save()

	@classmethod
	def tearDownClass(cls):
		User.objects.delete()
		db.disconnect()

	def test_user_object_exists(self):
		""" test that a user instannce was created well in the db"""
		self.assertIsInstance(self.uche, User)
		self.assertIsNotNone(User.objects(username=self.uche.username).first())

	def test_user_set_password_method(self):
		""" test that the set password method actually fills the password_hash field
		and that the value in the password hash field is infact not the actual password"""

		newguy = User(username="steve")
		password = "gibberish56"
		newguy.set_password(password)	
		
		self.assertIsNotNone(newguy.password_hash)
		self.assertNotEqual(password, newguy.password_hash)	

	def test_user_check_password_method(self):
		""" ensure that the checkpassword method actually works as expected"""
		password = "gibberish"
		newgirl = User(username="ada") 
		newgirl.set_password(password)

		self.assertTrue(newgirl.check_password(password))
		self.assertFalse(newgirl.check_password("wronmg password"))

class ChannelModelTests(Config):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		

class AuthViewTests(Config):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()

		cls.client = app.test_client()
		cls.USERNAME, cls.PASSWORD = "brian", "newpasswordwhothis"
		cls.user = User(username=cls.USERNAME)
		cls.user.set_password(cls.PASSWORD)
		cls.user.save()

		cls.register_url = "/register"
		cls.login_url = "/"

	# register route tests	
	def test_register_route_on_GET(self):
		""" test default register page"""
		response = self.client.get(self.register_url, content_type="html/text")

		self.assertEqual(response.status_code, 200)

	def test_register_route_user_created_successfully(self):
		""" test to ensure that a user was created successfuly"""
		newuser, newuserpassword = "James", "password_hehe"
		data = {"username":newuser, "password":newuserpassword, 
					 "confirm_password":newuserpassword}
		response = self.client.post(self.register_url, data=data, follow_redirects=True)

		# check if there are 2 users in the db, the user and setup and the new user created
		self.assertEqual(2, len(User.objects()))
		self.assertEqual(200, response.status_code)

	def test_register_route_user_creation_failed_when_username_is_duplicate(self):
		""" test for when a user creation fails"""

		# putting in a duplicate user to ensure failure
		data = {"username":self.user.username, "password":"bleh", "email":"blabla@mail.com",
					 "confirm_password":"bleh"}

		response = self.client.post(self.register_url, data=data)

		self.assertEqual(200, response.status_code)
		# need access to request context cant figure it out yet
		# using the with block seems to fail

	# login route
	def test_login_route_on_GET(self):
		response = self.client.get(self.login_url)

		self.assertEqual(response.status_code, 200)

	def test_login_route_user_login_successful(self):
		""" test that a user has successfully been logged in"""
		data = {"username":self.USERNAME, "password":self.PASSWORD}
		response = self.client.post(self.login_url, data=data, follow_redirects=True)

		self.assertEqual(response.status_code, 200)

	def test_login_route_user_login_failed(self):
		""" test for if a user is not authenticated """
		data = {"username":"randousername", "password":"randopassword"}
		response = self.client.post(self.login_url, data=data)

		self.assertEqual(response.status_code, 200)
		



# class ApiFunctionality(unittest.TestCase):

# 	@classmethod
# 	def setUpClass(self):
# 		# configurations
# 		app.config["TESTING"] = True
# 		app.config["DEBUG"] = False
# 		app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + TEST_DB
# 		self.app = app.test_client()
# 		db.drop_all()
# 		db.create_all()


# 		self.FOOD_ITEM = "soy_milk"
# 		self.CATEGORY = "beverages"
# 		self.SINGLE_FOOD_URL = "/api/foods/" + self.FOOD_ITEM
# 		self.FOOD_BY_CATEGORY_URL = "/api/food_category/" + self.CATEGORY
# 		self.ALL_FOODS_URL = "/api/foods"

# 		category = Category(name=self.CATEGORY)
# 		category.save()
# 		food = Food(name=self.FOOD_ITEM, url="url", category_id=1, 
# 			calories="123", carbs="678", protein="78", sugar="987",
# 			fat="678", sodium="12")
# 		food.save()

# 	def test_index(self):
# 		response = self.app.get("/", content_type="html/text")
# 		self.assertEqual(response.status_code, 200)
		
# 	def test_single_food_request(self):
# 		response = self.app.get(self.SINGLE_FOOD_URL)
# 		self.assertEqual(response.status_code, 200)
# 		self.assertIn(self.FOOD_ITEM.encode(), response.data)

# 	def test_bad_single_food_request(self):
# 		response = self.app.get(self.SINGLE_FOOD_URL + "bleh bleh")
# 		self.assertEqual(response.status_code, 404)
		
# 	def test_category_request(self):
# 		response = self.app.get(self.FOOD_BY_CATEGORY_URL)
# 		self.assertEqual(response.status_code, 200)
# 		self.assertIn(self.CATEGORY.encode(), response.data)

# 	def test_bad_category_request(self):
# 		response = self.app.get(self.FOOD_BY_CATEGORY_URL + "blehbleh")
# 		self.assertEqual(response.status_code, 404)

# 	def test_all_foods_request(self):
# 		response = self.app.get(self.ALL_FOODS_URL)
# 		self.assertEqual(response.status_code, 200)
# 		self.assertIsNotNone(response.data)


if __name__ == "__main__":
	unittest.main()