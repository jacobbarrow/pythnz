from gevent import monkey, sleep
monkey.patch_all()

from flask import Flask, render_template
from flask_socketio import SocketIO
from snake import Game, Snake
from flaskthreads import AppContextThread
from operator import attrgetter
import time, random

app = Flask(__name__, template_folder="views")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

g = Game(width=20, height=20)
user_snake = False

@app.route('/')
def index():
    return render_template('snake.html')

@app.route('/restart')
def restart():
    global g
    g = Game(width=20, height=20)
    g.addSnake(Snake(1, 7, 'red', 'Charlie', g))
    g.addSnake(Snake(5, 7, 'purple', 'Ellen', g)) 
    g.addSnake(Snake(10, 7, 'blue', 'Bob', g))

    with app.test_request_context():
        game_loop = AppContextThread(target=g.loop)
        game_loop.start()

    return 'done'

@socketio.on('connect')
def handle_message():
    global user_snake
    user_snake = Snake(10, 10, 'orange', 'User', g, is_ai=False)
    g.addSnake(user_snake)

    def send_room_state():
        old_board = []
        while not g.is_finished:
            time.sleep(0.1)
            # Don't need to send an update if the board's the same
            if not old_board == g.board:
                socketio.emit('board_changed', {'board': g.board}, broadcast=True)
                old_board = [x[:] for x in g.board] # Deep copies the list
    
    def send_scores():
        old_live_snakes = []
        while not g.is_finished:
            time.sleep(0.1)
            live_snakes = [{'name': s.name, 'colour': s.colour, 'score': s.score} for s in sorted(g.live_snakes, reverse=True)]
            dead_snakes = [{'name': s.name, 'colour': s.colour, 'score': s.score} for s in sorted(g.dead_snakes, reverse=True)]
            # Don't need to send an update if live snakes hasn't changed
            if not old_live_snakes == live_snakes:
                socketio.emit('scores_changed', 
                    {'live_snakes': live_snakes, 'dead_snakes': dead_snakes}, broadcast=True)
                old_live_snakes = live_snakes.copy() # Deep copies the list
    
    socketio.start_background_task(target=send_room_state)
    socketio.start_background_task(target=send_scores)

@socketio.on('move_snake')
def move_snake(direction):
    global user_snake

    user_snake.direction = direction

if __name__ == '__main__':
    socketio.run(app, debug=True)