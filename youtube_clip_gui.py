#!/usr/bin/env python3
"""
YouTube Clip Extractor GUI
A modern GUI application for extracting YouTube video clips
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import threading
from pathlib import Path
import json
from urllib.parse import urlparse, parse_qs
from PIL import Image, ImageTk
import requests
from io import BytesIO

class YouTubeClipExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Clip Extractor")
        self.root.geometry("700x650")
        self.root.resizable(False, False)

        # Set app icon if available
        self.root.configure(bg="#f0f0f0")

        # Script directory
        self.script_dir = Path(__file__).parent / "scripts"

        # Default download directory
        self.download_dir = str(Path.home() / "Downloads")

        # Video metadata
        self.video_id = None
        self.video_info = {}

        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""

        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = tk.Label(
            main_frame,
            text="🎬 YouTube Clip Extractor",
            font=("Helvetica", 24, "bold"),
            bg="#f0f0f0"
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # URL Section
        url_frame = ttk.LabelFrame(main_frame, text="Video URL", padding="10")
        url_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        self.url_entry = ttk.Entry(url_frame, width=60, font=("Helvetica", 11))
        self.url_entry.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        self.url_entry.bind("<FocusOut>", lambda e: self.fetch_thumbnail())
        self.url_entry.bind("<Return>", lambda e: self.fetch_thumbnail())

        self.load_btn = ttk.Button(
            url_frame,
            text="Load Video",
            command=self.fetch_thumbnail
        )
        self.load_btn.grid(row=0, column=1)

        # Thumbnail Section
        thumb_frame = ttk.LabelFrame(main_frame, text="Video Preview", padding="10")
        thumb_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Thumbnail display
        self.thumbnail_label = tk.Label(
            thumb_frame,
            text="Enter a YouTube URL and click 'Load Video'\nto see thumbnail preview",
            width=60,
            height=15,
            bg="#e0e0e0",
            relief=tk.SUNKEN
        )
        self.thumbnail_label.grid(row=0, column=0, pady=5)

        # Video info
        self.info_label = tk.Label(
            thumb_frame,
            text="",
            font=("Helvetica", 9),
            bg="#f0f0f0",
            justify=tk.LEFT
        )
        self.info_label.grid(row=1, column=0, pady=(5, 0))

        # Timeframe Section
        time_frame = ttk.LabelFrame(main_frame, text="Timeframe", padding="10")
        time_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        # Start time
        start_label = ttk.Label(time_frame, text="Start Time:")
        start_label.grid(row=0, column=0, sticky=tk.W)

        self.start_entry = ttk.Entry(time_frame, width=15, font=("Helvetica", 11))
        self.start_entry.grid(row=0, column=1, padx=(10, 20))
        self.start_entry.insert(0, "06:13")

        # End time
        end_label = ttk.Label(time_frame, text="End Time:")
        end_label.grid(row=0, column=2, sticky=tk.W)

        self.end_entry = ttk.Entry(time_frame, width=15, font=("Helvetica", 11))
        self.end_entry.grid(row=0, column=3, padx=(10, 0))
        self.end_entry.insert(0, "06:30")

        # Format hint
        format_hint = ttk.Label(
            time_frame,
            text="Format: MM:SS or HH:MM:SS",
            font=("Helvetica", 9, "italic")
        )
        format_hint.grid(row=1, column=0, columnspan=4, pady=(5, 0))

        # Download Directory Section
        dir_frame = ttk.LabelFrame(main_frame, text="Download Location", padding="10")
        dir_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        self.dir_entry = ttk.Entry(dir_frame, width=50, font=("Helvetica", 10))
        self.dir_entry.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E))
        self.dir_entry.insert(0, self.download_dir)

        self.browse_btn = ttk.Button(
            dir_frame,
            text="Browse...",
            command=self.browse_directory
        )
        self.browse_btn.grid(row=0, column=1)

        # Filename
        filename_label = ttk.Label(dir_frame, text="Filename:")
        filename_label.grid(row=1, column=0, sticky=tk.W, pady=(10, 0))

        self.filename_entry = ttk.Entry(dir_frame, width=50, font=("Helvetica", 10))
        self.filename_entry.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        self.filename_entry.insert(0, "clip.mp4")

        # Progress Section
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))

        self.progress = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=600
        )
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.status_label = tk.Label(
            progress_frame,
            text="Ready",
            font=("Helvetica", 9),
            bg="#f0f0f0"
        )
        self.status_label.grid(row=1, column=0, pady=(5, 0))

        # Download Button
        self.download_btn = ttk.Button(
            main_frame,
            text="⬇ Download Clip",
            command=self.download_clip,
            style="Accent.TButton"
        )
        self.download_btn.grid(row=6, column=0, columnspan=2, pady=(0, 10))

        # Configure style for accent button
        style = ttk.Style()
        style.configure("Accent.TButton", font=("Helvetica", 12, "bold"))

    def browse_directory(self):
        """Open directory browser"""
        directory = filedialog.askdirectory(initialdir=self.download_dir)
        if directory:
            self.download_dir = directory
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def extract_video_id(self, url):
        """Extract video ID from YouTube URL"""
        try:
            result = subprocess.run(
                [str(self.script_dir / "parse_video_id.sh"), url],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def fetch_thumbnail(self):
        """Fetch video thumbnail and metadata"""
        url = self.url_entry.get().strip()

        if not url:
            return

        self.status_label.config(text="Loading video information...")
        self.root.update()

        # Extract video ID
        video_id = self.extract_video_id(url)

        if not video_id:
            messagebox.showerror("Error", "Invalid YouTube URL")
            self.status_label.config(text="Error: Invalid URL")
            return

        self.video_id = video_id

        # Fetch video info using yt-dlp
        try:
            result = subprocess.run(
                ["yt-dlp", "--dump-json", "--no-warnings", f"https://www.youtube.com/watch?v={video_id}"],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )

            self.video_info = json.loads(result.stdout)

            # Get thumbnail URL
            thumbnail_url = self.video_info.get('thumbnail')

            if thumbnail_url:
                # Download and display thumbnail
                response = requests.get(thumbnail_url, timeout=10)
                img_data = response.content
                img = Image.open(BytesIO(img_data))

                # Resize to fit
                img.thumbnail((600, 340), Image.Resampling.LANCZOS)

                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)
                self.thumbnail_label.config(image=photo, text="")
                self.thumbnail_label.image = photo  # Keep a reference

            # Display video info
            title = self.video_info.get('title', 'Unknown')
            duration = self.video_info.get('duration', 0)
            uploader = self.video_info.get('uploader', 'Unknown')

            duration_str = f"{int(duration // 60)}:{int(duration % 60):02d}"

            info_text = f"📹 {title}\n👤 {uploader}  |  ⏱ {duration_str}"
            self.info_label.config(text=info_text)

            # Update filename suggestion
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:50]
            self.filename_entry.delete(0, tk.END)
            self.filename_entry.insert(0, f"{safe_title}.mp4")

            self.status_label.config(text="✓ Video loaded successfully")

        except subprocess.TimeoutExpired:
            messagebox.showerror("Error", "Request timed out. Please try again.")
            self.status_label.config(text="Error: Timeout")
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Failed to fetch video information")
            self.status_label.config(text="Error: Failed to fetch info")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            self.status_label.config(text="Error")

    def validate_inputs(self):
        """Validate all inputs before download"""
        url = self.url_entry.get().strip()
        start_time = self.start_entry.get().strip()
        end_time = self.end_entry.get().strip()
        filename = self.filename_entry.get().strip()

        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return False

        if not start_time or not end_time:
            messagebox.showerror("Error", "Please enter start and end times")
            return False

        if not filename:
            messagebox.showerror("Error", "Please enter a filename")
            return False

        if not filename.endswith('.mp4'):
            filename += '.mp4'
            self.filename_entry.delete(0, tk.END)
            self.filename_entry.insert(0, filename)

        # Validate timeframe
        timeframe = f"{start_time}-{end_time}"
        try:
            subprocess.run(
                [str(self.script_dir / "validate_timeframe.sh"), timeframe],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError:
            messagebox.showerror("Error", "Invalid timeframe format. Use MM:SS or HH:MM:SS")
            return False

        return True

    def download_clip(self):
        """Download the video clip"""
        if not self.validate_inputs():
            return

        # Disable download button
        self.download_btn.config(state=tk.DISABLED)
        self.progress.start(10)
        self.status_label.config(text="Downloading and extracting clip...")

        # Run download in separate thread
        thread = threading.Thread(target=self._download_thread)
        thread.daemon = True
        thread.start()

    def _download_thread(self):
        """Background thread for downloading"""
        try:
            url = self.url_entry.get().strip()
            start_time = self.start_entry.get().strip()
            end_time = self.end_entry.get().strip()
            timeframe = f"{start_time}-{end_time}"
            filename = self.filename_entry.get().strip()
            output_path = os.path.join(self.download_dir, filename)

            # Run extraction script
            result = subprocess.run(
                [
                    str(self.script_dir / "extract_clip.sh"),
                    url,
                    timeframe,
                    output_path
                ],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                self.root.after(0, self._download_success, output_path)
            else:
                error_msg = result.stderr or "Unknown error occurred"
                self.root.after(0, self._download_error, error_msg)

        except subprocess.TimeoutExpired:
            self.root.after(0, self._download_error, "Download timed out")
        except Exception as e:
            self.root.after(0, self._download_error, str(e))

    def _download_success(self, output_path):
        """Handle successful download"""
        self.progress.stop()
        self.download_btn.config(state=tk.NORMAL)
        self.status_label.config(text="✓ Clip downloaded successfully!")

        # Get file size
        file_size = os.path.getsize(output_path)
        size_mb = file_size / (1024 * 1024)

        result = messagebox.askyesno(
            "Success",
            f"Clip downloaded successfully!\n\n"
            f"File: {os.path.basename(output_path)}\n"
            f"Size: {size_mb:.1f} MB\n"
            f"Location: {output_path}\n\n"
            f"Open download folder?"
        )

        if result:
            # Open folder
            subprocess.run(["open", os.path.dirname(output_path)])

    def _download_error(self, error_msg):
        """Handle download error"""
        self.progress.stop()
        self.download_btn.config(state=tk.NORMAL)
        self.status_label.config(text="✗ Download failed")

        messagebox.showerror("Download Failed", f"Error:\n{error_msg}")

def main():
    root = tk.Tk()
    app = YouTubeClipExtractorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
