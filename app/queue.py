"""This module will serve the api request."""

from config import client
from app import *
from flask import request, jsonify
import json
import ast
import imp
from flask_jwt_extended import (jwt_required)

# Import the helpers module
helper_module = imp.load_source('*', './app/helpers.py')

# Select the database
db = client.dashboard
# Select the collection
collection = db.queue


@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({
        'ok': False,
        'message': 'Missing Authorization Header'
    }), 401


@app.route("/api/v1/queue", methods=['GET'])
@jwt_required
def fetch_queue():
    """
       Function to fetch the users.
       """
    try:

        # Fetch all the record(s)
        # record_fetched = collection.find_one({"popup": 0})
        record_fetched = collection.find()

        if record_fetched.count() > 0:
            # Prepare the response
            tdata = []
            for data in record_fetched:
                tdata.append(data)
            return jsonify(tdata)

        else:
            # No records are found
            return jsonify([]), 404
        # Check if the records are found
        # record_fetched = collection.find_one()
        # if record_fetched:
        #     return jsonify(record_fetched)
        # else:
        #     # No records are found
        #     return jsonify([]), 404
    except Exception as err:
        # Error while trying to fetch the resource
        # Add message for debugging purpose
        app.logger.error('Data: ' + str(request.data))
        app.logger.error('Exception: ' + str(err))
        return err, 500


@app.route("/api/v1/queue", methods=['POST'])
@jwt_required
def create_queue():
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
            app.logger.error('bad body: '+str(request.data))
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
        app.logger.error('Data: ' +str(request.data))
        app.logger.error('Exception: ' +str(err))
        return err, 500


@app.route("/api/v1/queue/<queue_id>", methods=['POST'])
@jwt_required
def update_queue(queue_id):
    """
       Function to update the queue.
       """
    try:
        # Create new teams
        try:
            body = ast.literal_eval(json.dumps(request.get_json()))
        except:
            # Bad request as request body is not available
            # Add message for debugging purpose
            app.logger.error('Bad Data: ' + str(request.data))
            return "", 400

        record_updated = collection.update_one({"id": int(queue_id)}, {"$set": body})

        if record_updated.modified_count > 0:
            # Prepare the response as resource is updated successfully
            return jsonify({'ok': True, 'data': body}), 200
        else:
            # Bad request as the resource is not available to update
            # Add message for debugging purpose
            return jsonify({'ok': False, 'message': 'Not Found', 'data': body}), 404
    except Exception as err:
        # Error while trying to create the resource
        # Add message for debugging purpose
        app.logger.error('Data: ' + str(request.data))
        app.logger.error('Exception: ' + str(err))
        return err, 500


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
