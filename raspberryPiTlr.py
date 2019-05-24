from flask import Flask, render_template, Response, request
from flask_socketio import SocketIO, emit
from flask_jsonpify import jsonify
from flask_cors import CORS

import io
import time
from threading import Condition

# Raspberry Pi camera module (requires picamera package, developed by Miguel Grinberg)
from picamera import PiCamera
from timelapse_recorder import TimelapseRecorder

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

camera = PiCamera(resolution='640x480', framerate=24)
time.sleep(2)
output = StreamingOutput()
camera.start_recording(output, format='mjpeg')

app = Flask(__name__)
"""For Dev only"""
cors = CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app)

# Timelapse recorder
timelapseRecorder = TimelapseRecorder(camera, app.logger, socketio)

#
#  Static route for test and video feed
#
@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def gen():
    """Video streaming generator function."""
    while True:
        with output.condition:
            output.condition.wait()
            frame = output.frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n'
               + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

#
# Web socket implementation
#
@socketio.on('connect')
def onConnect():
    socketio.emit('statusUpdate', timelapseRecorder.getStatus())

@socketio.on('startRecording')
def onStartRecording(timelapseInfo):
    return {'result': 'success', 'message': 'Recording of time-lapse ' +
                    timelapseInfo.timelapseName + ' started!'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port =5000, debug=True, threaded=True)
