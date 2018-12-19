import sys

from PyQt5.QtWidgets import *

from app.ui.window import Window
from app.reminder.service import ReminderService
from app.settings.custom_settings import SHOW_CALENDAR_ON_STARTUP


if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = Window()
	ReminderService(app, window).start()
	if SHOW_CALENDAR_ON_STARTUP:
		window.show()
	sys.exit(app.exec_())
