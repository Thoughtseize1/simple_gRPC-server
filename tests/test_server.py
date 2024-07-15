import pytest
import grpc
from server.server import FileExchangerServicer
from protos import file_manager_pb2


@pytest.fixture
def servicer():
    return FileExchangerServicer()


@pytest.fixture
def context():
    class FakeContext:
        def __init__(self):
            self.code = None
            self.details = None

        def set_code(self, code):
            self.code = code

        def set_details(self, details):
            self.details = details

    return FakeContext()


def test_list_files_in_directory_includes_all_files(servicer, context):
    request = file_manager_pb2.Request(path=".", show_hidden_files=False)
    response = servicer.ListFiles(request, context)
    assert (
        len(response.files) > 0
    )  # Assuming there's at least one file in the current directory


def test_list_files_in_directory_excludes_hidden_files(servicer, context):
    request = file_manager_pb2.Request(path=".", show_hidden_files=False)
    response = servicer.ListFiles(request, context)
    assert all(not file.name.startswith(".") for file in response.files)


def test_list_files_in_directory_includes_hidden_files_when_requested(
    servicer, context
):
    request = file_manager_pb2.Request(path="tests/", show_hidden_files=True)
    response = servicer.ListFiles(request, context)
    assert any(file.name.startswith(".") for file in response.files)


def test_download_file_sends_chunks_for_existing_file(servicer, context):
    request = file_manager_pb2.DownloadRequest(file_name="tests/test_data.txt")
    response = list(servicer.DownloadFile(request, context))
    assert len(response) > 0  # Assuming 'test_data.txt' exists and is not empty


def test_download_file_sets_not_found_status_for_nonexistent_file(servicer, context):
    request = file_manager_pb2.DownloadRequest(file_name="nonexistent_file.txt")
    list(servicer.DownloadFile(request, context))
    assert context.code == grpc.StatusCode.NOT_FOUND


def test_download_file_sets_not_found_status_for_directory_request(servicer, context):
    request = file_manager_pb2.DownloadRequest(file_name="test_folder_which_not_exists")
    list(servicer.DownloadFile(request, context))
    assert (
        context.code == grpc.StatusCode.NOT_FOUND
    )  # Assuming requesting a directory instead of a file
