#!/usr/bin/env python3
import getpass
import sys
import os
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal,QSignalMapper,QProcess
import gettext
import subprocess
from edupals.ui import QAnimatedStatusBar
from app2menu import App2Menu
import time
QString=type("")


class th_runApp(QThread):
	signal=pyqtSignal("PyQt_PyObject")
	def __init__(self,app,display,parent=None):
		QThread.__init__(self,parent)
		self.display=display
		self.app=app
		self.dbg=False

	def _debug(self,msg):
		if self.dbg:
			print("th_runApp: %s"%msg)

	def __del__(self):
		self.wait()
		pass

	def run(self):
		retval=False
		self._debug("Launching thread...")
		try:
			dsp=os.environ['DISPLAY']
			os.environ['DISPLAY']=self.display
			subprocess.Popen([self.app],stdin=None,stdout=None,stderr=None,shell=False)
			os.environ['DISPLAY']=dsp
			retval=True
		except Exception as e:
			print("Error running: %s"%e)
		self.signal.emit(retval)


class appRun():
	def __init__(self):
		self.dbg=True
		self.pid=0
		self.xephyr_servers={}
		self.username=getpass.getuser()
		self.main_display=os.environ['DISPLAY']
		self.categories={"lliurex-infantil":"applications-games","network":"applications-internet","education":"applications-education"}
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("appRun: %s"%msg)
	#def _debug

	def get_wid(self,display=":13"):
		wid=0
		count=0
		if display in self.xephyr_servers.keys():
			self._debug("Search WID for server at display %s"%display)
			self._debug("PID searched: %s"%self.xephyr_servers[display])
			self._debug("User searched: %s"%self.username)
			while not wid and count<=150:
				p_wid=self._run_cmd_on_display(["xdotool","search","--any","--name","Xephyr on %s"%display],self.main_display)
#				p_wid=self._run_cmd_on_display(["xdotool","search","--pid","%s"%self.xephyr_servers[display]],self.main_display)
				wid=p_wid.stdout.decode()
				time.sleep(0.1)
				count+=1
			if not wid:
				self._debug("Searching WID for active window")
#				p_wid=self._run_cmd_on_display(["xdotool","getactivewindow"],self.main_display)
#				wid=p_wid.stdout.decode()
		self._debug("WID %s"%wid)
		return(wid)
	#def get_wid

	def new_Xephyr(self,qwidget,display=":13"):
		return(self.init_Xephyr(qwidget,display,True))

	def init_Xephyr(self,qwidget,display=":13",create_new=False):
		os.environ["HOME"]="/home/%s"%self.username
		os.environ["XAUTHORITY"]="/home/%s/.Xauthority"%self.username
		if display not in self.xephyr_servers.keys() or create_new:
			display=self._find_free_display(display)
			self._debug("Display is set to %s"%display)
			if display==":-1":
				self._debug("No free display found")
				self.xephyr_servers[display]=-1
			if self.pid>=0:
				args=[]
				self._debug("Width: %s Height: %s"%(qwidget.width(),qwidget.height()))
				xephyr_cmd=["Xephyr",
				"-br",
				"-ac",
				"-screen",
				"%sx%s"%(qwidget.width(),qwidget.height()),
				"%s"%display]
				p_pid=subprocess.Popen(xephyr_cmd)
				self.xephyr_servers[display]=p_pid.pid
				self._debug("Xephyr PID: %s"%p_pid.pid)
		return (display,self.xephyr_servers[display])
	#def init_Xephyr

	def _run_cmd_on_display(self,cmd=[],display=":13"):
		os.environ["HOME"]="/home/%s"%self.username
		os.environ["XAUTHORITY"]="/home/%s/.Xauthority"%self.username
		dsp=os.environ['DISPLAY']
		os.environ['DISPLAY']=display
		self._debug("Running cmd on %s"%display)
		self._debug("CMD %s"%cmd)
		prc=subprocess.run(cmd,stdout=subprocess.PIPE)
		os.environ['DISPLAY']=dsp
		return(prc)
	#def _run_cmd_on_display

	def launch(self,app,display=":13"):
		#launch wm
		self._debug("Launching WM for display %s"%display)
#		th_run=th_runApp("ratpoison",display)
#		th_run.start()
		th_run=th_runApp(app,display)
		th_run.start()
	
	def _find_free_display(self,display=":13"):
		count=int(display.replace(":",""))
		self._debug("Search %s"%count)
		while(os.path.isfile('/tmp/.X%s-lock'%count)):
				count+=1
		try:
				display=":%s"%count
		except Exception as e:
			print ("Err: %s"%e)
			display=":-1"
		return("%s"%display)
	#def get_first_display
