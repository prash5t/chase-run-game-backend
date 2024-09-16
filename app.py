from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

players = {}
chaser = None


@app.route('/')
def index():
    return 'Game Server is running'


@socketio.on('connect')
def handle_connect():
    global chaser
    player_id = request.sid
    print(f'Player connected: {player_id}')

    if not players:
        chaser = player_id
        players[player_id] = {'x': 100, 'y': 100, 'is_chaser': True}
    else:
        players[player_id] = {'x': random.randint(
            50, 350), 'y': random.randint(50, 350), 'is_chaser': False}

    emit('updatePlayers', {'players': players,
         'chaser': chaser}, broadcast=True)


@socketio.on('disconnect')
def handle_disconnect():
    global chaser
    player_id = request.sid
    print(f'Player disconnected: {player_id}')
    if player_id in players:
        del players[player_id]
        if player_id == chaser and players:
            chaser = random.choice(list(players.keys()))
            players[chaser]['is_chaser'] = True
        elif not players:
            chaser = None
        emit('updatePlayers', {'players': players,
             'chaser': chaser}, broadcast=True)


@socketio.on('move')
def handle_move(data):
    global chaser
    player_id = request.sid
    x = data['x']
    y = data['y']
    players[player_id]['x'] = x
    players[player_id]['y'] = y

    # Check for collisions
    for other_id, other_player in players.items():
        if other_id != player_id:
            distance = ((x - other_player['x']) **
                        2 + (y - other_player['y'])**2)**0.5
            if distance < 20:  # Collision threshold
                if players[player_id]['is_chaser']:
                    players[player_id]['is_chaser'] = False
                    players[other_id]['is_chaser'] = True
                    chaser = other_id
                    break

    emit('updatePlayers', {'players': players,
         'chaser': chaser}, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, host='10.10.10.149', port=5001)
