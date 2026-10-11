from flask import Flask, request, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

devices = {}

@app.route('/')
def index():
    return 'OK'

@app.route('/command', methods=['POST'])
def send_command():
    data = request.json
    device_id = data.get('device_id')
    command = data.get('command')
    if device_id in devices:
        socketio.emit('execute', {'command': command}, room=devices[device_id])
        return jsonify({'status': 'sent'})
    return jsonify({'status': 'device not found'}), 404

@socketio.on('register')
def handle_register(data):
    devices[data['device_id']] = request.sid
    print(f"Device registered: {data['device_id']}")

@socketio.on('disconnect')
def handle_disconnect():
    for did, sid in list(devices.items()):
        if sid == request.sid:
            del devices[did]
            print(f"Device disconnected: {did}")
            break

if __name__ == '__main__':
    socketio.run(app)
