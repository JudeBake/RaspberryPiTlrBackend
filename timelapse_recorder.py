#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  timelapse_recorder.py
#  
#  
#
import os
import threading
import time

class TimelapseRecorder(object):
    logger = None
    camera = None
    thread = None
    workingDir = '/home/pi/timelapse/'
    progressMsg = 'Not recording right now!'
    settings = {'timelaspeName': '', 'totalFrameCount': 0}
    stopRecordingThread = False

    def __init__(self, camera):
        TimelapseRecorder.camera = camera

    def getState(self):
        if TimelapseRecorder.thread is None:
            return {'state': 'Idle'}
        else:
            return {'state': 'Recording'}

    def startRecording(self, settings):
        """Start recording a timelapse"""
        if self.__setupTimelapseDir(settings['timelapseName']):
            print('Recording time lapse ' + settings['timelapseName'])
            TimelapseRecorder.settings = settings
            TimelapseRecorder.stopRecordingThread = False
            TimelapseRecorder.thread = threading.Thread(target=self.__recording)
            TimelapseRecorder.thread.start()
            return {'result': 'success', 'message': 'Recording of time-lapse ' +
                    TimelapseRecorder.settings['timelapseName'] + ' started!'}
        else:
            print('Stop recording current time-lapse')
            return {'result': 'failure', 'message': 'Time-lapse already exists!'}

    def stopRecording(self):
        """Stop recording the current timelapse"""
        print('Stop recording current timelapse')
        TimelapseRecorder.stopRecordingThread = True
        return {'result': 'success', 'message': 'Recording time-lapse ' +
                TimelapseRecorder.settings['timelapseName'] + ' stopped!'}

    def __setupTimelapseDir(self, dirName):
        """Create working directory for a timelapse"""
        if os.path.isdir(self.workingDir + dirName):
            """Timelapse already exists"""
            return False
        else:
            os.mkdir(self.workingDir + dirName)
            return True

    @classmethod
    def __recording(cls):
        print('Recording thread started')
        frameCount = 0

        while not cls.stopRecordingThread:
            print('Capturing frame #' + frameCount + ' of ' + cls.settings['totalFrameCount'])
            time.sleep(cls.settings['frameDelay'])
            if frameCount > cls.settings['totalFrameCount']:
                cls.stopRecordingThread = True
        cls.thread = None
        
