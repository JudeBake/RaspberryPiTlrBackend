#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  timelapse_recorder.py
#  
#  
#
import os
import threading

class TimelapseRecorder(object):
    camera = None
    logger = None
    thread = None
    workingDir = '/home/pi/timelapse/'
    progressMsg = 'Not recording right now!'
    settings
    stopRecordingThread = False

    def __init__(self, camera, logger):
        TimelapseRecorder.camera = camera
        TimelapseRecorder.logger = logger

    def startRecording(self, settings):
        """Start recording a timelapse"""
        if self.__setupTimelapseDir(settings['timelapseName']):
            TimelapseRecorder.logger.debug('Recording time lapse ' + settings['timelapseName'])
            TimelapseRecorder.settings = settings
            TimelapseRecorder.stopRecordingThread = False
            TimelapseRecorder.thread = threading.Thread(target=self.__recording)
            TimelapseRecorder.thread.start()
            return {'result': 'success', 'message': 'Recording of time-lapse ' +
                    TimelapseRecorder.settings['timelapseName'] + ' started!'}
        else:
            TimelapseRecorder.logger.debug('Stop recording current time-lapse')
            return {'result': 'failure', 'message': 'Time-lapse already exists!'}

    def stopRecording(self):
        """Stop recording the current timelapse"""
        TimelapseRecorder.logger.debug('Stop recording current timelapse')
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
        cls.logger.debug('Recording thread started')
        frameCount = 0

        while not cls.stopRecordingThread:
            cls.logger.debug('Capturing frame #' + frameCount + ' of ' + cls.settings['totalFrameCount'])
            if frameCount > cls.settings['totalFrameCount']:
                cls.stopRecordingThread = True
        cls.thread = None
        
