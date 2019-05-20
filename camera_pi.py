#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  camera_pi.py
#  
#  
#
import logging  
import time
import io
import threading
import picamera

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = threading.Condition()

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

class Camera(object):
    def __init__(self):
        logging.info('Initializing camera')
        self.stream = StreamingOutput()
        self.camera = picamera.PiCamera(resolution='1920x1080', framerate=24)
        time.sleep(2)
        self.camera.start_recording(self.stream, format='mjpeg')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        this.camera.close()

    def stopRecording(self):
        self.camera.stop_recording()

    def get_frame(self):
        with self.stream.condition:
            self.stream.condition.wait()
            return (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + self.stream.frame + b'\r\n')
