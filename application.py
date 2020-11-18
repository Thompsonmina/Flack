import os

from flask import Flask, session, render_template, url_for, request, redirect, jsonify
from flask_login import LoginManager
from flask_mongoengine import MongoEngine
from flask_socketio import SocketIO, emit, join_room, leave_room

# get chat objects from module
from chatobjects import Chat, PublicChannel, PrivateChannel
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

app.config["MONGODB_SETTINGS"] = {
	"db": "flack",
	"connect": False
}
db = MongoEngine(app)
login_manager = LoginManager(app)
socketio = SocketIO(app)

# # Configure session to use filesystem
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# # global dictionary of public channels 
# channels = dict()
# channels["general"] = PublicChannel() # default general channel
# channels["general"].addChat(Chat("welcome, this is the default channel", "", "Admin"))

# # global dictionary of private channels
# privateChannels = dict()

# # global users list
# users = []
from models import User

@app.route("/")
def login():
	""" render the login page"""
	return render_template("login.html")

@app.route("/register")
def register():
	"handle registration functionality"
	return render_template("register.html")

@app.route("/old")
def oldlogin():
	return render_template("welcome.html")

def register():
	pass

@app.route("/newclient")
def new():
	return render_template("newclient.html")

@app.route("/send", methods=["POST"])
def send():
	""" gets called by the ajax request to bypass sign up page if user already exists"""
	user = request.form.get("username")
	if (request.form.get("newuser") == "true"):
		session["username"] = user
		users.append(user)
		
	return redirect(f"/client/{user}")

@app.route("/client/<string:username>")
def clientView(username):
	""" the main application view """
	if username == session["username"]: # ensure that a user can only access ther url
		return render_template("client.html", channels=channels.keys(), isLoggedIn=True)
	else: 
		return redirect("/error")

@app.route("/error")
def errorView():
	return render_template("error.html")

@app.route("/getUsers", methods=["POST"])
def getUsers():
	""" gets all the users registered on the app apart from the user making the request"""
	otherusers = [user for user in users if user != session["username"]]
	return jsonify({"users": otherusers})
	
@app.route("/leave")
def delete():
	""" remove the user from every private room and delete the user's session data"""
	user = session["username"]
	for channel in privateChannels.values():
		if channel.isMember(user):
			channel.removeMember(user)
	try:
	 	users.remove(user)
	except Exception as e:
	 	raise e
	finally: 
		session.clear()
		return redirect("/")

@socketio.on("add newchannel")
def createChannel(data):
	""" listen on the add newchannel socket, add a new channel to server and emit the new channel"""
	channel = data["name"]
	channels[channel] = PublicChannel()
	emit("show newchannel", {"channel": channel}, broadcast=True)

@socketio.on("add new privatechannel")
def createAPrivateChannel(data):
	""" listen on the add new private channel socket, add a new private channel to the server, store the members and emit the new channel"""
	channelname = data["name"]
	channel = PrivateChannel(data["members"])
	privateChannels[channelname] = channel
	emit("show new privatechannel", {"channel": channelname, "members": channel.getAllMembers()}, broadcast=True)

@app.route("/getPrivateChannels", methods=["POST"])
def getAUserPrivateChannels():
	""" return the private channels a user belongs to"""
	user = request.form.get("user")
	channels = []
	
	for channel in privateChannels:
		if privateChannels[channel].isMember(user):
			channels.append(channel)

	return jsonify({"channels": channels})

@app.route("/getChats", methods=["POST"])
def getChats():
	""" returns the messages that belongs to a channel"""
	channel = request.form.get("channel")
	ispublic = request.form.get("ispublic")
	
	# if a channel is successfully retrieved
	if channel:
		if ispublic == "true": 
			try: # check if key exists in public channels
				channels[channel]
			except KeyError:
				return jsonify({"error": "KeyError", "success":False})
		else:
			try: # check if key exists in private channels
				privateChannels[channel]
			except KeyError:
				return jsonify({"error": "KeyError", "success":False})

		# get all the chats stored in a channel
		if ispublic == "true":
			chatstuples = channels[channel].getChats()
		else:
			chatstuples = privateChannels[channel].getChats()
		
		# convert each chat to a dict to be passed to the client
		messages =list(map(lambda chat: chat._asdict(), chatstuples)) 
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
	join_room(room)

@socketio.on("leave")
def leftRoom(data):
	""" remove a user from a room """
	room = data["channel"]
	leave_room(room)



@socketio.on("got a message")
def addMessage(data):
	""" adds a message that was just typed by a user to the channel its on and emits it to be shown only to users currently on that channel """
	time = data["time"]
	user = data["user"]
	message = data["message"]
	channel = data["channel"]
	typeOfchannel = data["type"]
	chat = Chat(message, time, user) # create a new chat with extracted details
	
	if typeOfchannel == "private":
		privateChannels[channel].addChat(chat)
	else:
		channels[channel].addChat(chat) # add chat to channel

	# emit the message to the client to be displayed to only those currently in the channel
	emit("show message", chat._asdict(), room=channel)