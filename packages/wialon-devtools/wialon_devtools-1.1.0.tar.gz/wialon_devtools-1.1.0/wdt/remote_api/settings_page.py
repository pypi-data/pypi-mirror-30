from PyQt5 import QtWidgets
from wdt.remote_api import wialon_sdk_client
from wdt.dt import devtools_preset


class SettingsPage(QtWidgets.QWidget):
	def __init__(self, wialon_client):
		super().__init__()
		self.wc = wialon_client

		# Connection widgets
		self.host_le = QtWidgets.QLineEdit()
		self.port_le = QtWidgets.QLineEdit()
		self.sid_le = QtWidgets.QLineEdit()
		self.secure_chx = QtWidgets.QCheckBox()

		# Credentials widgets
		self.user_le = QtWidgets.QLineEdit()
		self.password_le = QtWidgets.QLineEdit()
		self.password_le.setEchoMode(QtWidgets.QLineEdit.Password)
		self.login_btn = QtWidgets.QPushButton('Login')
		self.login_cancel_btn = QtWidgets.QPushButton('Cancel')
		self.login_cancel_btn.setEnabled(False)

		# Token widgets
		self.token_le = QtWidgets.QLineEdit()
		self.t_login_btn = QtWidgets.QPushButton('Login')
		self.t_login_cancel_btn = QtWidgets.QPushButton('Cancel')
		self.t_login_cancel_btn.setEnabled(False)

		self.status_lbl = QtWidgets.QStatusBar()
		self.initPage()


	def initPage(self):
		# bind widgets to wialon_sdk_client
		self.host_le.textChanged.connect(self.wc.set_host)
		self.port_le.textChanged.connect(self.wc.set_port)
		self.sid_le.textChanged.connect(self.wc.set_sid)
		self.secure_chx.stateChanged.connect(self.wc.set_secure)

		self.login_btn.clicked.connect(self.try_login)
		self.login_cancel_btn.clicked.connect(self.cancel_login)

		self.t_login_btn.clicked.connect(self.try_t_login)
		self.t_login_cancel_btn.clicked.connect(self.cancel_t_login)

		# draw layout
		page_lo = QtWidgets.QVBoxLayout()
		
		s_gr = QtWidgets.QGroupBox('Settings')
		s_lo = QtWidgets.QHBoxLayout()

		cl_sett_lo = QtWidgets.QFormLayout()
		cl_sett_lo.addRow('Host', self.host_le)
		cl_sett_lo.addRow('Port', self.port_le)
		cl_sett_lo.addRow('SID', self.sid_le)
		cl_sett_lo.addRow('Secure', self.secure_chx)

		s_lo.addLayout(cl_sett_lo)
		s_lo.setStretch(0, 4)
		s_lo.setStretch(1, 3)
		s_lo.addStretch(3)
		s_gr.setLayout(s_lo)

		lc_gr = QtWidgets.QGroupBox('Login by password')
		lc_lo = QtWidgets.QHBoxLayout()

		cred_lo = QtWidgets.QFormLayout()
		cred_lo.addRow('User', self.user_le)
		cred_lo.addRow('Password', self.password_le)
		login_btn_lo = QtWidgets.QHBoxLayout()
		login_btn_lo.addWidget(self.login_btn)
		login_btn_lo.addWidget(self.login_cancel_btn)
		login_btn_lo.addStretch(1)
		cred_lo.addRow(login_btn_lo)

		lc_lo.addLayout(cred_lo)
		lc_lo.addStretch(1)
		lc_lo.setStretch(0, 2)
		lc_lo.setStretch(1, 5)
		lc_gr.setLayout(lc_lo)

		lt_gr = QtWidgets.QGroupBox('Login by token')
		lt_lo = QtWidgets.QHBoxLayout()

		token_lo = QtWidgets.QFormLayout()
		token_lo.addRow('Token', self.token_le)
		t_login_btn_lo = QtWidgets.QHBoxLayout()
		t_login_btn_lo.addWidget(self.t_login_btn)
		t_login_btn_lo.addWidget(self.t_login_cancel_btn)
		t_login_btn_lo.addStretch(1)
		token_lo.addRow(t_login_btn_lo)

		lt_lo.addLayout(token_lo)
		lt_lo.addStretch(1)
		lt_lo.setStretch(0, 3)
		lt_lo.setStretch(1, 1)
		lt_gr.setLayout(lt_lo)

		page_lo.addWidget(s_gr)
		page_lo.addWidget(lc_gr)
		page_lo.addWidget(lt_gr)

		presets_widget = devtools_preset.PresetsWidget({
				"name": "Settings presets",
				"file_name": "settings.preset",
				"widgets": [
					{
						"name": "host",
						"widget": self.host_le
					},
					{
						"name": "port",
						"widget": self.port_le
					},
					{
						"name": "secure",
						"widget": self.secure_chx
					},
					{
						"name": "user",
						"widget": self.user_le
					},
					{
						"name": "password",
						"widget": self.password_le
					},
					{
						"name": "token",
						"widget": self.token_le
					}
				]
			})
		page_lo.addStretch(1)
		page_lo.addWidget(presets_widget)
		page_lo.addWidget(self.status_lbl)

		self.setLayout(page_lo)
		# init widgets with wialon_sdk_client state
		self.updatePage()


	def updatePage(self):
		self.host_le.setText(self.wc.get_host())
		self.port_le.setText(str(self.wc.get_port()))
		self.sid_le.setText(self.wc.get_sid())
		self.secure_chx.setChecked(self.wc.is_secure())

	# Login routines

	def try_login(self):
		# Login button clicked - disable some widgets and try to login with sdk client
		self.login_btn.setEnabled(False)
		self.t_login_btn.setEnabled(False)
		self.sid_le.setEnabled(False)
		self.status_lbl.showMessage('Trying to login')
		user = self.user_le.text()
		password = self.password_le.text()
		self.login_rt = self.wc.login(user, password, self.finish_login)
		if self.login_rt:
			self.login_cancel_btn.setEnabled(True)
			self.t_login_cancel_btn.setEnabled(True)


	def cancel_login(self):
		if self.login_rt:
			self.login_rt.cancel()


	def try_t_login(self):
		# Login button clicked - disable some widgets and try to login with sdk client
		self.login_btn.setEnabled(False)
		self.t_login_btn.setEnabled(False)
		self.sid_le.setEnabled(False)
		self.status_lbl.showMessage('Trying to login')
		token = self.token_le.text()
		self.t_login_rt = self.wc.token_login(token, self.finish_login)
		if self.t_login_rt:
			self.login_cancel_btn.setEnabled(True)
			self.t_login_cancel_btn.setEnabled(True)


	def cancel_t_login(self):
		if self.t_login_rt:
			self.t_login_rt.cancel()


	def finish_login(self, error, status):
		# callback called after login attempt
		self.status_lbl.showMessage(status)
		self.updatePage()
		self.sid_le.setEnabled(True)

		self.login_btn.setEnabled(True)
		self.login_cancel_btn.setEnabled(False)
		self.t_login_btn.setEnabled(True)
		self.t_login_cancel_btn.setEnabled(False)
