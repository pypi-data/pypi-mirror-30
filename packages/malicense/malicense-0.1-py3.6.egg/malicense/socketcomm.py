''' malicense.socketcomm.py '''

import socket
import time
import sys

def sendMessage(hostname, port, message):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (hostname, port)
    try:
        sock.connect(server_address)
        try:
            # Send data
            sock.sendall(message.encode())
        finally:
            sock.close()
    except:
        # Fail quietly
        pass

# Logger settings
timeFormat = '%Y-%m-%d.%H:%M:%S'

def startServer(port):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ('', port)
    print('starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)

    while True:
        # Wait for a connection
        try:
            connection, client_address = sock.accept()
        except KeyboardInterrupt:
            sys.exit(0)
        client_ip, client_port = client_address
        access_time = time.gmtime()

        try:
            # Receive the data in small chunks
            full_data = ''
            while True:
                try:
                    data = connection.recv(16).decode()
                except:
                    full_data += '...CORRUPTED'
                    break
                if data:
                    full_data += data
                else:
                    break

        finally:
            # Clean up the connection
            connection.close()

        # Log this access
        accInfo = (time.strftime(timeFormat, access_time), client_ip, full_data)
        yield accInfo
