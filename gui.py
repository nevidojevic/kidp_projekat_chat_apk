import tkinter as tk
from tkinter import scrolledtext
import threading

from network import Network


class ChatGUI:
    def __init__(self):
        self.network = Network()
        self.network.on_message = self.safe_add_message
        self.root = tk.Tk()
        self.root.title("Python Chat")

        self.nickname = ""

        self.build_login()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # LOGIN SCREEN
    def build_login(self):
        self.clear_window()

        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack(pady=20)

        tk.Label(self.login_frame, text="Enter nickname:").pack()

        self.nick_entry = tk.Entry(self.login_frame)
        self.nick_entry.pack()

        tk.Button(
            self.login_frame,
            text="Connect",
            command=self.connect
        ).pack(pady=10)

    def connect(self):
        self.nickname = self.nick_entry.get()

        if not self.nickname:
            return

        self.network.connect(self.nickname)

        self.build_chat()

    # CHAT SCREEN
    def build_chat(self):
        self.clear_window()

        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.pack()

        # chat display
        self.chat_area = scrolledtext.ScrolledText(
            self.chat_frame,
            width=60,
            height=20
        )
        self.chat_area.pack()
        self.chat_area.config(state="disabled")

        # input field
        self.entry = tk.Entry(self.chat_frame, width=50)
        self.entry.pack(side=tk.LEFT, pady=10)

        self.entry.bind("<Return>", lambda event: self.send_message())

        # send button
        tk.Button(
            self.chat_frame,
            text="Send",
            command=self.send_message
        ).pack(side=tk.LEFT)

        # disconnect button
        tk.Button(
            self.root,
            text="Disconnect",
            command=self.disconnect
        ).pack(pady=5)

    def safe_add_message(self, msg):
        self.root.after(0, self.add_message, msg)

    def send_message(self):
        msg = self.entry.get()
        if not msg:
            return

        if msg == "/exit":
            self.disconnect()
            return

        self.network.send(msg)
        self.entry.delete(0, tk.END)

    def add_message(self, msg):
        self.chat_area.config(state="normal")
        self.chat_area.insert(tk.END, msg + "\n")
        self.chat_area.yview(tk.END)
        self.chat_area.config(state="disabled")

    def disconnect(self):
        self.network.disconnect()
        self.root.destroy()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def on_close(self):
        self.disconnect()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ChatGUI()
    app.run()