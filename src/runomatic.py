#!/usr/bin/python3
import getpass
import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QShortcut,\
				QDialog,QStackedWidget,QGridLayout,QTabBar,QTabWidget,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar,QFileDialog,QDialogButtonBox,QScrollBar,QScrollArea,QCheckBox,QTableWidget,\
				QTableWidgetItem,QHeaderView,QTableWidgetSelectionRange,QInputDialog,QDesktopWidget
from PyQt5 import QtGui
from PyQt5.QtCore import QSize,pyqtSlot,Qt, QPropertyAnimation,QThread,QRect,QTimer,pyqtSignal,QSignalMapper,QProcess,QEvent
from edupals.ui import QAnimatedStatusBar
import gettext
import subprocess
import signal
import psutil
from passlib.hash import pbkdf2_sha256 as hashpwd
import time
import tempfile
from urllib.request import urlretrieve
from libAppRun import appRun
QString=type("")
QInt=type(0)
TAB_BTN_SIZE=96
BTN_SIZE=128
gettext.textdomain('runomatic')
_ = gettext.gettext

class appZone(QWidget):
	def __init__(self,parent):
		super (appZone,self).__init__(parent)
		self.setObjectName("appzone")
		self.wid=0

	def createZone(self,wid):
		zone=QtGui.QWindow()
		zone.show()
		self.wid=wid
		try:
			subZone=QtGui.QWindow.fromWinId(int(wid))
		except:
			pass
		zone=self.createWindowContainer(subZone,self,Qt.FramelessWindowHint)
		zone.show()
		zone.setParent(self)
		zone.setFocusPolicy(Qt.NoFocus)
		return(zone,self)
	#def createZone
#class appZone


class navButton(QPushButton):
	keypress=pyqtSignal("PyQt_PyObject")
	focusIn=pyqtSignal("PyQt_PyObject")
	def __init__(self,parent):
		super (navButton,self).__init__("",parent)
		self.keymap={}
		self.index=1
		a=QGridLayout()
		self.statusBar=QAnimatedStatusBar.QAnimatedStatusBar()
		self.statusBar.btn_close.hide()
		self.statusBar.setStateCss("error","border-radius:25px;background-color:qlineargradient(x1:110 y1:110,x2:0 y2:1,stop:0 rgba(0,110,110,0.2), stop:1 rgba(110,110,0,0.2));color:red;text-align:center;border:0px;font-size:36px;height:256px")
		self.cssError=("border-radius:25px;margin:0px;border:0px;text-decoration:none;text-align:center;background-image: url(../rsrc/blocked.png);background-position:center;background-repeat:no-repeat;color:white;font-size:%spx;min-width:%s;min-height:%s"%(BTN_SIZE,BTN_SIZE,BTN_SIZE-40))
		self.cssRun=("border-radius:25px;margin:0px;border:0px;text-decoration:none;text-align:center;background-color:rgba(255,0,0,0.6);color:white;font-size:%spx;min-height:%s"%(BTN_SIZE,BTN_SIZE-40))
		a.addWidget(self.statusBar,0,0,1,1)
		self.setLayout(a)
		for key,value in vars(Qt).items():
			if isinstance(value, Qt.Key):
				self.keymap[value]=key.partition('_')[2]
		self.modmap={
					Qt.ControlModifier: self.keymap[Qt.Key_Control],
					Qt.AltModifier: self.keymap[Qt.Key_Alt],
					Qt.ShiftModifier: self.keymap[Qt.Key_Shift],
					Qt.MetaModifier: self.keymap[Qt.Key_Meta],
					Qt.GroupSwitchModifier: self.keymap[Qt.Key_AltGr],
					Qt.KeypadModifier: self.keymap[Qt.Key_NumLock]
					}
		self.setObjectName("PushButton")
	#def __init__

	def enterEvent(self,event):
		self.statusBar.height_=self.height()
		if self.isEnabled():
			self.setFocus()
			self.focusIn.emit(self)
			self.resize(QSize(BTN_SIZE*1.2,BTN_SIZE*1.2))
			self.setIconSize(QSize(BTN_SIZE*1.2,BTN_SIZE*1.2))
	#def enterEvent
	
	def leaveEvent(self,event):
		if self.isEnabled():
			self.resize(QSize(BTN_SIZE,BTN_SIZE))
			self.setIconSize(QSize(BTN_SIZE,BTN_SIZE))
	#def leaveEvent

	def keyPressEvent(self,event):
		sw_mod=False
		keypressed=[]
		if (event.type()==QEvent.KeyPress):
			for modifier,text in self.modmap.items():
				if event.modifiers() & modifier:
					sw_mod=True
					keypressed.append(text)
			key=self.keymap.get(event.key(),event.text())
			if key not in keypressed:
				if sw_mod==True:
					sw_mod=False
				keypressed.append(key)
			if sw_mod==False:
				key=("+".join(keypressed))
		if key not in ("Alt","Control","Super_L"):
			self.keypress.emit(key)
		else:
				#Alt key is passed to parent. Parent then grabs the keyboard to prevent window switching 
				event.setAccepted(False)
	#def keyPressEvent
