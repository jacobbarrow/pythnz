import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, redirect, url_for, make_response
from flask_socketio import SocketIO, join_room, leave_room, rooms
from flaskthreads import AppContextThread
from operator import attrgetter
import time, random

from game.room import Room
from game.snake import Snake
from game import user

thread_lock = None


app = Flask(__name__, template_folder="views")
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

game_rooms = {
    'easy': Room(speed=0.25, name='Easy Peasy'),
    'medium': Room(speed=0.2, name='Kinda Medium'),
    'difficult': Room(speed=0.15, name='Rather Difficult'),
    'nelly': Room(speed=0.08, name='Woah Nelly')
}

user_snakes = {}
user_ids = {}

def isLoggedIn():
    if 'uid' in request.cookies:
        return True if user.findById(request.cookies['uid']) else False
    return False

@app.route('/')
def show_scores():
    return redirect(url_for('show_rooms'))


@app.route('/rooms')
def show_rooms():
    return render_template('rooms.html', rooms=game_rooms, leaderboard=user.findAll(), is_logged_in=isLoggedIn())

@app.route('/rooms/<id>')
def show_room(id):
    return render_template('snake.html', id=id, room=game_rooms[id], is_logged_in=isLoggedIn())


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    error = None
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        this_user = user.findByName(username)
        if this_user is None:
            error = 'User does not exist'
        elif password != this_user[2]:
            error = 'Wrong password'
        else:
            res = make_response("Setting a cookie")
            res.set_cookie('uid', this_user[0], max_age=60*60*24*365*2)
            res.headers['location'] = url_for('show_rooms')
            return res, 302

    return render_template('auth_form.html', action="in", error=error, is_logged_in=False)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        this_user = user.findByName(username)
        if this_user is not None:
            error = 'Nickname taken'
        else:
            user.create(username, password)
            this_user = user.findByName(username)
            res = make_response("Setting a cookie")
            res.set_cookie('uid', this_user[0], max_age=60*60*24*365*2)
            res.headers['location'] = url_for('show_rooms')
            return res, 302

    return render_template('auth_form.html', action="up", error=error, is_logged_in=False)

@app.route('/signout')
def signout():
    res = make_response("Removing a cookie")
    res.set_cookie('uid', '', expires=0)
    res.headers['location'] = url_for('show_rooms')
    return res, 302

@socketio.on('connect')
def connected():
    socketio.emit('connected')

@socketio.on('disconnect')
def disconnect():
    for room in rooms():
         if room in game_rooms:
            try:
                game_rooms[room].removeSnake(request.sid)
                del user_snakes[request.sid]
            except KeyError: 
                pass

@socketio.on('join')
def on_join(data):
    global thread_lock

    this_user = user.findById(data['user_id'])
    room_id = data['room_id']
    room = game_rooms[room_id]

    join_room(room_id)
    if this_user is not None and len(room.snakes) < 5:
        user_ids[request.sid] = data['user_id']        
        
        user_snakes[request.sid] = Snake(name=this_user[1], is_ai=False, sid=request.sid, uid=data['user_id'])
        
        room.removeSnake(request.sid)
        room.addSnake(user_snakes[request.sid])
        socketio.emit('status_update', user_snakes[request.sid].colour)
    else:
        socketio.emit('status_update', 'spectating')

    def send_room_state():
        while True:
            time.sleep(0.1)
            for room_id, room in game_rooms.items():
                old_board = []
                # Don't need to send an update if the board's the same
                if not old_board == room.board:
                    socketio.emit('board_changed', {'board': room.board}, room=room_id)
                    old_board = [x[:] for x in room.board] # Deep copies the list

    def send_scores():
        while True:
            time.sleep(0.1)
            for room_id, room in game_rooms.items():
                old_snakes = []
                snakes = [{'name': s.name, 'colour': s.colour, 'score': s.score} for s in sorted(room.snakes, reverse=True)]
                # Don't need to send an update if snakes hasn't changed
                if not old_snakes == snakes:
                    socketio.emit('scores_changed', 
                        {'snakes': snakes}, room=room_id)
                    old_snakes = snakes.copy() # Deep copies the list

    if thread_lock == None:
        thread_lock = True
    socketio.start_background_task(target=send_room_state)
    socketio.start_background_task(target=send_scores)

@socketio.on('change_direction')
def move_snake(data):
    global user_snakes
    user_snakes[request.sid].setDirection(data['direction'])


with app.test_request_context():
        for room in game_rooms.values():
            game_loop = AppContextThread(target=room.loop)

            game_loop.start()
            room.reset(num_ais=random.randint(3,5))

if __name__ == '__main__':
    socketio.run(app, debug=False, host='0.0.0.0')