"""This module will serve the api request."""

from config import client
from app import *
# from bson.json_util import dumps
from flask import request, jsonify
import json
import ast
import imp
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required, get_jwt_identity)
from app.schemas import validate_user

# Import the helpers module
helper_module = imp.load_source('*', './app/helpers.py')

# Select the database
db = client.dashboard
# Select the collection
collection = db.users



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


@app.route("/api/v1/users", methods=['POST'])
@jwt_required
def create_user():
    """
       Function to create new users.
       """
    try:
        # Create new users
        try:
            body = ast.literal_eval(json.dumps(request.get_json()))
        except:
            # Bad request as request body is not available
            # Add message for debugging purpose
            return "", 400

        record_created = collection.insert(body)

        # Prepare the response
        if isinstance(record_created, list):
            # Return list of Id of the newly created item
            return jsonify([str(v) for v in record_created]), 201
        else:
            # Return Id of the newly created item
            return jsonify(str(record_created)), 201
    except Exception as err:
        # Error while trying to create the resource
        # Add message for debugging purpose
        return err, 500


@app.route("/api/v1/users", methods=['GET'])
@jwt_required
def fetch_users():
    """
       Function to fetch the users.
       """
    try:
        # Call the function to get the query params
        query_params = helper_module.parse_query_params(request.query_string)
        # Check if dictionary is not empty
        if query_params:

            # Try to convert the value to int
            query = {k: int(v) if isinstance(v, str) and v.isdigit() else v for k, v in query_params.items()}
            # Fetch all the record(s)
            records_fetched = collection.find(query)

            # Check if the records are found
            if records_fetched.count() > 0:
                # Prepare the response
                # return dumps(records_fetched)

                tdata = []
                for data in records_fetched:
                    # tdata.append(JSONEncoder().encode(data))
                    tdata.append(data)
                # return jsonify(tdata)
                return jsonify(tdata)

            else:
                # No records are found
                return jsonify([]), 404

        # If dictionary is empty
        else:
            # Return all the records as query string parameters are not available
            if collection.find().count() > 0:
                # Prepare response if the users are found
                # return dumps(collection.find())
                records_fetched = collection.find()
                tdata = []
                for data in records_fetched:
                    # tdata.append(JSONEncoder().encode(data))
                    tdata.append(data)
                # return jsonify(tdata)
                return jsonify(tdata)
            else:
                # Return empty array if no users are found
                return jsonify([])
    except Exception as err:
        # Error while trying to fetch the resource
        # Add message for debugging purpose
        return err, 500


@app.route("/api/v1/users/<user_id>", methods=['POST'])
@jwt_required
def update_user(user_id):
    """
       Function to update the user.
       """
    try:
        # Get the value which needs to be updated
        try:
            body = ast.literal_eval(json.dumps(request.get_json()))
        except:
            # Bad request as the request body is not available
            # Add message for debugging purpose
            return jsonify({'ok': False, 'message': 'No body', 'data': body}), 400

        # Updating the user
        records_updated = collection.update_one({"id": int(user_id)}, {"$set": body})
        # Check if resource is updated
        if records_updated.modified_count > 0:
            # Prepare the response as resource is updated successfully
            return jsonify({'ok': True, 'data': body}), 200
        else:
            # Bad request as the resource is not available to update
            # Add message for debugging purpose
            return jsonify({'ok': False, 'message': 'Not Found', 'data': body}), 404
    except Exception as err:
        # Error while trying to update the resource
        # Add message for debugging purpose
        return err, 500


@app.route("/api/v1/users/<user_id>", methods=['DELETE'])
@jwt_required
def remove_user(user_id):
    """
       Function to remove the user.
       """
    try:
        # Delete the user
        delete_user = collection.delete_one({"id": int(user_id)})

        if delete_user.deleted_count > 0 :
            # Prepare the response
            return "", 204
        else:
            # Resource Not found
            return "", 404
    except:
        # Error while trying to delete the resource
        # Add message for debugging purpose
        return "", 500


@app.errorhandler(404)
def page_not_found(e):
    """Send message to the user with notFound 404 status."""
    # Message to the user
    message = {
        "err":
            {
                "msg": "This route is currently not supported. Please refer API documentation."
            }
    }
    # Making the message looks good
    resp = jsonify(message)
    # Sending OK response
    resp.status_code = 404
    # Returning the object
    return resp