#class navButton

class runomatic(QWidget):
	update_signal=pyqtSignal("PyQt_PyObject")
	def __init__(self):
		super().__init__()
		self._plasmaMetaHotkey(enable=False,reconfigure=True)
		self.dbg=False
		exePath=sys.argv[0]
		if os.path.islink(sys.argv[0]):
			exePath=os.path.realpath(sys.argv[0])
		self.baseDir=os.path.abspath(os.path.dirname(exePath))
		signal.signal(signal.SIGUSR1,self._end_process)
		signal.signal(signal.SIGUSR2,self._fail_process)
		self.runoapps="/usr/share/runomatic/applications"
		self.launched=[]
		self.blocked=[]
		self.procMon=[]
		self.categories={}
		self.desktops={}
		self.pid=0
		self.app_icons={}
		self.tab_icons={}
		self.tab_id={}
		self.focusWidgets=[]
		self.appsWidgets=[]
		self.launchErr=False
		self.id=0
		self.firstLaunch=True
		self.currentTab=0
		self.currentBtn=0
		self.closeKey=False
		self.confKey=False
		self.keymap={}
		self.display=os.environ['DISPLAY']
		self.cache="%s/.cache/runomatic/"%os.environ['HOME']
		self.defaultBg="/usr/share/runomatic/rsrc/background2.png"
		self.username=getpass.getuser()
		self.runner=appRun()
		self._set_keymapping()
		self._read_config()
		self._plasmaMetaHotkey(enable=True)
		self._render_gui()
	#def init

	def _plasmaMetaHotkey(self,enable=None,reconfigure=None):
		env=os.environ.copy()
		cmd='kwriteconfig5 --file ~/.config/kwinrc --group ModifierOnlyShortcuts --key Meta "org.kde.plasmashell,/PlasmaShell,org.kde.PlasmaShell,activateLauncherMenu"'
		if enable==False:
			cmd='kwriteconfig5 --file ~/.config/kwinrc --group ModifierOnlyShortcuts --key Meta ""'
		try:
			a=subprocess.Popen(cmd,stdin=None,stdout=None,stderr=None,shell=True,env=env)
			a.wait()
		except Exception as e:
			self._debug("kwriteconfig: %s"%e)
		
		if reconfigure==True:
			try:
				cmd='qdbus org.kde.KWin /KWin reconfigure'
				a=subprocess.Popen(cmd,stdin=None,stdout=None,stderr=None,shell=True,env=env)
				a.wait()
			except Exception as e:
				self._debug("qdbus: %s"%e)

	def _fail_process(self,*args):
		self.launchErr=True
		self._debug("PROCESS %s FAILED TO LAUNCH"%args[0])
	#def _fail_process

	def _end_process(self,*args):
		for thread in self.runner.getDeadProcesses():
			idx=self._get_tabId_from_thread(thread)
			if idx and idx>0:
				if self.launchErr:
					self.blocked.append(self.tab_id[idx]['app'])
				self._on_tabRemove(idx)
				self.focusWidgets[self.currentBtn].index=None
				self.focusWidgets[self.currentBtn].statusBar.setText("")
				if self.launchErr:
					self.launchErr=False
					self.focusWidgets[self.currentBtn].statusBar.label.setStyleSheet(self.focusWidgets[self.currentBtn].cssError)
					self.focusWidgets[self.currentBtn].statusBar.show(state='error')
				#	self._on_tabSelect(0)
					self.focusWidgets[self.currentBtn].setFocus()
	#def _end_process

	def _debug(self,msg):
		if self.dbg:
			print("runomatic: %s"%msg)
	#def _debug

	def _set_keymapping(self):
		#Disable meta association within plasma. I've no eggs to capture and block this event in kde
		for key,value in vars(Qt).items():
			if isinstance(value, Qt.Key):
				self.keymap[value]=key.partition('_')[2]
		self.modmap={
					Qt.ControlModifier: self.keymap[Qt.Key_Control],
					Qt.AltModifier: self.keymap[Qt.Key_Alt],
					Qt.ShiftModifier: self.keymap[Qt.Key_Shift],
					Qt.MetaModifier: self.keymap[Qt.Key_Meta],
					Qt.GroupSwitchModifier: self.keymap[Qt.Key_AltGr],
					Qt.KeypadModifier: self.keymap[Qt.Key_NumLock]
					}
		self.sigmap_tabSelect=QSignalMapper(self)
		self.sigmap_tabSelect.mapped[QInt].connect(self._on_tabSelect)
		self.sigmap_tabRemove=QSignalMapper(self)
		self.sigmap_tabRemove.mapped[QInt].connect(self._on_tabRemove)
		#Shortcut for super_keys


	#def _set_keymapping

	def _read_config(self):
		data=self.runner.get_apps()
		self.categories=data.get('categories')
		self.desktops=data.get('desktops')
		self.keybinds=data.get('keybinds',{})
		self.password=data.get('password')
		self.close_on_exit=data.get('close',False)
		self.bg=data.get('background',self.defaultBg)
		if (not(os.path.isfile(self.bg))):
			self.bg=self.defaultBg
		self.runner.setBg(self.bg)
	#def _read_config(self):

	def _init_gui(self):
		self.setWindowFlags(Qt.FramelessWindowHint)
		self.setWindowFlags(Qt.X11BypassWindowManagerHint)
		self.setWindowState(Qt.WindowFullScreen)
		self.setWindowFlags(Qt.WindowStaysOnTopHint)
		self.setWindowModality(Qt.WindowModal)
		self.bg="/usr/share/runomatic/rsrc/background2.png"
		self.previousIcon=QtGui.QIcon.fromTheme("go-previous")
		self.previousIcon=QtGui.QIcon.fromTheme("go-home")
		btnPrevious=QPushButton()
		btnPrevious.setObjectName("PushButton")
		btnPrevious.setIcon(self.previousIcon)
		btnPrevious.setIconSize(QSize(TAB_BTN_SIZE,TAB_BTN_SIZE))
		self.sigmap_tabSelect.setMapping(btnPrevious,0)
		btnPrevious.clicked.connect(self.sigmap_tabSelect.map)
		self.homeIcon=QtGui.QIcon.fromTheme("go-home")
		btnHome=QPushButton()
		btnHome.setObjectName("PushButton")
		btnHome.setIcon(self.homeIcon)
		btnHome.setIconSize(QSize(TAB_BTN_SIZE,TAB_BTN_SIZE))
		self.tab_id[0]={'index':self.id,'thread':0,'xephyr':None,'wid':0,'show':btnHome,'close':btnPrevious,'display':"%s"%os.environ['DISPLAY']}
		self.closeIcon=QtGui.QIcon.fromTheme("window-close")
		self.grab=False
		self.setStyleSheet(self._define_css())
		monitor=QDesktopWidget().screenGeometry(1)
		self.move(monitor.left(),monitor.top())
		cursor=QtGui.QCursor(Qt.PointingHandCursor)
		self.setCursor(cursor)
		self.showFullScreen()
		#self.show()
	#def _init_gui(self):

	def _render_gui(self):
		#Enable transparent window
