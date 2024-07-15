import os
import sys

import pytest
from unittest.mock import patch, MagicMock, mock_open


sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")
sys.path.append(os.path.join(os.path.dirname(__file__), "../protos"))

from protos import file_manager_pb2
from client.client import download_file, list_of_files


@pytest.fixture
def mock_file_system():
    with (
        patch("os.listdir") as mock_listdir,
        patch("os.path.isfile") as mock_isfile,
        patch("os.stat") as mock_stat,
    ):

        mock_listdir.return_value = ["file1.txt", "file2.txt", ".hidden_file"]
        mock_isfile.side_effect = lambda path: not os.path.isdir(path)
        mock_stat.return_value = MagicMock(st_size=100)
        yield mock_listdir, mock_isfile, mock_stat


@pytest.fixture
def mock_stub():
    with patch("client.client.file_manager_pb2_grpc.FileExchangerStub") as mock:
        yield mock.return_value


@pytest.fixture
def mock_response():
    response = MagicMock()
    response.chunk = b"Test data"
    return [response]


def test_successful_download_creates_downloads_directory_if_not_exists(
    mock_stub, mock_response
):
    with (
        patch("os.makedirs") as mock_makedirs,
        patch("builtins.open", mock_open()),
        patch.object(mock_stub, "DownloadFile", return_value=mock_response),
    ):
        download_file(
            stub=mock_stub,
            file_path="test_file.txt",
            is_absolute=True,
        )
        mock_makedirs.assert_called_once_with(
            os.path.join(os.getcwd(), "downloads"), exist_ok=True
        )


def test_list_of_files(mock_stub):
    file1 = file_manager_pb2.Response.File(
        name="file1.txt", size="100", path="/path/to/file1.txt"
    )
    file2 = file_manager_pb2.Response.File(
        name="file2.txt", size="200", path="/path/to/file2.txt"
    )
    response = file_manager_pb2.Response(path="/path/to", files=[file1, file2])
    mock_stub.ListFiles.return_value = response
    with patch("builtins.print") as mock_print:
        list_of_files(mock_stub, path="/path/to", show_hidden_files=False)
        mock_print.assert_any_call("Received files in directory '/path/to':")
        mock_print.assert_any_call(
            "Name: file1.txt, Size: 100 bytes, Path: /path/to/file1.txt"
        )
        mock_print.assert_any_call(
            "Name: file2.txt, Size: 200 bytes, Path: /path/to/file2.txt"
        )
