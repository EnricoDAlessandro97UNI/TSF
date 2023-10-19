from tkinter import *
from tkinter import ttk
import os
import socket
import struct
import time

PORT = 12345


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


def download_file(ip_server, remote_file_path, local_directory):
    print(f"[!] Richiesto il file {remote_file_path} al server {ip_server}")

    # Crea la directory locale se non esiste
    os.makedirs(local_directory, exist_ok=True)

    # Crea socket TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connessione al server
        client_socket.connect((ip_server, PORT))

        # Invia il percorso del file remoto al server
        send_data(client_socket, remote_file_path)

        # Ricezione del nome del file remoto
        remote_file_name = receive_data(client_socket)
        if remote_file_name == "*empty*":
            print("[+] Il file richiesto non è presente sul server")
            error_label["text"] = "File non trovato sul server"
            return
        print(f"[+] In attesa del file {remote_file_name}")

        # Ricezione della dimensione del file
        file_size = int(receive_data(client_socket))
        print(f"[+] Dimensione del file in byte: {file_size}")

        # Imposta il valore massimo della progress bar
        progress_bar["maximum"] = file_size
        # Imposta il valore iniziale della progress bar
        progress_bar["value"] = 0

        # Ricezione del contenuto del file
        file_path = os.path.join(local_directory, remote_file_name)
        print(f"[+] Ricezione del file {remote_file_name} nella cartella locale {local_directory}")

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
                progress_bar["value"] = bytes_received
                percent_label["text"] = f"{progress_rounded}%"
                # Aggiorna l'interfaccia grafica
                window.update_idletasks()

    except ConnectionRefusedError:
        print(f"[!] Impossibile connettersi al server {ip_server}:{PORT}")
        error_label["text"] = f"Impossibile connettersi al server {ip_server}"
    except Exception as e:
        print(f"[!] Errore durante il trasferimento: {str(e)}")
        error_label["text"] = "Errore durante il download del file"

    finally:
        client_socket.close()


def on_btn_download_click():
    btn_download.config(state=DISABLED)
    progress_bar["value"] = 0
    percent_label["text"] = ""
    error_label["text"] = ""
    ip_server = entry_ipServer.get()
    file_path = entry_filePath.get()
    local_directory = entry_downloadDir.get()
    download_file(ip_server, file_path, local_directory)
    btn_download.config(state=ACTIVE)


def on_btn_get_file_list_click():

    error_label["text"] = ""

    ip_server = entry_ipServer.get()
    print(f"[!] Richiesta della lista dei file disponibili al server {ip_server}")

    # Crea socket TCP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connessione al server
        client_socket.connect((ip_server, PORT))

        # Invia il comando per ottenere la lista dei file disponibili
        send_data(client_socket, "LIST")

        # Ricezione dei dati
        file_list = receive_data(client_socket)

        # Aggiorna l'interfaccia grafica con la lista dei file
        file_list_box.delete(0, END)
        for file_name in file_list.split('\n'):
            file_list_box.insert(END, file_name)

    except ConnectionRefusedError:
        print(f"[!] Impossibile connettersi al server {ip_server}:{PORT}")
        error_label["text"] = f"Impossibile connettersi al server {ip_server}"
    except Exception as e:
        print(f"[!] Errore durante la ricezione della lista dei file: {str(e)}")
        error_label["text"] = "Errore durante l'ottenimento della lista dei file"

    finally:
        client_socket.close()


def on_file_list_select(event):
    selected_file = file_list_box.get(file_list_box.curselection())
    entry_filePath.delete(0, END)
    entry_filePath.insert(END, selected_file)


window = Tk()
window.title("TSF")
window.configure(background="#222222")
window.geometry("800x920")
window.resizable(False, False)

style = ttk.Style()
style.theme_use("default")
style.configure("Custom.Horizontal.TProgressbar",
                troughcolor="#222222",
                background="#00ff00",
                borderwidth=0
                )

lbl_ipServer = Label(window,
                     text="IP SERVER:",
                     font=("Arial", 16, "bold"),
                     compound="bottom",
                     background="#222222",
                     foreground="#dcdcdc"
                     )
lbl_ipServer.pack(pady=20)
entry_ipServer = Entry(window,
                       font=("Arial", 14),
                       width=15,
                       background="#dcdcdc",
                       justify="center"
                       )
entry_ipServer.pack(padx=10)

btn_getList = Button(window,
                     text="Get File List",
                     command=on_btn_get_file_list_click,
                     font=("Arial", 14),
                     compound="bottom"
                     )
btn_getList.pack(pady=20)

file_list_box = Listbox(window,
                        font=("Arial", 14),
                        width=50,
                        background="#dcdcdc"
                        )
file_list_box.pack(padx=15)
file_list_box.bind("<<ListboxSelect>>", on_file_list_select)

lbl_filePath = Label(window,
                     text="PATH REMOTE FILE:",
                     font=("Arial", 16, "bold"),
                     compound="bottom",
                     background="#222222",
                     foreground="#dcdcdc"
                     )
lbl_filePath.pack(pady=20)
entry_filePath = Entry(window,
                       font=("Arial", 14),
                       width=50,
                       background="#dcdcdc"
                       )
entry_filePath.pack(padx=15)

lbl_downloadDir = Label(window,
                        text="DOWNLOAD DIRECTORY:",
                        font=("Arial", 16, "bold"),
                        compound="bottom",
                        background="#222222",
                        foreground="#dcdcdc"
                        )
lbl_downloadDir.pack(pady=20)
entry_downloadDir = Entry(window,
                          font=("Arial", 14),
                          width=50,
                          background="#dcdcdc"
                          )
entry_downloadDir.insert(0, "DownloadTSF")
entry_downloadDir.pack(padx=15)

btn_download = Button(window,
                      text="Download",
                      command=on_btn_download_click,
                      font=("Arial", 14),
                      compound="bottom"
                      )
btn_download.pack(pady=60)

progress_bar = ttk.Progressbar(window,
                               mode="determinate",
                               length=300,
                               style="Custom.Horizontal.TProgressbar"
                               )
progress_bar.pack()
percent_label = Label(window,
                      text="",
                      width=10,
                      font=("Arial", 14),
                      background="#222222",
                      foreground="#dcdcdc"
                      )
percent_label.pack(pady=10)

error_label = Label(window,
                    text="",
                    background="#222222",
                    font=("Arial", 14),
                    foreground="#ee0000"
                    )
error_label.pack(pady=10)

developer_label = Label(window,
                        text="Developed by Enrico D'Alessandro",
                        background="#222222",
                        font=("Arial", 14),
                        foreground="#dcdcdc"
                        )
developer_label.pack(pady=10)

window.mainloop()
