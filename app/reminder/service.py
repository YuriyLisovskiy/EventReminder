import time
import platform
from datetime import (
	date,
	datetime,
	timedelta
)

from PyQt5.QtCore import QThread

from pynotifier import Notification

from app.settings import Settings
from app.reminder.db import storage


class ReminderService(QThread):

	def __init__(self, parent, calendar):
		super().__init__(parent=parent)
		self.calendar = calendar
		self.settings = Settings()

	def __del__(self):
		self.wait()

	def run(self):
		try:
			storage.connect()
			while True:
				try:
					time.sleep(1)
					self.process_events()
				except Exception as exc:
					with open('./errors_file.txt', 'a') as the_file:
						the_file.write('Service error: {}\n'.format(exc))
					print('Service error: {}\n'.format(exc))
		except Exception as exc:
			with open('./fatal_errors_file.txt', 'a') as the_file:
				the_file.write('Fatal error: {}\n'.format(exc))
			print('Service error: {}\n'.format(exc))
		storage.disconnect()

	def process_events(self):
		events = storage.get_events(date.today())
		need_to_update = False
		for event in events:
			now = datetime.now()
			if event.time <= now.time().strftime('%H:%M:00') and event.date <= now.date():
				self.__send_notification(event)
				if event.repeat_weekly is True:
					storage.update_event(
						pk=event.id,
						e_date=event.date + timedelta(days=7)
					)
					need_to_update = True
				else:
					storage.update_event(pk=event.id, is_past=True)
					if self.settings.user.remove_event_after_time_up:
						storage.delete_event(event.id)
						need_to_update = True
		if need_to_update:
			self.calendar.update()

	def __send_notification(self, event):
		Notification(
			title=self.settings.app.name,
			icon_path=self.settings.app.icon('Linux' not in platform.system(), q_icon=False),
			description='{}\n\n{}'.format(event.title, event.description),
			duration=self.settings.user.notification_duration,
			urgency=Notification.URGENCY_CRITICAL
		).send()
