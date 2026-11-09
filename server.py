import os
from flask import Flask, request, jsonify
import requests as req

app = Flask(__name__)

API_KEY = "lz1102mm"
AI_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-0ec9e7b66f6547d5b2561b558ab1f17f")
AI_API_URL = "https://api.deepseek.com/chat/completions"

commands = {}
results = {}
battery_info = {}

def check_auth():
    key = request.headers.get("X-API-Key", "")
    return key == API_KEY

@app.route('/')
def index():
    return 'OK'

@app.route('/ping', methods=['GET'])
def ping():
    return 'pong'

@app.route('/battery', methods=['POST'])
def receive_battery():
    global battery_info
    data = request.json
    if data:
        battery_info = data
        return jsonify({'status': 'battery_updated'}), 200
    return jsonify({'status': 'no_data'}), 400

@app.route('/get_battery', methods=['GET'])
def get_battery():
    if not check_auth():
        return jsonify({'status': 'unauthorized'}), 401
    return jsonify({'battery': battery_info})

@app.route('/ai', methods=['POST'])
def ai_command():
    if not check_auth():
        return jsonify({'status': 'unauthorized'}), 401
    data = request.json
    user_msg = data.get('message', '')
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a phone control assistant. When the user wants to check phone info, respond with exactly one of these commands: battery, storage, contacts, sms, calllog, all. Only respond with the command word, nothing else."},
            {"role": "user", "content": user_msg}
        ],
        "max_tokens": 50
    }
    try:
        r = req.post(AI_API_URL, json=payload, headers=headers, timeout=30)
        ai_response = r.json()
        cmd = ai_response["choices"][0]["message"]["content"].strip().lower()
        commands["mengmeng_phone"] = cmd
        return jsonify({'status': 'command_sent', 'command': cmd})
    except Exception as e:
        return jsonify({'status': 'error', 'detail': str(e)}), 500

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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
