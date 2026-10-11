from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__)
@app.route('/')
def index():
    return 'OK'
app.config['SECRET_KEY'] = 'mm091102'
socketio = SocketIO(app, cors_allowed_origins="*")

connected_devices = {}

@socketio.on('connect')
def handle_connect():
    device_id = request.args.get('device_id', 'unknown')
    connected_devices[device_id] = request.sid
    print(f'Device connected: {device_id}')

@socketio.on('disconnect')
def handle_disconnect():
    for device_id, sid in list(connected_devices.items()):
        if sid == request.sid:
            del connected_devices[device_id]
            print(f'Device disconnected: {device_id}')

@socketio.on('screen_data')
def handle_screen(data):
    emit('screen_update', data, broadcast=True)

@socketio.on('command')
def handle_command(data):
    target = data.get('target')
    if target in connected_devices:
        emit('execute', data, room=connected_devices[target])

@app.route('/status')
def status():
    return jsonify({'devices': list(connected_devices.keys())})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    socketio.run(app, host='0.0.0.0', port=port)
