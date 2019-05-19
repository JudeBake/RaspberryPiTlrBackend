#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  camera_pi.py
#  
#  
# 
from flask import Flask, render_template, Response, request
from flask_restful import Resource, Api
from flask_jsonpify import jsonify
from flask_cors import CORS

# Raspberry Pi camera module (requires picamera package, developed by Miguel Grinberg)

from camera_pi import Camera
camera = Camera()

app = Flask(__name__)
"""For Dev only"""
cors = CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

class Recording(Resource):
    def post(self):
        """Start recording"""
        settings = request.get_json()
        app.logger.debug('Received settings for time lapse:' + settings['timelapseName'])
        app.logger.info('Starting to record time lapse: ' + settings['timelapseName'])
        return jsonify({'result': 'Success', 'message': 'Stating to record ' + settings['timelapseName']})
    def delete(self):
        """Stop recording"""
        app.logger.info('Stopping to record time lapse')
        return jsonify({'result': 'Success', 'message': 'Stopping to record'})


api.add_resource(Recording, '/recording')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port =5000, debug=True, threaded=True)
