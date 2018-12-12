//app and http are for the express server
var app = require('express')();
var http = require('http').Server(app);

//socket.io is used to send and recieve messages from client
var io = require('socket.io')(http);

//session and casauthentication
var session = require('express-session');
var CASAuthentication = require('cas-authentication');

//Allos for SSH
var SSH = require('simple-ssh');
var hostip = "secret";
var rPiuser = "secret";
var rPipass = "secret";

//mongoose and models to insert data into db
var mongoose = require("mongoose");
var Lab = require("./models/lab.js");
var User = require("./models/user.js");


// Set up an Express session, which is required for CASAuthentication.
app.use( session({
    secret            : 'super secret key',
    resave            : true,
    saveUninitialized : true
}));


// Create a new instance of CASAuthentication.
var cas = new CASAuthentication({
    cas_url     : 'https://cas-auth.rpi.edu/cas',
    service_url : 'http://localhost:3000'
});

//return index
app.route('/')
	.get(function(req, res) {
        res.sendFile(__dirname + '/index.html');
	});

//return main.css
app.get('/css/main.css', function(req, res){
    res.sendFile(__dirname + '/css/main.css');
});

//return lablist.css
app.get('/css/labList.css', function(req, res){
    res.sendFile(__dirname + '/css/labList.css');
});

//return lablist.css
app.get('/cssAdmin/adminHome.css', function(req, res){
    res.sendFile(__dirname + '/cssAdmin/adminHome.css');
});

//return admin.js
app.get('/js/admin.js', function(req, res){
    res.sendFile(__dirname + '/js/admin.js');
});

//return student.js
app.get('/js/student.js', function(req, res){
    res.sendFile(__dirname + '/js/student.js');
});

//return logo
app.get('/img/logo-landing.svg', function(req, res){
    res.sendFile(__dirname + '/img/logo-landing.svg');
});


// Unauthenticated clients will be redirected to the CAS login and then back to
// this route once authenticated.
app.get( '/home', cas.bounce, function ( req, res ) {
   
    //get the username
    var curUser = req.session[cas.session_name].toLowerCase();
    
    //check if the user is an admin
    isAdmin(curUser)
    .then(function (found){
        //if it is the admin, return the admin page
        if (found){
            res.sendFile(__dirname + '/adminUser/adminHome.html');
        }else{
            //else return the student page
            res.sendFile(__dirname + '/studentUser/labList.html');
        }   
    })
    //log if an error exists
    .catch(function(error){
        console.log(error);
    });
    
});

// Unauthenticated clients will be redirected to the CAS login and then back to
// this route once authenticated.
app.get( '/addLab', cas.bounce, function ( req, res ) {
    //get current user
    var curUser = req.session[cas.session_name].toLowerCase();
    //if the user is an admin
    isAdmin(curUser)
    .then(function (found){
        //allow them to get the add file page, else they can't
        if (found){
            res.sendFile(__dirname + '/adminUser/addLab.html');
        }else{
            res.sendFile(__dirname + '/studentUser/labList.html');
        } 
    })
    .catch(function(error){
        console.log(error);
    });

});

// Unauthenticated clients will be redirected to the CAS login and then back to
// this route once authenticated.
app.get( '/visibleLabs', cas.bounce, function ( req, res ) {
    //get user name
    var curUser = req.session[cas.session_name].toLowerCase();
    //if admin
    isAdmin(curUser)
    .then(function (found){
        //allow them to choose what labs are visible
        if (found){
            res.sendFile(__dirname + '/adminUser/visibleLabs.html');
        }else{
            res.sendFile(__dirname + '/studentUser/labList.html');
        }
    })
    .catch(function(error){
        console.log(error);
    });
});

//return adminlab.html
app.get( '/adminLab', cas.bounce, function ( req, res ) {
    console.log(cas.session_name);
    res.sendFile(__dirname + '/adminUser/adminLab.html');
});

//return lab.html
app.get( '/lab', cas.bounce, function ( req, res ) {
    console.log(cas.session_name);
    res.sendFile(__dirname + '/studentUser/lab.html');
});

//return lab.css
app.get( '/cssAdmin/lab.css', cas.bounce, function ( req, res ) {
    console.log(cas.session_name);
    res.sendFile(__dirname + '/cssAdmin/lab.css');
});

// Unauthenticated clients will receive a 401 Unauthorized response instead of
// the JSON data.
app.get( '/api', cas.block, function ( req, res ) {
    res.json( { success: true } );
});

// An example of accessing the CAS user session variable. This could be used to
// retrieve your own local user records based on authenticated CAS username.
app.get( '/api/user', cas.block, function ( req, res ) {
    res.json( { cas_user: req.session[ cas.session_name ] } );
});

// Unauthenticated clients will be redirected to the CAS login and then to the
// provided "redirectTo" query parameter once authenticated.
app.get( '/authenticate', cas.bounce_redirect );

