#!/usr/bin/python3
import sys
import os
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout
from PySide6 import QtGui
from PySide6.QtCore import Qt
from passlib.hash import pbkdf2_sha256 as hashpwd
#from appconfig.appConfigStack import appConfigStack as confStack
from QtExtraWidgets import QStackedWindowItem
from appconfig import manager
import gettext
_ = gettext.gettext

i18n={"MENU":_("Master password"),
	"DESC":_("Set a master password"),
	"TOOLTIP":_("The master password let the user close or configure runomatic")
	}

class password(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self.setProps(shortDesc=i18n["MENU"],
			longDesc=i18n["DESC"],
			icon="document-new",
			tooltip=_("Add custom repositories"),
			index=5,
			visible=True)
		self.icon=('dialog-password')
		self.enabled=True
		self.level='user'
	
	def _debug(self,msg):
		if self.dbg:
			print("ConfPass: %s"%msg)
	#def _debug

	def __initScreen__(self):
		self.txt_pass=QLineEdit()
		self.txt_pass.setEchoMode(QLineEdit.Password)
		self.txt_pass.setPlaceholderText(_("Password"))
		self.txt_pass2=QLineEdit()
		self.txt_pass2.setPlaceholderText(_("Repeat password"))
		self.txt_pass2.setEchoMode(QLineEdit.Password)
		box=QVBoxLayout()
		lbl_txt=QLabel(_("If a master password is set then the app will prompt for it to exit"))
		lbl_txt.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_txt,1)
		box.addWidget(self.txt_pass,1,Qt.AlignBottom)
		box.addWidget(self.txt_pass2,2,Qt.AlignTop)
		self.setLayout(box)
	
	def writeConfig(self):
		pwd=self.txt_pass.text()
		if pwd==self.txt_pass2.text() and pwd.replace(' ','')!='':
			pwd=hashpwd.hash(pwd)
			key='password'
			self.saveChanges(key,pwd)
		elif pwd==self.txt_pass2.text:
			self._debug("Password don't match")
			self.showMsg(_("Passwords don't match"))
		else:
			self._debug("Blank Password")
			self.showMsg(_("Password is empty"))
	#def _save_apps

	def updateScreen(self):
		self.txt_pass.setText('')
		self.txt_pass2.setText('')
	#def updateScreen
