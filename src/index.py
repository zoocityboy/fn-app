import os
from flask import Flask, jsonify, request, json
from werkzeug.exceptions import HTTPException
from gevent.pywsgi import WSGIServer

import json
from src.model.exception import InvalidApiKeyException
from src.model.webshare import Webshare
from src.model.scstream import hashPassword

def get_apikey():
    safeApiKey = os.environ.get('FLASK_API_KEY')
    if not safeApiKey:
        safeApiKey = "not-so-secret-key"
    return safeApiKey

def is_valid_apikey(data):
    try:
        headers = request.headers
        key = headers.get("X-Api-Key")
        app.logger.info("header api key 'key'", key)
        return key == get_apikey()
    except ValueError:
        return False

app = Flask(__name__)

@app.errorhandler(InvalidApiKeyException)
def invalid_api_key(e):
    return jsonify(e.to_dict()), e.status_code

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response

@app.route('/auth', methods=['POST'])
def auth():
    if not is_valid_apikey(request):
        raise InvalidApiKeyException("Invalid API key received.")
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    try:
        username = data.get("username")
        password = data.get("password")
        deviceId = data.get("deviceId")
        if not deviceId:
            raise Exception("DeviceId is required")

        if not username:
            raise Exception("Username is required")
        if not password:
            raise Exception("Password is required")

        client = Webshare(deviceId)
        token = client.login(username, password)
        if not token:
            raise Exception("Token not found")

        return jsonify({
            "token": token
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/protect_stream', methods=['POST'])
def protect_single():
    download_type = "video_stream"
    output = {}
    if not is_valid_apikey(request):
        raise InvalidApiKeyException("Invalid API key received.")
    data = request.get_json()
    stream = data.get("item")
    ident = stream.get("ident")
    deviceId = data.get("deviceId")
    token = data.get("token")


    ws = Webshare(deviceId, token)
    salt = ws.file_password_salt(ident)
    if not salt:
        output = {
            "ident": ident,
            "salt": salt,
            "password": None
        }
    else:
        password = hashPassword("1", stream, download_type, salt)
        output = {
            "ident": ident,
            "salt": salt,
            "password": password
        }

    return jsonify({
        "success": True,
        "item": output,
    })

if __name__ == "__main__":
    app.run()
    # Debug/Development
    # app.run(debug=False, host="0.0.0.0", port="5000")
    # Production
    # http_server = WSGIServer(('', 5000), app)
    # http_server.serve_forever()
