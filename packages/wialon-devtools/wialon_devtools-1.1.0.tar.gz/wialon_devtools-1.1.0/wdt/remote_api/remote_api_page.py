from PyQt5 import QtWidgets
from wdt.remote_api import wialon_sdk_client
from wdt.remote_api import settings_page
from wdt.remote_api import requests_page

class RemoteAPIPage(QtWidgets.QTabWidget):
	def __init__(self):
		super().__init__()
		self.wialon_client = wialon_sdk_client.WialonSDKClient()

		self.initPage()

	def initPage(self):
		self.addTab(settings_page.SettingsPage(self.wialon_client), "Settings")
		self.addTab(requests_page.RequestsPage(self.wialon_client), "Requests")
