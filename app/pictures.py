from app import *
import os
from flask import request, jsonify #, flash, redirect
from flask_jwt_extended import (jwt_required)
from werkzeug.utils import secure_filename
import ast


# ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@jwt.unauthorized_loader
def unauthorized_response():
    return jsonify({
        'ok': False,
        'message': 'Missing Authorization Header'
    }), 401


@app.route('/api/v1/upload', methods=['POST', 'DELETE'])
@jwt_required
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            # flash('No file part')
            return jsonify({'ok': False, 'message': "Unsupported Media Type"}), 415
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            # flash('No selected file')
            return jsonify({'ok': False, 'message': "Empty filename"}), 424
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                return jsonify({'ok': True, 'url': str(request.scheme + "://" + request.host + "/images/" + filename), 'message': "File exists"}), 424
            else:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return jsonify({'ok': True, 'url': str(request.scheme+"://"+request.host+"/images/"+filename)}), 200

    if request.method == 'DELETE':
        try:
            body = ast.literal_eval(json.dumps(request.get_json()))
            if body['file']:
                filename = secure_filename(body['file'])
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    return jsonify({'ok': True, 'message': "deleted"}), 200
                except OSError as err:
                    return jsonify({'ok': False, 'message': "failed. " + str(err)}), 422
        except:
            return jsonify({'ok': False, 'message': "No json with file"}), 424
        pass

