from flask import Flask, render_template, Response, request, send_from_directory
from flask_socketio import SocketIO, emit
from flask_jsonpify import jsonify
from flask_cors import CORS

import io
import time
from threading import Condition

# Raspberry Pi camera module (requires picamera package, developed by Miguel Grinberg)
from picamera import PiCamera
from timelapse_recorder import TimelapseRecorder
from timelapse_manager import TimelapseManager

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

# Timelapse objects
timelapseRecorder = TimelapseRecorder(camera, app.logger, socketio)
timelapseManager = TimelapseManager(app.logger, timelapseRecorder)

#
#  Static route for test and video feed
#
@app.route('/', methods=['GET'])
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

@app.route('/video_feed', methods=['GET'])
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/downloads/<path:timelapseName>', methods=['GET'])
def downloads(timelapseName):
    timelapsePath = timelapseManager.getPath(timelapseName)
    return send_from_directory(directory=timelapsePath, filename=timelapseName+'.mp4')

#
# Web socket implementation
#
@socketio.on('connect')
def onConnect():
    socketio.emit('statusUpdate', timelapseRecorder.getStatus())

@socketio.on('startRecording')
def onStartRecording(timelapseInfo):
    return timelapseRecorder.startRecording(timelapseInfo)

@socketio.on('stopAndProcess')
def onStopAndProcess():
    return timelapseRecorder.stopAndProcessTimelapse()

@socketio.on('stopAndDiscard')
def onStopAndDiscard():
    return timelapseRecorder.stopAndDiscardTimelapse()

@socketio.on('getTimelapseList')
def onGetTimelapseList():
    return timelapseManager.getTimelaspeList()

@socketio.on('deleteTimelapse')
def onDeleteTimelapse(timelapseInfo):
    return timelapseManager.deleteTimelapse(timelapseInfo)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port =5000, debug=False, threaded=True)
