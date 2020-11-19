// global username and the last channel accessed 
const username = localStorage.getItem("username"); 
let lastChannel = localStorage.getItem("channel") || "general";

// register a helper fumction to handlebar that helps to differientiate btw the user and others
Handlebars.registerHelper("isCurrentUser", function(name)
{
		return name === username;
});


document.addEventListener("DOMContentLoaded", () => {
	
	
	var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
	console.log(socket)
	// when logged out, clear local storage 
	document.querySelector("#forget").onclick = () => {
		localStorage.clear();
		return true;
	};

	// if a channel doesnt exist set the channel to general
	if (!document.getElementsByName(lastChannel)[0])
	{
		lastChannel = "general";
	}


	// // display the chats of the last channel the user was on, on load
	// getChats(socket, lastChannel);
			
	// show all the private channels a user belongs to on load
	// the same thing is done for public channels but using jinja to display
	// couldnt use jinja for the private channels because of the added complexity
	//showPrivateChannelsOnLoad(socket)

	//	configure channel buttons to show chats on click when page is loaded
	document.querySelectorAll(".public").forEach(a => {
		a.onclick = function() {
			// getChats(socket, this.name)
			}; 

	});

	// when connected configure
	socket.on("connect", () => {

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
	    

// 		// gets all the users of the app from the server, and uses them to display a create private channel modal
// 		// the modal is the interface allows you to create and add users to a private channel
// 		document.querySelector("#create-privatebtn").onclick = () => {
// 			const request = new XMLHttpRequest();
// 			request.open("POST", "/getUsers");

// 			// on load pass all the users to be displayed in the modal
// 			request.onload = () => {
				
// 				const data = JSON.parse(request.responseText);
// 				users = data.users;

// 				// creates the modal and then retrievs and emits the relevant data to the server for private channel creation 
// 				renderModalAndEmitData(socket, users); 
				
// 			}

// 			request.send()
	    	
//       	};

// 	});
	
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
					// getChats(socket, this.name)
		}; 
		// add the channel button to the dom
		const li = document.createElement("li")
		li.appendChild(a)
		document.querySelector(".channelbuttons").appendChild(li);
	});

// 	// wait for show new privatechannel event and add a new private channel button to those that have access
// 	socket.on("show new privatechannel", data => {
// 		console.log(data, "new private channel emit")
// 		// if the user is a member of the channel create a private channel button for the user
// 		if (data.members.includes(username)){

// 			const buttn = document.createElement("button");
// 			buttn.className = "buttn privateButtn";
// 			buttn.name =  data.channel;
// 			buttn.innerHTML = data.channel.replace(/-\d+$/, "");
// 			buttn.setAttribute("data-type", "private")
			
// 			// sets each new channel to get messages and display if clicked
// 			buttn.onclick = function(){
// 						getChats(socket, this.name, false)
// 			};
// 			// add the channel
// 			document.querySelector(".privatechannelbuttons").append(buttn);	
// 		}		
// 	});

// 	// when the user types and sends a single chat
// 	document.querySelector("#sentmssg").onsubmit = () =>{

// 		const message = document.querySelector("#comment").value;
// 		// reset the textbox
// 		document.querySelector("#comment").value = "";
		
// 		if (message.length >= 1){  // send only if message is not blank
			
// 			// emit the single chat's details to the server
// 			console.log("message", message);
// 			const time = moment().format("YYYY-MM-DD hh:mm:ss")
// 			const user = username;
// 			bttn = document.getElementsByName(localStorage.getItem('channel'))[0];
// 			socket.emit("got a message", {"message":message, "time":time, 
// 				"user":user, "channel":bttn.name, "type":bttn.dataset.type});
// 		}
// 		return false;
// 	};

// 	// wait for message that was typed  from server and show to only people currently on the channel
// 	socket.on("show message", data => {
// 		const singlemessagelist = [data];
// 		// use the same template that handles a list of multiple chat dicts but this time passing only 1 item
// 		const template = Handlebars.compile(document.querySelector("#chatstemplate").innerHTML);		
// 		const message = template({"messages": singlemessagelist});
		
// 		// add the message to the chat window 
// 		chatspace = document.querySelector(".chatspace")
// 		chatspace.innerHTML += message; 
// 		chatspace.scrollTop = chatspace.scrollHeight;

// 	})	

});

// // helper function that checks the occurence of a channel button and returns it,
// // public channel buttons can only have 1 occurence but private can as many occurences
// // so a user may have a multiple private channels with the same name.
// function channelOccurence(channel, bttnClassname){
// 	console.log(channel);
// 	let occurence = 0;
// 	document.querySelectorAll(`.${bttnClassname}`).forEach(btn =>{
// 		console.log(btn.innerText);
// 		if (btn.innerText === channel) 
// 		{	
// 			occurence += 1;
// 		}
// 	});
// 	return occurence;
// }


// function leavechannel(socket, channel){

