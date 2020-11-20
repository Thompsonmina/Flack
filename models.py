from application import db, login_manager
import datetime
import pytz
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

import json

@login_manager.user_loader
def load_user(user_id):
	return User.objects(pk=user_id).first()


"""  
	mongo db Odm interface
"""

DEFAULTCHANNEL = "General"

class User(UserMixin, db.Document):
	username = db.StringField(required=True, unique=True)
	password_hash = db.StringField(required=True)
	privatechannels = db.ListField(db.StringField())
	lastchannel = db.StringField(default=DEFAULTCHANNEL)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		""" check if the password is the correct one""" 	
		return check_password_hash(self.password_hash, password)

	def __str__(self):
		return f"<{self.username}>"

class Chat(db.EmbeddedDocument):
	sender = db.StringField(required=True)
	message = db.StringField(required=True)
	date = db.DateTimeField(default=datetime.datetime.utcnow())

class PublicChannel(db.Document):
	""" represents the public channels internally"""
	name = db.StringField(required=True, max_length=15, unique=True)
	chats = db.EmbeddedDocumentListField(Chat)

	@classmethod
	def getchannels(cls):
		""" returns a list of all the public channel names"""
		channels = cls.objects.only('name')
		return [channel.name for channel in channels]

	def addChat(self, **chatdict):
		""" adds a single chat document to the lists of chats
		chats args are passed as kwargs
		"""
		try: 
			self.chats.create(**chatdict)
			self.chats.save()
		except:
			raise

	def getlastchat(self):
		""" returns the last added chat object as a dict"""
		chat = self.chats[-1]
		return {"sender":chat.sender, "date":chat.date.isoformat(), "message":chat.message}

	def getChats(self):
		""" returns a sorted list of chat dicts"""
		chats = []	
		for x in sorted(self.chats, key=lambda x: x.date):
			x.date = x.date.isoformat()
			chats.append({"sender":x.sender, "date":x.date, "message":x.message})
		
		return chats

	def __str__(self):
		return f"<{self.name}>"

class PrivateChannel(db.Document):
	name = db.StringField(required=True, max_length=15, unique=True)
	chats = db.EmbeddedDocumentListField(Chat)
	users = db.ListField(db.ReferenceField(User, reverse_delete_rule=db.PULL))