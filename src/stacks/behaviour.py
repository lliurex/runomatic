#!/usr/bin/python3
import sys
import os
import base64
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QFileDialog
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize
#from appconfig.appConfigStack import appConfigStack as confStack
from appconfig import manager
from QtExtraWidgets import QStackedWindowItem

import gettext
_ = gettext.gettext

i18n={"MENU":_("App behaviour"),
	"DESC":_("Set app behaviour"),
	"TOOLTIP":_("From here you can change background, start and exit options...")
	}

class behaviour(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("confApp Load")
		self.setProps(shortDesc=i18n["MENU"],
			longDesc=i18n["DESC"],
			icon="document-new",
			tooltip=_("Add custom repositories"),
			index=1,
			visible=True)
		self.bg="/usr/share/runomatic/rsrc/background2.png"
		self.defaultBg="/usr/share/runomatic/rsrc/background2.png"
		self.manager=manager.manager(name="runoconfig.json",relativepath="runoconfig")
		self.enabled=True
		self.level='user'
	#def __init__
	
	def __initScreen__(self):
		def _change_osh():
			idx=self.cmb_level.currentIndex()
			#if idx==0:
			#	lbl_help.setText(_("The config will be applied per user"))
			#elif idx==1:
			#	lbl_help.setText(_("The config will be applied to all users"))
			#elif idx==2:
			#	lbl_help.setText(_("The config will be applied to all users and clients"))
			self.fakeUpdate()
		box=QVBoxLayout()
		lbl_txt=QLabel(_("Choose the config level that should use the app"))
		lbl_txt.setAlignment(Qt.AlignTop)
		#box.addWidget(lbl_txt,0)
		wdg_level=QWidget()
		hbox=QHBoxLayout()
		lbl_help=QLabel(_("The config will be applied per"))
		hbox.addWidget(lbl_help,0,Qt.AlignTop)
		self.cmb_level=QComboBox()
		self.cmb_level.addItem(_("User"))
		self.cmb_level.addItem(_("System"))
		#self.cmb_level.addItem(_("N4d"))
		self.cmb_level.activated.connect(_change_osh)
		self.cmb_level.setFixedWidth(100)
		hbox.addWidget(self.cmb_level,1,Qt.AlignLeft)
		wdg_level.setLayout(hbox)
		box.addWidget(wdg_level,1,Qt.AlignLeft)
		#box.addWidget(QLabel(_("Session settings")),1,Qt.AlignTop)
		self.chk_startup=QCheckBox(_("Launch at startup"))
		box.addWidget(self.chk_startup,1)
		self.chk_close=QCheckBox(_("Close session when application exits"))
		box.addWidget(self.chk_close,2)
		self.lbl_warning=QLabel(_("For session closing it's mandatory a keybind for launch configuration within run-o-matic"))
		self.lbl_warning.setWordWrap(True)
		box.addWidget(self.lbl_warning,3,Qt.AlignTop)
		self.lbl_warning.setVisible(False)
		self.lbl_warning.setEnabled(False)
		lbl_img=QLabel(_("Choose the background image"))
		box.addWidget(lbl_img,Qt.AlignTop)
		icn=QtGui.QIcon(self.bg)
		self.btn_img=QPushButton()
		self.btn_img.setStyleSheet("border:1px solid black;")
		self.btn_img.clicked.connect(self._setBg)
		self.btn_img.setIcon(icn)
		self.btn_img.setIconSize(QSize(102,76))
		box.addWidget(self.btn_img,Qt.AlignTop)
		self.setLayout(box)
		_change_osh()
		#self.updateScreen()
		return(self)
	#def _load_screen

	def fakeUpdate(self):
		idx=self.cmb_level.currentIndex()
		level='user'
		if idx==0:
			level='user'
		elif idx==1:
			level='system'
		elif idx==2:
			level='n4d'
		config=self.manager.getConfig()
		#Block close session if there's no keybind for config
		keybind=config.get(level,{}).get('keybinds',{}).get('conf','')
		if keybind.strip()=="":
			self.chk_close.setEnabled(False)
			self.lbl_warning.setVisible(True)
		else:
			self.chk_close.setEnabled(True)
			self.lbl_warning.setVisible(False)
		#Set state
		close=False
		if level in config.keys():
			close=config[level].get('close',False)
		if close:
			if str(close).lower()=='true':
				close=True
			else:
				close=False
		try:
			self.chk_close.setChecked(close)
		except:
			pass
		startup=config.get(level,{}).get('startup',False)
		if startup:
			if str(startup).lower()=='true':
				startup=True
			else:
				startup=False
		try:
			self.chk_startup.setChecked(startup)
		except:
			pass

		self.bg=config.get(level,{}).get('background',self.defaultBg)
		if os.path.isfile(self.bg):
			icon=QtGui.QIcon(self.bg)
			self.btn_img.setIcon(icon)
	#def fakeUpdate

	def updateScreen(self):
		self.refresh=True
		self.changes=True
		self.level="user"
		config=self.manager.getConfig()
		if self.level:
			idx=0
			if self.level.lower()=='system':
				idx=1
			elif self.level.lower()=='n4d':
				idx=2
			self.cmb_level.setCurrentIndex(idx)
			self.cmb_level.activated.emit(idx)
		if self.level not in config.keys():
			config[self.level]={}
		#Block close session if there's no keybind for config
		keybind=config.get(self.level,{}).get('keybinds',{}).get('conf','')
		if keybind.strip()=="":
			self.chk_close.setEnabled(False)
			self.lbl_warning.setVisible(True)
		else:
			self.chk_close.setEnabled(True)
			self.lbl_warning.setVisible(False)
		#Set state
		close=config[self.level].get('close',False)
		if close:
			if str(close).lower()=='true':
				close=True
			else:
				close=False
		self.chk_close.setChecked(close)
		startup=config.get(self.level,{}).get('startup',False)
		if startup:
			if str(startup).lower()=='true':
				startup=True
			else:
				startup=False
		self.chk_startup.setChecked(startup)
		bg=config.get(self.level,{}).get('background',self.defaultBg)
		if bg:
			if not os.path.isfile(bg):
				imgName=config.get(self.level,{}).get('background',"generic.png")
				bg="%s/.config/runomatic/backgrounds/%s"%(os.environ['HOME'],os.path.basename(imgName))
				if not os.path.isfile(bg):
					if config.get(self.level,{}).get("background64"):
						if not os.path.isdir("%s/.config/runomatic/backgrounds"%os.environ['HOME']):
							os.makedirs("%s/.config/runomatic/backgrounds"%os.environ['HOME'])
						with open(bg,"wb") as f:
							f.write(base64.decodebytes(config.get(self.level,{}).get('background64','').encode("utf-8")))
				config[self.level]['background']=bg
			icon=QtGui.QIcon(bg)
			self.btn_img.setIcon(icon)
	#def _udpate_screen

	def _setBgDlg(self):
		self._debug("Changing background")
		fdia=QFileDialog()
		fchoosed=''
		fdia.setFileMode(QFileDialog.AnyFile)
		if os.path.isdir("/usr/share/lliurex/pixmaps/lliurex_art/stamps"):
			fdia.setDirectory("/usr/share/lliurex/pixmaps/lliurex_art/stamps")
		else:
			fdia.setDirectory("/usr/share/wallpapers")
		fdia.setNameFilter(_("images(*.png *.svg *jpg *bmp)"))
		if (fdia.exec_()):
			fchoosed=fdia.selectedFiles()[0]
			self.bg=fdia.selectedFiles()[0]
			icn=QtGui.QIcon(self.bg)
			self.btn_img.setIcon(icn)
		return(fchoosed)
	#def _setBg(self)

	def _setBg(self):
		if self._setBgDlg()!='':
			self.force_change=True
			self.setChanged(True)
	#def _setBg(self)

	def _setAutostart(self,enable):
		desktopFile="runomatic.desktop"
		desktopSystemPath="/usr/share/applications"
		desktopUserPath=os.path.join(os.environ.get('HOME'),".config/autostart")
		if enable==True:
			desktopPath=os.path.join(desktopSystemPath,desktopFile)
			if os.path.isfile(desktopPath):
				with open (desktopPath,'r') as f:
					flines=f.readlines()
				desktopPath=os.path.join(desktopUserPath,desktopFile)
				if os.path.isdir(desktopUserPath)==False:
					os.makedirs(desktopUserPath)
				with open (desktopPath,'w') as f:
					f.writelines(flines)
		else:
			desktopPath=os.path.join(desktopUserPath,desktopFile)
			if os.path.isfile(desktopPath):
				os.remove(desktopPath)
	#def _setAutostart(self,enable):
	
	def writeConfig(self):
		level=self.level
		idx=self.cmb_level.currentIndex()
		if idx==0:
			configLevel='user'
		elif idx==1:
			configLevel='system'
		elif idx==2:
			configLevel='n4d'

		#Block n4d 
		#if configLevel!='system':
		#	configLevel='user'

		if configLevel!=level:
			if not self.saveChanges('config',configLevel,'system'):
				#If write fails revert to old config level
				self.saveChanges('config',level,'system')
			else:
				return()
		startup=self.chk_startup.isChecked()
		self._setAutostart(startup)
		self.saveChanges('startup',startup)
		close=self.chk_close.isChecked()
		self.saveChanges('close',close)
		self.saveChanges('background',self.bg)
		with open(self.bg,"rb") as img:
			if self.saveChanges('background64',base64.b64encode(img.read()).decode("utf-8"))==False:
				self.showMsg("Failed to write config")
	#def writeConfig

