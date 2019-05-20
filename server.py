import io
import picamera
import logging
import socketserver
from http import server
from threading import Condition
import json

from timelapse_recorder import TimelapseRecorder

PAGE="""\
<html>
<head>
<title>picamera MJPEG streaming demo</title>
</head>
<body>
<h1>PiCamera MJPEG Streaming Demo</h1>
<img src="video_feed" width="640" height="480" />
</body>
</html>
"""


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

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        handleGet(self)
    def do_PUT(self):

# GET Handling function
def handleGet(reqHandler):
    if reqHandler.path == '/':
        reqHandler.send_response(301)
        reqHandler.send_header('Location', '/index.html')
        reqHandler.end_headers()
    elif reqHandler.path == '/index.html':
        content = PAGE.encode('utf-8')
        reqHandler.send_response(200)
        reqHandler.send_header('Content-Type', 'text/html')
        reqHandler.send_header('Content-Length', len(content))
        reqHandler.end_headers()
        reqHandler.wfile.write(content)
    elif reqHandler.path == '/state':
        json_str = json.dumps(timelapseRecorder.getState())
        reqHandler.send_response(200)
        reqHandler.send_header('Content-Type', 'application/json')
        reqHandler.send_header('Access-Control-Allow-Origin', '*')
        reqHandler.end_headers()
        reqHandler.wfile.write(json_str.encode(encoding='utf_8'))
    elif reqHandler.path == '/video_feed':
        reqHandler.send_response(200)
        reqHandler.send_header('Age', 0)
        reqHandler.send_header('Cache-Control', 'no-cache, private')
        reqHandler.send_header('Pragma', 'no-cache')
        reqHandler.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
        reqHandler.end_headers()
        try:
            while True:
                with output.condition:
                    output.condition.wait()
                    frame = output.frame
                reqHandler.wfile.write(b'--FRAME\r\n')
                reqHandler.send_header('Content-Type', 'image/jpeg')
                reqHandler.send_header('Content-Length', len(frame))
                reqHandler.end_headers()
                reqHandler.wfile.write(frame)
                reqHandler.wfile.write(b'\r\n')
        except Exception as e:
            logging.warning(
                'Removed streaming client %s: %s',
                reqHandler.client_address, str(e))
    else:
        reqHandler.send_error(404)
        reqHandler.end_headers()

# PUT handling function
def handlePut(reqHandler):
    if reqHandler == '/recording/start':
        logger.debug('Handling PUT /recording/start')
        json_str = json.dumps(timelapseRecorder.startRecording())
        reqHandler.send_response(200)
        reqHandler.send_header('Content-Type', 'application/json')
        reqHandler.send_header('Access-Control-Allow-Origin', '*')
        reqHandler.end_headers()
        reqHandler.wfile.write(json_str.encode(encoding='utf_8'))
    elif reqHandler == '/recording/stop':
        logger.debug('Handling PUT /recording/stop')
        json_str = json.dumps(timelapseRecorder.stopRecording())
        reqHandler.send_response(200)
        reqHandler.send_header('Content-Type', 'application/json')
        reqHandler.send_header('Access-Control-Allow-Origin', '*')
        reqHandler.end_headers()
        reqHandler.wfile.write(json_str.encode(encoding='utf_8'))
    else:
        reqHandler.send_error(404)
        reqHandler.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        timelapseRecorder = TimelapseRecorder(camera)
        address = ('', 5000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
