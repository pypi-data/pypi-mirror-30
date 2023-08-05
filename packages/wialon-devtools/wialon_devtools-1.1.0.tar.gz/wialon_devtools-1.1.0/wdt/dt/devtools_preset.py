from PyQt5 import QtGui, QtWidgets, QtCore
import json
import os, appdirs, shutil, pkg_resources

class PresetsWidget(QtWidgets.QGroupBox):
	"""Widget for applying presets to parent widget"""
	def __init__(self, settings):
		super().__init__(settings['name'])

		presets_dir = appdirs.user_data_dir("wialon_devtools", "WialonApps")

		if not os.path.exists(presets_dir):
			os.makedirs(presets_dir)

		settings['file_path'] = os.path.join(presets_dir, settings['file_name'])
		if not os.path.exists(settings['file_path']):
			if os.path.exists(pkg_resources.resource_filename('wdt', 'presets/' + settings['file_name'])):
				shutil.copy(pkg_resources.resource_filename('wdt', 'presets/' + settings['file_name']), settings['file_path'])
			else:
			    os.mknod(settings['file_path'])

		print(settings['name'] + ' path is ' + settings['file_path'])

		self.presets = Presets(settings)
		self.save_btn = QtWidgets.QPushButton('Save')
		self.save_btn.clicked.connect(self.presets.save_preset)

		self.load_btn = QtWidgets.QPushButton('Load')
		self.load_btn.clicked.connect(self.presets.load_preset)
		self.initWidget()


	def initWidget(self):
		lo = QtWidgets.QHBoxLayout()
		lo.addWidget(self.load_btn)
		lo.addWidget(self.save_btn)
		lo.addStretch(1)
		self.setLayout(lo)


class Presets(QtCore.QAbstractTableModel):
	def __init__(self, settings):
		super().__init__()

		self.settings = settings
		self.loaded_presets = []

		self.load_presets()


	def save_preset(self):
		preset_name = QtWidgets.QInputDialog.getText(None, "Name for new preset", "Enter name:", QtWidgets.QLineEdit.Normal)
		if not preset_name[1]:
			return

		new_preset = {
			'name': preset_name[0],
			'preset': dict()
		}

		widgets = self.settings['widgets']		
		for w in widgets:
			widget_name = w['name']
			widget = w['widget']
			if not widget or not widget_name:
				continue

			if type(widget) is QtWidgets.QLineEdit:
				value = widget.text()
				if value:
					new_preset['preset'][widget_name] = value
			elif type(widget) is QtWidgets.QTextEdit:
				value = widget.toPlainText()
				if value:
					try:
						# drop json formatting
						value = json.dumps(json.loads(value))
					except:
						pass
					new_preset['preset'][widget_name] = value
			elif type(widget) is QtWidgets.QCheckBox:
				value = widget.checkState()
				if value:
					new_preset['preset'][widget_name] = True
				else:
					new_preset['preset'][widget_name] = False


		if len(new_preset['preset']):
			self.loaded_presets.append(new_preset)

		self.dump_presets()


	def load_preset(self):
		load_dlg = PresetsLoadDialog(self)
		load_dlg.exec()
		self.dump_presets()


	def load_presets(self):
		presets_path = self.settings['file_path']
		if not presets_path:
			return
		try:
			with open(presets_path, 'r') as presets_file:
				try:
					loaded_presets = json.load(presets_file)
					if type(loaded_presets) is list:
						self.loaded_presets = loaded_presets
					else:
						print('Presets format is invalid')
				except json.JSONDecodeError:
					print('Failed to load presets')
		except FileNotFoundError:
			print('Incorrect presets path')

		self.update(0)


	def dump_presets(self):
		presets_path = self.settings['file_path']
		if not presets_path:
			return
		try:
			with open(presets_path, 'w') as presets_file:
				json.dump(self.loaded_presets, presets_file, indent=4)
		except FileNotFoundError:
			print('Incorrect presets path')

	def update(self, preset_index):
		if len(self.loaded_presets) < preset_index + 1:
			return

		loaded_preset = self.loaded_presets[preset_index]
		if not preset_valid(loaded_preset):
			# try next
			self.update(preset_index + 1)
			return

		preset_name = loaded_preset['name']
		preset_params = loaded_preset['preset']

		widgets = self.settings['widgets']

		for w in widgets:
			widget_name = w['name']
			widget = w['widget']
			if not widget or not widget_name:
				continue
			if type(widget) is QtWidgets.QLineEdit or type(widget) is QtWidgets.QTextEdit:
				if widget_name in preset_params:
					widget.setText(str(preset_params[widget_name]))
				else:
					widget.setText('')
			elif type(widget) is QtWidgets.QCheckBox:
				if widget_name in preset_params and type(preset_params[widget_name]) is bool:
					widget.setChecked(preset_params[widget_name])
				else:
					widget.setChecked(False)

		if 'callback' in self.settings:
			self.settings['callback']()

	def rowCount(self, index):
		return len(self.loaded_presets)

	def columnCount(self, index):
		return len(self.settings['widgets']) + 1

	def data(self, index, role):
		if role == QtCore.Qt.DisplayRole:
			if index.column() == 0:
				return self.loaded_presets[index.row()]['name']

			# find associated widget name
			widget_name = self.settings['widgets'][index.column() - 1]['name']
			if widget_name in self.loaded_presets[index.row()]['preset']:
				return self.loaded_presets[index.row()]['preset'][widget_name]

	def headerData(self, section, orientation, role):
		if role == QtCore.Qt.DisplayRole and orientation == QtCore.Qt.Horizontal:
			if section == 0:
				return 'Preset Name'
			return self.settings['widgets'][section - 1]['name']

	def removeRows(self, position, count, parent):
		self.beginRemoveRows(QtCore.QModelIndex(), position, position)
		del self.loaded_presets[position]
		self.endRemoveRows()


