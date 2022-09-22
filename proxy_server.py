#!/usr/bin/env python3
#
# Author: Michael Huang

import socket

from multiprocessing import Process

HOST = '127.0.0.1'
PORT = 8001
BUFFER_SIZE = 4096

def recv_full(conn: socket.socket) -> bytes:
    '''Fetch all available data from a socket.'''
    buf = b''
    while True:
        data = conn.recv(BUFFER_SIZE)
        if not data:
            break

        buf += data

    return buf

def connect_to_google() -> socket.socket | None:
    try:
        google_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        google_socket.connect((socket.gethostbyname('www.google.com'), 80))
    except socket.gaierror:
        return None

    #google_socket.setblocking(False)
    google_socket.settimeout(1)
    return google_socket

def run_process(client: socket.socket):
    google = connect_to_google()
    if not google:
        client.sendall(b"Could not resolve Google's hostname")
        return client.close()

    while True:
        try:
            request = recv_full(client)
            if not request:
                break

            google.sendall(request)

            response = recv_full(google)
            if len(response):
                client.sendall(response)

        except TimeoutError:
            continue
        except KeyboardInterrupt:
            break

    google.shutdown(socket.SHUT_RDWR)
    google.close()

    client.shutdown(socket.SHUT_RDWR)
    return client.close()

def main():
    processes: list[Process] = []
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, PORT))
        server.listen()

        try:
            while True:
                client, _ = server.accept()

                process = Process(target=run_process, args=(client,))
                process.start()
                processes.append(process)  # Record started processes

        except KeyboardInterrupt:
            print('Closing server')
    
        # Wait for all processes to finish
        for process in processes:
            process.join()


if __name__ == '__main__':
    main()
