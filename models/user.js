<<<<<<< HEAD
//require mongoose to create the model
var mongoose = require('mongoose');

//create a schema for each tweet based on what information will be kept
//when a tweet is streamed in
var userSchema = mongoose.Schema({
  username: String,
  admin: Boolean,
  mentor: Boolean,
  student: Boolean
});

//create a Tweet model from the scheme
var user = mongoose.model('user', userSchema);

//export the model
module.exports = user;
=======
//require mongoose to create the model
var mongoose = require('mongoose');

//create a schema for each tweet based on what information will be kept
//when a tweet is streamed in
var userSchema = mongoose.Schema({
  username: String,
  admin: Boolean,
  mentor: Boolean,
  student: Boolean
});

//create a Tweet model from the scheme
var user = mongoose.model('user', userSchema);

//export the model
module.exports = user;
>>>>>>> 8692799d4435c45805bff9424c1b948ac3a76aea
