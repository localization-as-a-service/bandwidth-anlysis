import socket
import threading
import time
import numpy as np
from io import BytesIO


def recv(conn):
    length = None
    buffer = bytearray()
    while True:
        data = conn.recv(1024)
        buffer += data
        
        if len(buffer) == length:
            break
        
        if length is None: 
            if b':' in buffer:
                length_str, _, buffer = buffer.partition(b':')
                length = int(length_str)
            if b'done' in buffer:
                return None
                
    return np.load(BytesIO(buffer))['frame']


# Function to handle each client connection
def handle_client(conn, addr):
    print(f"New client connected: {addr}")

    while True:
        try:
            data = recv(conn)
            print(f"Received data: {data.shape if data is not None else 'None'}")
        
            # If the data is not empty, send a success message back to the client
            if data is not None:
                message = "Data received successfully"
                conn.sendall(message.encode())
                
            if data is None:
                print("Client disconnected")
                break
                
            time.sleep(0.001)
        except KeyboardInterrupt:
            break
    
    conn.close()
    print(f"Client disconnected: {addr}")


if __name__ == "__main__":
    # Define the IP address and port number
    ip = "192.168.10.109"
    port = 5001

    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the IP address and port number
    s.bind((ip, port))

    # Listen for incoming connections
    s.listen()
    print(f"Listening on {ip}:{port}")

    # Main loop to accept new client connections
    try:
        while True:
            conn, addr = s.accept()
            # Start a new thread to handle the client connection
            t = threading.Thread(target=handle_client, args=(conn, addr))
            t.start()
    except KeyboardInterrupt:
        print("Server shutting down...")
        s.close()