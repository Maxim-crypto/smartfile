import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
import json
from datetime import datetime


logging.basicConfig(filename='organizer.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')


class HistoryManager:
    def __init__(self, history_file='history.json'):
        self.history_file = history_file
        self.history = []
        self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=4)

    def log_move(self, src, dest):
        self.history.append({"src": src, "dest": dest})
        self.save_history()

    def undo_last(self):
        if not self.history:
            return False
        last_move = self.history.pop()
        try:
            shutil.move(last_move['dest'], last_move['src'])
            self.save_history()
            logging.info(f"Undo move: {last_move['dest']} -> {last_move['src']}")
            return True
        except Exception as e:
            logging.error(f"Undo failed: {e}")
            return False

class FileOrganizer:
    def __init__(self, folder_path, history_manager):
        self.folder_path = folder_path
        self.history_manager = history_manager

    def organize(self):
        try:
            for file_name in os.listdir(self.folder_path):
                full_path = os.path.join(self.folder_path, file_name)
                if os.path.isfile(full_path):
                    ext = os.path.splitext(file_name)[1][1:] or 'no_extension'
                    dest_folder = os.path.join(self.folder_path, ext.upper())
                    os.makedirs(dest_folder, exist_ok=True)
                    dest_path = os.path.join(dest_folder, file_name)

                    if os.path.exists(dest_path):
                        base, extn = os.path.splitext(file_name)
                        dest_path = os.path.join(dest_folder, f"{base}_{datetime.now().strftime('%H%M%S')}{extn}")

                    shutil.move(full_path, dest_path)
                    self.history_manager.log_move(full_path, dest_path)
                    logging.info(f"Moved: {full_path} -> {dest_path}")
        except Exception as e:
            logging.error(f"Error organizing files: {e}")
            messagebox.showerror("Error", str(e))

class OrganizerApp:
    def __init__(self):
        self.history_manager = HistoryManager()
        self.root = tk.Tk()
        self.root.title("Smart File Organizer")
        self.root.geometry("400x200")

        self.folder_path = tk.StringVar()

        tk.Label(self.root, text="Select Folder:").pack(pady=5)
        tk.Entry(self.root, textvariable=self.folder_path, width=50).pack(padx=10)
        tk.Button(self.root, text="Browse", command=self.browse_folder).pack(pady=5)
        tk.Button(self.root, text="Organize", command=self.start_organizing).pack(pady=5)
        tk.Button(self.root, text="Undo Last", command=self.undo_move).pack(pady=5)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def start_organizing(self):
        if not self.folder_path.get():
            messagebox.showwarning("Warning", "Please select a folder first.")
            return
        organizer = FileOrganizer(self.folder_path.get(), self.history_manager)
        organizer.organize()
        messagebox.showinfo("Done", "Files organized successfully.")

    def undo_move(self):
        success = self.history_manager.undo_last()
        if success:
            messagebox.showinfo("Undo", "Last move undone.")
        else:
            messagebox.showwarning("Undo", "Nothing to undo.")

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = OrganizerApp()
    app.run()