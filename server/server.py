import sys
import os

import grpc
from concurrent import futures

print("sys.path:", sys.path)
sys.path.append(os.path.join(os.path.dirname(__file__), '../protos'))
print(__file__)

from protos import file_manager_pb2
from protos import file_manager_pb2_grpc


class FileExchangerServicer(file_manager_pb2_grpc.FileExchangerServicer):
	def ListFiles(self, request, context):
		path = os.path.abspath(path=request.path)
		show_hidden_files = request.show_hidden_files
		files = []
		for file in os.listdir(path):
			if file.startswith('.') and not show_hidden_files:
				continue
			filepath = os.path.join(path, file)
			if os.path.isfile(filepath):
				file_stat = os.stat(filepath)
				file_info = file_manager_pb2.Response.File(
					name=file,
					size=str(file_stat.st_size),
					path=filepath
				)
				files.append(file_info)
		print(f"Received request for file {os.path.abspath('.')}. HIDDEN FILES = {request.show_hidden_files}")
		return file_manager_pb2.Response(path=path, files=files)


def serve():
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
	file_manager_pb2_grpc.add_FileExchangerServicer_to_server(FileExchangerServicer(), server)
	server.add_insecure_port('[::]:50051')
	server.start()
	print("Server started on port 50051 and listening on all network interfaces (IPv4 and IPv6)")
	server.wait_for_termination()
	print("Server is running...")


if __name__ == '__main__':
	serve()
