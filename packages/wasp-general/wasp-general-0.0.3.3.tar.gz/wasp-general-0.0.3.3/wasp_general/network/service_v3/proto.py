# -*- coding: utf-8 -*-
# wasp_general/network/service_v2/proto.py
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

from wasp_general.verify import verify_type, verify_subclass
from wasp_general.uri import WURI, WSchemeHandler, WSchemeCollection
from wasp_general.config import WConfigSelection


# noinspection PyAbstractClass
class WServiceSocketProto(WSchemeHandler):

	@abstractmethod
	@verify_type(config_selection=WConfigSelection)
	def configure_socket(self, config_selection):
		raise NotImplementedError('This method is abstract')

	@classmethod
	def scheme_specification(cls):
		""" Return scheme specification

		:return: WSchemeSpecification
		"""
		raise NotImplementedError('This method is abstract')

	@classmethod
	@verify_type(uri=WURI)
	def create_handler(cls, uri, **kwargs):
		pass


class WSocketFactoryProto(WSchemeCollection):

	@verify_type(uri=WURI, config_selection=WConfigSelection)
	def create_socket(self, uri, config_selection):
		handler = self.open(uri)
		handler.configure_socket(config_selection)
		return handler

	@verify_subclass(scheme_handler_cls=WServiceSocketProto)
	def add(self, scheme_handler_cls):
		return WSchemeCollection.add(self, scheme_handler_cls)


class WPollingHandlerProto(metaclass=ABCMeta):

	class PollingError(Exception):

		def __init__(self, *file_objects):
			Exception.__init__(self, 'Error during polling file-objects')
			self.__file_objects = file_objects

		def file_objects(self):
			return self.__file_objects

	class PollingEvent(Enum):
		read = 1
		write = 2

	def __init__(self):
		self.__file_obj = None
		self.__event_mask = None
		self.__timeout = None

	def file_obj(self):
		return tuple(self.__file_obj)

	def event_mask(self):
		return self.__event_mask

	def timeout(self):
		return self.__timeout

	def setup_poll(self, event_mask, timeout):
		if isinstance(event_mask, WPollingHandlerProto.PollingEvent) is True:
			event_mask = event_mask.value
		self.__event_mask = event_mask
		self.__timeout = timeout
		self.__file_obj = []

	def poll_fd(self, file_obj):
		if self.__file_obj is None:
			raise RuntimeError('!')
		self.__file_obj.append(file_obj)

	@abstractmethod
	def polling_function(self):
		raise NotImplementedError('This method is abstract')


class WServiceWorkerProto(metaclass=ABCMeta):

	@abstractmethod
	def process(self, socket_obj):
		raise NotImplementedError('This method is abstract')


class WServiceFactoryProto(metaclass=ABCMeta):

	@abstractmethod
	def worker(self, stop_event):
		raise NotImplementedError('This method is abstract')
