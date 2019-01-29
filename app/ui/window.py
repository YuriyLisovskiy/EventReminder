from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from app.ui import utils
from app.settings import Settings
from app.ui.widgets.calendar_widget import CalendarWidget


class MainWindow(QMainWindow):

	def __init__(self):
		self.settings = Settings()
		if self.settings.is_always_on_top:
			super().__init__(None, Qt.WindowStaysOnTopHint)
		else:
			super().__init__()
		self.window().setWindowTitle(self.settings.name)
		self.resize(self.settings.size)
		self.move(self.settings.pos)
		self.setWindowIcon(self.settings.icon())
		self.calendar = self.init_calendar()
		self.setCentralWidget(self.calendar)
		self.setup_navigation_menu()
		self.statusBar().showMessage('Status: Ok')
		self.setFont(QFont(str(self.settings.font)))

		self.open_action = QAction('Open {}'.format(self.settings.name), self)
		self.hide_action = QAction('Minimize To Tray', self)
		if not self.settings.show_calendar_on_startup:
			self.hide_action.setEnabled(False)
		self.close_action = QAction('Quit {}'.format(self.settings.name), self)

		self.tray_icon = self.init_tray_icon()

		self.setPalette(self.settings.theme)

	def closeEvent(self, event):
		event.ignore()
		self.hide()

	def quit_app(self):
		self.settings.autocommit(False)
		self.settings.set_pos(self.pos())
		self.settings.set_size(self.size())
		self.settings.commit()
		qApp.quit()

	def init_tray_icon(self):
		tray_icon = QSystemTrayIcon(self)
		tray_icon.setIcon(self.settings.icon())
		actions = {
			self.open_action: self.show,
			self.hide_action: self.hide,
			self.close_action: self.quit_app
		}
		tray_menu = QMenu()
		for key, value in actions.items():
			key.triggered.connect(value)
			tray_menu.addAction(key)
		tray_icon.setContextMenu(tray_menu)
		tray_icon.show()
		return tray_icon

	def init_calendar(self):
		calendar = CalendarWidget(self, self.width(), self.height())
		calendar.setLocale(QLocale(QLocale.English))
		calendar.setFont(QFont(str(self.settings.font)))
		calendar.set_status_bar(self.statusBar())
		return calendar

	def hide(self):
		super().hide()
		self.hide_action.setEnabled(False)
		self.open_action.setEnabled(True)

	def show(self):
		super().show()
		self.hide_action.setEnabled(True)
		self.open_action.setEnabled(False)

	def resizeEvent(self, event):
		self.calendar.resize_handler()
		QMainWindow.resizeEvent(self, event)

	def setup_navigation_menu(self):
		self.statusBar()
		main_menu = self.menuBar()
		self.setup_file_menu(main_menu=main_menu)

	def setup_file_menu(self, main_menu):
		file_menu = main_menu.addMenu('&File')
		file_menu.addAction(
			utils.create_action(self, 'New Event', 'Ctrl+N', 'Create event', self.calendar.create_event)
		)
		file_menu.addAction(
			utils.create_action(self, 'Settings...', 'Ctrl+Alt+S', 'Settings', self.calendar.open_settings)
		)

	def enterEvent(self, event):
		super().enterEvent(event)
		self.setWindowOpacity(float(self.settings.mouse_enter_opacity))

	def leaveEvent(self, event):
		super().leaveEvent(event)
		self.setWindowOpacity(float(self.settings.mouse_leave_opacity))
