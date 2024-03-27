import socket
import threading
import tkinter as tk
from tkinter import scrolledtext


class ServerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Server GUI")

        self.chat_rooms = {}

        master.configure(bg='#1e1e1e')
        self.log_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=40, height=20, bg='#333333', fg='white')
        self.log_text.pack(padx=10, pady=10)

        self.start_button = tk.Button(master, text="Uruchom serwer", command=self.start_server, bg='#4CAF50',
                                      fg='white')
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="Zatrzymaj serwer", command=self.stop_server, state=tk.DISABLED,
                                     bg='#FF5733', fg='white')
        self.stop_button.pack(pady=10)

        self.clear_history_button = tk.Button(master, text="Wyczyść historię", command=self.clear_chat_history,
                                              bg='#3498db', fg='white')
        self.clear_history_button.pack(pady=10)

        self.exit_button = tk.Button(master, text="Exit", command=self.exit_application, bg='#ffffff', fg='black')
        self.exit_button.pack(pady=10)

        self.server_socket = None
        self.nicknames = {}

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('192.168.100.22', 5678)
        self.server_socket.bind(server_address)
        self.server_socket.listen(5)
        self.log_to_history("Serwer uruchomiony. Oczekiwanie na połączenia...\n")

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        threading.Thread(target=self.accept_clients).start()

    def accept_clients(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            self.log_to_history(f"Połączono z {client_address}\n")

            nickname = client_socket.recv(1024).decode('utf-8')
            self.log_to_history(f"{client_address} połączony z pseudonimem: {nickname}\n")

            chat_room_code = client_socket.recv(1024).decode('utf-8')

            if chat_room_code not in self.chat_rooms:
                self.chat_rooms[chat_room_code] = []
            self.chat_rooms[chat_room_code].append(client_socket)

            self.nicknames[client_socket] = nickname
            self.broadcast_to_room(('SERVERMSG:' + str(self.chat_rooms[chat_room_code].__len__())), chat_room_code)
            threading.Thread(target=self.handle_client, args=(client_socket, chat_room_code)).start()

    def broadcast_to_room(self, message, chat_room_code):
        if chat_room_code in self.chat_rooms:
            for client in self.chat_rooms[chat_room_code]:
                client.send(message.encode('utf-8'))

    def handle_client(self, client_socket, chat_room_code):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                message = f"{self.nicknames[client_socket]}: {data.decode('utf-8')}\n"
                self.log_to_history(message)

                self.broadcast_to_room(message, chat_room_code)

                if data.decode('utf-8') == "exit":
                    break
        except Exception as e:
            print(f"Błąd obsługi klienta: {e}")
        finally:
            client_socket.close()
            self.chat_rooms[chat_room_code].remove(client_socket)
            if self.chat_rooms[chat_room_code].__len__() > 0:
                self.broadcast_to_room(('SERVERMSG:' + str(self.chat_rooms[chat_room_code].__len__())), chat_room_code)
            elif self.chat_rooms[chat_room_code].__len__() == 0:
                del self.chat_rooms[chat_room_code]
            del self.nicknames[client_socket]
            self.log_to_history(f"Połączenie z {self.nicknames[client_socket]} zakończone z powodu błędu\n")

    def stop_server(self):
        if self.server_socket:
            self.server_socket.close()
        self.log_to_history("Serwer zatrzymany\n")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def log_to_history(self, message):
        self.log_text.insert(tk.END, message)

    def clear_chat_history(self):
        self.log_text.delete(1.0, tk.END)
        self.save_chat_history(clear_file=True)

    def save_chat_history(self, filename="historia_czatu.txt", clear_file=False):
        try:
            mode = "w" if clear_file else "a"
            with open(filename, mode) as file:
                chat_history = self.log_text.get("1.0", tk.END)
                chat_history = chat_history.replace("Serwer uruchomiony. Oczekiwanie na połączenia...\n", "")
                chat_history = chat_history.replace("Serwer zatrzymany\n", "")
                file.write(chat_history)
        except Exception as e:
            print(f"Błąd podczas zapisywania historii czatu: {e}")

    def exit_application(self):
        self.save_chat_history()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg='#1e1e1e')
    server_gui = ServerGUI(root)

    root.protocol("WM_DELETE_WINDOW", server_gui.exit_application)

    root.mainloop()
