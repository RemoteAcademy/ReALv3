//angular app
var studentApp = angular.module('studentApp', [])

//service to store information in session
studentApp.service('SessionStorageService', ['$window',function ($window) {
  var service = {
      store: store,
      retrieve: retrieve,
      clear: clear,
      clearAll: clearAll
  };

  return service;

  //function to store info
  function store(key, value) {
      $window.sessionStorage.setItem(key, angular.toJson(value, false));
  }

  //retireve info
  function retrieve(key) {
      return angular.fromJson($window.sessionStorage.getItem(key));
  }

  //remove info
  function clear(key) {
      $window.sessionStorage.removeItem(key);
  }

  //remove all info
  function clearAll() {
      $window.sessionStorage.clear();
  }
}]);

//controller for the student home page
studentApp.controller('home', function($scope, $window, $location, SessionStorageService) {

  //arrays for lab titles and titles
  $scope.ids = [];
  $scope.titles = [];

  //connect to server
  var socket = io.connect('http://localhost:3000');

  //ask server for labs
  socket.emit("getVisibleLabs");

  //when labs are returned,
  socket.on("returnLabs", (msg) => {
    //save each labs info to variable
    for (var i = 0; i < msg.length; i++){
      $scope.ids.push(msg[i]["_id"]);
      $scope.titles.push(msg[i]["title"]);

    }

    //update the scope
    $scope.$apply();

  });

  //function to go to lab page
  $scope.goToLab = function(msg){
    //save currentlab id into session storage
    SessionStorageService.store("currentLab", msg);
    //go to lab page
    $window.location.href = "./lab";
  }

});

//controller for the lab page
studentApp.controller('lab', function($scope, SessionStorageService) {

  //title and instructions in the lab
  $scope.title = "";
  $scope.instructions = [];

  //get the id of the lab from the session storage
  var id = SessionStorageService.retrieve("currentLab");

  //connect to te server
  var socket = io.connect('http://localhost:3000');
  //get the lab from the given id
  socket.emit("getLab", id);

  //when the lab is returned
  socket.on("returnLabInfo", (msg) => {
    //save the information
    $scope.title = msg[0]["title"];
    $scope.instructions = msg[0]["instructions"];

    //update the scope
    $scope.$apply();

  });

});