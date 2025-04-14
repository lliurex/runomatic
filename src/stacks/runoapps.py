#!/usr/bin/python3
import os
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,\
				QDialog,QGridLayout,QHBoxLayout,QFormLayout,QLineEdit,QComboBox,\
				QStatusBar,QFileDialog,QDialogButtonBox,QScrollBar,QScrollArea,QListWidget,\
				QListWidgetItem,QStackedWidget,QButtonGroup,QComboBox,QTableWidget,QTableWidgetItem,\
				QHeaderView,QMenu,QCompleter,QAbstractItemView
from PySide6 import QtGui
from PySide6.QtCore import QPoint,QSize,Slot,Qt, QPropertyAnimation,QThread,QRect,QTimer,Signal,QSignalMapper,QProcess,QEvent,QMimeData
from libAppRun import appRun
from app2menu import App2Menu
from appconfig.manager import manager
from QtExtraWidgets import QStackedWindowItem
import tempfile
from urllib.request import urlretrieve
import gettext
_ = gettext.gettext

QString=type("")
QBool=type(True)
BTN_SIZE_FULL=128
BTN_SIZE=32


class desktopChooser(QDialog):
	dblClicked=Signal("PyObject")
	def __init__(self,parent):
		super (desktopChooser,self).__init__(parent)
		self.parent=parent
		self.menu=App2Menu.app2menu()
		self.setWindowTitle(_("Launcher select"))
		self.setModal(False)
		self.desktopList=QListWidget()
		self.desktopList.setSortingEnabled(True)
		self.desktopList.setDragEnabled(True)
		self.desktopList.setAcceptDrops(True)
		self.desktopList.setSpacing(3)
		self.desktopList.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.desktopList.itemDoubleClicked.connect(self._dblClick)
		self.desktopList.itemPressed.connect(self._loadMime)
		self.data={}
		self._renderGui()
	#def __init__
	
	def _renderGui(self):
		def searchList():
			items=self.desktopList.findItems(inp_search.text(),Qt.MatchFlag.MatchContains)
			if items:
				self.desktopList.scrollToItem(items[0])
				self.desktopList.setCurrentItem(items[0])

		box=QVBoxLayout()
		inp_search=QLineEdit()
		inp_search.setPlaceholderText(_("Search"))
		inp_search.textChanged.connect(searchList)
		completer=QCompleter()
		completer.setCaseSensitivity(Qt.CaseInsensitive)
		model=QtGui.QStandardItemModel()
		#Load available desktops
		desktopDict=self._getDesktops(model)
		cont=0
		for desktop in sorted(desktopDict.keys(),key=str.lower):
			self.data[cont]={'path':os.path.join(self.menu.desktoppath,desktopDict[desktop].get('desktop')),'icon':desktopDict[desktop].get('icon','')}
			cont+=1
		completer.setModel(model)
		inp_search.setCompleter(completer)
		box.addWidget(inp_search)
		box.addWidget(self.desktopList)
		btnClose=QPushButton(_("Close"))
		btnClose.clicked.connect(self.close)
		box.addWidget(btnClose)
		self.setLayout(box)
	#def _renderGui

	def _getDesktops(self,model):
		desktopDict={}
		categories=self.menu.get_categories()
		for category in categories:
			desktops=self.menu.get_apps_from_category(category)
			for desktop in desktops.keys():
				desktopInfo=self.menu.get_desktop_info(os.path.join(self.menu.desktoppath,desktop))
				if desktopInfo.get("NoDisplay",False):
					continue
				listWidget=QListWidgetItem()
				desktopLayout=QGridLayout()
				ficon=desktopInfo.get("Icon","shell")
				icon=QtGui.QIcon.fromTheme(ficon)
				if not icon:
					continue
				name=desktopInfo.get("Name","shell")
				model.appendRow(QtGui.QStandardItem(name))
				comment=desktopInfo.get("Comment","shell")
				listWidget.setIcon(icon)
				listWidget.setText(name)
				if name not in desktopDict.keys():
					self.desktopList.addItem(listWidget)
				desktopDict[name]={'icon':icon,'desktop':desktop}
		return(desktopDict)
	#def _getDesktops

	def _dblClick(self):
		listWidget=self.desktopList.currentRow()
		path=self.data[listWidget]
		self.dblClicked.emit(path)
		self.close()
	#def _dblClick
	
	def _loadMime(self):
		listWidget=self.desktopList.currentRow()
		mimedata=QMimeData()
		mimedata.setText(self.data[listWidget]['path'])
		drag=QtGui.QDrag(self)
		drag.setMimeData(mimedata)
		pixmap=self.data[listWidget]['icon'].pixmap(QSize(BTN_SIZE,BTN_SIZE))
		drag.setPixmap(pixmap)
		dropAction=drag.exec_(Qt.MoveAction)
	#def _loadMime
	
	def dragMoveEvent(self,e):
		e.accept()
	#def dragEnterEvent
	
	def dragEnterEvent(self,e):
		e.accept()
	#def dragEnterEvent