class PresetsLoadDialog(QtWidgets.QDialog):
	def __init__(self, presets_widget):
		super().__init__()
		self.loaded_preset = None
		self.presets_model = presets_widget

		self.presets_view = QtWidgets.QTableView()
		self.presets_view.setFocusPolicy(QtCore.Qt.NoFocus)
		self.presets_view.verticalHeader().hide()
		self.presets_view.horizontalHeader().setStyleSheet('font-weight: bold')
		self.presets_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
		self.presets_view.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
		self.presets_view.setModel(self.presets_model)
		self.presets_view.selectionModel().currentRowChanged.connect(self.presetSelected)
		self.presets_view.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
		self.presets_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.presets_view.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.presets_view.resizeColumnsToContents()
		self.presets_view.setFixedSize(self.presets_view.horizontalHeader().length() + self.presets_view.verticalHeader().width(), self.presets_view.verticalHeader().length()+self.presets_view.horizontalHeader().height())

		self.buttonBox = QtWidgets.QDialogButtonBox()

		self.delete_btn = QtWidgets.QPushButton('Delete')
		self.delete_btn.clicked.connect(self.deletePreset)
		self.delete_btn.setEnabled(False)

		self.load_btn = QtWidgets.QPushButton('Load')
		self.load_btn.clicked.connect(self.loadPreset)
		self.load_btn.setEnabled(False)

		self.buttonBox.addButton(QtWidgets.QDialogButtonBox.Cancel)
		self.buttonBox.addButton(self.delete_btn, QtWidgets.QDialogButtonBox.ActionRole)
		self.buttonBox.addButton(self.load_btn, QtWidgets.QDialogButtonBox.AcceptRole)

		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)

		self.dialog_lo = QtWidgets.QVBoxLayout()
		self.dialog_lo.addWidget(self.presets_view)
		self.dialog_lo.addWidget(self.buttonBox)

		self.setLayout(self.dialog_lo)

	def deletePreset(self):
		selected = self.presets_view.selectionModel().selectedRows()
		if selected:
			self.presets_model.removeRows(selected[0].row(), 1, None)

	def loadPreset(self):
		selected = self.presets_view.selectionModel().selectedRows()
		if selected:
			self.presets_model.update(selected[0].row())

	def presetSelected(self):
		self.load_btn.setEnabled(True)
		self.delete_btn.setEnabled(True)



def preset_valid(preset):
	return preset and type(preset) is dict and \
		'name' in preset and 'preset' in preset and type(preset['preset']) is dict