// This route will de-authenticate the client with the Express server and then
// redirect the client to the CAS logout page.
app.get( '/logout', cas.logout );

//connect to seockets
io.on('connection', function(socket){

	// log connect event
	console.log('a user connected');


	// log disconnect event
	socket.on('disconnect', function(){
		console.log('user disconnected');
    });

    //when asked to get the labs
    socket.on("getLabs", function(){

        //connect to database
        mongoose.connect('mongodb://localhost/RemoteAcademy', function(err){
			//if there's an error, tell the user
			if (err){
				console.log(err);
			} else {
				//query to get all the labs
				Lab.find({}).exec(function(err, labs){
					//if there's an error, throw it
					if (err){
						throw err
					}
					//send the array of labs to the front end
					io.of('/').emit("returnLabs", labs);
				});
			}
		});
    });

    //on get visible labs
    socket.on("getVisibleLabs", function(){

        //connect to database
        mongoose.connect('mongodb://localhost/RemoteAcademy', function(err){
			//if there's an error, tell the user
			if (err){
				console.log(err);
			} else {
				//query to get all the labs where visible is true
				Lab.find({visible: true}).exec(function(err, labs){
					//if there's an error, throw it
					if (err){
						throw err
					}
					//send the array of labs to the front end
					io.of('/').emit("returnLabs", labs);
				});
			}
		});

    });

    //get the users
    socket.on("getUsers", function(){

        //connect to the database
        mongoose.connect('mongodb://localhost/RemoteAcademy', function(err){
			//if there's an error, tell the user
			if (err){
				console.log(err);
			} else {
				//query to get all the users
				User.find({}).exec(function(err, users){
					//if there's an error, throw it
					if (err){
						throw err
					}
					//send the array of users to the front end
					io.of('/').emit("returnUsers", users);
				});
			}
		});

    });

    //get lab given an id
    socket.on("getLab", function(msg){

        //connect to the database
        mongoose.connect('mongodb://localhost/RemoteAcademy', function(err){
			//if there's an error, tell the user
			if (err){
				console.log(err);
			} else {
				//query to get lab with given id
				Lab.find({_id: msg}).exec(function(err, labInfo){
					//if there's an error, throw it
					if (err){
						throw err
					}
					//send the lab to the front end
					io.of('/').emit("returnLabInfo", labInfo);
				});
			}
		});

    });

    //store the lab with the info in msg
    socket.on("saveLab", function(msg){
        //create a Lab object from the model and msg
        var tempLab = new Lab ({
            title: msg[0],
            visible: msg[1],
            instructions: msg[2]
        });

        //connect to the database
        mongoose.connect('mongodb://localhost/RemoteAcademy', function(err){
			//if there's an error, tell the user
			if (err){
				console.log(err);
			} else {
                //save the lab
                tempLab.save(function(err) {
                    //throw an error if there is one
                    if (err){
                        console.log(err);
                    }
                    //let the user know it's inserted
                    io.of('/').emit("inserted");

                });
            }

		});       

    });

    //update visiblity of lab
    socket.on("updateLab", function(msg) {
        //find the lab with the given id and change the visibility
        Lab.findByIdAndUpdate(msg[0], {visible: msg[1]}, function(err) {
            //let user know if there's an error
            if (err){
                console.log(err);
            }
        });
    });

    //run the lab by SSHing into the rPi and running commands
    socket.on("runLab", function() {
        var ssh = new SSH({
            host: hostip,
            user: rPiuser,
            pass: rPipass
        });

        ssh
            /*
            .exec("cd Scripts", {
                out: function(stdout) {
                    console.log(stdout);
                },
            })
            */
            .exec("./Scripts/" + "a.out", {
                out: function(stdout) {
                    console.log(stdout);
                    io.of('/').emit("returnLabData", stdout);
                },
                err: function(stderr) {
                    console.log(stderr);
                }
            })
            
            .start();

        //ssh.end();

        console.log("Lab ran");
    });
    
});

//see if a user is an admin
function isAdmin(curUser){

    //it's a promise, so any function that calls it must wait for it to finish before moving on
    return new Promise(function(resolve, reject){

        //connect to database
        mongoose.connect('mongodb://localhost/RemoteAcademy', function(err){
            //if there's an error, tell the user
            if (err){
                //promise is broken if error
                reject(err)
            } else {
                //query to get all the users
                User.find({}).exec(function(err, users){
                    //if there's an error, throw it
                    if (err){
                        throw err
                    }

                    //go through users
                    for (var i = 0; i < users.length; i++){
                        //if the current user is found and the admin field is true
                        if ((curUser == users[i]["username"]) && (users[i]["admin"])) {
                            //the promise has been resolved and its true
                            resolve(true)
                        }
                    }

                    //else the promise is resolved and it's false.
                    resolve(false);
                    
                });
            }
        });

    });
}

//start the server on port 3000
http.listen(3000, function(){
    console.log("Server up on *:3000");
});
