############################################################################
#                                                                          #
# Version 0.1    Created by Alex Filyaev wth AI 19.04.2025                 #
#                                                                          #
############################################################################

import os
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from urllib.parse import urljoin

# Global variables
save_dir = ""
stop_download = False  # Flag to stop downloading

# Choose download directory
def choose_directory():
    global save_dir
    directory = filedialog.askdirectory()
    if directory:
        save_dir = directory
        dir_label.config(text=f"Folder: {save_dir}")

# Stop download function
def stop_download_func():
    global stop_download
    stop_download = True
    messagebox.showinfo("Stopped", "Download process has been stopped!")

# Clear URL input
def clear_url():
    url_entry.delete(0, tk.END)

# Insert URL from clipboard
def insert_url():
    url_entry.insert(tk.END, root.clipboard_get())

# Download MP3 files
def download_mp3():
    global stop_download
    stop_download = False

    if not save_dir:
        messagebox.showerror("Error", "Select a folder first!")
        return

    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Error", "Enter a valid URL!")
        return

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch page: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    mp3_links = [urljoin(url, link["href"]) for link in soup.find_all("a", href=True) if link["href"].endswith(".mp3")]

    if not mp3_links:
        messagebox.showinfo("Info", "No MP3 files found on the page.")
        return

    progress["maximum"] = len(mp3_links)
    for idx, file_url in enumerate(mp3_links, start=1):
        if stop_download:  # Stop process if flag is set
            messagebox.showinfo("Stopped", "Download interrupted.")
            return

        file_name = os.path.join(save_dir, os.path.basename(file_url))
        try:
            file_content = requests.get(file_url, headers={"User-Agent": "Mozilla/5.0"}).content
            with open(file_name, "wb") as file:
                file.write(file_content)
            table.insert("", "end", values=(file_url, file_name))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download {file_url}: {e}")

        progress["value"] = idx  # Update progress bar
        root.update_idletasks()  # Refresh UI

    messagebox.showinfo("Done!", "All MP3 files downloaded successfully!")

# Create UI window
root = tk.Tk()
root.title("MP3 Downloader")

# Set adaptive window size
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width * 0.26)  # Adjusted width for proper fit
window_height = int(screen_height * 0.62)  # Adjusted height for visibility
root.geometry(f"{window_width}x{window_height}+{screen_width - window_width}+{screen_height // 2 - window_height // 2}")

# URL input with Download button next to it
tk.Label(root, text="Enter URL:").pack(pady=5)
url_frame = tk.Frame(root)
url_entry = tk.Entry(url_frame, width=40)
url_entry.pack(side=tk.LEFT, padx=5)
download_button = tk.Button(url_frame, text="Download MP3", command=download_mp3)
download_button.pack(side=tk.RIGHT)
url_frame.pack(pady=5)

# Bind Ctrl+V for paste functionality
root.bind("<Control-v>", lambda event: url_entry.event_generate("<<Paste>>"))

# Buttons for Clear (Del) and Insert
button_frame = tk.Frame(root)
del_button = tk.Button(button_frame, text="Del", command=clear_url)
del_button.pack(side=tk.LEFT, padx=5)
insert_button = tk.Button(button_frame, text="Insert", command=insert_url)
insert_button.pack(side=tk.RIGHT, padx=5)
button_frame.pack(pady=5)

# Select folder
dir_label = tk.Label(root, text="Select folder for download", fg="blue")
dir_label.pack(pady=5)
dir_button = tk.Button(root, text="Choose Folder", command=choose_directory)
dir_button.pack(pady=5)

# Stop button
stop_button = tk.Button(root, text="Stop Download", command=stop_download_func, fg="red")
stop_button.pack(pady=5)

# Progress bar
progress = ttk.Progressbar(root, length=300, mode="determinate")
progress.pack(pady=10)

# Table for downloaded files
columns = ("URL", "File")
table = ttk.Treeview(root, columns=columns, show="headings")
table.heading("URL", text="URL")
table.heading("File", text="File")
table.pack(pady=10)

# Credit line
credit_label = tk.Label(root, text="Created by Alex Filyaev with AI 2025", fg="gray")
credit_label.pack(pady=10)

# Start UI
root.mainloop()
