# Remote.Academy
### Rensselaer Polytechnic Institute
### Sponsored by RPI Physics Department and Rensselaer Center for Open Source Software
### Hosted at http://remoteacademy.phys.rpi.edu/
### in collaboration with RPI DOTCIO and Office of Undergraduate Education
Originally created by: *Miles Konstantin, Osvaldo Rosado and Keaton Brandt* <br>
Version 2 by: *Karl Nasrallah, Cole Baxter, Zoran Lalvani, Harrison Lee, Richi Young*
Currently Maintained by *Andrew Leaf*
***

## Running RemoteAcademy

1. Install these tools on your computer (Windows, Mac, or Linux)

* NPM 3 or higher
* Node 4 or higher

2. Download or `git checkout` this repository

3. In a command line, navigate to the directory you downloaded and install the dependencies
  `npm install`

4. In a command line, start the server
  `node app`

You should now be able to access the RemoteAcademy front-end interface running on your
local computer. The Node command line will inform you of the port.

As of now, there isn't a MongoDB database running on a server. This means that, to get full
functionality, an instance of MongoDB must be running locally. To set it up, make sure you
have MongoDB installed on your computer. To run it, cd to the bin folder and run the command,
`mongod.exe`
The bin directory should be somewhere like C:\Program Files\MongoDB\Server\3.6\bin on windows.

Labs can be added through the Remote Laboratory but admin users must be added manually. I'd
recommend using Robomongo as a GUI interface with the database. Inserting a user should follow
the schema specified in models/user.js

***

## Tech Stack

### Server Technologies

* **REST API:** A special kind of application programming interface based on a stateless
structure. This means that every request from the client contains all of the data necessary
for the server to process it. The server does not store sessions or anything of that nature.
Basically, think of the server as the DMV - If you want it to do what you want, you better
have all of the information it needs, and don't expect it to remember you from last time.

* **WebSocket:** Most HTTP connections are "One and Done" - meaning that the client requests
some data, the server sends it back, and then the transaction is done. This adds a lot of
overhead to situations where the client and server want to be in frequent communication with
each-other. One solution is WebSockets, which stay open and allow both the client and
server to 'push' data to the other.

* **CAS / OAuth:** OAuth is a secure way for a user to log in to a website using a third
party service. This is how "Login with Facebook" buttons work. Schools aren't Facebook, but
it turns out many of them (including RPI) do have OAuth-compatible login systems. The
specific standard they usually use is called CAS (Common Authentication System).


### Server Tools

* **Node JS:** Server software built on top of Google's V8 Javascript interpreter. This means 
the frontend and backend code can be
written in the same language and even share code.

* **MongoDB:** A nonrelational database that stores data in documents instead of tables. This
allows for much more versatile data storage without sacrificing performance.

* **Express JS:** This handles HTTP serving.

### Frontend Tools

* **Angular.js 1.x:** Google's answer to web app development, this Javascript framework
enables us to write structured, reusable code. Angular has directives, which represent HTML
components, and services, which represent singleton libraries and controllers.

https://www.npmjs.com/package/cas-authentication
https://github.com/kylepixel/cas-authentication
https://stackoverflow.com/questions/44334172/how-to-implement-cas-authentication-for-rest-api-built-on-express

https://github.com/UniconLabs/node-with-cas