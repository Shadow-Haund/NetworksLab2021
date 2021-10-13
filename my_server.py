import socket
import threading
from datetime import datetime
from pytz import timezone
from tzlocal import get_localzone

code_table = 'utf-8'
length_of_message = 8


host = '127.0.0.1'
port = 55555


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

u_sockets = []


def broadcast(message):
    for client in u_sockets:
        client.send(message)


def handle(client):
    buffer = 0
    while True:
        try:
            if buffer == 0:
                message = client.recv(length_of_message).decode(code_table)
                if message.strip().isdigit():
                    buffer = int(message.strip())
            else:
                message = client.recv(buffer).decode(code_table)
                time_zone = message[message.find('<') + 1: message.find('>')]
                now_time = datetime.now(timezone(time_zone)).strftime("%Y-%m-%d %H:%M")
                message_send = '<' + now_time + '> ' + message[message.find('>') + 1:]
                message_len_send = f'{len(message_send.encode(code_table)) + 2:<{length_of_message}}'.encode(code_table)
                broadcast(message_len_send + message_send.encode(code_table))
                print(message)
                buffer = 0
        except:
            u_sockets.remove(client)
            client.close()
            break


def receive_connection():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        u_sockets.append(client)
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


receive_connection()
