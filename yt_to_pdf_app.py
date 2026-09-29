"""
yt_to_pdf_app.py - A simple window app for making transcript PDFs.

Paste one or more YouTube links into the box, click "Make PDF", and the
PDFs are saved into the "output" folder next to this file.

It does exactly the same job as yt_to_pdf.py (and uses its code),
just with buttons instead of terminal commands.

Run it with:   python3 yt_to_pdf_app.py
(or use the app-menu shortcut that install_app.sh creates on Ubuntu)
"""

import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import scrolledtext

# Reuse all the real work from the command-line tool.
import yt_to_pdf


class TranscriptApp:
    def __init__(self, window):
        self.window = window
        window.title("YouTube Transcript to PDF")
        window.geometry("700x560")
        window.minsize(500, 400)

        # Messages from the background worker are put in this queue,
        # and the window picks them up and shows them (see check_messages).
        self.messages = queue.Queue()

        # --- Instructions ---------------------------------------------------
        tk.Label(
            window,
            text="Paste YouTube links below (one per line), then click Make PDF.",
            font=("TkDefaultFont", 12),
        ).pack(anchor="w", padx=12, pady=(12, 4))

        # --- Box where you paste links --------------------------------------
        self.links_box = scrolledtext.ScrolledText(window, height=6, wrap="none")
        self.links_box.pack(fill="x", padx=12)
        self.links_box.focus_set()
        self.add_right_click_menu(self.links_box)

        # --- Buttons ---------------------------------------------------------
        buttons = tk.Frame(window)
        buttons.pack(fill="x", padx=12, pady=8)

        tk.Button(buttons, text="Paste link", command=self.paste_link).pack(side="left")
        tk.Button(buttons, text="Clear", command=self.clear_links).pack(side="left", padx=6)

        self.make_button = tk.Button(
            buttons, text="Make PDF", font=("TkDefaultFont", 12, "bold"),
            command=self.start,
        )
        self.make_button.pack(side="left", padx=6)

        tk.Button(
            buttons, text="Open PDF folder", command=self.open_output_folder
        ).pack(side="right")

        # --- Area that shows what's happening --------------------------------
        tk.Label(window, text="Progress:").pack(anchor="w", padx=12)
        self.log_box = scrolledtext.ScrolledText(window, height=14, state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.log(f"PDFs will be saved in:\n  {yt_to_pdf.OUTPUT_FOLDER}")

        # Start checking for messages from the worker.
        self.window.after(100, self.check_messages)

    # ------------------------------------------------------------------------
    # Small helpers for the buttons
    # ------------------------------------------------------------------------

    def add_right_click_menu(self, text_box):
        """Right-click on the links box shows a Paste option."""
        menu = tk.Menu(text_box, tearoff=False)
        menu.add_command(label="Paste", command=self.paste_link)
        menu.add_command(label="Clear", command=self.clear_links)
        text_box.bind("<Button-3>", lambda event: menu.tk_popup(event.x_root, event.y_root))

    def paste_link(self):
        """Paste whatever you copied onto a new line in the links box."""
        try:
            copied = self.window.clipboard_get().strip()
        except tk.TclError:
            self.log("Nothing to paste - copy a YouTube link first.")
            return
        existing = self.links_box.get("1.0", "end").strip()
        if existing:
            self.links_box.insert("end", "\n")
        self.links_box.insert("end", copied)

    def clear_links(self):
        self.links_box.delete("1.0", "end")

    def open_output_folder(self):
        """Open the output folder in your file manager."""
        folder = yt_to_pdf.OUTPUT_FOLDER
        os.makedirs(folder, exist_ok=True)
        if sys.platform.startswith("win"):
            os.startfile(folder)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])

    def log(self, message):
        """Add a line of text to the progress area."""
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    # ------------------------------------------------------------------------
    # Making the PDFs
    # ------------------------------------------------------------------------

    def start(self):
        """Called when you click Make PDF."""
        text = self.links_box.get("1.0", "end")
        links = [line.strip() for line in text.splitlines() if line.strip()]
        if not links:
            self.log("Please paste at least one YouTube link first.")
            return

        # Grey out the button so it isn't clicked twice.
        self.make_button.configure(state="disabled", text="Working...")

        # Downloading takes a few seconds, so do it in the background.
        # Otherwise the window would freeze until it's finished.
        worker = threading.Thread(target=self.make_pdfs, args=(links,), daemon=True)
        worker.start()

    def make_pdfs(self, links):
        """Runs in the background. Sends messages to the window via the queue."""
        successes = 0
        for link in links:
            if yt_to_pdf.process_link(link, log=self.messages.put):
                successes += 1
        self.messages.put(f"\nFinished: {successes} of {len(links)} PDF(s) created.")
        self.messages.put("DONE")

    def check_messages(self):
        """Show any new messages from the background worker."""
        while not self.messages.empty():
            message = self.messages.get()
            if message == "DONE":
                self.make_button.configure(state="normal", text="Make PDF")
                self.clear_links()
            else:
                self.log(message)
        self.window.after(100, self.check_messages)


def main():
    window = tk.Tk()
    TranscriptApp(window)
    window.mainloop()


if __name__ == "__main__":
    main()
