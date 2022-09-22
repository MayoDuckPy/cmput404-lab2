#!/usr/bin/env python3
import socket
import time

from multiprocessing import Process

#define address & buffer size
HOST = '127.0.0.1'
PORT = 8001
BUFFER_SIZE = 1024

def run_process(client: socket.socket):
    #recieve data, wait a bit, then send it back
    full_data = client.recv(BUFFER_SIZE)
    time.sleep(0.5)
    client.sendall(full_data)
    client.shutdown(socket.SHUT_RDWR)
    client.close()

def main():
    processes: list[Process] = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen(2)
        
        try:
            #continuously listen for connections
            while True:
                conn, addr = server.accept()
                print("Connected by", addr)
                
                process = Process(target=run_process, args=(conn,))
                process.start()
                processes.append(process)  # Record started processes

        except KeyboardInterrupt:
            print('Closing server')

        # Wait for all processes to finish
        for process in processes:
            process.join()

if __name__ == "__main__":
    main()
