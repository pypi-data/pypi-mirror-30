# -*- coding: utf-8 -*-
# wasp_general/<FILENAME>.py
#
# Copyright (C) 2018 the wasp-general authors and contributors
# <see AUTHORS file>
#
# This file is part of wasp-general.
#
# wasp-general is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wasp-general is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with wasp-general.  If not, see <http://www.gnu.org/licenses/>.

# TODO: document the code
# TODO: write tests for the code

# noinspection PyUnresolvedReferences
from wasp_general.version import __author__, __version__, __credits__, __license__, __copyright__, __email__
# noinspection PyUnresolvedReferences
from wasp_general.version import __status__

from abc import ABCMeta, abstractmethod
from enum import Enum
from threading import Event, Semaphore, Thread
from select import select
from datetime import timedelta

from wasp_general.verify import verify_type
from wasp_general.network.service_v3.proto import WPollingHandlerProto


class WSelectPollingHandler(WPollingHandlerProto):

	def polling_function(self):
		r_list = []
		w_list = []
		x_list = []

		fds = self.file_obj()
		event_mask = self.event_mask()

		if event_mask >> 0 & 1:
			r_list.extend(fds)
		if event_mask >> 1 & 1:
			w_list.extend(fds)
		x_list.extend(fds)

		function_args = (r_list, w_list, x_list, self.timeout())

		def result():
			r_list, w_list, x_list = select(
				function_args[0], function_args[1], function_args[2], function_args[3]
			)
			if len(x_list) > 0:
				raise WPollingHandlerProto.PollingError(*x_list)

			if len(r_list) == 0 and len(w_list) == 0:
				return

			return r_list, w_list

		return result


'''
class WSimpleClientConnectionHandler(WClientConnectionHandlerProto):

	def __init__(self):
		pass




class WSimpleConnectionHandler(WAcceptConnectionHandlerProto):

	def __init__(self, maximum_threads):
		self.__maximum_threads = maximum_threads
		self.__semaphore = Semaphore(maximum_threads)
		self.__threads = []

	def maximum_threads(self):
		return self.__maximum_threads

	def semaphore(self):
		return self.__semaphore

	def handle_connection(self, socket_obj):

		def threading_fn():
			try:
				print('read from socket')
				print(socket_obj)
				client = socket_obj.accept()

			finally:
				self.semaphore().release()

		self.semaphore().acquire()
		th = Thread(target=threading_fn)
		th.start()
		self.__threads.append(th)
'''


class WNetworkService(metaclass=ABCMeta):

	__default_timeout__ = 1

	@verify_type(timeout=(int, None))
	def __init__(self, socket_obj, service_factory, stop_event=None, timeout=None, polling_handler=None):
		self.__socket_obj = socket_obj
		self.__service_factory = service_factory
		self.__timeout = timeout if timeout is not None else self.__default_timeout__
		self.__stop_event = stop_event if stop_event is not None else Event()
		self.__polling_handler = polling_handler if polling_handler is not None else WSelectPollingHandler()

	def socket(self):
		return self.__socket_obj

	def service_factory(self):
		return self.__service_factory

	def timeout(self):
		return self.__timeout

	def stop_event(self):
		return self.__stop_event

	def polling_handler(self):
		return self.__polling_handler

	def start(self):
		service_factory = self.service_factory()

		polling_handler = self.polling_handler()
		polling_handler.setup_poll(WPollingHandlerProto.PollingEvent.read, self.timeout())
		polling_handler.poll_fd(self.socket())

		polling_fn = polling_handler.polling_function()

		while self.stop_event().is_set() is False:
			polling_result = polling_fn()
			if polling_result is not None:
				connection = polling_result[0][0].accept()
				try:
					worker = service_factory.worker(self.stop_event())
					worker.process(connection[0])
				except RuntimeError:
					pass

	def stop(self):
		self.stop_event().set()