#		self.setStyleSheet('background:transparent')
#		self.setAttribute(Qt.WA_TranslucentBackground)
		####
		def launchConf():
				try:
					if os.path.isfile("%s/runoconfig.py"%self.baseDir):
						if self.close():
							os.execv("%s/runoconfig.py"%self.baseDir,["1"])
					else:
						self.showMessage(_("runoconfig not found at %s"%self.baseDir),"error2",20)
				except:
					print(_("runoconfig not found"))
		self._init_gui()
		self.box=QGridLayout()
		self.statusBar=QAnimatedStatusBar.QAnimatedStatusBar()
		self.statusBar.setStateCss("error","background-color:qlineargradient(x1:0 y1:0,x2:0 y2:1,stop:0 rgba(255,255,0,1), stop:1 rgba(255,0,0,0.6));text-decoration:none;color:white;text-align:center;font-size:128px;height:256px")
		self.statusBar.setStateCss("error2","background-color:qlineargradient(x1:0 y1:0,x2:0 y2:1,stop:0 rgba(255,0,0,1), stop:1 rgba(255,0,0,0.6));color:white;text-align:center;text-decoration:none;font-size:12px;height:20px")
		self.statusBar.height_=152
		self.box.addWidget(self.statusBar,0,0,1,2)
		self.tabBar=self._tabBar()
		self.setObjectName("tabbar")
