import socket
import threading
from datetime import datetime
from pytz import timezone
from tzlocal import get_localzone

code_table = 'utf-8'
length_of_message = 8
name = input("Username. No more then 16 symbols: ")
if len(name) > 16:
    print("No more then 16 symbols, try again")
    nickname = input("Username: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))


def receive_message():
    buffer = 0
    while True:
        if buffer == 0:
            message = client.recv(length_of_message).decode(code_table)
            if message.strip().isdigit():
                buffer = int(message.strip())
        else:
            message = client.recv(buffer).decode(code_table)
            print(message)
            buffer = 0


def send_message():
    while True:
        local_tz = get_localzone()
        message = f'<{local_tz}>{name}->{input("")}'.encode(code_table)
        message_len_send = f'{len(message)+2:<{length_of_message}}'.encode(code_table)
        client.send(message_len_send + message)


receive_thread = threading.Thread(target=receive_message)
receive_thread.start()

write_thread = threading.Thread(target=send_message)
write_thread.start()