// 	socket.emit("leave", {"channel": channel});

// }

// function joinchannel(socket, channel){

// 	socket.emit("join", {"channel":channel, "username":username});

// }

// // gets the messages from the server and adds it to the channel button
// // takes the socket, the name of the channel, and an optional ispublic boolean arguement 
// function getChats(socket, channelname, ispublic = true){ 

// 	// leave the channel the user was coming from
// 	leavechannel(socket, localStorage.getItem("channel"))

// 	const request = new XMLHttpRequest();
// 	request.open("POST", "/getChats");

// 	// when messages have been recieved join the channel then display the chats
// 	request.onload = () => {
// 		// parse response
// 		const data = JSON.parse(request.responseText)
// 		if (data.success) // render chats
// 		{
// 			const messages = data.messages;
// 			joinchannel(socket, channelname);

// 			// display all the messages on the chat window
// 			showChats(channelname, messages)

// 			// set last channel to the channel being clicked
// 			console.log(channelname)
// 			localStorage.setItem("channel", channelname);						 
// 		}
// 		else {console.log("something is wrong");}
// 	}
	
// 	// send channel data to server to recieve the channel's chats
// 	const data = new FormData();
// 	data.append("channel", channelname);
// 	data.append("ispublic", ispublic)
// 	request.send(data);	
	
// }

// // displays chats on the window, takes a channel, and its messages as an arguement
// function showChats(channel, listOFMessages){

// 	// if the messages is not empty
// 	if (listOFMessages.length > 0){

// 		// compile handle bar template that takes in a list of message dictionaries as input and renders it
// 		const template = Handlebars.compile(document.querySelector("#chatstemplate").innerHTML);
// 		const messages = template({"messages": listOFMessages});

// 		// add the message to the dom
// 		document.querySelector(".chatspace").innerHTML = messages;
// 	}
// 	else
// 	 { 
// 	 	// if a channel has no messages display nothing
// 		document.querySelector(".chatspace").innerHTML = "";
// 	}

// 	// change name to reflect current channel
// 	document.querySelector(".channelbanner h5").innerHTML = channel.replace(/-\d+$/, "");
// }

// // displays a create private channel modal and retrieves a list of members and the channel name from the user
// // it then emits the data to the server
// function renderModalAndEmitData(socket, userlist) {
	
// 	$("#modalLoginForm").modal("show"); // show modal

// 	// compile template of users
//     const template = Handlebars.compile(document.querySelector("#addUserCheckboxes").innerHTML);
    
//     // create html templates of users that is then added as checkboxes to the modal
//     const usersChecks = template({"users": userlist});
//     document.querySelector(".privatemembers").innerHTML = usersChecks
  
//     document.querySelector("#modal-confirm"). onclick = () => {

//     	// get channel name and ensure it isn't blank
//     	let privateChannelName = document.querySelector("#privateChannelName").value

//     	if (privateChannelName === "")
//     	{
//     		return false;
//     	}

//     	// store the channel name as [channelname]-[itsposition] eg food-2 is the 3rd private channel with a name of food
//     	// ensures that each private name is uniquely stored on the server even though it is repeated  
//     	privateChannelName = privateChannelName +  "-" + String(channelOccurence(privateChannelName, "privateButtn")); 
//     	console.log(privateChannelName)
//     	// get all user boxes that was checked 
//     	const members = document.querySelectorAll("input[name='members']:checked"); 

//     	// store the names of the users that will be members of the private channel
//     	const memberArray = []
//      	members.forEach((chkbox) => {
//         	memberArray.push(chkbox.value);
//       	})
//       	memberArray.push(username);
//       	$("#modalLoginForm").modal("hide");
      
//       	privatechanneldata = {"members": memberArray, "name":privateChannelName};
//       	console.log(privatechanneldata, "should be an object");
// 		socket.emit("add new privatechannel", privatechanneldata);
//     };

// }

// //gets all the private channels from the server that a user is on when the page is loaded
// function showPrivateChannelsOnLoad(socket){

// 	const request = new XMLHttpRequest();
// 	request.open("POST", "/getPrivateChannels");

// 	request.onload = () => {
// 		// parse response
// 		const data = JSON.parse(request.responseText)
// 		const channels = data.channels;

// 		//  display all the retrieved private channels from the dom
// 		for ( const channel of channels) {

// 			const buttn = document.createElement("button");
// 			buttn.className = "buttn privateButtn";
// 			buttn.name =  channel;
// 			buttn.innerText = channel.replace(/-\d+$/, "");
// 			buttn.setAttribute("data-type", "private")

// 			// sets each new channel to get messages if clicked
// 			buttn.onclick = function(){
// 						getChats(socket, this.name, false)
// 			};
// 			document.querySelector(".privatechannelbuttons").append(buttn);
// 		}					 
		
// 	}
	
// 	const data = new FormData();
// 	data.append("user", username);
// 	request.send(data);	


});