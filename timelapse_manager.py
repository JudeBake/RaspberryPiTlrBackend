#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  timelapse_manager.py
#
#
#
import os
import shutil
from datetime import datetime
from pymediainfo import MediaInfo
import json

class TimelapseManager(object):
    def __init__(self, logger, timelapseRecorder):
        """ Time-lapse manager constructor """
        self.workingDir = '/home/pi/timelapse'
        self.logger = logger
        self.timelapseRecorder = timelapseRecorder

    def getTimelaspeList(self):
        """ Getting time-lapse list """
        timelapseList = []
        recordingTimelapse = ''
        recorderStatus = self.timelapseRecorder.getStatus()
        if recorderStatus['state'] == 'Recording':
            recordingTimelapse = recorderStatus['timelapseInfo']['name']
        for d in os.listdir(self.workingDir):
            if d != recordingTimelapse:
                timelapseFile = os.path.join(self.workingDir, d, d + '.mp4')
                timelapseStat = os.stat(timelapseFile)
                creation = datetime.fromtimestamp(timelapseStat[8]).strftime('%Y-%m-%d %H:%M')
                duration = self.__getTimelapseDuration(timelapseFile)
                timelapseList.append({'name': d, 'creation': creation, 'duration': duration})
        return {'timelapses': timelapseList}

    def deleteTimelapse(self, timelapseInfo):
        """ Delete a time-lapse """
        try:
            shutil.rmtree(os.path.join(self.workingDir, timelapseInfo['name']))
            return {'result': 'success', 'message': 'Time-lapse "'
                + timelapseInfo['name'] + '" deleted!'}
        except:
            return {'result': 'failure', 'message': 'Unable to delete time-lapse "'
                + timelapseInfo['name'] + '"!'}

    def getPath(self, timelapseName):
        """ Getting time-lapse file """
        return os.path.join(self.workingDir, timelapseName)

    def __getTimelapseDuration(self, timelapseFile):
        """ Getting time-lapse duration """
        mediaInfo = json.loads(MediaInfo.parse(timelapseFile).to_json())
        return mediaInfo['tracks'][1]['other_duration'][0]
