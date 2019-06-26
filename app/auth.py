from flask import request, jsonify
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity)
import imp
from app import *
from app.schemas import validate_user
from config import client

helper_module = imp.load_source('*', './app/helpers.py')
db = client.dashboard
# Select the collection
collection = db.users


@app.route("/")
def get_initial_response():
    """Welcome message for the API."""
    # Message to the user
    message = {
        'apiVersion': 'v1.0',
        'status': '200',
        'message': 'Welcome to the Flask API'
    }
    # Making the message looks good
    resp = jsonify(message)
    # Returning the object
    return resp


@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({
        'ok': False,
        'message': 'Missing Authorization Header'
    }), 401


@app.route('/api/v1/auth', methods=['POST'])
def auth_user():
    ''' auth endpoint '''
    data = validate_user(request.get_json())
    if data['ok']:
        data = data['data']
        user = db.admin.find_one({'email': data['email']}, {"_id": 0})
        if user and flask_bcrypt.check_password_hash(user['password'], data['password']):
            try:
                if user['isadmin'] == 1:
                    del user['password']
                    access_token = create_access_token(identity=data)
                    refresh_token = create_refresh_token(identity=data)
                    user['token'] = access_token
                    user['refresh'] = refresh_token
                    return jsonify({'ok': True, 'data': user}), 200
                else:
                    return jsonify({'ok': False, 'message': 'No rights'}), 400
            except KeyError:
                return jsonify({'ok': False, 'message': 'No rights'}), 400
        else:
            return jsonify({'ok': False, 'message': 'invalid username or password'}), 401
    else:
        return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400


@app.route('/api/v1/register', methods=['POST'])
def register():
    ''' register user endpoint '''
    data = validate_user(request.get_json())
    if data['ok']:
        data = data['data']
        data['password'] = flask_bcrypt.generate_password_hash(
            data['password'])
        db.admin.insert_one(data)
        return jsonify({'ok': True, 'message': 'User created successfully!'}), 200
    else:
        return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400


@app.route('/api/v1/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    ''' refresh token endpoint '''
    current_user = get_jwt_identity()
    ret = {
        'token': create_access_token(identity=current_user)
    }
    return jsonify({'ok': True, 'data': ret}), 200

