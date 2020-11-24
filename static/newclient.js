// global username and the last channel accessed 
const username = document.querySelector("#userinfo").dataset.username;
let lastChannel = document.querySelector("#userinfo").dataset.lastchannel;
let ispublic = document.querySelector("#userinfo").dataset.ispublic;

if (ispublic === "true"){
	ispublic = true;
}else{
	ispublic = false;
}

// register a helper fumction to handlebar that helps to differientiate btw the user and others
Handlebars.registerHelper("isCurrentUser", function(name)
{
		return name === username;
});


document.addEventListener("DOMContentLoaded", () => 
{
	var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
	console.log(socket)
	// when logged out, clear local storage 

	// display the chats of the last channel the user was on, on load
	getChats(socket, lastChannel, ispublic);
			
	//	configure channel buttons to show chats on click when page is loaded
	document.querySelectorAll(".public").forEach(a => {
		a.onclick = function() {
			getChats(socket, this.name)
			}; 
	});

	//	configure channel buttons to show chats on click when page is loaded
	document.querySelectorAll(".private").forEach(a => {
		a.onclick = function() {
			console.log('yippe kayeee')
			getChats(socket, this.name, false)
			}; 
	});

	document.querySelector("#sentmssg").onsubmit = () =>{

		const message = document.querySelector("#message").value;
		// reset the textbox
		document.querySelector("#message").value = "";
		
		if (message.length >= 1){  // send only if message is not blank
			
			// emit the single chat's details to the server
			console.log("message", message);
			const user = username;
			a = document.getElementsByName(lastChannel)[0];
			socket.emit("got a message", {"message":message, 
				"sender":user, "channel":lastChannel, 
				"type":a.dataset.type});
		}
		return false;
	};

	// when connected configure
	socket.on("connect", function() {
		console.log("connected")
		// when a create public button is clicked emit a new channel if it already doesnt exist
		document.querySelector('#create-public').onclick = () => {

		    	const channel = prompt(`Create Public Channel \nEnter the channel name:`);

		    	if (channel === ""){
		    		alert("You didnt enter input");
		    	}
		    	else if (channel.length > 15){ // set a chanenl name limit
		    		alert("channel name lenght has exceed limit");
		    	}
		    	else {
		    		fetch(`/is_channel_valid?channel=${channel}`)
		    		.then(response => response.json())
		    		.then(data => {
		    			if (data.success){
		    				socket.emit("add newchannel", {"name": channel});
		    				console.log("emmited")
		    			}
		    			else {
		    				alert("the channel already exists");
		    			}
		    		})
		    	}
	    	};
		
		document.querySelector('#create-private').onclick = () => {

	    		fetch(`/getAllUsers`)
	    		.then(response => response.json())
	    		.then(data => {
	    			if (data.success){
	    				let users = data.users
	    				renderModalAndEmitData(socket, users); 
	    			}
	    			else {
	    				alert("omo something sup");
	    			}
	 
	    		})	
	    	};
	});  
	

	// wait for message that was typed  from server and show to only people currently on the channel
	socket.on("show message", data => {
		const singlemessagelist = [data];
		singlemessagelist.map(x => x.date = luxon.DateTime.fromISO(x.date).toLocaleString(luxon.DateTime.DATETIME_MED))

		// use the same template that handles a list of multiple chat dicts but this time passing only 1 item
		const template = Handlebars.compile(document.querySelector("#chatstemplate").innerHTML);		
		const message = template({"messages": singlemessagelist});
			
		console.log('got here boss')
		// add the message to the chat window 
		chatspace = document.querySelector(".chat-box")
		console.log(chatspace)
		chatspace.innerHTML += message; 
		chatspace.scrollTop = chatspace.scrollHeight;

	});	

	// wait for show newchannel event and add a new channel button
	socket.on("show newchannel", data => {
		// create a new button and set the relevant information

		const a = document.createElement("a");
		a.className = "public";
		a.name =  data.channel;
		a.innerText = data.channel;
		a.setAttribute("data-type", "public")

		// sets each new channel button  to get messages and display if clicked
		a.onclick = function(){
			 getChats(socket, this.name)
		}; 
		// add the channel button to the dom
		const li = document.createElement("li")
		li.appendChild(a)
		document.querySelector(".channel-links").appendChild(li);
	});

	// wait for show new private pair event and add a dm pair link to those that have access
	socket.on("show new private pair", data => {
		console.log(data, "new private channel emit")
		// if the user is a member of the channel create a private channel button for the user
		pair = data.pairname.split('-')
		if (pair.includes(username)){
			othername = (username === pair[0]) ? pair[1] : pair[0]

			const a = document.createElement("a");
			a.className = "private";
			a.name =  data.pairname;
			a.innerText = othername;
			a.setAttribute("data-type", "private")
			
			// sets each new channel to get messages and display if clicked
			a.onclick = function(){
						getChats(socket, this.name, ispublic=false)
			};
			// add the channel
			const li = document.createElement("li")
			li.appendChild(a)
			document.querySelector(".directmessage-links").appendChild(li);
		}		
	});
	socket.on("error", data => {
		// log any emit error
		console.log("error", data.message)
	});

});

