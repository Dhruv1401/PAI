import tkinter as tk
from threading import Thread

class Plugin:
    def __init__(self, brain, config):
        self.brain = brain
        self.config = config

    def run(self):
        root = tk.Tk()
        root.title("Jarvis Assistant")
        root.geometry("600x400")

        chat_box = tk.Text(root, state="disabled", wrap="word")
        chat_box.pack(expand=True, fill="both")

        entry = tk.Entry(root)
        entry.pack(fill="x")

        def send_message(event=None):
            user_input = entry.get()
            entry.delete(0, tk.END)

            chat_box.config(state="normal")
            chat_box.insert(tk.END, f"You: {user_input}\n")
            chat_box.config(state="disabled")

            response = self.brain.process_input(user_input)

            chat_box.config(state="normal")
            chat_box.insert(tk.END, f"Jarvis: {response}\n\n")
            chat_box.config(state="disabled")

        entry.bind("<Return>", send_message)
        root.mainloop()
