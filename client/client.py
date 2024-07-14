import sys
import os

import grpc
import logging

print("sys.path:", sys.path)
sys.path.append(os.path.join(os.path.dirname(__file__), '../protos'))

from protos import file_manager_pb2
from protos import file_manager_pb2_grpc


def run():
	print("Attempting to connect to localhost:50051...")
	with grpc.insecure_channel('localhost:50051') as channel:
		try:
			grpc.channel_ready_future(channel).result(timeout=10)
			print("Connected to the server!")
		except grpc.FutureTimeoutError:
			print("Failed to connect to the server.")
			return

		stub = file_manager_pb2_grpc.FileExchangerStub(channel)
		request = file_manager_pb2.Request(path='/home/msher/Downloads', show_hidden_files=True)
		response = stub.ListFiles(request)
		print(f"Received files in directory '{os.path.abspath(response.path)}':")
		for file in response.files:
			print(f"Name: {file.name}, Size: {file.size}, Path: {file.path}")


if __name__ == '__main__':
	logging.basicConfig(level=logging.CRITICAL)
	run()
