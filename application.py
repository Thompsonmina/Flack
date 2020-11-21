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
	"db": "flack",
	"connect": False
}
db = MongoEngine(app)
login_manager = LoginManager(app)
socketio = SocketIO(app,  manage_session=False)

from models import User, PublicChannel, Pair

@app.route("/", methods=["GET", "POST"])
def login():
	""" handle login functionality"""
	error = "" # will show errors on template if any exist
	if current_user.is_authenticated == True:
		return redirect(url_for("new"))

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
					print(current_user.lastchannel)

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
	DEFAULTCHANNEL = "General"
	public_channels = PublicChannel.getchannels()
	current_user.lastchannel = current_user.lastchannel if current_user.lastchannel in public_channels else DEFAULTCHANNEL
	return render_template("newclient.html", public=public_channels)

@app.route("/is_channel_valid")
def isChannelValid():
	channel = request.args.get("channel")
	
	channel = PublicChannel.objects(name=channel).first()
	if channel is not None:
		return jsonify({"success": False, "message": "channel already exists"})
	
	return jsonify({"success": True})

@app.route("/delete_channels")
def deletechannel():
	PublicChannel.objects.delete()
	return jsonify({"success": True})

# @app.route("/send", methods=["POST"])
# def send():
# 	""" gets called by the ajax request to bypass sign up page if user already exists"""
# 	user = request.form.get("username")
# 	if (request.form.get("newuser") == "true"):
# 		session["username"] = user
# 		users.append(user)
		
# 	return redirect(f"/client/{user}")

# @app.route("/client/<string:username>")
# def clientView(username):
# 	""" the main application view """
# 	if username == session["username"]: # ensure that a user can only access ther url
# 		return render_template("client.html", channels=channels.keys(), isLoggedIn=True)
# 	else: 
# 		return redirect("/error")

# @app.route("/error")
# def errorView():
# 	return render_template("error.html")

# @app.route("/getUsers", methods=["POST"])
# def getUsers():
# 	""" gets all the users registered on the app apart from the user making the request"""
# 	otherusers = [user for user in users if user != session["username"]]
# 	return jsonify({"users": otherusers})
	
# @app.route("/leave")
# def delete():
# 	""" remove the user from every private room and delete the user's session data"""
# 	user = session["username"]
# 	for channel in privateChannels.values():
# 		if channel.isMember(user):
# 			channel.removeMember(user)
# 	try:
# 	 	users.remove(user)
# 	except Exception as e:
# 	 	raise e
# 	finally: 
# 		session.clear()
# 		return redirect("/")

# @socketio.on("add newchannel")
# def createChannel(data):
# 	""" listen on the add newchannel socket, add a new channel to server and emit the new channel"""
# 	channel = data["name"]
# 	channel = PublicChannel(name=channel).save()
# 	emit("show newchannel", {"channel": channel.name}, broadcast=True)

# @socketio.on("add new privatechannel")
# def createAPrivateChannel(data):
# 	""" listen on the add new private channel socket, add a new private channel to the server, store the members and emit the new channel"""
# 	channelname = data["name"]
# 	channel = PrivateChannel(data["members"])
# 	privateChannels[channelname] = channel
# 	emit("show new privatechannel", {"channel": channelname, "members": channel.getAllMembers()}, broadcast=True)

# @app.route("/getPrivateChannels", methods=["POST"])
# def getAUserPrivateChannels():
# 	""" return the private channels a user belongs to"""
# 	user = request.form.get("user")
# 	channels = []

# 	for channel in privateChannels:
# 		if privateChannels[channel].isMember(user):
# 			channels.append(channel)

# 	return jsonify({"channels": channels})

@app.route("/getChats", methods=["POST"])
def getChats():
	""" returns the messages that belongs to a channel if the 
	channel is valid"""
	channel = request.form.get("channel")
	ispublic = request.form.get("ispublic")
	
	channel = PublicChannel.objects(name=channel).first()
	if channel and ispublic:
		current_user.lastchannel = channel.name
		current_user.save()
		messages = channel.getChats()
		
		return jsonify({"success": True, "messages":messages})

	# if channel doesn't exist send a failure 	
	else:
		return jsonify({"success": False})

@socketio.on("join")
def joinedRoom(data):
	""" add a user to a room, which is kind of a subset of  users that 
		can get a broadcast message """
	username = data["username"]
	room = data["channel"]
	print(rooms(), "before join")
	join_room(room)
	print(rooms())


@socketio.on("leave")
def leftRoom(data):
	""" remove a user from a room """
	room = data["channel"]
	print(rooms(), "before leave")
	leave_room(room)
	print(rooms())

@socketio.on("got a message")
def addMessage(data):
	""" adds a message that was just typed by a user to the channel its on and emits it to be shown only to users currently on that channel """
	sender = data["sender"]
	message = data["message"]
	channel = data["channel"]
	typeOfchannel = data["type"]

	# chat = Chat(message, time, user) # create a new chat with extracted details
	
	if typeOfchannel == "private":
		privateChannels[channel].addChat(chat)
	else:
		channel = PublicChannel.objects(name=channel).first()
		if channel:
			# add chat to channel
			channel.addChat(sender=sender, message=message)
		print("message sent", channel)

	# emit the message to the client to be displayed to only those currently in the channel
	emit("show message", channel.getlastchat(), room=channel.name)
	print(channel.getlastchat())

if __name__ == '__main__':
    socketio.run(app)