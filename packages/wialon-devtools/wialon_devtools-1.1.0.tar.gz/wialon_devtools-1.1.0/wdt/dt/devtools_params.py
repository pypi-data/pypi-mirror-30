from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit, QInputDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize


def render(layout, elem, update_cb, location=None, add_deleter=False):
	if type(elem) is dict:
		dict_widget = render_dictionary(elem, update_cb, location, add_deleter)
		layout.addWidget(dict_widget)
	elif type(elem) is list:
		list_widget = render_list(elem, update_cb, location, add_deleter)
		layout.addWidget(list_widget)
	else:
		# HBox
		le = DictValue(elem, location)
		le.setStyleSheet("background-color: white;")
		layout.addWidget(le)
		if add_deleter:
			layout.addWidget(Deleter(location, update_cb))
		layout.addStretch(1)


def render_dictionary(elem, update_cb, location, add_deleter):
	dict_widget = QWidget()
	dict_layout = QVBoxLayout()

	dict_start = QHBoxLayout()
	dict_start.addWidget(QLabel('{'))

	dict_start.addWidget(DictAdder({}, elem, '{ }', update_cb))
	dict_start.addWidget(DictAdder([], elem, '[ ]', update_cb))
	dict_start.addWidget(DictAdder('', elem, '+', update_cb))
	if add_deleter and location:
		dict_start.addWidget(Deleter(location, update_cb))

	dict_start.addStretch(1)

	dict_layout.addLayout(dict_start) # start

	# render dictionary fields
	for (k, v) in elem.items():
		field_layout = QHBoxLayout()

		field_layout.addWidget(QLabel('    ')) # add indentation

		delete_layout = QVBoxLayout()
		delete_layout.addWidget(Deleter((elem, k), update_cb)) # add indentation
		delete_layout.addStretch(1)

		field_layout.addLayout(delete_layout)

		label_layout = QVBoxLayout()
		label_layout.addWidget(DictKey(k, elem, update_cb))
		label_layout.addStretch(1)
		field_layout.addLayout(label_layout) # add dictionary key

		render(field_layout, v, update_cb, (elem, k), False) # add dictionary value

		dict_layout.addLayout(field_layout)

	dict_layout.addWidget(QLabel('}')) # finish
	dict_widget.setLayout(dict_layout)
	dict_widget.setStyleSheet("background-color: #e7fcca; opacity: 0.5");

	return dict_widget


def render_list(elem, update_cb, location, add_deleter):
	list_widget = QWidget()
	list_layout = QVBoxLayout()

	list_start = QHBoxLayout()
	list_start.addWidget(QLabel('['))

	list_start.addWidget(ListAdder({}, elem, '{ }', update_cb))
	list_start.addWidget(ListAdder([], elem, '[ ]', update_cb))
	list_start.addWidget(ListAdder('', elem, '+', update_cb))
	if add_deleter and location:
		list_start.addWidget(Deleter(location, update_cb))
	list_start.addStretch(1)

	list_layout.addLayout(list_start) # start

	elem_ind = 0
	for i in elem:
		cell_layout = QHBoxLayout()
		cell_layout.addWidget(QLabel('    '))
		render(cell_layout, i, update_cb, (elem, elem_ind), True)
		elem_ind = elem_ind + 1	
		list_layout.addLayout(cell_layout)

	list_layout.addWidget(QLabel(']')) # finish
	list_widget.setLayout(list_layout)
	list_widget.setStyleSheet("background-color: #d1f396");

	return list_widget


class DictKey(QLabel):
	def __init__(self, key, location, update_cb):
		super().__init__(key + ':')
		self.key = key
		self.location = location
		self.update = update_cb

	def mousePressEvent(self, event):
		if self.location == None:
			return

		new_key = QInputDialog.getText(self, "Rename element", "Enter key:", QLineEdit.Normal, self.key)

		if not new_key[1] or not new_key[0]:
			return # Cancelled

		if new_key[0] in self.location:
			return

		self.location[new_key[0]] = self.location[self.key]
		del self.location[self.key]

		self.update()


class DictValue(QLineEdit):
	def __init__(self, elem, location):
		super().__init__(str(elem))
		self.elem = elem
		self.location = location
		self.textChanged.connect(self.edit)

	def edit(self, value):
		parent = self.location[0]
		index_in_parent = self.location[1]
		parent[index_in_parent] = value


class Adder(QPushButton):
	def __init__(self, value, location, label, update_cb):
		super().__init__(label)
		self.setStyleSheet('font-size: 8pt')
		self.setFixedSize(20, 20)
		# self.setIcon(icon)
		# self.setIconSize(QSize(12, 12))
		# print(super().iconSize())
		self.value = value
		self.location = location
		self.update = update_cb


class ListAdder(Adder):
	def mousePressEvent(self, event):
		if self.location == None:
			return
		self.location.append(self.value)

		self.update()


class DictAdder(Adder):
	def mousePressEvent(self, event):
		if self.location == None:
			return

		key = ''
		for i in range(0, 1000):
			new_key = 'key_' + str(i)
			if new_key not in self.location:
				key = new_key
				break

		if not key:
			return

		text = QInputDialog.getText(self, "New element", "Enter key:", QLineEdit.Normal, key)

		if not text[1] or not text[0]:
			return # Cancelled

		self.location[text[0]] = self.value

		self.update()


class Deleter(QPushButton):
	def __init__(self, location, update_cb):
		super().__init__()
		super().setIcon(QIcon('images/delete.png'))
		super().setIconSize(QSize(8, 8))
		self.location = location
		self.update = update_cb

	def mousePressEvent(self, event):
		if self.location == None:
			return
		parent = self.location[0]
		index_in_parent = self.location[1]
		del parent[index_in_parent]

		self.update()
