from gevent import monkey, sleep
monkey.patch_all()

from flask import Flask, render_template
from flask_socketio import SocketIO
from flaskthreads import AppContextThread
from operator import attrgetter
import time, random

from game.room import Room
from game.snake import Snake


app = Flask(__name__, template_folder="views")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


r = Room(width=20, height=20)
user_snake = Snake('orange', 'User', is_ai=False)


@app.route('/')
def index():
    return render_template('snake.html')

@app.route('/set/<float:speed>')
def set_speed(speed):
    r.speed = speed
    return str(speed)

@app.route('/load')
def load():
    r.reset()

    r.addSnake(Snake('red', 'Charlie'))
    r.addSnake(Snake('purple', 'Ellen')) 
    r.addSnake(Snake('blue', 'Bob'))
    r.addSnake(Snake('green', 'Chris'))
    r.addSnake(user_snake)
    return 'done'

@socketio.on('connect')
def handle_message():
    def send_room_state():
        old_board = []
        while not r.is_finished:
            time.sleep(0.1)
            # Don't need to send an update if the board's the same
            if not old_board == r.board:
                socketio.emit('board_changed', {'board': r.board}, broadcast=True)
                old_board = [x[:] for x in r.board] # Deep copies the list
    
    def send_scores():
        old_snakes = []
        while not r.is_finished:
            time.sleep(0.1)
            snakes = [{'name': s.name, 'colour': s.colour, 'score': s.score} for s in sorted(r.snakes, reverse=True)]
            # Don't need to send an update if snakes hasn't changed
            if not old_snakes == snakes:
                socketio.emit('scores_changed', 
                    {'snakes': snakes}, broadcast=True)
                old_snakes = snakes.copy() # Deep copies the list
    
    socketio.start_background_task(target=send_room_state)
    socketio.start_background_task(target=send_scores)

@socketio.on('move_snake')
def move_snake(direction):
    global user_snake
    user_snake.setDirection(direction)

if __name__ == '__main__':
    with app.test_request_context():
        game_loop = AppContextThread(target=r.loop)
        game_loop.start()

    r.reset()
    socketio.run(app, debug=True, host='0.0.0.0')