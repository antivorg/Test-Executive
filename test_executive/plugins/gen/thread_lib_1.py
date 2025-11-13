
from threading import Lock, local
from queue import Queue, LifoQueue, PriorityQueue
from collections import deque

# This file has been automatically generated



def gui_input_handling(thread_io_dict):
	'''
		thread_io_dict:
		- type: <dict>
		- entrys:
			gui_in: type=<Queue>
			test_mutex: type=<Lock>
	'''
	with thread_io_dict["test_mutex"]:
		assert(type(thread_io_dict["gui_in"])==Queue)
	pass


def mutable(thread_io_dict):
	'''
		thread_io_dict:
		- type: <dict>
		- entrys:
			gui_in: type=<Queue>
			test_mutex: type=<Lock>
			start: type=<Lock>
	'''
	with thread_io_dict["test_mutex"]:
		assert(type(thread_io_dict["gui_in"])==Queue)
	pass


def everything(thread_io_dict):
	'''
		thread_io_dict:
		- type: <dict>
		- entrys:
			gui_in: type=<Queue>
			test_mutex: type=<Lock>
			start: type=<Lock>
			lifo: type=<LifoQueue>
			priority: type=<PriorityQueue>
			dewque: type=<deque>
			Lock: type=<Lock>
			areyalocal: type=<local>
			stwing: type=<str>
			iandcount: type=<int>
			whenigetintothepool: type=<float>
			imnotterribly: type=<complex>
			readmy: type=<list>
			ibeneedingthat: type=<dict>
			set: type=<set>
			isittruewhattheysay: type=<bool>
			dont: type=<bytes>
			many: type=<bytearray>
			nothing: type=<NoneType>
	'''
	with thread_io_dict["test_mutex"]:
		assert(type(thread_io_dict["gui_in"])==Queue)
		assert(type(thread_io_dict["lifo"])==LifoQueue)
		assert(type(thread_io_dict["priority"])==PriorityQueue)
		assert(type(thread_io_dict["dewque"])==deque)
		assert(type(thread_io_dict["areyalocal"])==local)
		assert(type(thread_io_dict["stwing"])==str)
		assert(type(thread_io_dict["iandcount"])==int)
		assert(type(thread_io_dict["whenigetintothepool"])==float)
		assert(type(thread_io_dict["imnotterribly"])==complex)
		assert(type(thread_io_dict["readmy"])==list)
		assert(type(thread_io_dict["ibeneedingthat"])==dict)
		assert(type(thread_io_dict["set"])==set)
		assert(type(thread_io_dict["isittruewhattheysay"])==bool)
		assert(type(thread_io_dict["dont"])==bytes)
		assert(type(thread_io_dict["many"])==bytearray)
	pass