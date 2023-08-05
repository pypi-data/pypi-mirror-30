import sys
from wdt.ips import wialon_ips_page
from wdt.remote_api import remote_api_page
from PyQt5 import QtWidgets, QtGui
import pkg_resources


class DevtoolsWidget(QtWidgets.QTabWidget):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.setWindowTitle('Wialon Devtools')
		self.setWindowIcon(QtGui.QIcon(pkg_resources.resource_filename('wdt', 'images/wialon.png')))
		self.setGeometry(300, 300, 800, 620)

		self.addTab(remote_api_page.RemoteAPIPage(), 'Remote API')
		self.addTab(wialon_ips_page.WialonIPSPage(), "Wialon IPS")

		self.show()

def run():
	app = QtWidgets.QApplication(sys.argv)
	devtools_widget = DevtoolsWidget()
	sys.exit(app.exec_())
