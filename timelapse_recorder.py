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
    workingDir = '/home/pi/timelapse'
    recordingStep = ''
    progessValue = 0
    stopRecordingThread = False
    timelapseName = ''
    timelapseDir = ''
    timelapseFile = ''
    frameCount = 0
    totalFrameCount = 0
    frameDelay = 1
    stillsNameFormat = ''

    def __init__(self, camera, logger):
        TimelapseRecorder.logger = logger
        TimelapseRecorder.camera = camera

    def getStatus(self):
        if TimelapseRecorder.thread is None:
            return {'state': 'Idle'}
        else:
            return {'state': 'Recording',
                    'progress': {'recordingStep': TimelapseRecorder.recordingStep,
                                 'value': TimelapseRecorder.progessValue}}

    def startRecording(self, settings):
        """Start recording a timelapse"""
        if self.__setupTimelapseDir(settings['timelapseName']):
            self.__saveSettings(settings)
            TimelapseRecorder.logger.info('Start recording')
            TimelapseRecorder.stopRecordingThread = False
            TimelapseRecorder.thread = threading.Thread(target=self.__recording)
            TimelapseRecorder.thread.start()
            return {'result': 'success', 'message': 'Recording of time-lapse ' +
                    TimelapseRecorder.timelapseName + ' started!'}
        else:
            TimelapseRecorder.logger.info('Stop recording current time-lapse')
            return {'result': 'failure', 'message': 'Time-lapse already exists!'}

    def stopRecording(self):
        """Stop recording the current timelapse"""
        TimelapseRecorder.logger.info('Stop recording current timelapse')
        TimelapseRecorder.stopRecordingThread = True
        return {'result': 'success', 'message': 'Recording time-lapse ' +
                TimelapseRecorder.timelapseName + ' stopped!'}

    def __setupTimelapseDir(self, dirName):
        """Create working directory for a timelapse"""
        if os.path.isdir(TimelapseRecorder.workingDir + '/' + dirName):
            """Timelapse already exists"""
            return False
        else:
            os.mkdir(self.workingDir + '/' + dirName)
            return True
    def __saveSettings(self, settings):
        TimelapseRecorder.timelapseName = settings['timelapseName']
        TimelapseRecorder.timelapseDir = os.path.join(TimelapseRecorder.workingDir,
                                                      settings['timelapseName'])
        TimelapseRecorder.timelapseFile = os.path.join(TimelapseRecorder.timelapseDir,
                                                       settings['timelapseName'] + '.mp4')
        TimelapseRecorder.stillsNameFormat = os.path.join(TimelapseRecorder.timelapseDir,
                                                          '%05d.jpg')
        TimelapseRecorder.totalFrameCount = settings['totalFrameCount']
        TimelapseRecorder.frameDelay = settings['frameDelay']

    @classmethod
    def cleanupDir(cls):
        stillsList = [still for still in os.listdir(cls.timelapseDir) if still.endswith('.jpg')]
        for still in stillsList:
            os.remove(os.path.join(cls.timelapseDir, still))

    @classmethod
    def __recording(cls):
        cls.logger.info('Recording thread started')
        TimelapseRecorder.recordingStep = 'Capturing Frames'
        TimelapseRecorder.frameCount = 1

        while not cls.stopRecordingThread:
            cls.camera.capture(cls.stillsNameFormat % TimelapseRecorder.frameCount, use_video_port=True)
            TimelapseRecorder.frameCount += 1
            TimelapseRecorder.progessValue = round(TimelapseRecorder.frameCount/TimelapseRecorder.totalFrameCount*100)
            time.sleep(cls.frameDelay)
            if TimelapseRecorder.frameCount > cls.totalFrameCount:
                cls.stopRecordingThread = True
        TimelapseRecorder.recordingStep = 'Processing Time-lapse'
        ffmpegCmd = "ffmpeg -r 30 -i " + TimelapseRecorder.stillsNameFormat + " -vcodec libx264 -preset veryslow -crf 18 " + TimelapseRecorder.timelapseFile
        os.system(ffmpegCmd)
        TimelapseRecorder.recordingStep = 'Cleanup'
        cls.cleanupDir()
        cls.thread = None

