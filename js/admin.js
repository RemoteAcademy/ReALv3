var app = angular.module('AdminApp', ['ngMaterial'])

//service to store information in the browswer
//Used store the lab id chosen by the user so when the lab page loads, it knows what
//lab to import the information from
app.service('SessionStorageService', ['$window',function ($window) {
  //what the service allows other controllers to interact with
  var service = {
      store: store,
      retrieve: retrieve,
      clear: clear,
      clearAll: clearAll
  };

  return service;

  //store info in session
  function store(key, value) {
      $window.sessionStorage.setItem(key, angular.toJson(value, false));
  }

  //retrieve stored info
  function retrieve(key) {
      return angular.fromJson($window.sessionStorage.getItem(key));
  }

  //remove stored info
  function clear(key) {
      $window.sessionStorage.removeItem(key);
  }

  //remove all info
  function clearAll() {
      $window.sessionStorage.clear();
  }


}]);

//controller for the hidden labs page
app.controller('hiddenLabs', function($scope) {

  //arrays to hold ids, titles, initial visible values, and current visible values of all labs
  $scope.ids = [];
  $scope.titles = [];
  $scope.initialVisible = [];
  $scope.visible = [];

  //create a connection to server
  var socket = io.connect('http://localhost:3000');

	//on load, emit the message to get all the labs
  socket.emit("getLabs");
  
  //when all the labs are returned
  socket.on("returnLabs", (msg) => {
    //go through all the labs
    for (var i = 0; i < msg.length; i++){
      //save each labs id, title, and visible state
      $scope.ids.push(msg[i]["_id"]);
      $scope.titles.push(msg[i]["title"]);
      $scope.initialVisible.push(msg[i]["visible"]);
      $scope.visible.push(msg[i]["visible"]);
    }

    //update the scope
    $scope.$apply();

  });

  //when the update button is clicked
  $scope.update = function(){
    
    //go through all the labs
    for (var i = 0; i < $scope.visible.length; i++){
      //if the visibility has changed,
      if ($scope.initialVisible[i] != $scope.visible[i]){
        //store the id and new visible variable of the lab
        var msg = [$scope.ids[i], $scope.visible[i]];
        //send info to server to update the database
        socket.emit("updateLab", msg);
      }
    }

    //let the user know it was updated
    alert("Updated");

  }
});

//controller for the create lab page
app.controller('createLab', function($scope, $window, $location) {
  
  //variabls to hold information on the lab
  $scope.title = "";
  $scope.steps = [""];

  //connect to backend
  var socket = io.connect('http://localhost:3000');

  //add step adds an empty string to step array
  $scope.addStep = function(){
    $scope.steps.push("");
  }

  //remove the last index in the steps array
  $scope.remStep = function(){
    $scope.steps.pop();
  }

  //when the lab is submitted
  $scope.submit = function(){
    
    //save the lab information in a variable
    var msg = [$scope.title, false, $scope.steps];

		//emit the message and the info
    socket.emit("saveLab", msg);
  }

  //when the server says the information has been inserted
  socket.on('inserted', () => {
    //go to the visible labs page
    $window.location.href = "./visibleLabs";
  });

});

//controller for the home page
app.controller('home', function($scope, $window, $location, SessionStorageService) {

  //variabls to hold the information on the labs
  $scope.ids = [];
  $scope.titles = [];

  //arrays to hold mentors and students
  $scope.mentors = [];
  $scope.students = [];

  //connect to the server
  var socket = io.connect('http://localhost:3000');
  
  //emit to get the visible labs and users
  socket.emit("getVisibleLabs");
  socket.emit("getUsers");
  
  //when the labs are returned
  socket.on("returnLabs", (msg) => {
    //add the lab information to the scope 
    for (var i = 0; i < msg.length; i++){
      $scope.ids.push(msg[i]["_id"]);
      $scope.titles.push(msg[i]["title"]);
    }

    //update the scope
    $scope.$apply();
  });

  //when the users are returned
  socket.on("returnUsers", (msg) => {

    //go through all the users
    for (var i = 0; i < msg.length; i++) {
      //add them to the mentor or student array based on what they are
      if (msg[i]["mentor"]){
        $scope.mentors.push(msg[i]["username"])
      }
      else if (msg[i]["student"]){
        $scope.students.push(msg[i]["username"])
      }
    }

    //update the scope
    $scope.$apply();


  });

  //when a lab is clicked
  $scope.goToLab = function(msg){
    //save the clicked lab id to the session storage
    SessionStorageService.store("currentLab", msg);
    //go to the lab page
    $window.location.href = "./adminLab";
  }

});

//controller for the lab page
app.controller('lab', function($scope, SessionStorageService) {

  //variables to hold information on the labs
  $scope.title = "";
  $scope.instructions = [];

  //get the id of the lab from session storage
  var id = SessionStorageService.retrieve("currentLab");

  //create a connection to the backend
  var socket = io.connect('http://localhost:3000');

  //send the lab id to the backend to get the lab info
  socket.emit("getLab", id);

  //when the lab info is returned
  socket.on("returnLabInfo", (msg) => {
    
    //save the information to the variables
    $scope.title = msg[0]["title"];
    $scope.instructions = msg[0]["instructions"];

    //update the scope
    $scope.$apply();

  });

});