#		self.tabBar.setAttribute(Qt.WA_TranslucentBackground)
		self.tabBar.currentChanged.connect(lambda:self._on_tabChanged(False))
		self.box.addWidget(self.tabBar,0,0,1,1)
		self.setLayout(self.box)
		self.tabBar.setFocusPolicy(Qt.NoFocus)
		if self.focusWidgets:
			self._set_focus("")
		else:
			wdg=QWidget()
			lyt=QVBoxLayout()
			wdg.setLayout(lyt)
			lbl=QLabel(_("There's no launchers to show.\nDid you run the configure app?"))
			lyt.addWidget(lbl)
			btn=QPushButton(_("Launch configuration app"))
			btn.clicked.connect(launchConf)
			lyt.addWidget(btn)
			self.box.addWidget(wdg,0,0,1,1,Qt.AlignCenter)
	#def _render_gui

	def closeEvent(self,event):
		if self.password:
			text=_("Insert the password")
			if self.close_on_exit==True:
				text=_("Insert the password. Current session will also be closed.")
			pwd,resp=QInputDialog.getText(self,_("Confirm close"),text,QLineEdit.Password)
			if resp:
				if not hashpwd.verify(pwd,self.password):
					event.ignore()
			else:
				event.ignore()
		self._plasmaMetaHotkey(reconfigure=True)
		for index in self.tab_id.keys():
			if index:
				th=self.tab_id[index].get('thread',None)
				if th:
					self.runner.send_signal_to_thread("kill",th)
				xe=self.tab_id[index].get('xephyr',None)
				if xe:
					self.runner.send_signal_to_thread("kill",xe)
				dsp=self.tab_id[index].get('display',None)
				if dsp:
					self.runner.stop_display(self.tab_id[index].get('wid',''),dsp)
					xlockFile=os.path.join("/tmp",".X%s-lock"%dsp.replace(":",""))
					if os.path.isfile(xlockFile):
						os.remove(xlockFile)
		if str(self.close_on_exit).lower()=='true':
			print("Closing session...")
			subprocess.run(["loginctl","terminate-user","%s"%self.username])
	#def closeEvent

	def keyPressEvent(self,event):
		key=self.keymap.get(event.key(),event.text())
		if key in ("Alt" ,"Super_L"):
			self.grab=True
		self.grabKeyboard()
	#def eventFilter
	
	def keyReleaseEvent(self,event):
		key=self.keymap.get(event.key(),event.text())
		confKey=''
		if self.keybinds:
			confKey=self.keybinds.get('conf',None)
		if key not in ('Tab','Super_L'):
			if key=='F4' and self.grab:
				self.closeKey=True
			elif key==confKey:
				if os.path.isfile("%s/runoconfig.py"%self.baseDir):
					if self.close():
						os.execv("%s/runoconfig.py"%self.baseDir,["1"])
				else:
					event.ignore()
					self.showMessage(_("runoconfig not found"),"error2",20)
			elif key.isdigit():
				if int(key)<=self.tabBar.count():
					self._on_tabSelect(int(key),True)
					cont=0
					for btn in self.focusWidgets:
						if btn.statusBar.label.text()==key:
							self.currentBtn=cont
							self.focusWidgets[cont].setFocus()
						cont+=1
				else:
					event.ignore()
			self.releaseKeyboard()
		if key in ('Alt','Control','Super_L'):
			if key!='Super_L':
				self.releaseKeyboard()
			else:
				event.setAccepted(True)
				self._on_tabSelect(0,True)
				event.accept()
			self.grab=False
			if key=='Alt':
				if self.closeKey:
					self.closeKey=False
					self.close()
				if self.confKey:
					self.confKey=False
	#def keyReleaseEvent

	def _set_focus(self,key):
		cursor=QtGui.QCursor(Qt.PointingHandCursor)
		self.setCursor(cursor)
		self.grabMouse()
		#cursor.setPos(50,50)
		self.releaseMouse()
		if key=="Space" or key=="NumLock+Enter" or key=="Return":
			self.focusWidgets[self.currentBtn].clicked.emit()
		elif key=="Tab":
			tabCount=self.tabBar.count()
			newTab=self.tabBar.currentIndex()+1
			if newTab>tabCount:
				newTab=0
			self.tabBar.setCurrentIndex(newTab)
		if key=="Alt":
			return(True)

		else:
			self.focusWidgets[self.currentBtn].resize(QSize(BTN_SIZE,BTN_SIZE))
			self.focusWidgets[self.currentBtn].setIconSize(QSize(BTN_SIZE,BTN_SIZE))
			if key=="Left":
				self.currentBtn+=1
				if self.currentBtn>=len(self.focusWidgets):
					self.currentBtn=0
			elif key=="Right":
				self.currentBtn-=1
				if self.currentBtn<0:
					self.currentBtn=len(self.focusWidgets)-1
			elif key=="Up":
				currentBtn=self.currentBtn
				currentBtn-=self.maxCol
				if currentBtn<0:
					currentBtn=self.currentBtn
				self.currentBtn=currentBtn
			elif key=="Down":
				currentBtn=self.currentBtn
				currentBtn+=self.maxCol
				if currentBtn>=len(self.focusWidgets):
					currentBtn=self.currentBtn
				self.currentBtn=currentBtn
			self.focusWidgets[self.currentBtn].setFocus()
			self._debug("Focus to %s"%self.focusWidgets[self.currentBtn])
			self.focusWidgets[self.currentBtn].resize(QSize(BTN_SIZE*1.2,BTN_SIZE*1.2))
			self.focusWidgets[self.currentBtn].setIconSize(QSize(BTN_SIZE*1.2,BTN_SIZE*1.2))
	#def _set_focus(self,key):

	def _get_focus(self,widget):
		self.currentBtn=self.focusWidgets.index(widget)
	#def _get_focus(self,widget)

	def _add_widgets(self,vbox,apps):
		row=int(len(self.appsWidgets)/self.maxCol)
		col=(self.maxCol*(row+1))-len(self.appsWidgets)
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self._launch)
		for appName,data in apps.items():
			appIcon=data['Icon']
			appDesc=data['Name']
			if QtGui.QIcon.hasThemeIcon(appIcon):
				icnApp=QtGui.QIcon.fromTheme(appIcon)
			elif os.path.isfile(appIcon):
					iconPixmap=QtGui.QPixmap(appIcon)
					scaledIcon=iconPixmap.scaled(QSize(BTN_SIZE*1.2,BTN_SIZE*1.2))
					icnApp=QtGui.QIcon(scaledIcon)
			elif appIcon.startswith("http"):
				if not os.path.isdir("%s/icons"%self.cache):
					os.makedirs("%s/icons"%self.cache)
				tmpfile=os.path.join("%s/icons"%self.cache,appIcon.split("/")[2].split(".")[0])
				if not os.path.isfile(tmpfile):
					try:
						urlretrieve(appIcon,tmpfile)
					except:
						tmpfile=QtGui.QIcon.fromTheme("shell")
				iconPixmap=QtGui.QPixmap(tmpfile)
				scaledIcon=iconPixmap.scaled(QSize(BTN_SIZE*1.2,BTN_SIZE*1.2))
				icnApp=QtGui.QIcon(scaledIcon)
				appIcon=tmpfile
			else:
				continue
			if not appName:
				continue
			self.app_icons[appName]=appIcon
			self._debug("Adding %s"%appName)
			btnApp=navButton(self)
			btnApp.setIcon(icnApp)
			btnApp.setIconSize(QSize(BTN_SIZE,BTN_SIZE))
			btnApp.setToolTip(appDesc)
			btnApp.setFocusPolicy(Qt.NoFocus)
			btnApp.keypress.connect(self._set_focus)
			btnApp.focusIn.connect(self._get_focus)
			self.focusWidgets.append(btnApp)
			self.appsWidgets.append(appName)
			sigmap_run.setMapping(btnApp,appName)
			btnApp.clicked.connect(sigmap_run.map)
			vbox.addWidget(btnApp,row,col,Qt.Alignment(-1))
			col+=1
			if col==self.maxCol:
				col=0
				row+=1
	#def _add_widgets
	
	def _tabBar(self):
		tabBar=QTabWidget()
		tabScroll=QWidget()
		tabScroll.setObjectName("scroll")
		tabScroll.setStyleSheet("#scroll{background-image:url('%s');}"%self.bg)
		tabScroll.setFocusPolicy(Qt.NoFocus)
		scrollArea=QScrollArea(tabScroll)
		scrollArea.setFocusPolicy(Qt.NoFocus)
		tabContent=QWidget()
		vbox=QGridLayout()
		scr=app.primaryScreen()
		w=scr.size().width()-BTN_SIZE
		h=scr.size().height()-(2*BTN_SIZE)
		self.maxCol=int(w/BTN_SIZE)-3
		self._debug("Size: %s\nCols: %s"%(self.width(),self.maxCol))
		for desktop in self.desktops:
			apps=self._get_desktop_apps(desktop)
			self._add_widgets(vbox,apps)

		tabContent.setLayout(vbox)
		scrollArea.setWidget(tabContent)
		scrollArea.setObjectName("launcher")
		scrollArea.alignment()
		tabBar.addTab(tabScroll,"")
		tabBar.tabBar().setTabButton(0,QTabBar.LeftSide,self.tab_id[0]['show'])
		tabBar.tabBar().tabButton(0,QTabBar.LeftSide).setFocusPolicy(Qt.NoFocus)
		scrollArea.setGeometry(QRect(0,0,w,h))
		tabBar.setObjectName("tabbar")
		return (tabBar)
	#def _tabBar

	def _on_tabChanged(self,remove=True):
		self._debug("From Tab: %s"%self.currentTab)
		index=self._get_tabId_from_index(self.currentTab)
		self._debug("Tab Index: %s"%index)
		key='show'
		if self.currentTab==0:
			index=0
			key='close'
		self.tabBar.tabBar().setTabButton(self.currentTab,QTabBar.LeftSide,self.tab_id[index][key])
		self._debug("Pressed: %s"%self.tab_id[index][key])
		try:
			self.tabBar.tabBar().tabButton(self.currentTab,QTabBar.LeftSide).setFocusPolicy(Qt.NoFocus)
		except:
			pass
		self.runner.send_signal_to_thread("stop",self.tab_id[index]['thread'])
		index=self._get_tabId_from_index(self.tabBar.currentIndex())
		self.currentTab=self.tabBar.currentIndex()
		key='close'
		if self.currentTab==0:
			self.focusWidgets[self.currentBtn].setFocus()
			index=0
			key='show'
		self._debug("New Tab Index: %s"%self.tab_id[index])
		self._debug("New index: %s"%index)
		self._debug("Btn: %s"%self.tab_id[index][key])
		self.tabBar.tabBar().setTabButton(self.currentTab,QTabBar.LeftSide,self.tab_id[index][key])
		self.tabBar.tabBar().tabButton(self.currentTab,QTabBar.LeftSide).setFocusPolicy(Qt.NoFocus)
		self.runner.send_signal_to_thread("cont",self.tab_id[index]['thread'])
		#os.environ['DISPLAY']=self.tab_id[index]['display']
		self._debug("New Current Tab: %s Icon:%s"%(self.currentTab,key))
	#def _on_tabChanged

	def _on_tabSelect(self,index,btn=None):
		self._debug("Select tab: %s"%index)
		if btn:
			index=self._get_tabId_from_index(index)
		self.tabBar.setCurrentIndex(self.tab_id[index]['index'])
		cursor=QtGui.QCursor()
		self.setCursor(cursor)
		cursor.setPos(300,300)
	#def _on_tabSelect

	def _on_tabRemove(self,index):
		self._debug("Remove tab: %s"%index)
		self.tabBar.blockSignals(True)
		self.tabBar.removeTab(self.tab_id[index]['index'])

		xlockFile=os.path.join("/tmp",".X%s-lock"%self.tab_id[index]['display'].replace(":",""))
		if os.path.isfile(xlockFile):
			os.remove(xlockFile)
		if (self.tab_id[index].get('app',"") in self.launched):
			self.launched.remove(self.tab_id[index]['app'])
		for idx in range(index+1,len(self.tab_id)):
			if idx in self.tab_id.keys():
				self._debug("Tab Array: %s"%self.tab_id)
				if 'index' in self.tab_id[idx].keys():
					self._debug("Reasign %s"%(self.tab_id[idx]['index']))
					self.tab_id[idx]['index']=self.tab_id[idx]['index']-1
					self.focusWidgets[self.appsWidgets.index(self.tab_id[idx]['app'])].statusBar.setText(str(self.tab_id[idx]['index']))
					self.focusWidgets[self.appsWidgets.index(self.tab_id[idx]['app'])].index=self.tab_id[idx]['index']
					self._debug("Reasigned %s -> %s"%(idx,self.tab_id[idx]['index']))
		th=self.tab_id[index].get('thread',None)
		if th:
			self.runner.send_signal_to_thread("term",th)
		xe=self.tab_id[index].get('xephyr',None)
		if xe:
			self.runner.send_signal_to_thread("term",xe)
		dsp=self.tab_id[index].get('display',None)
		self.focusWidgets[self.appsWidgets.index(self.tab_id[index]['app'])].statusBar.hide()
		if dsp:
			self.runner.stop_display(self.tab_id[index].get('wid',''),dsp)
			xlockFile=os.path.join("/tmp",".X%s-lock"%dsp.replace(":",""))
			if os.path.isfile(xlockFile):
				os.remove(xlockFile)
		self.tab_id[index]={}
		if self.launchErr:
			self.currentTab=self._get_tabId_from_index(0)
		else:
			self.currentTab=self._get_tabId_from_index(self.tabBar.currentIndex())
		index=self.currentTab
		self._debug("New tab: %s"%self.currentTab)
		self._on_tabChanged()
		self.tabBar.blockSignals(False)
		self.tabBar.setFocus()
		self.tabBar.setCurrentIndex(index)
		self._debug("Removed tab: %s"%index)
	#def _on_tabRemove

	def _get_category_apps(self,category):
		apps=self.runner.get_category_apps(category.lower())
		return (apps)
	#def _get_category_apps
	
	def _get_desktop_apps(self,desktop):
		#Check if desktop is from run-o-matic
		if "run-o-matic" in self.categories:
			if os.path.isdir(self.runoapps):
				if desktop in os.listdir(self.runoapps):
					desktop=os.path.join(self.runoapps,desktop)
		apps=self.runner.get_desktop_app(desktop,True)
		return (apps)
	#def _get_category_apps

	def _launchZone(self,app):
		tabContent=QWidget()
		box=QVBoxLayout()
		wid=self.runner.get_wid("Xephyr on",self.display)
		self._debug("Window Wid: %s"%wid)
		zone=None
		if wid:
			(zone,zone_window)=appZone(tabContent).createZone(wid)
			zone.setObjectName("appzone")

		if not zone or not wid:
			self._debug("Xephyr failed to launch")
			tabContent.destroy()
			wid=None
		else:
			box.addWidget(zone)
			zone.setFocusPolicy(Qt.NoFocus)
			tabContent.setLayout(box)
			icn=QtGui.QIcon.fromTheme(self.app_icons[app])
			btn=QPushButton()
			btn.setObjectName("PushButton")
			btn.setIconSize(QSize(TAB_BTN_SIZE,TAB_BTN_SIZE))
			btn.setIcon(icn)
			self.id+=1
			self._debug("New Tab id %s"%self.id)
			self.sigmap_tabSelect.setMapping(btn,self.id)
			btn.clicked.connect(self.sigmap_tabSelect.map)
			btn_close=QPushButton()
			btn_close.setObjectName("PushButton")
			btn_close.setIcon(self.closeIcon)
			btn_close.setIconSize(QSize(TAB_BTN_SIZE,TAB_BTN_SIZE))
			self.sigmap_tabRemove.setMapping(btn_close,self.id)
			btn_close.clicked.connect(self.sigmap_tabRemove.map)
			self.tab_id[self.id]={'index':self.tabBar.count(),'thread':None,'wid':zone_window,'show':btn,'close':btn_close,'display':self.display}

			self.tabBar.addTab(tabContent,"")

		return(wid)
	#def _launchZone

	def _launch(self,app):
		if app in self.launched:
			self._on_tabSelect(self.focusWidgets[self.appsWidgets.index(app)].index,True)
			return
		if app in self.blocked:
			return
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		self.grabMouse()
		self.tabBar.setTabIcon(0,self.previousIcon)
		self._debug("Tab count: %s"%self.tabBar.count())
		#Tabs BEFORE new tab is added
		tabCount=self.tabBar.count()
		btn=None
		try:
			btn=self.appsWidgets.index(app)	
		except:
			btn=None
		if btn:
			self.currentBtn=btn

		os.environ["HOME"]="/home/%s"%self.username
		os.environ["XAUTHORITY"]="/home/%s/.Xauthority"%self.username
		self.display,self.pid,x_pid=self.runner.new_Xephyr(self.tabBar)
		if self._launchZone(app):
			self.tab_id[self.id]['thread']=self.runner.launch(app,self.display)
			self.tab_id[self.id]['xephyr']=x_pid
			self.tab_id[self.id]['app']=app
			self.launched.append(app)
		else:
			if self.pid:
				self.runner.send_signal_to_thread("kill",self.pid)
			cursor=QtGui.QCursor(Qt.PointingHandCursor)
			self.setCursor(cursor)
			self.releaseMouse()
			return
		self.tabBar.setCurrentIndex(tabCount)
		self.focusWidgets[self.appsWidgets.index(app)].index=tabCount
		self.focusWidgets[self.appsWidgets.index(app)].statusBar.setText(str(tabCount))
		self.focusWidgets[self.appsWidgets.index(app)].statusBar.label.setStyleSheet(self.focusWidgets[self.currentBtn].cssRun)
		self.focusWidgets[self.appsWidgets.index(app)].statusBar.show(state='error')
		cursor=QtGui.QCursor(Qt.PointingHandCursor)
		self.releaseMouse()
		self.setEnabled(True)
		self.setCursor(cursor)
		self.focusWidgets[self.appsWidgets.index(app)].setEnabled(True)
	#def _launch

	def _get_tabId_from_index(self,index):
		idx=index
		self._debug("Search id for display: %s"%(index))
		self._debug("Current id: %s"%(self.tab_id))
		for key,data in self.tab_id.items():
			if 'index' in data.keys():
				if index==data['index']:
					idx=key
					break
		self._debug("Found tab idx: %s For selected index: %s"%(idx,index))
		return idx
	#def _get_tabId_from_index
	
	def _get_tabId_from_thread(self,thread):
		idx=-1
		self._debug("Search id for thread: %s"%(thread))
		self._debug("Current id: %s"%(self.tab_id))
		for key,data in self.tab_id.items():
			if 'thread' in data.keys():
				if thread==data['thread']:
					idx=key
					break
		self._debug("Found idx: %s For thread: %s"%(idx,thread))
		return idx
	#def _get_tabId_from_thread
	
	def showMessage(self,msg,status="error",height=252):
		return()
		self.statusBar.height_=height
		self.statusBar.setText(msg)
		if status:
			self.statusBar.show(state=status)
		else:
			self.statusBar.show(state=None)
	#def _show_message

	def _define_css(self):
		css="""
		#PushButton{
			padding:10px;
			margin:0px;
			border:0px;
			background-color:transparent;
		}
		#PushButton:active{
			font: 14px Roboto;
			color:black;
			background:none;
			background-color:transparent;
		}	
		#PushButton:focus{
			background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 silver,stop:1 white);
			border-radius:25px;
		}
		#launcher{
			background-repeat:no-repeat;
			background-position:center;
			border:0px solid red;

		}
		#appzone{
			background-color:transparent;
			border:10px solid red;
		}
		"""
		self._debug("Setting background: %s"%self.bg)
		return(css)
		#def _define_css
#class runomatic

app=QApplication(["Run-O-Matic"])
runomaticLauncher=runomatic()
app.exec_()

