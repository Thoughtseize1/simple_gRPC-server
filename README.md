# Server Overview
### Features:
* List Files: Retrieves a list of files in a specified directory, optionally including hidden files.
* Download File: Allows downloading of files by either absolute path or file name.

## Installation
1. Clone the repository and go to project directory:
   ```
   git clone https://github.com/Thoughtseize1/simple_gRPC-server
   cd <path to your directory with all project files>
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
6. Start the server from main directory
   ```
   python -m server.server
   ```

6. Start the client from main directory
   ```
   python -m client.client
   ```
9. Run tests using pytest:
   ```
   pytest
   ```
   
### Customizable Parameters in client.py
* The `download_file` function in client.py allows for downloading files from a gRPC server. It includes the following customizable parameters:

`file_path`: Specifies the path or name of the file to be downloaded.
Usage: This parameter determines which file to download from the server. It can be an absolute path or a relative file name, depending on the value of is_absolute.

`is_absolute`: Boolean flag to indicate whether file_path is an absolute path (True) or a relative file name (False).
Usage: Set this parameter based on whether file_path represents an absolute file path or a relative file name within the server's file system.


* The `list_of_files` function in client.py retrieves a list of files from a specified directory on the gRPC server. It supports customization through the following parameters:

`path`: Specifies the directory path from which to list files.
Usage: Use this parameter to specify the directory path on the server where files should be listed. Defaults to '.' for the current directory.

`show_hidden_files`: Boolean flag to determine whether to include hidden files in the listing (True) or not (False).
Usage: Toggle this parameter to control whether hidden files (files whose names start with '.') are included in the list of files retrieved from the server.

* The `run_task` function in client.py is a utility function used to execute tasks with a gRPC stub, such as `download_file` or `list_of_files`.
Usage: Pass either `download_file` or `list_of_files` as the first argument to run_task, followed by the appropriate parameters (stub, file_path, is_absolute for `download_file`; stub, path, show_hidden_files for `list_of_files`).
