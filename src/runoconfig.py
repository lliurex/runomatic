#!/usr/bin/python3
import sys
import os,shutil
from PySide6.QtWidgets import QApplication
from QtExtraWidgets import QStackedWindow

oldUser="{}/.config/runomatic.conf".format(os.environ.get('HOME'))
if os.path.isfile(oldUser):
	newUser="{}/.config/runomatic/runomatic.conf".format(os.environ.get('HOME'))
	if os.path.isdir(os.path.dirname(newUser))==False:
		os.makedirs(os.path.dirname(newUser))
	if os.path.isfile(newUser)==False:
		shutil.move(oldUser,newUser)

app=QApplication(["Run-O-Matic"])
config=QStackedWindow()
if os.path.islink(__file__)==True:
	abspath=os.path.join(os.path.dirname(__file__),os.path.dirname(os.readlink(__file__)))
else:
	abspath=os.path.dirname(__file__)
config.addStacksFromFolder(os.path.join(abspath,"stacks"))
config.setBanner("/usr/share/runoconfig/rsrc/runoconfig_banner.png")
#config.setWiki("https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Repoman-en-Lliurex-21")
config.setIcon("runoconfig")
config.show()
config.setMinimumWidth(config.sizeHint().width()*1.6)
config.setMinimumHeight(config.sizeHint().width()*0.9)
app.exec()

