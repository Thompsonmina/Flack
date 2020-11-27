import os

from flask import Flask, session, render_template, url_for, request, redirect, jsonify
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_mongoengine import MongoEngine
from flask_socketio import SocketIO, emit, join_room, leave_room, rooms

# get chat objects from module
# from chatobjects import Chat, PublicChannel, PrivateChannel
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["MONGODB_SETTINGS"] = {
	"db": "flack-2",
	"connect": False,
	'host': os.getenv("MONGO_URI") if os.getenv("MONGO_URI") else 'mongodb://localhost'
}

db = MongoEngine(app)
login_manager = LoginManager(app)
socketio = SocketIO(app,  manage_session=False)

from models import User, PublicChannel, Pair, Chat

@app.route("/", methods=["GET", "POST"])
def login():
	""" handle login functionality"""
	error = "" # will show errors on template if any exist
	if current_user.is_authenticated == True:
		return redirect(url_for("client"))

	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		if not (username and password):
			error = "one or all input fields are blank"
		else:
			user = User.objects(username=username).first()
			if user:
				if user.check_password(password):
					login_user(user)
					return redirect(url_for("client"))
				else:
					error = "incorrect password"
			else:
				error = "username does not exist"	
	return render_template("login.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
	"""handle registration functionality"""
	error = "" # will show errors on template if any exist
	if request.method == "POST":
		username = request.form["username"]
		correctpassword = request.form["password"] if request.form["password"] == request.form["confirm_password"] else ""
		if not (username and correctpassword):
			error = "invalid credentials, passwords do not match"
		else:
			# check if user is unique and proceed
			if User.objects(username=username).first() is None:
				user = User(username=username)
				user.set_password(request.form["password"])
				user.save()
				return redirect(url_for("login"))
			else:
				error = "username already exists, choose another one"

	return render_template("register.html", error=error)

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for("login"))

@app.route("/client")
@login_required
def client():
	""" the main view for the application"""
	# if a user has no lastchannel information dafault to general
	DEFAULTCHANNEL = "General"
	
	# get all the channnels and get all the people the user has dmed 
	# for rendering
	user = User.objects(username=current_user.username).get()
	public_channels = PublicChannel.getchannels()
	pairnames = user.pairnames
	othernames = [user.getotherperson(x) for x in pairnames]
	othernameAndPairname = list(zip(othernames, pairnames))

	# check if a user's lastchannel was a general channel or a dm
	ispublic = "true"
	if user.lastchannel in public_channels:
		pass
	elif user.lastchannel in pairnames:
		ispublic = "false"
	else:
		user.lastchannel = DEFAULTCHANNEL

	return render_template("client.html", public=public_channels, 
								directs=othernameAndPairname,
								ispublic=ispublic
							)

@app.route("/isChannelValid")
def isChannelValid():
	""" checks whether a channel exists """
	channel = request.args.get("channel")
	
	channel = PublicChannel.objects(name=channel).first()
	if channel is not None:
		return jsonify({"success": False, "message": "channel already exists"})

	return jsonify({"success": True})

@app.route("/getAllUsers")
def getUsers():
	""" returns all a list of the users registered apart from the current user """
	users = User.getUsers()
	users = [user for user in users if current_user.username != user]
	return jsonify({"success":True, "users":users})

@app.route("/getChats", methods=["POST"])
def getChats():
	""" returns the messages that belongs to a channel 
		or dm if it is valid
	"""
	channel = request.form.get("channel")
	ispublic = request.form.get("ispublic")
	
	if ispublic == "true":
		# get the channel information if the it exists otherwise fail
		channel = PublicChannel.objects(name=channel).first()
		if channel:
			# set the last channel to the channel just accessed
			current_user.lastchannel = channel.name
			current_user.save()
			messages = channel.getChats()
		else:
			return jsonify({"success": False})
	else:
		# fetch a Pair's messages if the pair exists else fail
		otheruser = current_user.getotherperson(channel)
		otheruser = User.objects(username=otheruser).first()
		if otheruser:
			user = User.objects(username=current_user.username).get()
			pair = Pair.getAPair(user, otheruser)
			if pair:
				messages = pair.getChats()
				current_user.lastchannel = pair.pairname
				current_user.save()
		else:
			return jsonify({"success": False})
		
	# send the messages
	return jsonify({"success": True, "messages":messages})

@socketio.on("add newchannel")
def createChannel(data):
	""" listen on the add newchannel socket, add a new channel to server and emit the new channel"""
	channel = data["name"]
	channel = PublicChannel(name=channel).save()
	emit("show newchannel", {"channel": channel.name, 
				"event_sender":current_user.username},
				broadcast=True)

@socketio.on("add new private pair")
def createADirectMessagePair(data):
	""" listen on the add new private channel socket, add a new private channel to the server, store the members and emit the new channel"""
	otheruser = data["name"]
	otheruser = User.objects(username=otheruser).first()

	if otheruser:
		# fetching the user again because currentuser is not compatible with Pair
		user = User.objects(username=current_user.username).get()
		try:
			pair = Pair(person1=user, person2=otheruser)
			pair.save()
			emit("show new private pair",{"pairname":pair.pairname,
					"event_sender":current_user.username},
					broadcast=True
			)
			print(pair.pairname)
		except:
			raise
			emit("error", {"message": "pair already exists"})			
	else:
		emit("error", {"message": "pair not created"})

@socketio.on("join")
def joinedRoom(data):
	""" add a user to a room, which is kind of a subset of  users that 
		can get a broadcast message """
	username = data["username"]
	room = data["channel"]
	join_room(room)

@socketio.on("leave")
def leftRoom(data):
	""" remove a user from a room """
	room = data["channel"]
	leave_room(room)

@socketio.on("got a message")
def addMessage(data):
	""" adds a message that was just typed by a user to the channel its on 
		and emits it to be shown only to users currently on that channel 
	"""
	sender = data["sender"]
	message = data["message"]
	channel = data["channel"]
	typeOfchannel = data["type"]
	
	if typeOfchannel == "private":
		otheruser = current_user.getotherperson(channel)
		otheruser = User.objects(username=otheruser).first()
		if otheruser:
			user = User.objects(username=current_user.username).get()
			pair = Pair.getAPair(otheruser, user)
			pair.addChat(sender=sender, message=message)
			emit("show message", pair.getlastchat(), room=pair.pairname)

	else:
		channel = PublicChannel.objects(name=channel).first()
		if channel:
			# add chat to channel
			channel.addChat(sender=sender, message=message)
			emit("show message", channel.getlastchat(), room=channel.name)


if __name__ == '__main__':
    app.run()