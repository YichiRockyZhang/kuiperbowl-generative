var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
var gamesock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + window.location.pathname);

var player_name;
var player_id;

var game_state = 'idle';

var current_time;
var start_time;
var end_time;
var buzz_start_time;
var buzz_passed_time = 0;
var grace_time = 3;

var question;
var category;
var curr_question_content;
var score_dict;

// Set up client
function setup(){
  // set up user
  retrieve_userdata();
  if(player_id == undefined){
    new_user();
  }
  ping();
  $('#name').val(player_name);

  // set up current time
  current_time = buzz_start_time;
}

// Update game locally
function update(){
  if(question == undefined){
    return;
  }

  var time_passed = current_time - start_time;
  var duration = end_time - start_time;

  // Update if game is going
  if(time_passed < duration){

    if(game_state == 'playing'){
      curr_question_content = question.substring(0, Math.round(question.length * (time_passed / (duration-grace_time) )))
      current_time += 0.1;

      var content_progress = $('#content-progress');
      content_progress.attr('class', 'progress-bar bg-success');
      content_progress.css('width', 5+Math.round(100 * (time_passed / duration ))+'%');
    }
    else if(game_state == 'contest'){
      time_passed = buzz_start_time - start_time;
      curr_question_content = question.substring(0, Math.round(question.length * (time_passed / (duration-grace_time) )))

      //var time_passed_buzz = current_time - buzz_start_time;
      //var duration_buzz = grace_time;
      var content_progress = $('#content-progress');
      content_progress.attr('class', 'progress-bar bg-danger');
      content_progress.css('width', 100+'%');
    }

    var question_body = $('#question-space');
    question_body.html(curr_question_content);
  }
  else if(time_passed >= duration){
    game_state = 'idle';

    var content_progress = $('#content-progress');
    content_progress.css('width', '0%');
  }
}

// Handle server response
gamesock.onmessage = function(message){
  var data = JSON.parse(message.data);
  console.log(data);

  if(data.response_type == "update"){
    // sync client with server
    game_state = data.game_state;
    current_time = data.current_time;
    start_time = data.start_time;
    end_time = data.end_time;
    buzz_start_time = data.buzz_start_time;
    question = data.current_question_content;
    category = data.category;
    scores = data.scores;

    // update ui
    var scoreboard = $('#scoreboard-body');
    scoreboard.html("")
    for(i=0; i<scores.length; i++){
      scoreboard.append("<tr><td>"+scores[i][0]+"</td><td>"+scores[i][1]+"</td></tr>")
    }

    $('#category-header').html("Category: " + category);
  }
  else if(data.response_type == "new_user"){
    setCookie('player_id', data.player_id);
    setCookie('player_name', data.player_name);
    player_id = data.player_id;
    player_name = data.player_name;

    // Update name
    $('#name').val(player_name);
    ping()
  }
}

// Ping server for state
function ping(){
  var message = {
    player_id: player_id,
    current_time: Date.now(),
    request_type:"ping",
    content:""
  }
  gamesock.send(JSON.stringify(message));
}

// Request new user
function new_user(){
  var message = {
    player_id: player_id,
    current_time: Date.now(),
    request_type:"new_user",
    content:""
  }
  gamesock.send(JSON.stringify(message));
}

// Request change name
function set_name(){
  setCookie('player_name', $('#name').val());
  var message = {
    player_id: player_id,
    current_time: Date.now(),
    request_type:"set_name",
    content:$('#name').val()
  }
  gamesock.send(JSON.stringify(message));
}

// Buzz
function buzz(){
  if(game_state == 'playing'){
    game_state = 'contest';
    var message = {
      player_id: player_id,
      current_time: Date.now(),
      request_type:"buzz_init",
      content:""
    }
    gamesock.send(JSON.stringify(message));
  }
}

// Answer
function answer(){
  if(game_state == 'contest'){
    game_state = 'playing';
    var message = {
      player_id: player_id,
      current_time: Date.now(),
      request_type:"buzz_answer",
      content:""
    }
    gamesock.send(JSON.stringify(message));
  }
}

// Request next question
function next(){
  if(game_state == 'idle'){
    var question_body = $('#question-space');
    question_body.html("");

    var message = {
      player_id: player_id,
      current_time: Date.now(),
      request_type:"next",
      content:""
    }
    gamesock.send(JSON.stringify(message));
  }
}
