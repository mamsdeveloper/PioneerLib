import socket
from datetime import datetime
from threading import Thread
from typing import Iterable, Sequence
import cv2
import numpy as np

from pioneer_sdk import Pioneer

LOG_DISCONNECTED = (
	'Drone is not connected.',
	'Connect to drone Wi-Fi and call Drone.connect()'
)
LOG_GET_FRAME_DENY = ('Camera frame getting denied', )
LOG_LED_INCORRECT_INDEX = (
	'Incorrect led index or color',
	'Led index must be in range from 0 to 3, or 255 for set all led'
)
LOG_LED_INCORRECT_COLOR = (
	'Incorrect led color format'
	'Color must have format [r, g, b], when each item is float in range from 0 to 255.0'
)


class Drone():
	def __init__(self, loging: bool = False) -> None:
		self.move = False

		self.__loging = loging
		self.__log(*LOG_DISCONNECTED)
		self.__target = False
		return
		try:
			self.__drone = Pioneer(logger=False)
		except socket.error:
			self.__log(*LOG_DISCONNECTED)
			self.__drone = None

		Thread(target=self.__update_thread).start()

	def arm(self):
		self.__drone.arm()

	def connect(self) -> bool:
		if self.__drone is None:
			try:
				self.__drone = Pioneer(logger=False)
			except socket.error:
				self.__log(*LOG_DISCONNECTED)
				self.__drone = None

	def disarm(self):
		self.__drone.disarm()

	def get_camera_frame_array(self) -> np.array:
		frame = self.get_camera_frame_bytes()
		try:
			img = cv2.imdecode(
                            np.frombuffer(frame, dtype=np.uint8),
                            cv2.IMREAD_COLOR
                        )
		except:
			img = None
		return img

	def get_camera_frame_bytes(self) -> bytes:
		try:
			frame = self.__drone.get_raw_video_frame()
		except socket.error:
			self.__log(LOG_GET_FRAME_DENY)
			frame = None
		return frame

	def go_to_point(
		self,
		x: float = None, y: float = None, z: float = None,
		vx: float = None, vy: float = None, vz: float = None,
		ax: float = None, ay: float = None, az: float = None,
		angle: float = None
	):
		self.__target = True

	def land(self):
		self.__drone.land()

	def set_led(self, led_id: int, color: tuple[int, int, int]):
		try:
			self.__drone.led_control(led_id, *color)
		except IndexError:
			self.__log(LOG_LED_INCORRECT_INDEX)
		except ValueError:
			self.__log(LOG_LED_INCORRECT_COLOR)

	def set_leds(self, colors: Sequence[tuple[int, int, int]]):
		colors = list(colors)
		colors = colors[:3]
		for i, color in enumerate(colors):
			self.set_led(i, color)

	def takeoff(self):
		self.__drone.takeoff()

	def __log(self, *messages: str):
		Thread(target=self.__log_thread, args=(messages, )).start()

	def __log_thread(self, *messages: str):
		strtime = datetime.now().strftime('%d.%m.%y %H:%M:%S')
		strtime = f'[{strtime}]'

		with open('log.log', 'a') as log:
			log.write(strtime + '\n')
			if self.__loging:
				print(strtime)

			for msg in messages:
				line = f'"{msg}"'
				log.write(line + '\n')
				if self.__loging:
					print(f'"{line}"')

	def __update_thread(self):
		self.moving = self.__drone.point_reached() & self.__target


if __name__ == '__main__':
	Drone()