class dropTable(QTableWidget):
	drop=Signal("PyObject")
	def __init__(self,parent,row,col):
		super (dropTable,self).__init__(row,col,parent)
		self.parent=parent
		self.setAcceptDrops(True)
		self.setDragEnabled(True)
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)
		Hheader=self.horizontalHeader()
		Vheader=self.verticalHeader()
		self.setShowGrid(False)
		self.horizontalHeader().hide()
		self.verticalHeader().hide()
	#def __init__
	
	def dragEnterEvent(self,e):
		e.accept()
	#def dragEnterEvent
	
	def dragMoveEvent(self,e):
		e.accept()
	#def dragEnterEvent
	
	def dropEvent(self,e):
		path=None
		e.setDropAction(Qt.MoveAction)
		e.accept()
		if e.mimeData().hasUrls():
			path=e.mimeData().urls()[0].path()
		elif e.mimeData().hasText():
			path=e.mimeData().text()
		self.drop.emit(path)
	#def dropEvent

class dropButton(QPushButton):
	drop=Signal("PyObject")
	def __init__(self,title,parent):
		super (dropButton,self).__init__("",parent)
		self.title=title
		a=QMenu()
		self.setMenu(a)
		self.parent=parent
		self.img=None
		self.icon=None
		self.setAcceptDrops(True)
		self.setMaximumWidth(BTN_SIZE)
		self.position=0
		home=os.environ['HOME']
		self.cache="%s/.cache/runomatic/"%home
	#def __init__(self,title,parent):

	def dragEnterEvent(self,e):
		e.accept()
	#def dragEnterEvent
	
	def mousePressEvent(self,e):
		if e.button() == Qt.RightButton:
			self.menu().popup(self.mapToGlobal(QPoint(0,self.height())))
			return()
		self.drop.emit({"drag":self})
		self.position=e.pos()
		mimedata=QMimeData()
		drag=QtGui.QDrag(self)
		drag.setMimeData(mimedata)
		pixmap=self.icon.pixmap(QSize(BTN_SIZE,BTN_SIZE))
		drag.setPixmap(pixmap)
		dropAction=drag.exec_(Qt.MoveAction)
	#def mousePressEvent

	def dropEvent(self,e):
		position=e.pos()
		e.setDropAction(Qt.MoveAction)
		e.accept()
		path=None
		if e.mimeData().hasUrls():
			path=e.mimeData().urls()[0].path()
		self.drop.emit({"drop":self,'path':path})
	#def dropEvent

	def setImage(self,img,state='show'):
		self.img=img
		if QtGui.QIcon.hasThemeIcon(self.img):
			self.icon=QtGui.QIcon.fromTheme(self.img)
		elif os.path.isfile(self.img):
				iconPixmap=QtGui.QPixmap(self.img)
				scaledIcon=iconPixmap.scaled(QSize(BTN_SIZE,BTN_SIZE))
				self.icon=QtGui.QIcon(scaledIcon)
		elif self.img.startswith("http"):
				if not os.path.isdir("%s/icons"%self.cache):
					os.makedirs("%s/icons"%self.cache)
				tmpfile=os.path.join("%s/icons"%self.cache,self.img.split("/")[2].split(".")[0])
				if not os.path.isfile(tmpfile):
					try:
						urlretrieve(self.img,tmpfile)
					except:
						tmpfile=QtGui.QIcon.fromTheme("shell")
				iconPixmap=QtGui.QPixmap(tmpfile)
				scaledIcon=iconPixmap.scaled(QSize(BTN_SIZE,BTN_SIZE))
				self.icon=QtGui.QIcon(scaledIcon)
		else:
			return None
		if state!='show':
			pixmap=self.icon.pixmap(QSize(BTN_SIZE,BTN_SIZE))
			image=pixmap.toImage().convertToFormat(QtGui.QImage.Format_Grayscale8)
			bg_pixmap=QtGui.QPixmap.fromImage(image)
			self.icon=QtGui.QIcon(bg_pixmap)
		self.setIcon(self.icon)
		self.setIconSize(QSize(BTN_SIZE,BTN_SIZE))
		return True
	#def setImage

	def setPopup(self,menu):
		self.setMenu(menu)

	def clone(self):
		btn=dropButton(self.title,self.parent)
		btn.setImage(self.img)
		btn.setMenu(self.menu())
		return(btn)
	#def clone
