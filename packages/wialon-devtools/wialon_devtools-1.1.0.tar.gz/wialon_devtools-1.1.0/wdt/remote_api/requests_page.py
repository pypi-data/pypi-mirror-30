from PyQt5 import QtWidgets
import json
from wdt.remote_api import wialon_sdk_client
from wdt.dt import devtools_preset
from wdt.dt import devtools_jstable


class RequestsPage(QtWidgets.QWidget):
	def __init__(self, wialon_client):
		super().__init__()
		self.wc = wialon_client
		self.clipboard = QtWidgets.QApplication.clipboard()

		self.target = QtWidgets.QLineEdit()
		self.command = QtWidgets.QLineEdit()
		self.send_btn = QtWidgets.QPushButton('Send')
		self.cancel_btn = QtWidgets.QPushButton('Cancel')
		self.cancel_btn.setEnabled(False)
		self.format_btn = QtWidgets.QPushButton('Format')
		self.copy_btn = QtWidgets.QPushButton('Copy')

		self.params_edit = QtWidgets.QTextEdit()

		self.response_table = QtWidgets.QTableView()
		self.response = {}

		self.status_lbl = QtWidgets.QStatusBar()
		self.initPage()


	def initPage(self):
		self.send_btn.clicked.connect(self.executeRequest)
		self.cancel_btn.clicked.connect(self.cancelRequest)
		self.format_btn.clicked.connect(self.formatParams)
		self.copy_btn.clicked.connect(self.copyResponse)

		# self.params_edit.setStyleSheet("background-color: #e7fcca; opacity: 0.5");

		page_lo = QtWidgets.QVBoxLayout()
		main_layout = QtWidgets.QHBoxLayout()

		left_lo = QtWidgets.QVBoxLayout()

		command_lo = QtWidgets.QVBoxLayout()
		command_lo.addWidget(QtWidgets.QLabel('<b>Target/Command</b>'))

		sdk_command_lo = QtWidgets.QHBoxLayout()
		sdk_command_lo.addWidget(self.target)
		sdk_command_lo.addWidget(self.command)

		command_lo.addLayout(sdk_command_lo)
		command_lo.addWidget(QtWidgets.QLabel('<b>Response</b>'))
		command_lo.addWidget(self.response_table)
		command_lo.addWidget(self.copy_btn)

		left_lo.addLayout(command_lo)

		right_lo = QtWidgets.QVBoxLayout()
		right_title_lo = QtWidgets.QHBoxLayout()
		right_title_lo.addWidget(QtWidgets.QLabel('<b>Parameters</b>'))
		right_title_lo.addStretch(1)
		right_title_lo.addWidget(self.format_btn)
		right_lo.addLayout(right_title_lo)
		right_lo.addWidget(self.params_edit)
		
		main_layout.addLayout(left_lo)
		main_layout.addLayout(right_lo)
		main_layout.setStretch(1, 2)

		page_lo.addLayout(main_layout)
		btn_lo = QtWidgets.QHBoxLayout()
		btn_lo.addWidget(self.send_btn)
		btn_lo.addWidget(self.cancel_btn)
		btn_lo.addStretch(1)
		page_lo.addLayout(btn_lo)
		presets_widget = devtools_preset.PresetsWidget({
				"name": "Request presets",
				"file_name": "requests.preset",
				"widgets": [
					{
						"name": "target",
						"widget": self.target
					},
					{
						"name": "command",
						"widget": self.command
					},
					{
						"name": "request_params",
						"widget": self.params_edit
					}
				],
				"callback": self.apply_cb
			})
		page_lo.addWidget(presets_widget)
		page_lo.addWidget(self.status_lbl)

		self.setLayout(page_lo)


	def executeRequest(self):
		target = self.target.text()
		if not target:
			self.status_lbl.showMessage('Target is invalid')
			return
		command = self.command.text()
		if not command:
			self.status_lbl.showMessage('Command is invalid')
			return
		self.status_lbl.showMessage('Making request...')
		svc = target + '/' + command
		self.send_btn.setEnabled(False)
		self.cancel_btn.setEnabled(True)
		self.request_rt = self.wc.execute_request(svc, self.params_edit.toPlainText(), self.handleExecute)


	def cancelRequest(self):
		self.request_rt.cancel()


	def handleExecute(self, error, response):
		if not error:
			self.status_lbl.showMessage('Response received')
			self.response = response
			self.updateResponseWidget()
		else:
			self.status_lbl.showMessage(str(response))

		self.send_btn.setEnabled(True)
		self.cancel_btn.setEnabled(False)


	def updateResponseWidget(self):
		devtools_jstable.render(self.response_table, self.response)


	def formatParams(self):
		try:
			params = json.loads(self.params_edit.toPlainText())
			self.params_edit.setText(json.dumps(params, indent=4))
		except:
			pass

	def copyResponse(self):
		try:
			self.clipboard.setText(json.dumps(self.response, indent=4))
		except:
			self.clipboard.setText(str(self.response))

	# Methods for presets widget

	def apply_cb(self):
		self.response = {}
		self.updateResponseWidget()
		self.formatParams()
