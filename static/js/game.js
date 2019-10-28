var socket = io();

let game_el = document.getElementById('game');
let scores_el = document.getElementById('scores');

socket.on('board_changed', function(data) {
    for(var y=0, row; row = game_el.rows[y]; y++) {
        for (var x = 0, col; col = row.cells[x]; x++) {
            col.className = data['board'][y][x]
        }  
    }
});

socket.on('scores_changed', function(data) {
    // Updates scores
    scores_el.innerHTML = "";
    for(var i=0, snake; snake=data['snakes'][i]; i++){
        score_el = document.createElement('li');
        score_el.innerHTML = snake.name + ': ' + snake.score;
        scores_el.appendChild(score_el);
        
    }

});

function changeDirection(direction) {
    socket.emit('move_snake', direction);
}

document.onkeydown = function(event) {
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
};