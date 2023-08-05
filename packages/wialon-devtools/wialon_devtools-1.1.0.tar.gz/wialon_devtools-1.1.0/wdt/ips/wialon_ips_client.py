from PyQt5 import QtNetwork, QtCore

from PyCRC.CRC16 import CRC16
import datetime

class WialonIPSClient(QtCore.QObject):
	def __init__(self, logger_callback):
		super().__init__()
		self.log = logger_callback
		self.ip = '193.193.165.165'
		self.port = 20332
		self.socket = QtNetwork.QTcpSocket()
		self.socket.readyRead.connect(self.read_answer)
		self.socket.connected.connect(self.handle_connected)
		self.socket.disconnected.connect(self.handle_disconnected)
		self.socket.error.connect(self.handle_error)

	connected = QtCore.pyqtSignal()
	disconnected = QtCore.pyqtSignal()
	error_occured = QtCore.pyqtSignal()


	def connect(self):
		if not self.ip or not self.port:
			self.log('Specify host to connect')
			self.error_occured.emit()
			return
		if self.socket.state() != QtNetwork.QAbstractSocket.UnconnectedState:
			self.log('Socket is connected already')
			self.error_occured.emit()
			return
		self.socket.connectToHost(self.ip, self.port)
		self.log('Connecting...')


	def handle_connected(self):
		log_msg = 'Connected to {}:{}'.format(self.socket.peerAddress().toString(), self.socket.peerPort())
		self.log(log_msg)
		self.connected.emit()


	def disconnect(self):
		self.socket.disconnectFromHost()


	def handle_disconnected(self):
		log_msg = 'Disconnected from {}:{}'.format(self.socket.peerAddress().toString(), self.socket.peerPort())
		self.log(log_msg)
		self.disconnected.emit()


	def handle_error(self):
		self.log(self.socket.errorString())
		self.error_occured.emit()


	def login(self, object_id, object_password):
		self.send_packet('L', True, '2.0', object_id, object_password)


	def ping(self):
		self.send_packet('P', False)


	def send_short_data(self, lat, lon, speed, course, height, sats):
		lat1 = 0
		try:
			lat1 = float(lat)
		except:
			pass
		lat2 = 'N'
		if lat1 < 0:
			lat2 = 'S'
			lat1 = lat1 * -1
		lon1 = 0
		try:
			lon1 = float(lon)
		except:
			pass
		lon2 = 'E'
		if lon1 < 0:
			lon2 = 'W'
			lon1 = lon1 * -1
		self.send_packet('SD', True, GET_DATE(), GET_TIME(), lat1, lat2, lon1, lon2, speed, course, height, sats)


	def send_file(self, file_path):
		if self.socket.isValid() and self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
			file_content = None
			with open(file_path, mode='rb') as file:
			    file_content = file.read()
			crc16 = hex(CRC16().calculate(file_content))[2:].upper()
			self.send_packet('I', False, len(file_content), '0', '0', GET_DATE(), GET_TIME(), 'dt.jpg', crc16)
			self.socket.write(file_content)
		else:
			self.log('Failed to send file. Socket state is {}'.format(self.socket.state()))


	def send_packet(self, packet_type, calc_crc, *args):
		if self.socket.isValid() and self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
			packet_header = '#' + packet_type + '#'
			packet_body = ';'.join('NA' if not arg else str(arg) for arg in args)
			if calc_crc:
				packet_body = packet_body + ';'
				crc16 = CRC16().calculate(packet_body.encode())
				packet_body = packet_body + hex(crc16)[2:].upper()
			packet = packet_header + packet_body + '\r\n'
			self.log(packet)
			self.socket.write(packet.encode())
		else:
			self.log('Failed to send packet. Socket state is {}'.format(self.socket.state()))

	def read_answer(self):
		if self.socket.bytesAvailable():
			answer = self.socket.readAll().data().decode()
			self.log(answer)


	def set_ip(self, ip):
		self.ip = ip


	def set_port(self, port):
		if not port:
			self.port = 0
		else:
			self.port = int(port)


	# def abort(self):
	# 	self.socket.abort()


def GET_DATE():
	return datetime.datetime.utcnow().strftime('%d%m%y')


def GET_TIME():
	return datetime.datetime.utcnow().strftime('%H%M%S')
