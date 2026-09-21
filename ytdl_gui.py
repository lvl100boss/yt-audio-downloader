import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import threading
import os

class App:
    def __init__(self, root):
        self.root = root
        root.title("YT Audio Downloader")
        root.geometry("520x340")
        root.resizable(False, False)

        # URL
        tk.Label(root, text="YouTube URL:").pack(anchor="w", padx=12, pady=(12,0))
        self.url = tk.Entry(root, width=65)
        self.url.pack(padx=12, pady=3)

        # Extension
        tk.Label(root, text="Audio format:").pack(anchor="w", padx=12, pady=(8,0))
        self.ext = ttk.Combobox(root, values=["m4a", "mp3", "opus", "wav"], state="readonly", width=22)
        self.ext.current(0)
        self.ext.pack(padx=12, pady=3)

        # Filename
        tk.Label(root, text="Filename (optional):").pack(anchor="w", padx=12, pady=(8,0))
        self.name = tk.Entry(root, width=65)
        self.name.pack(padx=12, pady=3)

        # Folder
        tk.Label(root, text="Save folder:").pack(anchor="w", padx=12, pady=(8,0))
        frame = tk.Frame(root)
        frame.pack(padx=12, pady=3, fill="x")
        self.folder = tk.Entry(frame, width=52)
        self.folder.insert(0, os.path.join(os.path.expanduser("~"), "Downloads"))
        self.folder.pack(side="left")
        tk.Button(frame, text="Browse", command=self.browse).pack(side="left", padx=6)

        # Download button
        self.btn = tk.Button(root, text="Download", command=self.start, bg="#28a745", fg="white", height=2)
        self.btn.pack(pady=12, fill="x", padx=12)

        # Progress Bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=480, mode="determinate")
        self.progress.pack(padx=12, pady=(5, 2))

        # Status text
        self.status = tk.Label(root, text="Ready", fg="gray", font=("Segoe UI", 10))
        self.status.pack(pady=4)

    def browse(self):
        path = filedialog.askdirectory()
        if path:
            self.folder.delete(0, tk.END)
            self.folder.insert(0, path)

    def progress_hook(self, d):
        if d["status"] == "downloading":
            percent_str = d.get("_percent_str", "0%").replace("%", "").strip()
            try:
                percent = float(percent_str)
                self.progress["value"] = percent
            except:
                pass

            speed = d.get("_speed_str", "")
            self.status.config(text=f"Downloading... {percent_str}%  {speed}", fg="blue")
            self.root.update_idletasks()

        elif d["status"] == "finished":
            self.progress["value"] = 100
            self.status.config(text="Processing...", fg="blue")
            self.root.update_idletasks()

    def start(self):
        if not self.url.get().strip():
            messagebox.showerror("Error", "Please paste a URL")
            return

        self.btn.config(state="disabled")
        self.progress["value"] = 0
        self.status.config(text="Starting...", fg="blue")
        threading.Thread(target=self.download, daemon=True).start()

    def download(self):
        url = self.url.get().strip()
        ext = self.ext.get()
        name = self.name.get().strip()
        folder = self.folder.get().strip()

        outtmpl = os.path.join(folder, f"{name}.%(ext)s" if name else "%(title)s.%(ext)s")

        ydl_opts = {
            "outtmpl": outtmpl,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [self.progress_hook],
            "extractor_args": {
                "youtube": {
                    "player_client": ["web", "android"],
                    "formats": ["missing_pot"],
                }
            },
            "force_ipv4": True,
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": ext,
            }],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.progress["value"] = 100
            self.status.config(text="Done!", fg="green")
            messagebox.showinfo("Success", "Download finished!")
        except Exception as e:
            self.status.config(text="Error", fg="red")
            messagebox.showerror("Error", str(e))
        finally:
            self.btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()