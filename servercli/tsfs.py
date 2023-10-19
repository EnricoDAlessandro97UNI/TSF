import os
import platform
import socket
import struct
import time
from pathlib import Path


PORT = 12345
SERVER_DIRECTORY_PATH = ""
WINDOWS = "windows"
LINUX = "linux"
MACOS = "darwin"


def send_data(client_socket, data):
    # Calcola la lunghezza dei dati
    data_length = len(data)

    # Converti la lunghezza dei dati in un prefisso binario
    prefix = struct.pack('!I', data_length)

    # Invia il prefisso di lunghezza
    client_socket.sendall(prefix)

    # Invia i dati effettivi
    client_socket.sendall(data.encode('utf-8'))


def receive_data(client_socket):
    # Ricevi il prefisso di lunghezza
    prefix = client_socket.recv(4)

    # Estrai la lunghezza dai dati ricevuti
    data_length = struct.unpack('!I', prefix)[0]

    # Ricevi i dati effettivi fino alla lunghezza specificata
    data = b''
    while len(data) < data_length:
        chunk = client_socket.recv(data_length - len(data))
        if not chunk:
            break
        data += chunk

    return data.decode('utf-8')


def send_file(client_socket, remote_file_path):
    # Verifica se il file esiste
    if not os.path.isfile(remote_file_path):
        print(f"[+] Il file richiesto dal client {client_socket.getpeername()[0]} non esiste: {remote_file_path}")
        send_data(client_socket, "*empty*")
        return

    # Invia il nome del file al client
    send_data(client_socket, os.path.basename(remote_file_path))

    # Invia la dimensione del file al client
    file_size = os.path.getsize(remote_file_path)
    send_data(client_socket, str(file_size))

    # Invia il contenuto del file al client
    with open(remote_file_path, 'rb') as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            client_socket.sendall(data)
            
    print(f"[+] Invio del file {remote_file_path} al client {client_socket.getpeername()[0]} completato")


def get_file_list():
    # Ottieni la lista dei file nella directory corrente
    files = os.listdir(SERVER_DIRECTORY_PATH)

    # Crea una stringa con i nomi dei file separati da una nuova riga
    for i in range(0, len(files)):
        files[i] = SERVER_DIRECTORY_PATH + files[i]

    file_list = '\n'.join(files)

    print(files)

    return file_list


def handle_client(client_socket):
    try:
        # Ricezione del percorso del file richiesto dal client
        remote_file_path = receive_data(client_socket)
        print(f"[+] Richiesta del file {remote_file_path} da parte del client {client_socket.getpeername()[0]}")

        if remote_file_path == "LIST":
            # Invia la lista dei file al client
            file_list = get_file_list()
            send_data(client_socket, file_list)
        else:
            # Invia il file al client
            send_file(client_socket, remote_file_path)

    except Exception as e:
        print(f"[!] Errore durante la gestione del client {client_socket.getpeername()[0]}: {str(e)}")

    finally:
        client_socket.close()
        print(f"[!] Connessione con il client chiusa")


def init_server_folder():
    global SERVER_DIRECTORY_PATH
    SERVER_DIRECTORY_PATH = str(Path.home())
    if platform.system().lower() == WINDOWS:
        SERVER_DIRECTORY_PATH = SERVER_DIRECTORY_PATH + "\\Downloads" + "\\SERVER_FILES\\"
    elif platform.system().lower() == LINUX:  
        SERVER_DIRECTORY_PATH = SERVER_DIRECTORY_PATH + "/Downloads" + "/SERVER_FILES/"
    elif platform.system().lower() == MACOS: 
        raise Exception("ci scusiamo, sistema operativo non supportato")
    else:
        raise Exception("ci scusiamo, sistema operativo non supportato")

    # Crea la directory locale per i download se non esiste
    print(SERVER_DIRECTORY_PATH)
    os.makedirs(SERVER_DIRECTORY_PATH, exist_ok=True)


def start_server():
    # Creazione della socket TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        init_server_folder()

        # Bind della socket al server e porta specificati
        server_socket.bind(('0.0.0.0', PORT))

        # Avvio dell'ascolto delle connessioni in ingresso
        server_socket.listen(1)
        print(f"[!] Server in ascolto sulla porta {PORT} ...")

        while True:
            # Accettazione di una connessione in entrata
            client_socket, client_address = server_socket.accept()
            print(f"[!] Connessione accettata da: {client_address}")

            # Gestione del client in un thread separato
            handle_client(client_socket)

    except KeyboardInterrupt:
        print("\n[!] Server interrotto")
        exit(1)
    except Exception as e:
        print(f"\n[!] Errore durante l'esecuzione del server: {str(e)}")
        exit(1)


if __name__ == '__main__':
    start_server()
