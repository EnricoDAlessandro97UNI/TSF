# TSF - File Transfer Client and Server

This is a simple client-server application written in Python for transferring files over a network. The application allows you to download files from the server to your local machine.

## Features

- File transfer from server to client
- Progress bar to track download progress
- Error handling for connection issues and file availability

## Requirements

- Python 3.x

## Usage

### Server

1. Open a terminal and navigate to the directory containing the server files.
2. Run the server script using the following command:
    ```
    python server.py
    ```
3. The server will start listening for incoming connections on port 12345.

### Client

1. Open a terminal and navigate to the directory containing the client files.
2. Run the client script using the following command:
    ```
    python client.py
    ```
3. Enter the IP address of the server when prompted.
4. Enter the remote file path of the file you want to download from the server.
5. Enter the local directory where you want to save the downloaded file.
6. Click the "Download" button to initiate the file transfer.

## Note

- Make sure both the client and server are running on the same network.
- The server must be started before running the client.
- If the specified file is not available on the server, an appropriate error message will be displayed.

## Author

- Enrico D'Alessandro

Feel free to modify and enhance this application as per your requirements.

Happy file transferring!