function leavechannel(socket, channel){

	socket.emit("leave", {"channel": channel});

}

function joinchannel(socket, channel){

	socket.emit("join", {"channel":channel, "username":username});

}

//gets the messages from the server and adds it to the channel button
//takes the socket, the name of the channel, and an optional ispublic boolean arguement 
function getChats(socket, channelname, ispublic = true){ 

	// leave the channel the user was coming from
	leavechannel(socket, lastChannel)

	// send channel data to server to recieve the channel's chats
	const data = new FormData();
	data.append("channel", channelname);
	data.append("ispublic", ispublic)

	fetch("/getChats", {
		method: "POST",
		body: data
	})
	.then(response => response.json())
	.then(data => {
		if (data.success){ // render chats
	
			const messages = data.messages;
			joinchannel(socket, channelname);

			// display all the messages on the chat window
			showChats(channelname, messages)

			// set last channel to the channel being clicked
			console.log(channelname)
			lastChannel = channelname						 
		}
		//refactor
		else {console.log("something is wrong");}			
	})		
}

// displays chats on the window, takes a channel, and its messages as an arguement
function showChats(channel, listOFMessages){

	listOFMessages.map(x => x.date = luxon.DateTime.fromISO(x.date).toLocaleString(luxon.DateTime.DATETIME_MED))
	console.log(listOFMessages)
	// if the messages is not empty
	if (listOFMessages.length > 0){

		console.log(listOFMessages[0].date)
		// compile handle bar template that takes in a list of message dictionaries as input and renders it
		const template = Handlebars.compile(document.querySelector("#chatstemplate").innerHTML);
		const messages = template({"messages": listOFMessages});

		// add the message to the dom
		document.querySelector(".chat-box").innerHTML = messages;
	}
	else
	{ 
	 	// if a channel has no messages display nothing
		document.querySelector(".chat-box").innerHTML = "";
	}

	// if it contains a hyphen then its a user pair and we want the banner to be just the other guys name

	let header = channel
	if (channel.includes('-')){
		pair = channel.split('-')
		if (pair.includes(username)){
			othername = (username === pair[0]) ? pair[1] : pair[0]
			header = othername
		}
	}
	// change name to reflect current channel
	document.querySelector("#channelname-header").innerText = header;
}

// displays a select of all the users apart from the sender 
// it then emits the person to be dmed to the server
function renderModalAndEmitData(socket, userlist) {
	
	console.log(userlist, 'server list')
	const template = Handlebars.compile(document.querySelector("#put-users").innerHTML);		
	const users = template({"users": userlist});
	console.log(users)

	const select = document.querySelector("#users-select")
	console.log(select)
	select.innerHTML = users
  	$("#dm-users").modal("show"); 	 // show modal
	$('.selectpicker').selectpicker('refresh');

    document.querySelector("#modal-confirm"). onclick = () => {

    	// get channel name and ensure it isn't blank
    	let name = document.querySelector("#users-select").value;

      	$("#dm-users").modal("hide");
		socket.emit("add new private pair", {"name": name});		
		console.log("emmited cnpair")      
    };

}
