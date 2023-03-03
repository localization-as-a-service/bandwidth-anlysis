import socket
import numpy as np
import pandas as pd
import time
import argparse

from io import BytesIO


def encode(data):
    f = BytesIO()
    np.savez(f, frame=data)
    
    packet_size = len(f.getvalue())
    header = '{0}:'.format(packet_size)
    # prepend length of array
    header = bytes(header.encode())  

    out = bytearray()
    out += header

    f.seek(0)
    out += f.read()
    return out


def connect(ip, port):
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    s.connect((ip, port))
    print(f"Connected to server on {ip}:{port}")
    return s


def send_data(s, data):
    start_time = time.time()
    s.sendall(encode(data))
    time_to_send = time.time() - start_time
    # print(f"Time taken to send: {end_time - start_time:0.4f} seconds")
    
    # Receive the response message from the server
    response = s.recv(1024)
    time_to_receive = time.time() - start_time
    
    # print(f"Rounoff time: {end_time - start_time:0.4f} seconds")

    # Print the response message
    print(f"Response: {response.decode()}")
    
    return time_to_send, time_to_receive


def main(ip, port, fname, device, wait):
    # Define the IP address and port number
    stats = []
    s = connect(ip, port)
    print("Connected to server on {ip}:{port}")
    
    pcds = np.load(fname, allow_pickle=True)
    
    for i in np.random.randint(0, len(pcds), 10000):
        try:
            time_to_send, time_to_receive = send_data(s, pcds[i])
            wait_time = np.random.poisson(wait) / 1e3
            stats.append([len(pcds[i]), wait_time, time_to_send, time_to_receive])
            print(f"Waiting for {wait_time:0.4f} seconds")
            time.sleep(wait_time)
        except KeyboardInterrupt:
            break
        
    pd.DataFrame(stats, columns=["size", "wait_time", "time_to_send", "time_to_receive"]).to_csv(f"stats_{device}_{time.time_ns()}.csv", index=False)
    
    s.sendall(b"done")

    s.close()
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Client for sending data to server')
    parser.add_argument('--ip', type=str, default="127.0.0.1", help='IP address of the server')
    parser.add_argument('--port', type=int, default=5001, help='Port number of the server')
    parser.add_argument('--fname', type=str, default="data/sample_pcds.npy", help='Path to the file containing the point clouds')
    parser.add_argument('--device', type=str, default="dev0", help='Device name')
    parser.add_argument('--wait', type=int, default=50, help='Wait time in ms')
    
    args = parser.parse_args()
    
    main(args.ip, args.port, args.fname, args.device, args.wait)
