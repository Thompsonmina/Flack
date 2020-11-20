from application import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.objects(pk=user_id).first()

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
	date = db.DateTimeField(default=datetime.utcnow)

class PublicChannel(db.Document):
	name = db.StringField(required=True, max_length=15, unique=True)
	chats = db.EmbeddedDocumentListField(Chat)

	@classmethod
	def getchannels(cls):
		""" returns a list of all the public channel names"""
		channels = cls.objects.only('name')
		return [channel.name for channel in channels]

	def addChat(self, chatdict):
		""" adds a single chat document to the lists of chats"""
		try: 
			self.chats.create(**chatdict)
			self.chats.save()
		except:
			raise

	def getChats(self):
		self.chats


	def __str__(self):
		return f"<{self.name}>"

class PrivateChannel(db.Document):
	name = db.StringField(required=True, max_length=15, unique=True)
	chats = db.EmbeddedDocumentListField(Chat)
	users = db.ListField(db.ReferenceField(User, reverse_delete_rule=db.PULL))