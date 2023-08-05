from PyQt5 import QtWidgets, QtCore
import sys


def render(table_view, data_to_render):
	TableRenderer(table_view, data_to_render)


class TableRenderer():
	def __init__(self, table_view, data_to_render):
		self.table_view = table_view
		self.table_view.setFocusPolicy(QtCore.Qt.NoFocus)
		self.table_view.horizontalHeader().hide()
		self.table_view.verticalHeader().hide()
		
		if type(data_to_render) is list or type(data_to_render) is dict:
			self.data_to_render = data_to_render
		else:
			self.data_to_render = {}
		
		self.show_table([])

	def show_table(self, path):
		# find frame according to path
		current_frame = self.data_to_render
		for level in path:
			current_frame = current_frame[level]

		# check if we are not on top frame
		nested = False
		if len(path):
			nested = True

		# create model for current frame and show it in view
		new_model = TableModel(current_frame, nested)
		self.table_view.setModel(new_model)
		self.table_view.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

		# also apply navigation widgets to view
		if nested:
			# add possibility to go to parent frame
			# first row is 'Up' button
			parent_path = list(path)
			del parent_path[-1]
			row_index = new_model.index(0, 1)
			navigation_btn = NavigationButton('..', self, parent_path)
			self.table_view.setIndexWidget(row_index, navigation_btn)

		# check either we will iterate over dict or list
		current_frame_is_list = (type(current_frame) is list)

		# apply widgets for navigation to child objects
		child_index = 0
		for child in current_frame:
			if current_frame_is_list:
				child = child_index

			# check if navigation button is needed
			child_is_object = type(current_frame[child]) is list or type(current_frame[child]) is dict

			if child_is_object:
				model_row_number = child_index
				if nested:
					model_row_number = child_index + 1

				row_index = new_model.index(model_row_number, 1)
				child_path = list(path)
				child_path.append(child)

				navigation_btn = NavigationButton(str(len(current_frame[child])), self, child_path)
				self.table_view.setIndexWidget(row_index, navigation_btn)

			child_index = child_index + 1


class TableModel(QtCore.QAbstractTableModel):
	def __init__(self, data, has_parent):
		super().__init__()
		self.table_data = data
		self.has_parent = has_parent

	def rowCount(self, index):
		if self.has_parent:
			# reserve placeholder for navigation to parent model
			return len(self.table_data) + 1
		else:
			return len(self.table_data)

	def columnCount(self, index):
		return 2

	def flags(self, index):
		flags = QtCore.Qt.ItemIsEnabled
		return flags

	def data(self, index, role):
		row = index.row()
		get_key = (index.column() == 0)

		if role == QtCore.Qt.DisplayRole:
			if self.has_parent and row == 0:
				# return placeholder for navigation to parent model
				return '..'

			if self.has_parent:
				row = row - 1

			requested_key = None

			if type(self.table_data) is list:
				requested_key = row
			elif type(self.table_data) is dict:
				requested_key = list(self.table_data.keys())[row]

			if get_key:
				# requested column with keys
				return requested_key
			else:
				# requested column with values
				elem_type = type(self.table_data[requested_key])
				if elem_type is not dict and elem_type is not list:
					# element is trivial value
					# simply render it
					return self.table_data[requested_key]
				else:
					# element is object
					# return placeholder for navigation to it's model
					return 'object placeholder'


class NavigationButton(QtWidgets.QPushButton):
	def __init__(self, label, tables_manager, path):
		super().__init__(label)
		self.tables_manager = tables_manager
		self.path = path

	def mousePressEvent(self, event):
		self.tables_manager.show_table(self.path)


if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	test_widget = QtWidgets.QWidget()
	l = QtWidgets.QHBoxLayout()

	tv = QtWidgets.QTableView()
	tv.setFocusPolicy(QtCore.Qt.NoFocus)
	tv.horizontalHeader().hide()
	tv.verticalHeader().hide()
	# data = {'k1': 5, 'k2': 'shse', 'k3': {'kd1': '4'}, 'k4': ['one', 'two', {'deep': 'inside'}]}
	# data = {'svc_error': 6}
	data = {"glossary":{"title":"exampleglossary","GlossDiv":{"title":"S","GlossList":{"GlossEntry":{"ID":"SGML","SortAs":"SGML","GlossTerm":"StandardGeneralizedMarkupLanguage","Acronym":"SGML","Abbrev":"ISO8879:1986","GlossDef":{"para":"Ameta-markuplanguage,usedtocreatemarkuplanguagessuchasDocBook.","GlossSeeAlso":["GML","XML"]},"GlossSee":"markup"}}}}}
	# data = None
	# data = [5, 'sss', 6]
	# data = 3
	tm = TableRenderer(tv, data)
	l.addWidget(tv)


	test_widget.setLayout(l)
	test_widget.show()
	sys.exit(app.exec_())
