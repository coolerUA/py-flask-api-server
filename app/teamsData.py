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
collection = db.teams


@app.route("/api/v1/teams", methods=['POST'])
@jwt_required
def create_team():
    """
       Function to create new teams.
       """
    try:
        # Create new teams
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


@app.route("/api/v1/teams", methods=['GET'])
@jwt_required
def fetch_teams():
    """
       Function to fetch the teams.
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
                # Prepare response if the teams are found
                # return dumps(collection.find())
                records_fetched = collection.find()
                tdata = []
                for data in records_fetched:
                    # tdata.append(JSONEncoder().encode(data))
                    tdata.append(data)
                # return jsonify(tdata)
                return jsonify(tdata)
            else:
                # Return empty array if no teams are found
                return jsonify([])
    except Exception as err:
        # Error while trying to fetch the resource
        # Add message for debugging purpose
        return err, 500


@app.route("/api/v1/teams/<team_id>", methods=['POST'])
@jwt_required
def update_team(team_id):
    """
       Function to update the team.
       """
    try:
        # Get the value which needs to be updated
        try:
            body = ast.literal_eval(json.dumps(request.get_json()))
        except:
            # Bad request as the request body is not available
            # Add message for debugging purpose
            return jsonify({'ok': False, 'message': 'No body', 'data': body}), 400

        # Updating the team
        records_updated = collection.update_one({"id": int(team_id)}, {"$set": body})
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


@app.route("/api/v1/teams/<team_id>", methods=['DELETE'])
@jwt_required
def remove_team(team_id):
    """
       Function to remove the team.
       """
    try:
        # Delete the team
        delete_team = collection.delete_one({"id": int(team_id)})

        if delete_team.deleted_count > 0 :
            # Prepare the response
            return "", 204
        else:
            # Resource Not found
            return "", 404
    except:
        # Error while trying to delete the resource
        # Add message for debugging purpose
        return "", 500
