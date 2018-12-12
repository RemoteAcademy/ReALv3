//require mongoose to create the model
var mongoose = require('mongoose');

//create a schema for each tweet based on what information will be kept
//when a tweet is streamed in
var labSchema = mongoose.Schema({
  title: String,
  visible: Boolean,
  instructions: { type: Array, "default": []}
});

//create a Tweet model from the scheme
var Lab = mongoose.model('Lab', labSchema);

//export the model
module.exports = Lab;
