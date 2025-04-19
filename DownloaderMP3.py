import os
import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from urllib.parse import urljoin
from pytube import YouTube
import winsound

# Проверяем наличие moviepy, устанавливаем при необходимости
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    os.system("pip install moviepy")
    try:
        from moviepy.editor import VideoFileClip
    except ImportError:
        messagebox.showerror("Ошибка", "MoviePy не удалось установить. Установите вручную с помощью 'pip install moviepy'.")

# Глобальные переменные
save_dir = ""
stop_download = False

# Выбор папки загрузки
def choose_directory():
    global save_dir
    directory = filedialog.askdirectory()
    if directory:
        save_dir = directory
        dir_label.config(text=f"Папка: {save_dir}")

# Остановка загрузки
def stop_download_func():
    global stop_download
    stop_download = True
    stop_button.config(bg="#FFC0CB")
    status_label.config(text="Загрузка остановлена.")
    messagebox.showinfo("Остановлено", "Процесс загрузки был прерван!")

# Очистка URL
def clear_url():
    url_entry.delete(0, tk.END)

# Вставка URL из буфера обмена
def insert_url():
    try:
        url_entry.insert(tk.END, root.clipboard_get())
    except tk.TclError:
        messagebox.showerror("Ошибка", "Буфер обмена пуст или недоступен.")

# Звуковой сигнал при завершении загрузки
def play_sound():
    try:
        notes = [523, 587, 659, 698, 784]
        duration = 300
        for note in notes:
            winsound.Beep(note, duration)
    except RuntimeError:
        messagebox.showinfo("Информация", "Воспроизведение звука не поддерживается!")

# Мигание кнопки остановки при длительной загрузке
def blink_button():
    if stop_download:
        stop_button.config(bg="#FFC0CB")
        return
    current_color = stop_button.cget("bg")
    stop_button.config(bg="#FFC0CB" if current_color == "white" else "white")
    root.after(500, blink_button)

# Загрузка MP3 файлов
def download_mp3():
    global stop_download
    stop_download = False
    blink_button()

    if not save_dir:
        messagebox.showerror("Ошибка", "Сначала выберите папку!")
        return

    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Ошибка", "Введите корректный URL!")
        return

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Ошибка", f"Не удалось получить страницу: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    mp3_links = [urljoin(url, link["href"]) for link in soup.find_all("a", href=True) if link["href"].endswith(".mp3")]

    if not mp3_links:
        messagebox.showinfo("Информация", "MP3 файлы не найдены на странице.")
        return

    progress["maximum"] = len(mp3_links)
    status_label.config(text="Загрузка MP3 файлов...")
    for idx, file_url in enumerate(mp3_links, start=1):
        if stop_download:
            status_label.config(text="Загрузка прервана.")
            messagebox.showinfo("Остановлено", "Загрузка прервана.")
            return

        file_name = os.path.join(save_dir, os.path.basename(file_url))
        try:
            file_content = requests.get(file_url, headers={"User-Agent": "Mozilla/5.0"}).content
            with open(file_name, "wb") as file:
                file.write(file_content)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить {file_url}: {e}")

        progress["value"] = idx
        root.update_idletasks()

    stop_button.config(bg="#FFC0CB")
    play_sound()
    status_label.config(text="Все MP3 файлы загружены.")
    messagebox.showinfo("Готово!", "MP3 файлы успешно загружены!")

# Конвертация MP4 в AVI
def convert_to_avi(video_path):
    avi_path = video_path.replace(".mp4", ".avi")
    try:
        clip = VideoFileClip(video_path)
        clip.write_videofile(avi_path, codec="png")
        return avi_path
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось конвертировать видео: {e}")
        return None

# Загрузка видео
def download_video():
    if not save_dir:
        messagebox.showerror("Ошибка", "Сначала выберите папку!")
        return

    url = url_entry.get().strip()
    if not url:
        messagebox.showerror("Ошибка", "Введите корректный URL!")
        return

    try:
        yt = YouTube(url, on_progress_callback=progress_update)
        video_stream = yt.streams.get_highest_resolution()
        status_label.config(text="Загрузка видео...")
        video_path = os.path.join(save_dir, video_stream.default_filename)
        video_stream.download(save_dir)

        # Конвертация MP4 в AVI
        avi_path = convert_to_avi(video_path)
        if avi_path:
            status_label.config(text=f"Видео загружено: {video_path}, AVI: {avi_path}")

            play_sound()
            messagebox.showinfo("Готово!", f"Видео сохранено как {video_path} и {avi_path}")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить видео: {e}")

# Обновление прогресса загрузки видео
def progress_update(stream, chunk, bytes_remaining):
    percent = (1 - bytes_remaining / stream.filesize) * 100
    progress["value"] = percent
    root.update_idletasks()

# UI
root = tk.Tk()
root.title("MP3 & Video Downloader")

# Ввод URL
tk.Label(root, text="Введите URL:").pack(pady=5)
url_entry = tk.Entry(root, width=40)
url_entry.pack(pady=5)
download_button = tk.Button(root, text="Скачать MP3", command=download_mp3)
download_button.pack(pady=5)

# Кнопка загрузки видео
video_button = tk.Button(root, text="Скачать видео", command=download_video)
video_button.pack(pady=5)

# Выбор папки
dir_label = tk.Label(root, text="Выберите папку для загрузки", fg="blue")
dir_label.pack(pady=5)
dir_button = tk.Button(root, text="Выбрать папку", command=choose_directory)
dir_button.pack(pady=5)

# Кнопка остановки
stop_button = tk.Button(root, text="Остановить", command=stop_download_func, fg="red")
stop_button.pack(pady=5)

# Прогресс бар
progress = ttk.Progressbar(root, length=300, mode="determinate")
progress.pack(pady=10)

# Запуск UI
root.mainloop()
