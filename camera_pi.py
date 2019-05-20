#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  camera_pi.py
#  
#  
#  
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
    thread = None  # background thread that reads frames from camera
    last_access = 0  # time of last client access to the camera
    stream = StreamingOutput()

    def initialize(self):
        with picamera.PiCamera(resolution='1920x1080', framerate=24) as camera:
            # camera setup
            # camera.hflip = True
            # camera.vflip = True

            # let camera warm up
            # camera.start_preview()
            time.sleep(2)

            camera.start_recording(self.stream, format='mjpeg')

        # if Camera.thread is None:
        #     # start background frame thread
        #     Camera.thread = threading.Thread(target=self._thread)
        #     Camera.thread.start()

        #     # wait until frames start to be available
        #     while self.stream.frame is None:
        #         time.sleep(0)

    def get_frame(self):
        with self.stream.condition:
            self.stream.condition.wait()
            return (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + self.stream.frame + b'\r\n')

    # @classmethod
    # def _thread(cls):
    #     with picamera.PiCamera(resolution='1920x1080', framerate=24) as camera:
    #         # camera setup
    #         # camera.hflip = True
    #         # camera.vflip = True

    #         # let camera warm up
    #         # camera.start_preview()
    #         time.sleep(2)

    #         camera.start_recording(cls.stream, format='mjpeg')
