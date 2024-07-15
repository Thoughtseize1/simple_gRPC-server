import sys
import os

import grpc

sys.path.append(os.path.join(os.path.dirname(__file__), "../protos"))

from protos import file_manager_pb2, file_manager_pb2_grpc


def run_task(task, *args, **kwargs):
    connection_path = "localhost:50051"
    print(f"Attempting to connect to connection_path {connection_path}...")
    with grpc.insecure_channel(connection_path) as channel:
        try:
            grpc.channel_ready_future(channel).result(timeout=10)
            print("Connected to the server!")
            stub = file_manager_pb2_grpc.FileExchangerStub(channel)
            task(stub, *args, **kwargs)
        except grpc.FutureTimeoutError:
            print("Failed to connect to the server.")


def list_of_files(stub, path=".", show_hidden_files=True):
    """
    Lists files in a specified directory through a gRPC stub.
    This function sends a request to a gRPC server to list files in a specified directory.
    It can optionally include hidden files in the listing based on the `show_hidden_files` flag.
    Args:
        stub: The gRPC stub for communicating with the server.
        path (str): The path of the directory to list files from. Defaults to '/home/msher/Downloads'.
        show_hidden_files (bool): Flag to determine if hidden files should be included. Defaults to False.
    Prints:
        A list of files in the specified directory, including the name, size, and path of each file.
    """
    request = file_manager_pb2.Request(path=path, show_hidden_files=show_hidden_files)
    response = stub.ListFiles(request)
    print(f"Received files in directory '{os.path.abspath(response.path)}':")
    for file in response.files:
        print(f"Name: {file.name}, Size: {file.size} bytes, Path: {file.path}")


def download_file(
    stub,
    file_path="./my_file.txt",
    is_absolute=True,
):
    """
    Downloads a file from a gRPC server and saves it locally.

    This function sends a request to a gRPC server to download a file. The file can be specified
    either by an absolute path or a relative file name, based on the `is_absolute` flag. The downloaded
    file's contents are accumulated in memory before being written to a file in a 'downloads' directory
    within the current working directory. If the 'downloads' directory does not exist, it is created.
    Args:
        stub: The gRPC stub for communicating with the server.
        file_path (str): The path or name of the file to download. Defaults to './my_file.txt'.
        is_absolute (bool): Flag to determine if `file_path` is an absolute path or a file name. Defaults to True.
    Creates:
        A 'downloads' directory in the current working directory if it does not exist.
    Saves:
        The downloaded file in the 'downloads' directory.
    Prints:
        A success message with the file path if the download is successful.
        An error message with the file path and error details if the download fails.
    """

    if is_absolute:
        request = file_manager_pb2.DownloadRequest(absolute_path=file_path)
    else:
        request = file_manager_pb2.DownloadRequest(file_name=file_path)
    try:
        response = stub.DownloadFile(request)
        file_contents = b""
        for chunk in response:
            file_contents += chunk.chunk
        if file_contents:
            download_dir = os.path.join(os.getcwd(), "downloads")
            os.makedirs(download_dir, exist_ok=True)
            save_path = os.path.join(download_dir, os.path.basename(file_path))
            with open(save_path, "wb") as file:
                file.write(file_contents)
            print(f"File {file_path} downloaded successfully.")
    except grpc.RpcError as error:
        print(f"Error downloading file {file_path}: {error.code()}. {error.details()}")


if __name__ == "__main__":
    run_task(download_file, file_path="my_file2.txt", is_absolute=False)
