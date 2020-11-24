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
	pairnames = db.ListField(db.StringField())
	lastchannel = db.StringField(default=DEFAULTCHANNEL)

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		""" check if the password is the correct one""" 	
		return check_password_hash(self.password_hash, password)

	def getotherperson(self, pairname):
			other = None
			both = pairname.split("-")		
			if self.username in both:	
				other = both[0] if both[0] != self.username else both[1]
			
			return other

	def addToPairNames(self, pairname):
		if pairname not in self.pairnames:
			self.pairnames.append(pairname)

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

class Pair(db.Document):
	""" a pair holds the chats between 2 people """
	pairname = db.StringField()
	chats = db.EmbeddedDocumentListField(Chat)
	person1 = db.ReferenceField(User,
					reverse_delete_rule=db.CASCADE,
					required=True
				)
	person2 = db.ReferenceField(User, 
					unique_with="person1",
					reverse_delete_rule=db.CASCADE,
					required=True
				)
	hasBeenModified = db.BooleanField(default=False)

	@classmethod
	def getAPair(cls, person1, person2):
		firstTry = cls.objects(person1=person1, person2=person2).first()
		lastTry = cls.objects(person1=person2, person2=person1).first()
		
		return firstTry or lastTry

	def generate_pairname(self):
		return self.person1.username + "-" + self.person2.username

	def save(self):
		def addthemselves():
			self.pairname = self.generate_pairname()
			self.person1.addToPairNames(self.pairname)
			self.person2.addToPairNames(self.pairname)
			self.person2.save()

		if not self.hasBeenModified:
			identical = Pair.objects(person1=self.person2, person2=self.person1).first()
			if not identical:
				self.hasBeenModified = True	
				addthemselves()
			else:
				raise Exception
		
		super().save()
		self.person1.save()
		self.person2.save()

		
	def delete(self):
		try:
			x = self.person1.pairnames.index(self.pairname)
			y = self.person2.pairnames.index(self.pairname)
		except ValueError:
			return -1
		self.person1.pairnames.pop(x)
		self.person2.pairnames.pop(y)

		super().delete()
		
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
		return f"<{self.person1} {self.person2}>"

