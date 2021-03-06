#!/usr/bin/python3
import sys
import os
from PyQt5.QtWidgets import QApplication
from appconfig.appConfigScreen import appConfigScreen as appConfig
app=QApplication(["Run-O-Matic"])
config=appConfig("Runoconfig",{'app':app})
config.setRsrcPath("/usr/share/runomatic/rsrc")
config.setIcon('runomatic.svg')
config.setBanner('banner.png')
config.setBackgroundImage('background.png')
config.setConfig(confDirs={'system':'/usr/share/runomatic','user':'%s/.config'%os.environ['HOME']},confFile="runomatic.conf")
config.Show()
config.setFixedSize(config.width(),config.height())

app.exec_()
