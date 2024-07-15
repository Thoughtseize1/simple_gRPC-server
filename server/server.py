import sys
import os

import grpc
from concurrent import futures

sys.path.append(os.path.join(os.path.dirname(__file__), "../protos"))

from protos import file_manager_pb2
from protos import file_manager_pb2_grpc


class FileExchangerServicer(file_manager_pb2_grpc.FileExchangerServicer):
    def ListFiles(self, request, context):
        path = os.path.abspath(path=request.path)
        files = []
        for file in os.listdir(path):
            if file.startswith(".") and not request.show_hidden_files:
                continue
            filepath = os.path.join(path, file)
            if os.path.isfile(filepath):
                file_stat = os.stat(filepath)
                file_info = file_manager_pb2.Response.File(
                    name=file, size=str(file_stat.st_size), path=filepath
                )
                files.append(file_info)
        print(
            f"Received request for file {os.path.abspath('.')}. HIDDEN FILES = {request.show_hidden_files}"
        )
        return file_manager_pb2.Response(path=path, files=files)

    def DownloadFile(self, request, context):
        CHUNK_SIZE = 1024
        if request.HasField("absolute_path"):
            print("Requesting absolute path")
            file_path = request.absolute_path
        elif request.HasField("file_name"):
            print("Requesting file name")
            file_path = os.path.join(os.getcwd(), request.file_name)
        else:
            context.set_details("File not found")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return

        print("FILE_PATH = ", file_path)
        try:
            with open(file_path, "rb") as file:
                while True:
                    chunk = file.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    yield file_manager_pb2.FileChunkResponse(chunk=chunk)
        except Exception as error:
            context.set_details(str(error))
            context.set_code(grpc.StatusCode.NOT_FOUND)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    file_manager_pb2_grpc.add_FileExchangerServicer_to_server(
        FileExchangerServicer(), server
    )
    server.add_insecure_port("[::]:50051")
    server.start()
    print(
        "Server started on port 50051 and listening on all network interfaces (IPv4 and IPv6)"
    )
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
