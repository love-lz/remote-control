from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = "lz1102mm"

commands = {}
results = {}

def check_auth():
    key = request.headers.get("X-API-Key", "")
    return key == API_KEY

@app.route('/')
def index():
    return 'OK'

@app.route('/send', methods=['POST'])
def send_command():
    if not check_auth():
        return jsonify({'status': 'unauthorized'}), 401
    data = request.json
    device_id = data.get('device_id', 'default')
    command = data.get('command', '')
    commands[device_id] = command
    return jsonify({'status': 'queued'})

@app.route('/poll', methods=['GET'])
def poll_command():
    device_id = request.args.get('device_id', 'default')
    if device_id in commands:
        cmd = commands.pop(device_id)
        return jsonify({'command': cmd})
    return jsonify({'command': None})

@app.route('/result', methods=['POST'])
def post_result():
    data = request.json
    device_id = data.get('device_id', 'default')
    result = data.get('result', '')
    results[device_id] = result
    return jsonify({'status': 'ok'})

@app.route('/getresult', methods=['GET'])
def get_result():
    if not check_auth():
        return jsonify({'status': 'unauthorized'}), 401
    device_id = request.args.get('device_id', 'default')
    if device_id in results:
        return jsonify({'result': results.pop(device_id)})
    return jsonify({'result': None})

if __name__ == '__main__':
    app.run()
