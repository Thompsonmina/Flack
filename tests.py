# basic tests for the functionality of the api

import os 
import unittest
import mongomock
from application import app, db, User, PublicChannel, Pair, url_for

class Config(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		# configurations
		app.config["TESTING"] = True
		app.config["DEBUG"] = False
		app.config["SECRET_KEY"] = "JEJ78623YBEEHKUK21"
		db.disconnect()
		db.connect("test", host="mongomock://localhost")

		
	@classmethod
	def tearDownClass(cls):
		User.objects.delete()
		PublicChannel.objects.delete()
		Pair.objects.delete()
		db.disconnect()


class UserModelTests(Config):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.uche = User(username="uclw", password_hash="blablabla")
		cls.uche.save()

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

	def test_user_getotherperson_method(self):
		""" test that the method works as prescribed"""

		billy = User(username="billy")
		billy.set_password("billy")
		billy.save()
		p = Pair(person1=billy, person2=self.uche)
		p.save()
		self.assertEqual(billy.username, self.uche.getotherperson(p.pairname))
		self.assertEqual(self.uche.username, billy.getotherperson(p.pairname))



class PublicChannelModelTests(Config):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		cls.channel1 = PublicChannel(name='first')
		cls.channel1.save()

	def tearDown(self):
		""" delete all the other temp classes apart from the one
			created at class scope
		"""
		PublicChannel.objects[1:].delete()
	
	def test_channel_getchannels_method(self):
		""" ensure that the method works as expected"""

		second = PublicChannel(name='second')
		second.save()

		self.assertEqual(2, len(PublicChannel.getchannels()))
		second.delete()
		self.assertEqual(1, len(PublicChannel.getchannels()))
		self.assertEqual(self.channel1.name, PublicChannel.getchannels()[0])

	def test_channel_addChat_method(self):
		""" ensure that the method works as expected"""
		channel2 = PublicChannel(name='channel2')
		channel2.save()

		chat = {"sender":"joe", "message":"this is message"}
		channel2.addChat(**chat)

		self.assertIsNotNone(channel2.chats)
		recievedchat = channel2.chats[0]
		
		self.assertEqual({
							"sender":recievedchat.sender, 
							"message":recievedchat.message
							}, chat)

		# add test for validity of date

	@unittest.expectedFailure
	def test_channel_addChat_method_fails_wrong_args(self):
		""" ensure that the method works as expected"""
		channel2 = PublicChannel(name='channel2')
		channel2.save()

		badchat = {"sender":"joe", "message":"this is message", "rando":32}

		# will cause error and decorator shall handle it
		channel2.addChat(**badchat)

	def test_channel_getlastchat_method(self):
		""" ensure that the method works as expected"""

		channel2 = PublicChannel(name='channel2')
		channel2.save()

		chat1 = {"sender":"joe", "message":"this is message"}
		chat2 = {"sender":"jim", "message":"this is other message"}
		channel2.addChat(**chat1)
		channel2.addChat(**chat2)
		
		lastchat = channel2.getlastchat()
		lastchat.pop("date")
		self.assertEqual(chat2, lastchat)

	def test_channel_getChats_method(self):
		""" ensure that the method works as expected"""
		numberofchats = 5
		
		channel2 = PublicChannel(name='channel2')
		channel2.save()

		for i in range(numberofchats):
			channel2.addChat(**{"sender":"joe", "message":"this is message"})

		self.assertEqual(numberofchats, len(channel2.getChats()))


class PairModelTests(Config):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()

		cls.brian = User(username="brian")
		cls.brian.set_password("brian password ayyee")
		cls.brian.save()
		cls.suzy = User(username="suzy")
		cls.suzy.set_password("shwingggg")
		cls.suzy.save()

		cls.pair = Pair(person1=cls.brian, person2=cls.suzy)

	def tearDown(self):
		# delete all the other temp classes apart from the one
		# crated at class scope
		Pair.objects[1:].delete()
		User.objects[2:].delete()
		self.suzy.pairnames[1:] = []
		self.brian.pairnames[1:] = []		
		self.pair.chats = []
				
	# def test_channel_getchannels_method(self):
	# 	""" ensure that the methods works as expected"""

	# 	second = PublicChannel(name='second')
	# 	second.save()

	# 	self.assertEqual(2, len(PublicChannel.getchannels()))
	# 	second.delete()
	# 	self.assertEqual(1, len(PublicChannel.getchannels()))
	# 	self.assertEqual(self.channel1.name, PublicChannel.getchannels()[0])
	
	@unittest.expectedFailure
	def test_pair_doesnt_allow_symmetric_pairs(self):
		""" ensure that if a pair(a, b) is stored already, then a pair(b, a)
			cannot also be be stored 
		"""

		# we already have a pair brian, suzy so creating a pair suzy, brian should be an error
		Pair(person1=self.suzy, person2=self.brian).save()

	def test_pair_getAPair_method_works_as_prescribed(self):
		""" test that irrespective of order of users in the method it will
			return the same pair object regardless if the users exists
			or none if the user doesnt exist
		"""

		self.assertEqual(self.pair, Pair.getAPair(self.brian, self.suzy))
		self.assertEqual(self.pair, Pair.getAPair(self.suzy, self.brian))
		popo = User(username="popo")
		popo.set_password("popo")
		popo.save()
		self.assertIsNone(Pair.getAPair(popo, self.suzy))

	def test_pair_generate_pairname_method(self):
		""" test that generate pairnames actualy generates pairnames well"""
		expectedpairname = self.brian.username + '-' +  self.suzy.username

		generatedpairname = self.pair.generate_pairname()
		self.assertEqual(expectedpairname, generatedpairname)
		self.assertEqual(expectedpairname, self.pair.pairname)

	def test_pair_adds_pairnamesToIndividualUsers(self):
		""" test that when a pair is created its pairname is added to
			pairnames list of the users it references
		"""

		# test with a brand new pair
		eze = User(username="eze")
		eze.set_password('ezeiscool')
		eze.save()

		Pair(person1=eze, person2=self.suzy).save()
		self.assertEqual(1, len(eze.pairnames))
		self.assertIn(self.suzy.username, eze.pairnames[0])
		self.assertEqual(2, len(self.suzy.pairnames))

	def test_pair_doesnt_duplicate_pairnames_onRepeatedSaveCalls(self):
		""" test that if we call save on the same pair object again we doen
			add the same pairname a=on its user references again
		"""		

		eze = User(username="eze")
		eze.set_password('ezeiscool')
		eze.save()

		p = Pair(person1=eze, person2=self.suzy)
		p.save()
		p.save()
		p.save()

		self.assertNotEqual(3, len(eze.pairnames))
		self.assertEqual(1, len(eze.pairnames))

	def test_pair_ondelete_refrenceusers_associatingPairnamesAreDeleted(self):
		""" test that when we delete a pair the pairname stored in the 
			pair's referenced users are also deleted as well
		"""

		eze = User(username="eze")
		eze.set_password('ezeiscool')
		eze.save()

		p = Pair(person1=eze, person2=self.suzy)
		p.save()
		self.assertEqual(2, len(self.suzy.pairnames))
		p.delete()
		self.assertEqual(1, len(self.suzy.pairnames))

	def test_pair_addChat_method(self):
		""" ensure that the method works as expected"""

		chat = {"sender":"joe", "message":"this is message"}
		self.pair.addChat(**chat)

		self.assertIsNotNone(self.pair.chats)
		recievedchat = self.pair.chats[0]
		
		self.assertEqual({
							"sender":recievedchat.sender, 
							"message":recievedchat.message
							}, chat)

		# add test for validity of date

	@unittest.expectedFailure
	def test_pair_addChat_method_fails_wrong_args(self):
		""" ensure that the method works as expected"""

		badchat = {"sender":"joe", "message":"this is message", "rando":32}

		# will cause error and decorator shall handle it
		self.pair.addChat(**badchat)

	def test_channel_getlastchat_method(self):
		""" ensure that the method works as expected"""

		chat1 = {"sender":"joe", "message":"this is message"}
		chat2 = {"sender":"jim", "message":"this is other message"}
		self.pair.addChat(**chat1)
		self.pair.addChat(**chat2)
		
		lastchat = self.pair.getlastchat()
		lastchat.pop("date")
		self.assertEqual(chat2, lastchat)

	def test_channel_getChats_method(self):
		""" ensure that the method works as expected"""
		numberofchats = 5
		
		for i in range(numberofchats):
			self.pair.addChat(**{"sender":"joe", "message":"this is message"})

		self.assertEqual(numberofchats, len(self.pair.getChats()))


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