import socket
import threading
from datetime import datetime
from pytz import timezone


code_table = 'utf-8'
length_of_message = 8

hostS = 'networkslab-ivt.ftp.sh'
hostL = '127.0.0.1'
host = '127.0.0.1'
port = 55555


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
u_sockets = []


def broadcast(message, user):
    for client in u_sockets:
        #if client != user:
            client.send(message)


def handle(client):
    buffer = 1
    full_mes = bytes()
    full_file = bytes()
    while True:
        # try:
            if buffer == 1:
                message = client.recv(length_of_message).decode(code_table)
                if message.strip().isdigit():   # если число, то это просто сообщение и нужно изменить длину буфера
                    buffer = int(message.strip())
                if message == "file~~":   # если file, то хотят отправить файл
                    file_header_len = int(client.recv(length_of_message).decode())
                    file_name_size = client.recv(file_header_len).decode(code_table)# заголовок это имя файла и размер файла
                    file_size = file_name_size[file_name_size.find("<>")+2:]
                    file_size = int(file_size)
                    file_data_read = client.recv(file_size)
                    if "~~".encode(code_table) in file_data_read:
                        broadcast(f'{"file~~":<{length_of_message}}'.encode(code_table) +
                              f'{len(file_name_size.encode(code_table)):<{length_of_message}}'.encode(code_table) +
                              file_name_size.encode(code_table) + file_data_read, client)
                        print("serF1")
                    else:
                        while not "~~".encode(code_table) in file_data_read:
                            full_file += file_data_read
                            file_data_read = client.recv(file_size)
                        else:
                            full_file +=file_data_read
                            broadcast(f'{"file~~":<{length_of_message}}'.encode(code_table) +
                                      f'{len(file_name_size.encode(code_table)):<{length_of_message}}'.encode(
                                          code_table) +
                                      file_name_size.encode(code_table) + full_file, client)
                            print("serF2")
            else:
                message = client.recv(buffer)
                # это часть модернизируется с целью успешного получения всего сообщения при выкладке сервера удаленно
                if '~~'.encode(code_table) in message:
                    time_zone = message[message.find('<'.encode(code_table)) + 1: message.find('>'.encode(code_table))].decode(code_table)
                    now_time = datetime.now(timezone(time_zone)).strftime("%Y-%m-%d %H:%M") # время сервера измененное в соответствии с tz пользователя
                    message_send = '<'.encode(code_table) + now_time.encode(code_table) + '> '.encode(code_table) + \
                                   message[message.find('>'.encode(code_table)) + 1:]
                    message_len_send = f'{len(message_send):<{length_of_message}}'.encode(code_table)
                    broadcast(message_len_send + message_send, client)
                    print("sev1")
                    print(message_send)
                    buffer = 0
                else:
                    while not "~~".encode(code_table) in message:
                        full_mes += message
                        message = client.recv(buffer)
                    else:
                        full_mes += message
                        time_zone = full_mes[full_mes.find('<'.encode(code_table)) + 1: full_mes.find('>'.encode(code_table))]
                        now_time = datetime.now(timezone(time_zone)).strftime(
                            "%Y-%m-%d %H:%M")  # время сервера измененное в соответствии с tz пользователя
                        message_send = '<'.encode(code_table) + now_time.encode(code_table) + '> '.encode(code_table) \
                                       + full_mes[full_mes.find('>'.encode(code_table)) + 1:]
                        message_len_send = f'{len(message_send)-1000:<{length_of_message}}'.encode(
                            code_table)
                        broadcast(message_len_send + message_send, client)
                        print("sev2")
                        buffer = 0
        # except:
        #     u_sockets.remove(client)
        #     client.close()
        #     break


def receive_connection():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        u_sockets.append(client)
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


receive_connection()
