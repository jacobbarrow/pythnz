var socket = io();

// getCookie func taken verbatim from https://www.w3schools.com/js/js_cookies.asp
function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
      var c = ca[i];
      while (c.charAt(0) == ' ') {
        c = c.substring(1);
      }
      if (c.indexOf(name) == 0) {
        return c.substring(name.length, c.length);
      }
    }
    return "";
}

user_id = getCookie('uid')
console.log(user_id)

let game_el = document.getElementById('game');
let scores_el = document.getElementById('scores');

socket.on('connected', function() {
    socket.emit('join', 
        {'room_id': room_id, 'user_id': user_id}
        )
})

socket.on('board_changed', function(data) {
    for(var y=0, row; row = game_el.rows[y]; y++) {
        for (var x = 0, col; col = row.cells[x]; x++) {
            col.className = data['board'][y][x]
        }  
    }
});

socket.on('status_update', function(data) {
    document.getElementById('status').innerHTML = data;
});

socket.on('scores_changed', function(data) {
    // Updates scores
    scores_el.innerHTML = "";
    for(var i=0, snake; snake=data['snakes'][i]; i++){
        score_el = document.createElement('li');
        score_el.innerHTML = snake.name + ': ' + snake.score;
        score_el.className = snake.colour
        scores_el.appendChild(score_el);
    }
});

function changeDirection(direction) {
    socket.emit('change_direction', {'direction': direction, 'user_id': user_id});
}

document.onkeydown = function(event) {
    if (user_id != "") {
        charCode = event.keyCode;
        // North
        if (charCode == 38 || charCode == 87){
            event.preventDefault();
            changeDirection(1)
        }
        // East
        else if (charCode == 39 || charCode == 68){
            event.preventDefault();
            changeDirection(2)
        }
        // South
        else if (charCode == 40 || charCode == 83){
            event.preventDefault();
            changeDirection(3)
        }
        // West
        else if (charCode == 37 || charCode == 65){
            event.preventDefault();
            changeDirection(4)
        }
    }

};