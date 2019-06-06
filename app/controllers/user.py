''' controller and routes for users '''

from flask import request, jsonify

from app import app, flask_bcrypt, jwt



@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({
        'ok': False,
        'message': 'Missing Authorization Header'
    }), 401





