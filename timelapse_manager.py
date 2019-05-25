#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  timelapse_manager.py
#
#
#
import os
import shutil

class TimelapseManager(object):
    def __init__(self, logger):
        """ Time-lapse manager constructor """
        self.workingDir = '/home/pi/timelapse'
        self.logger = logger

    def getTimelaspeList(self):
        """ Getting time-lapse list """
        timelapseList = os.listdir(self.workingDir)
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
