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
    socketio = None
    workingDir = '/home/pi/timelapse'
    stopRecordingThread = False
    state = ''
    recordingStep = ''
    timelapseName = ''
    timelapseEndTime = ''
    timelapseDir = ''
    timelapseFile = ''
    frameCount = 0
    totalFrameCount = 0
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
                        'capturingEndTime': cls.timelapseEndTime,
                        'totalFrameCount': cls.totalFrameCount,
                        'frameDelay': cls.frameDelay,
                        'progress': {'recordingStep': cls.recordingStep,
                                     'capturedFrames': cls.frameCount,
                                    }
                    }   
                   }

    @classmethod
    def startRecording(cls, timelapseInfo):
        """Start recording a timelapse"""
        if cls.__setupTimelapseDir(timelapseInfo['name']):
            cls.__saveInfo(timelapseInfo)
            cls.logger.info('Start recording')
            cls.stopRecordingThread = False
            cls.thread = threading.Thread(target=cls.__recording)
            cls.thread.start()
            return {'result': 'success', 'message': 'Recording of time-lapse ' +
                    cls.timelapseName + ' started!'}
        else:
            cls.logger.info('Stop recording current time-lapse')
            return {'result': 'failure', 'message': 'Time-lapse '
                    + cls.timelapseName +' already exists!'}

    @classmethod
    def stopRecording(cls):
        """Stop recording the current timelapse"""
        cls.logger.info('Stop recording current timelapse')
        cls.stopRecordingThread = True
        return {'result': 'success', 'message': 'Recording time-lapse ' +
                TimelapseRecorder.timelapseName + ' stopped!'}

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
        cls.totalFrameCount = timelapseInfo['totalFrameCount']
        cls.frameDelay = timelapseInfo['frameDelay']
        cls.timelapseEndTime = timelapseInfo['capturingEndTime']

    @classmethod
    def cleanupDir(cls):
        stillsList = [still for still in os.listdir(cls.timelapseDir) if still.endswith('.jpg')]
        for still in stillsList:
            os.remove(os.path.join(cls.timelapseDir, still))

    @classmethod
    def __recording(cls):
        cls.logger.info('Recording thread started')
        cls.state = 'Recording'
        cls.recordingStep = 'Capturing Frames'
        cls.frameCount = 0
        cls.socketio.emit('statusUpdate', cls.getStatus())
        while not cls.stopRecordingThread:
            cls.camera.capture(cls.stillsNameFormat % cls.frameCount, use_video_port=True)
            cls.frameCount += 1
            cls.socketio.emit('statusUpdate', cls.getStatus())
            time.sleep(cls.frameDelay)
            if cls.frameCount > cls.totalFrameCount - 1:
                cls.stopRecordingThread = True
        cls.recordingStep = 'Processing Time-lapse'
        cls.socketio.emit('statusUpdate', cls.getStatus())
        ffmpegCmd = "ffmpeg -r 30 -i " + cls.stillsNameFormat + " -vcodec libx264 -preset veryslow -crf 18 " + cls.timelapseFile
        os.system(ffmpegCmd)
        cls.recordingStep = 'Cleaning Up'
        cls.socketio.emit('statusUpdate', cls.getStatus())
        cls.cleanupDir()
        cls.state = 'Idle'
        cls.socketio.emit('statusUpdate', {'state': cls.state})
        cls.thread = None

