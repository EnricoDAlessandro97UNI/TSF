import os
import platform
import socket
import struct


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


def list_file():

    global available_files

    available_files = []

    print(f"\n Richiesta della lista dei file disponibili al server {IP_SERVER}")

    # Crea socket TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connessione al server
        client_socket.connect((IP_SERVER, PORT))

        # Invia il comando per ottenere la lista dei file disponibili
        send_data(client_socket, "LIST")

        # Ricezione dei dati
        file_list = receive_data(client_socket)

        if len(file_list) == 0:
            print("\n Al momento non vi sono file disponibili per il download")
            return 0

        # Stampa la lista dei file
        print("\n File disponibili: ")  
        idx = 1  
        for file_name in file_list.split('\n'):
            available_files.append(file_name)
            print("  " + str(idx) + ": " + os.path.basename(file_name))
            idx += 1

        return 1

    except ConnectionRefusedError:
        print(f"\n [Attenzione] - Impossibile connettersi al server {IP_SERVER}:{PORT}")
        return 0
    except Exception as e:
        print(f"\n\n [Attenzione] - Errore durante la ricezione della lista dei file: {str(e)}")
        return 0

    finally:
        client_socket.close()


def download_file():
    
    if (list_file() == 0):
        return

    file_idx = int(input('\n Inserire il numero del file da scaricare: '))
    if (file_idx < 1 or file_idx > len(available_files)):
        print(" Indice inserito non valido")
        return
    
    print(" Download del file '" + os.path.basename(available_files[file_idx-1]) + "' in corso...")

    # Crea la directory locale se non esiste
    os.makedirs(LOCAL_DIRECTORY, exist_ok=True)

    # Crea socket TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connessione al server
        client_socket.connect((IP_SERVER, PORT))

        # Invia il percorso del file remoto al server
        send_data(client_socket, available_files[file_idx-1])

        # Ricezione del nome del file remoto
        remote_file_name = receive_data(client_socket)
        if remote_file_name == "*empty*":
            print("\n [Attenzione] - Il file richiesto non è più disponibile sul server")
            return

        # Ricezione della dimensione del file
        file_size = int(receive_data(client_socket))
        print(f"\n Dimensione del file in byte: {file_size}")

        # Ricezione del contenuto del file
        file_path = os.path.join(LOCAL_DIRECTORY, remote_file_name)
        print(f" Ricezione del file {remote_file_name} nella cartella locale {LOCAL_DIRECTORY}")

        bytes_received = 0
        with open(file_path, 'wb') as f:
            while bytes_received < file_size:
                data = client_socket.recv(min(1024, file_size - bytes_received))
                if not data:
                    break
                f.write(data)
                #f.flush()
                
                # Aggiorna la progress bar e la percentuale di ricezione
                bytes_received += len(data)
                progress = float((bytes_received / file_size) * 100)
                progress_rounded = round(progress, 2)
                print(f"\r {progress_rounded}%", end="", flush=True)
        print("\n")

    except ConnectionRefusedError:
        print(f"\n [Attenzione] - Impossibile connettersi al server {IP_SERVER}:{PORT}")
    except Exception as e:
        print(f"\n\n [Attenzione] - Errore durante la ricezione della lista dei file: {str(e)}")

    finally:
        client_socket.close()


def menu():
    if OS == WINDOWS:
        os.system('cls')
    elif OS == LINUX:
        os.system('clear')
    elif OS == MACOS:
        print("Sistema operativo non supportato")
        exit(1)
    else:
        print("Sistema operativo non supportato")
        exit(1)

    print('\n _________________________ ')
    print("|_________ MENU'__________|")
    print('|                         |')
    print('|  1. Mostra file         |')
    print('|  2. Scarica un file     |')
    print('|  3. Esci                |')
    print('|_________________________|')


def switch(cmd):
    if cmd == 1:
        list_file() 
    elif cmd == 2:
        download_file() 
    elif cmd == 3:
        print("\n Arrivederci!\n\n")
        exit(0)
    else:
        print("\n Errore inaspettato\n\n")
        exit(1)


if __name__ == '__main__':
    
    PORT = 12345
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "darwin"
    OS = platform.system().lower()

    IP_SERVER = input("Inserisci l'IP del server: ")

    if OS == WINDOWS:
        LOCAL_DIRECTORY = "downloadTSF"
    elif OS == LINUX:
        LOCAL_DIRECTORY = "downloadTSF"
    elif OS == MACOS:
        print("Sistema operativo non supportato")
        exit(1)
    else:
        print("Sistema operativo non supportato")
        exit(1)
        
    available_files = []

    while True:
        menu()
        cmd = int(input('\n Inserisci il comando: '))
        while cmd not in [1, 2, 3]:
            cmd = int(input('\n Comando inserito non valido, riprovare: '))

        switch(cmd)
        input('\n Premere un tasto per continuare...')