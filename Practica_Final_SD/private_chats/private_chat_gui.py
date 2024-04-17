import tkinter as tk
from tkinter import scrolledtext
import ChannelStorage as ChannelStorage

class ChatWindow:
    def __init__(self, master, name, multi_chat_app):
        self.multi_chat_app = multi_chat_app
        self.master = master
        self.name = name
        self.master.title(name)
        
        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill=tk.BOTH)
        
        self.message_entry = tk.Entry(master)
        self.message_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        self.send_button = tk.Button(master, text="Send", command=self.send_message)
        self.send_button.pack(side=tk.RIGHT)
        
        self.master.protocol("WM_DELETE_WINDOW", self.close_window)

    def send_message(self):
        message = self.message_entry.get()
        self.message_entry.delete(0, tk.END)
        if message:
            self.display_message("Me", message)
            self.multi_chat_app.send_grpc_message(self.name, message)

    def display_message(self, sender, content):
        self.text_area.insert(tk.END, f"{sender}: {content}\n")
        self.text_area.see(tk.END)

    def close_window(self):
        # Add any cleanup code here
        self.master.destroy()

class MultiChatApp:

    def __init__(self, me):
        self.root = tk.Tk()
        self.chat_windows = {}
        self.me = me
        self.channel_storage = ChannelStorage.ChannelStorage()
        self.setup_interface()

    def connect_to_chat_interface(self):
        sender = self.sender_entry.get()
        if sender:
            #Si no esta creado el chat, lo creamos 
            chat_window = self.get_chat_window(sender)
            self.sender_entry.delete(0, tk.END)

    def setup_interface(self):
        label = tk.Label(self.root, text="CLOSE THIS WINDOW FOR EXITING ALL CHATS", fg="red", font=("Helvetica", 12))
        label.pack(padx=20, pady=20)
        
        label = tk.Label(self.root, text="Welcome "+ self.me+"!", font=("Helvetica", 16))
        label.pack()

        self.sender_label = tk.Label(self.root, text="Enter Sender Name:")
        self.sender_label.pack()

        self.sender_entry = tk.Entry(self.root)
        self.sender_entry.pack()

        self.connect_button = tk.Button(self.root, text="Connect", command=self.connect_to_chat_interface)
        self.connect_button.pack()

    def get_chat_window(self, sender):
        if sender not in self.chat_windows:
            print(f"Creating chat window for {sender}")
            self.chat_windows[sender] = ChatWindow(tk.Toplevel(self.root), sender, self)
        return self.chat_windows[sender]

    def receive_message(self, sender, content):
        for item in self.chat_windows:
            print(item)
        chat_window = self.get_chat_window(sender)
        self.chat_windows[sender].display_message(sender, content)
        #chat_window.display_message(sender, content)
        print(f"Message received: {sender}: {content}")

    def send_grpc_message(self, destinatari, message):
        print(f"Sending message to {destinatari}: {message}")
        self.channel_storage.receptor_message(self.me,destinatari, message)

def main():
    app = MultiChatApp()
    app.root.mainloop()

if __name__ == "__main__":
    main()
