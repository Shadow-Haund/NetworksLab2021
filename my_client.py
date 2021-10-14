import os
import socket
import threading
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
            if message.strip() == "file":
                file_header_len = int(client.recv(length_of_message).decode())
                file_header = client.recv(file_header_len).decode(code_table) #заголовок это имя файла и размер файла
                file_name = file_header[:file_header.find("<>")]
                file_size = file_header[file_header.find("<>")+2:]
                file_name = os.path.basename(file_name) # если имя файла задано как путь к нему, останется только имя файла
                file_size = int(file_size)
                f = open("send"+file_name, "wb")
                file_data_write = client.recv(file_size)
                f.write(file_data_write)
                f.close()
                print(f'File {file_name} is received ')
        else:
            message = client.recv(buffer).decode(code_table)
            print(message)
            buffer = 0


def send_message():
    while True:
        local_tz = get_localzone()
        message = input("")
        if message == "file":
            file_name = input("Type file name: ")
            file_size = os.path.getsize(file_name)
            client.send(f"{message}".encode(code_table))
            file_name_size = f"{file_name}<>{file_size}".encode()
            client.send(f"{len(file_name_size):<{length_of_message}}".encode(code_table))
            client.send(file_name_size)
            f = open(file_name, "rb")
            file_data_write = f.read(file_size)
            client.sendall(file_data_write)
            f.close()
            print(f'File {file_name} is send')
        else:
            message_send = f'<{local_tz}>{name}->{message}'.encode(code_table)
            message_len_send = f'{len(message_send):<{length_of_message}}'.encode(code_table)
            client.send(message_len_send + message_send)


receive_thread = threading.Thread(target=receive_message)
receive_thread.start()

write_thread = threading.Thread(target=send_message)
write_thread.start()
