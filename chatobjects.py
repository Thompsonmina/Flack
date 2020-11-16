from collections import defaultdict, deque, namedtuple

""" this module contains the data structures that will be used
	a chat named tuple that will contain chat details and  public and private 
	channel classes 
"""


Chat = namedtuple("Chat", ["message", "date", "user"])

class PublicChannel:
	def __init__(self):
		"""initialize a queue that will hold chats"""
		self.chats = deque(maxlen=100) # max lenght of 100, the 101th chat will cause the 1 chat to popped to make room

	def addChat(self, chattuple):
		""" add a chat to the queue"""
		self.chats.append(chattuple)

	def getChats(self):
		""" return all the chats tuples"""
		return list(self.chats)
		
	def __repr__(self):
		return f"PublicChannel()"

class PrivateChannel:
	def __init__(self, listOfMembers):
		""" initialise a queue and create a list of members """
		self.members = list(listOfMembers)
		self.chats = deque(maxlen=100)

	def addChat(self, chattuple):
		""" add a chat to the queue"""
		self.chats.append(chattuple)

	def getChats(self):
		""" return all the chats"""
		return list(self.chats)

	def isMember(self, user):
		""" check if a user is a member of the channel"""
		for member in self.members:
			if user == member:
				return True
		return False

	def addMember(self, user):
		""" add a new member"""
		self.members.append(user)

	def removeMember(self, user):
		""" remove a member"""
		self.members.remove(user)

	def getAllMembers(self):
		return list(self.members)

	def __repr__(self):
		return f"private channel(), members are {[x for x in self.members]}"
