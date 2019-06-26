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
                    tdata.append(data)
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
        app.logger.error('Data: ' +str(request.data))
        app.logger.error('Exception: ' +str(err))
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
            app.logger.error('Bad body ' + str(request.data))
            return jsonify({'ok': False, 'message': 'No body', 'data': str(request.data)}), 400
        app.logger.error('Data: ' +str(request.data))
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
        app.logger.error('Data: ' +str(request.data))
        app.logger.error('Exception: ' +str(err))
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
    except Exception as err:
        # Error while trying to delete the resource
        # Add message for debugging purpose
        app.logger.error('Data: ' +str(request.data))
        app.logger.error('Exception: ' +str(err))
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