#class dropButton

i18n={"MENU":_("Configure launchers"),
	"DESC":_("Set visible launchers"),
	"TOOLTIP":_("Add custom launcher that will be shown in run-o-matic category")
	}

class runoapps(QStackedWindowItem):
	dragdrop_signal=Signal("PyObject")
	def __init_stack__(self,app=None):
		self.dbg=False
		self._debug("confLaunchers Load")
		self.appMenus=[]
		self.parm="app"
		self.app=None
		self.hidden=[]
		(self.columns,self.width,self.height)=(3,800,600)
		self.setStyleSheet(self._define_css())
		self.runner=appRun()
		self.tbl_app=dropTable(self,1,2)
		self.tbl_app.drop.connect(self._tbl_DropEvent)
		self.menu_cat=QMenu()
		self.btn_grid={}
		self.btn_drag=None
		self.visible_categories=[]
		self.menu=App2Menu.app2menu()
		self.categories=[]
		self.setProps(shortDesc=i18n["MENU"],
			longDesc=i18n["DESC"],
			icon="edit-group",
			tooltip=i18n["TOOLTIP"],
			index=2,
			visible=True)
		self.icon=('edit-group')
		self.enabled=True
		self.setStyleSheet(self._define_css())
		self.runoapps="/usr/share/runomatic/applications"
		self.userRunoapps="/usr/share/runomatic/applications"
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("ConfLaunchers: %s"%msg)
	#def _debug

	def apply_parms(self,app):
		self._debug("Set parm %s"%app)
		self.app=app
		(self.columns,self.width,self.height)=self._get_screen_size()

	def _get_screen_size(self):
		row=0
		col=0
		if self.app:
			scr=self.app.primaryScreen()
			w=scr.size().width()-BTN_SIZE_FULL
			h=scr.size().height()-(2*BTN_SIZE_FULL)
		else:
			w=800
			h=600
		columns=int(w/BTN_SIZE_FULL)-3
		return (columns,w,h)
	#def _get_screen_size

	def updateScreen(self):
		apps=self._update_apps_data()
		self.update_apps(apps)
	#def updateScreen

	def __initScreen__(self):
		def _update_categories(cat):
			if cat in self.visible_categories:
				self.visible_categories.remove(cat)
			else:
				self.visible_categories.append(cat)
			apps=self.runner.get_apps(self.visible_categories,False)
			apps['desktops'].extend(desktop_apps)
			self.update_apps(apps)
		
		def _update_desktops():
			cursor=QtGui.QCursor(Qt.WaitCursor)
			self.setCursor(cursor)
			fdia=desktopChooser(self)
			fdia.dblClicked.connect(self._tbl_DropEvent)
			cursor=QtGui.QCursor(Qt.PointingHandCursor)
			self.setCursor(cursor)
			fchoosed=''
			if (fdia.show()):
				fchoosed=fdia.selectedFiles()[0]
				apps=self._get_table_apps()
				apps['desktops'].append(fchoosed)
				desktop_apps.append(fchoosed)
				self.update_apps(apps)

		desktop_apps=[]
		self.tbl_app.clear()
		apps=self._update_apps_data()
		sigmap_catSelect=QSignalMapper(self)
		sigmap_catSelect.mappedString.connect(_update_categories)
		box=QVBoxLayout()
		btnBox=QHBoxLayout()
		btn_cat=QPushButton(_("Categories"))
		btn_cat.setFixedWidth(150)
		for cat in self._get_all_categories():
			if not cat:
				continue
			act=QtGui.QAction(cat,self.menu_cat)
			self.menu_cat.addAction(act)
			if cat!="run-o-matic":
				if len(self.menu.get_apps_from_menuentry(cat))<1:
					act.setEnabled(False)
					continue
			act.setCheckable(True)
			if cat in self.visible_categories:
				act.setChecked(True)
			sigmap_catSelect.setMapping(act,cat)
			act.triggered.connect(sigmap_catSelect.map)
		btn_cat.setMenu(self.menu_cat)
		btn_add=QPushButton(_("Add launcher"))
		btn_add.setToolTip(_("Add Launcher"))
		#btn_add.setFixedWidth(150)
		btn_add.clicked.connect(_update_desktops)
		btnBox.addWidget(btn_cat,1,Qt.AlignLeft)
		btnBox.addWidget(btn_add,2,Qt.AlignLeft)
		box.addLayout(btnBox,Qt.AlignLeft)
		tabScroll=QWidget()
		tabScroll.setFocusPolicy(Qt.NoFocus)
		scrollArea=QScrollArea(tabScroll)
		scrollArea.setFocusPolicy(Qt.NoFocus)
		self.update_apps(apps)
		scrollArea.setWidget(self.tbl_app)
		scrollArea.alignment()
		scrollArea.setGeometry(QRect(0,0,self.width,self.height))
		#self.tbl_app.setFixedWidth((self.columns+int(self.columns*0.5)+1)*BTN_SIZE)
		box.addWidget(self.tbl_app)
		self.setLayout(box)
	#def load_screen
	
	def _get_all_categories(self):
		categories=[]
		categories_tree=self.menu.get_categories_tree()
		categories=list(categories_tree.keys())
		categories.insert(0,'run-o-matic')
		return categories
	#def _get_all_categories(self):
	
	def _tbl_DropEvent(self,path):
		deskPath=''
		if type(path)==type({}):
			deskPath=path.get('path','')
		elif type(deskPath)==type(""):
			deskPath=path

		if deskPath:
			if deskPath.endswith('desktop'):
				if os.path.isfile(deskPath):
					apps=self._get_table_apps()
					apps['desktops'].append(deskPath)
					self.update_apps(apps)
		self.btn_ok.setEnabled(True)
	#def _tbl_DropEvent

	def _update_apps_data(self):
		apps=self.runner.get_apps(exclude=['background64'])
		self.visible_categories=apps['categories']
		self._debug("Visible: %s"%self.visible_categories)
		return apps
	#def _update_apps_data

	def update_apps(self,apps):
		row=0
		col=0
		def _add_desktop(desktops,state="show"):
			nonlocal row
			nonlocal col
			desktopsFixed=[]
			for desktop in desktops:
				#Check if desktop is from run-o-matic
				if os.path.isdir(self.userRunoapps):
					if desktop in os.listdir(self.userRunoapps):
						desktop=os.path.join(self.userRunoapps,desktop)
				deskInfo=self.runner.get_desktop_app(desktop)
				if not deskInfo or '' in deskInfo.keys():
					continue
				for appName,appIcon in deskInfo.items():
					btn_desktop=dropButton(desktop,self.tbl_app)
					if not btn_desktop.setImage(appIcon,state):
						self._debug("Discard: %s"%appName)
						btn_desktop.deleteLater()
						continue
					btnMenu=QMenu(appName)
					h_action=_("Remove button")
					e_action=_("Edit button")
				 #	r_action=_("Remove button")
					if state!="show":
						h_action=_("Remove button")
					show=btnMenu.addAction(h_action)
					edit=btnMenu.addAction(e_action)
					#remove=btnMenu.addAction(r_action)
					show.triggered.connect(lambda:self._changeBtnState(apps,state))
					edit.triggered.connect(lambda:self._editBtn(apps))
				#	remove.triggered.connect(lambda:self._removeBtn(apps))
					btn_desktop.setToolTip(desktop)
					btn_desktop.setMenu(btnMenu)
					self.appMenus.append(btnMenu)
					btn_desktop.setObjectName("confBtn")
					self.btn_grid[btn_desktop]={"row":row,"col":col,"state":state}
					btn_desktop.drop.connect(self._btn_dragDropEvent)
					self._debug("Adding %s at %s %s"%(appName,row,col))
					self.tbl_app.setCellWidget(row,col,btn_desktop)
					col+=1
					if col>=self.columns:
						col=0
						row+=1
						self.tbl_app.insertRow(row)
						self._debug("Insert row %s"%self.tbl_app.rowCount())
					desktopsFixed.append(desktop)
			desktops=desktopsFixed

		self.tbl_app.clear()
		self.tbl_app.setRowCount(1)
		self.tbl_app.setColumnCount(self.columns)
		_add_desktop(apps['desktops'])
		#_add_desktop(apps['hidden'],"hidden")
		self.tbl_app.resizeColumnsToContents()
		for act in self.menu_cat.actions():
			if act.text() in self.visible_categories:
				act.setChecked(True)
			else:
				act.setChecked(False)
		self.setChanged()
	#def update_apps

	def _changeBtnState(self,apps,state='show'):
		row=self.tbl_app.currentRow()
		col=self.tbl_app.currentColumn()
		btn=self.tbl_app.cellWidget(row,col)
		if state=='show':
			state='hidden'
			apps['desktops'].remove(btn.title)
			apps['hidden'].append(btn.title)
			self.hidden.append(btn.title)
		else:
			state='show'
			apps['desktops'].append(btn.title)
			apps['hidden'].remove(btn.title)
		self.btn_grid['state']=state
		self.update_apps(apps)
		self.btn_ok.setEnabled(True)
		self.btn_cancel.setEnabled(True)
		self.refresh=True
		retval=True
	#def _changeBtnState
	
	def _removeBtn(self,apps):
		row=self.tbl_app.currentRow()
		col=self.tbl_app.currentColumn()
		btn=self.tbl_app.cellWidget(row,col)
		apps['desktops'].remove(btn.title)
		self.update_apps(apps)
		self.btn_ok.setEnabled(True)
		self.btn_cancel.setEnabled(True)
		self.refresh=True
		retval=True
	#def _changeBtnState

	def _editBtn(self,apps):
		if self.btn_ok.isEnabled():
			self.writeConfig()
		row=self.tbl_app.currentRow()
		col=self.tbl_app.currentColumn()
		btn=self.tbl_app.cellWidget(row,col)
		self.stack.gotoStack(idx=3,parms=btn.title)
	#def _editBtn

	def _btn_dragDropEvent(self,btnEv):
		if 'drag' in btnEv.keys():
			self.btn_drag=btnEv['drag']
		else:
			if btnEv.get('drop')==self.btn_drag:
				self.btn_drag.showMenu()
				self.btn_drag=None
				return False
			btn=btnEv.get('drop')
			if self.btn_grid.get(btn,{}).get('state')=='hidden' or self.btn_grid.get(self.btn_drag,{}).get('state')=='hidden':
				self.btn_drag=None
				return False

			if self.btn_drag==None and btnEv.get('path',None)==None:
				return False
			replace=False
			self.setChanged(True)
			if replace:
				rowTo=self.btn_grid[btn]['row']
				colTo=self.btn_grid[btn]['col']
				rowFrom=self.btn_grid[self.btn_drag]['row']
				colFrom=self.btn_grid[self.btn_drag]['col']
				btnTo=btn.clone()
				btnTo.drop.connect(self._btn_dragDropEvent)
				self.btn_grid[btnTo]=self.btn_grid[self.btn_drag]
				btnFrom=self.btn_drag.clone()
				btnFrom.drop.connect(self._btn_dragDropEvent)
				self.btn_grid[btnFrom]=self.btn_grid[btn]
				del self.btn_grid[btn] 
				del self.btn_grid[self.btn_drag] 
				self.tbl_app.setCellWidget(rowFrom,colFrom,btnTo)
				self.tbl_app.setCellWidget(rowTo,colTo,btnFrom)
				self.btn_drag=None
			else:
				#Build desktops array
				apps=self._get_table_apps()
				position=apps['desktops'].index(btn.title)
				self._debug("Btn at pos: %s"%position)
				if btnEv.get('path',None):
					apps['desktops'].insert(position,btnEv['path'])
				else:
					apps['desktops'].remove(self.btn_drag.title)
					apps['desktops'].insert(position,self.btn_drag.title)
				self.update_apps(apps)
				self.btn_drag=None
	#def _btn_dragDropEvent

	def writeConfig(self):
		apps=self._get_table_apps()
		for key,data in apps.items():
			self.saveChanges(key,data)
		self.saveChanges('categories',self.visible_categories)
	#def writeConfig(self):

	def _get_table_apps(self):
		apps={'desktops':[],'hidden':[],'extra_desktops':[]}
		for row in range(0,self.tbl_app.rowCount()):
			for col in range(0,self.tbl_app.columnCount()):
				btn=self.tbl_app.cellWidget(row,col)
				if btn:
					self._debug("Item at %s: %s"%(row,btn))
					if self.btn_grid[btn]['state']=='show':
						apps['desktops'].append(btn.title)
					else:
						apps['hidden'].append(btn.title)
		config=self.getConfig(self.level)
		apps['hidden']=list(set(config.get(self.level,{}).get("hidden",[])+self.hidden))
		return apps
	#def _get_table_apps

	def setParms(self,parms):
		apps=self._update_apps_data()
		if parms not in apps['banned'] and 'run-o-matic' not in parms:
			apps['banned'].append(parms)
		for key,data in apps.items():
			self.saveChanges(key,data)
		self.stack.lst_options.setCurrentRow(1)
		self.updateScreen()

	def _define_css(self):
		css="""
		#confBtn{
			padding: 6px;
			margin:6px;
			border:solid black 10px;
			font: 14px Roboto;
		}
		"""
		return(css)
		#def _define_css
