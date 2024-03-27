import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, Entry, Button

class ClientGUI:
    def __init__(self, master):
        self.master = master

        master.configure(bg='#1e1e1e')
        self.online = tk.Label(master, text='Online:')
        self.online.pack(ipadx=10,ipady=10)
        self.log_text = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=40, height=20, bg='#333333', fg='white')
        self.log_text.pack(padx=10, pady=10)

        self.message_entry = Entry(master, width=30)
        self.message_entry.pack(pady=10)

        self.send_button = Button(master, text="Wyślij", command=self.send_message, bg='#3498db', fg='white')
        self.send_button.pack(pady=10)

        self.save_history_button = Button(master, text="Zapisz historię", command=self.save_history, bg='#2ecc71', fg='white')
        self.save_history_button.pack(pady=10)

        self.load_history_button = Button(master, text="Wczytaj historię", command=self.load_history, bg='#f39c12', fg='white')
        self.load_history_button.pack(pady=10)

        self.exit_button = Button(master, text="Exit", command=self.exit_application, bg='#e74c3c', fg='white')
        self.exit_button.pack(pady=10)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('192.168.100.22', 5678)
        self.client_socket.connect(server_address)

        nickname = input("Wpisz swój pseudonim: ")
        self.client_socket.send(nickname.encode('utf-8'))

        chatroom_code = input("Wpisz kod chatroomu lub wcisnij enter dla głównego chatu: ").strip() or "123456"
        self.client_socket.send(chatroom_code.encode('utf-8'))
        if chatroom_code == "123456":
            master.title(f"Client GUI - Chat glowny")
        else:
            master.title(f"Client GUI Kod chatu: {chatroom_code}")
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

        # Stała nazwa pliku historii klienta
        self.client_history_file = "historiaCzatuKlienta2.txt"

    def receive_messages(self):
        while True:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                message = data.decode('utf-8')
                if message.startswith('SERVERMSG'):
                    self.online['text'] = 'Online: ' + message.split(':')[1]
                else:
                    self.log_to_history(message)
            except ConnectionResetError:
                print("Utrata połączenia z serwerem.")
                break

    def send_message(self):
        message = self.message_entry.get()
        self.client_socket.send(message.encode('utf-8'))
        if message == "exit":
            self.client_socket.close()
            self.master.destroy()

    def save_history(self):
        with open(self.client_history_file, "a") as file:
            history = self.log_text.get("1.0", tk.END)
            file.write(history)

    def load_history(self):
        try:
            with open(self.client_history_file, "r") as file:
                history = file.read()
                self.log_text.delete("1.0", tk.END)
                self.log_text.insert(tk.END, history)
        except FileNotFoundError:
            print("Plik historii nie istnieje.")

    def exit_application(self):
        self.client_socket.close()
        self.master.destroy()

    def log_to_history(self, message):
        self.log_text.insert(tk.END, message + '\n')


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg='#1e1e1e')
    client_gui = ClientGUI(root)
    root.mainloop()
