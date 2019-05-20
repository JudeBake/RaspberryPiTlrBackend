from flask import Flask, render_template, Response, request
from flask_restful import Resource, Api
from flask_jsonpify import jsonify
from flask_cors import CORS

# Raspberry Pi camera module (requires picamera package, developed by Miguel Grinberg)
from camera_pi import Camera
from timelapse_recorder import TimelapseRecorder

app = Flask(__name__)
"""For Dev only"""
cors = CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app)

camera = Camera()
timeLapseRecorder = TimelapseRecorder(camera, app.logger)

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

class RecorderState(Resource):
    def get(self):
        """Getting recorder state"""
        return timeLapseRecorder.getState()

api.add_resource(RecorderState, '/state')

class StartRecording(Resource):
    def put(self):
        """Start recording"""
        settings = request.get_json()
        app.logger.debug('Received settings for time lapse:' + settings['timelapseName'])
        app.logger.info('Starting to record time lapse: ' + settings['timelapseName'])
        return jsonify({'result': 'Success', 'message': 'Stating to record ' + settings['timelapseName']})

api.add_resource(StartRecording, '/recording/start')

class StopRecording(Resource):
    def put(self):
        """Stop recording"""
        app.logger.info('Stopping to record time lapse')
        return jsonify({'result': 'Success', 'message': 'Stopping to record'})

api.add_resource(StopRecording, '/recording/stop')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port =5000, debug=True, threaded=True)
