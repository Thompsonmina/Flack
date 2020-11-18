from application import db, login_manager
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.objects(pk=user_id).first()

class User(UserMixin, db.Document):
	username = db.StringField(required=True, unique=True)
	password_hash = db.StringField(required=True)
	privatechannels = db.ListField(db.StringField())

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)

	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

class Chat(db.EmbeddedDocument):
	sender = db.StringField(required=True)
	message = db.StringField(required=True)
	date = db.DateTimeField(default=datetime.utcnow)

class PublicChannel(db.Document):
	name = db.StringField(required=True, max_length=15, unique=True)
	chats = db.EmbeddedDocumentListField(Chat)

class PrivateChannel(db.Document):
	name = db.StringField(required=True, max_length=15, unique=True)
	chats = db.EmbeddedDocumentListField(Chat)
	users = db.ListField(db.ReferenceField(User, reverse_delete_rule=db.PULL))