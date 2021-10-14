import socket
import threading
from datetime import datetime
from pytz import timezone


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
                if message.strip().isdigit():   # если число, то это просто сообщение и нужно изменить длину буфера
                    buffer = int(message.strip())
                if message == "file":   # если file, то хотят отправить файл
                    file_header_len = int(client.recv(length_of_message).decode())
                    file_header = client.recv(file_header_len).decode(code_table)#заголовок это имя файла и размер файла
                    file_size = file_header[file_header.find("<>")+2:]
                    file_size = int(file_size)
                    file_data_read = client.recv(file_size)
                    broadcast(f'{"file":<{length_of_message}}'.encode(code_table) +
                              f'{len(file_header.encode(code_table)):<{length_of_message}}'.encode(code_table) +
                              file_header.encode(code_table) + file_data_read)
            else:
                message = client.recv(buffer).decode(code_table)
                time_zone = message[message.find('<') + 1: message.find('>')]
                now_time = datetime.now(timezone(time_zone)).strftime("%Y-%m-%d %H:%M") # время сервера измененное в соответствии с tz пользователя
                message_send = '<' + now_time + '> ' + message[message.find('>') + 1:]
                message_len_send = f'{len(message_send.encode(code_table)):<{length_of_message}}'.encode(code_table)
                broadcast(message_len_send + message_send.encode(code_table))
                print(message_send)
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
