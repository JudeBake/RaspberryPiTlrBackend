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
from datetime import datetime, timedelta

class TimelapseRecorder(object):
    logger = None
    camera = None
    thread = None
    socketio = None
    workingDir = '/home/pi/timelapse'
    stopAndProcess = False
    stopAndDiscard = False
    state = ''
    recordingStep = ''
    timelapseName = ''
    timelapseEndTime = None
    timelapseTotalRecTime = None
    timelapseeRemainingTime = None
    timelapseDir = ''
    timelapseFile = ''
    frameCount = 0
    frameDelay = 1
    stillsNameFormat = ''

    def __init__(self, camera, logger, socketio):
        TimelapseRecorder.logger = logger
        TimelapseRecorder.camera = camera
        TimelapseRecorder.socketio = socketio
        TimelapseRecorder.state = 'Idle'

    @classmethod
    def getStatus(cls):
        if cls.thread is None:
            return {'state': cls.state}
        else:
            return {'state': cls.state,
                    'timelapseInfo': {
                        'name': cls.timelapseName,
                        'capturingEndTime': cls.timelapseEndTime.strftime('%y-%m-%d %H:%M:%S'),
                        'frameDelay': cls.frameDelay,
                        'progress': {'recordingStep': cls.recordingStep,
                                     'remainingTime': cls.timelapseRemainingTime.total_seconds(),
                                     'totalRecordingTime': cls.timelapseTotalRecTime.total_seconds()
                                    }
                    }
                   }

    @classmethod
    def startRecording(cls, timelapseInfo):
        """Start recording a timelapse"""
        if cls.__setupTimelapseDir(timelapseInfo['name']):
            cls.__saveInfo(timelapseInfo)
            cls.logger.info('Start recording')
            cls.stopAndProcess = False
            cls.stopAndDiscard = False
            cls.thread = threading.Thread(target=cls.__recording)
            cls.thread.start()
            return {'result': 'success', 'message': 'Recording of time-lapse ' +
                    cls.timelapseName + ' started!'}
        else:
            cls.logger.info('Stop recording current time-lapse')
            return {'result': 'failure', 'message': 'Time-lapse '
                    + cls.timelapseName +' already exists!'}

    @classmethod
    def stopAndProcessTimelapse(cls):
        """Stop recording and process the current timelapse"""
        cls.logger.info('Stop recording current timelapse')
        cls.stopAndProcess = True
        return {'result': 'success', 'message': 'Recording stopped. Now processing "' +
                TimelapseRecorder.timelapseName + '"'}

    @classmethod
    def stopAndDiscardTimelapse(cls):
        """Stop recording and discard the current timelapse"""
        cls.logger.info('Stop recording current timelapse')
        cls.stopAndDiscard = True
        return {'result': 'success', 'message': 'Recording stopped. Discarding "' +
                TimelapseRecorder.timelapseName + '"'}

    @classmethod
    def __setupTimelapseDir(cls, dirName):
        """Create working directory for a timelapse"""
        if os.path.isdir(os.path.join(cls.workingDir, dirName)):
            """Timelapse already exists"""
            return False
        else:
            os.mkdir(os.path.join(cls.workingDir, dirName))
            return True

    @classmethod
    def __saveInfo(cls, timelapseInfo):
        cls.timelapseName = timelapseInfo['name']
        cls.timelapseDir = os.path.join(TimelapseRecorder.workingDir,
                                        timelapseInfo['name'])
        cls.timelapseFile = os.path.join(TimelapseRecorder.timelapseDir,
                                         timelapseInfo['name'] + '.mp4')
        cls.stillsNameFormat = os.path.join(TimelapseRecorder.timelapseDir,
                                            '%05d.jpg')
        cls.frameDelay = timelapseInfo['frameDelay']
        cls.timelapseEndTime = datetime.strptime(timelapseInfo['capturingEndTime'], '%Y-%m-%d %H:%M:%S')
        cls.timelapseRemainingTime = cls.__calculateRemainingTime()
        cls.timelapseTotalRecTime = cls.__calculateRemainingTime()

    @classmethod
    def __calculateRemainingTime(cls):
        return cls.timelapseEndTime - datetime.now()

    @classmethod
    def __cleanupDir(cls):
        stillsList = [still for still in os.listdir(cls.timelapseDir) if still.endswith('.jpg')]
        for still in stillsList:
            os.remove(os.path.join(cls.timelapseDir, still))

    @classmethod
    def __recording(cls):
        cls.logger.info('Recording thread started')
        cls.state = 'Recording'
        cls.recordingStep = 'Capturing'
        cls.socketio.emit('statusUpdate', cls.getStatus())
        cls.frameCount = 0
        while not cls.stopAndProcess and not cls.stopAndDiscard:
            cls.camera.capture(cls.stillsNameFormat % cls.frameCount, use_video_port=True)
            cls.frameCount += 1
            cls.socketio.emit('statusUpdate', cls.getStatus())
            time.sleep(cls.frameDelay)
            cls.timelapseRemainingTime = cls.__calculateRemainingTime()
            if cls.timelapseRemainingTime.total_seconds() <= 0:
                cls.stopAndProcess = True
        if cls.stopAndProcess:
            cls.recordingStep = 'Processing'
            cls.socketio.emit('statusUpdate', cls.getStatus())
            ffmpegCmd = "ffmpeg -r 30 -i " + cls.stillsNameFormat + " -vcodec libx264 -preset veryslow -crf 18 " + cls.timelapseFile
            os.system(ffmpegCmd)
        cls.recordingStep = 'Cleaning Up'
        cls.socketio.emit('statusUpdate', cls.getStatus())
        cls.__cleanupDir()
        if cls.stopAndDiscard:
            os.rmdir(cls.timelapseDir)
        cls.state = 'Idle'
        cls.socketio.emit('statusUpdate', {'state': cls.state})
        cls.thread = None

