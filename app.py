import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from steganography.lsb import (
    calculate_capacity_bytes,
    embed_message,
    extract_message,
    visualize_lsb,
)
from steganography.metrics import calculate_mse, calculate_psnr, save_histogram


MAX_MESSAGE_BYTES = 5120


class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secret Services - LSB")
        self.root.geometry("980x720")
        self.root.minsize(900, 650)

        self.cover_path = None
        self.stego_path = None
        self.cover_image = None
        self.stego_image = None
        self.analysis_cover_path = None
        self.analysis_stego_path = None
        self.analysis_cover_image = None
        self.analysis_stego_image = None

        self.build_ui()

    def build_ui(self):
        self.configure_styles()

        header = tk.Frame(self.root, bg="#173b37", padx=26, pady=19)
        header.pack(fill="x")
        tk.Label(
            header,
            text="IMAGE SECURITY LAB  /  LSB",
            bg="#173b37",
            fg="#c8ef78",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="Secret Services",
            bg="#173b37",
            fg="#f4f7ef",
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w", pady=(3, 1))
        tk.Label(
            header,
            text="LSB embedding  |  XOR encryption  |  Stego-key protection",
            bg="#173b37",
            fg="#b6c9c2",
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=20, pady=(16, 20))

        self.embed_tab, self.embed_content = self.create_scrollable_tab(notebook)
        self.extract_tab, self.extract_content = self.create_scrollable_tab(notebook)
        self.analysis_tab, self.analysis_content = self.create_scrollable_tab(notebook)

        notebook.add(self.embed_tab, text="  01  Embed  ")
        notebook.add(self.extract_tab, text="  02  Extract  ")
        notebook.add(self.analysis_tab, text="  03  Analysis  ")

        self.build_embed_tab()
        self.build_extract_tab()
        self.build_analysis_tab()

    def create_scrollable_tab(self, notebook):
        tab = ttk.Frame(notebook, padding=10, style="Page.TFrame")
        canvas = tk.Canvas(
            tab,
            background="#f0f4f1",
            highlightthickness=0,
            borderwidth=0,
        )
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        content = ttk.Frame(canvas, padding=10, style="Page.TFrame")

        content_window = canvas.create_window((0, 0), window=content, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        content.bind(
            "<Configure>",
            lambda event: canvas.configure(scrollregion=canvas.bbox("all")),
        )
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(content_window, width=event.width),
        )
        canvas.bind(
            "<Enter>",
            lambda event: canvas.bind_all(
                "<MouseWheel>",
                lambda wheel_event: canvas.yview_scroll(
                    int(-wheel_event.delta / 120), "units"
                ),
            ),
        )
        canvas.bind("<Leave>", lambda event: canvas.unbind_all("<MouseWheel>"))

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return tab, content

    def configure_styles(self):
        self.root.configure(bg="#f0f4f1")
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background="#f0f4f1")
        style.configure("Page.TFrame", background="#f0f4f1")
        style.configure(
            "TLabel",
            background="#f0f4f1",
            foreground="#263b37",
            font=("Segoe UI", 10),
        )
        style.configure(
            "Section.TLabel",
            background="#f0f4f1",
            foreground="#173b37",
            font=("Segoe UI", 11, "bold"),
        )
        style.configure(
            "Status.TLabel",
            background="#e2eee7",
            foreground="#245a49",
            padding=(10, 7),
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "TButton",
            background="#ffffff",
            foreground="#24443d",
            bordercolor="#c9d8d0",
            padding=(12, 8),
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "TButton",
            background=[("active", "#e4eee8"), ("pressed", "#d5e4da")],
        )
        style.configure(
            "Action.TButton",
            background="#176b56",
            foreground="#ffffff",
            bordercolor="#176b56",
            padding=(16, 9),
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "Action.TButton",
            background=[("active", "#0f5745"), ("pressed", "#0b493a")],
        )
        style.configure(
            "TNotebook",
            background="#f0f4f1",
            borderwidth=0,
            tabmargins=(0, 0, 0, 0),
        )
        style.configure(
            "TNotebook.Tab",
            background="#e2eae5",
            foreground="#52655e",
            padding=(16, 10),
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", "#ffffff"), ("active", "#d6e4dc")],
            foreground=[("selected", "#176b56")],
        )
        style.configure(
            "TLabelframe",
            background="#f0f4f1",
            bordercolor="#d4dfd8",
            relief="solid",
        )
        style.configure(
            "TLabelframe.Label",
            background="#f0f4f1",
            foreground="#173b37",
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "TEntry",
            fieldbackground="#ffffff",
            foreground="#263b37",
            padding=8,
            bordercolor="#c9d8d0",
        )

    def build_embed_tab(self):
        frame = self.embed_content

        ttk.Label(frame, text="Cover Image (PNG/BMP)").grid(row=0, column=0, sticky="w")
        ttk.Button(frame, text="Choose Image", command=self.choose_cover).grid(
            row=0, column=1, padx=10, sticky="w"
        )

        self.cover_label = ttk.Label(frame, text="No image selected")
        self.cover_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=5)

        ttk.Label(frame, text="Capacity").grid(row=2, column=0, sticky="w", pady=5)
        self.capacity_var = tk.StringVar(value="-")
        ttk.Label(frame, textvariable=self.capacity_var).grid(row=2, column=1, sticky="w")

        ttk.Label(frame, text="Message").grid(row=3, column=0, sticky="nw", pady=(15, 5))
        self.message_text = tk.Text(
            frame,
            height=8,
            width=75,
            wrap="word",
            bg="#ffffff",
            fg="#263b37",
            insertbackground="#176b56",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#c9d8d0",
            highlightcolor="#176b56",
            padx=10,
            pady=9,
            font=("Segoe UI", 10),
        )
        self.message_text.grid(row=3, column=1, columnspan=2, sticky="ew", pady=(15, 5))
        self.message_size_var = tk.StringVar(
            value="Ukuran pesan: 0 byte | Kategori: Belum ada pesan"
        )
        ttk.Label(frame, textvariable=self.message_size_var, style="Status.TLabel").grid(
            row=4, column=1, columnspan=2, sticky="ew", pady=(0, 6)
        )
        self.message_text.bind("<<Modified>>", self.update_message_size)
        self.message_text.edit_modified(False)

        ttk.Label(frame, text="Stego-Key").grid(row=5, column=0, sticky="w", pady=5)
        self.embed_key = ttk.Entry(frame, width=45, show="*")
        self.embed_key.grid(row=5, column=1, sticky="w")

        ttk.Button(
            frame,
            text="EMBED MESSAGE",
            command=self.do_embed,
            style="Action.TButton",
        ).grid(row=6, column=1, sticky="w", pady=15)

        self.embed_status = tk.StringVar(value="Status: Waiting")
        ttk.Label(frame, textvariable=self.embed_status, style="Status.TLabel").grid(
            row=7, column=0, columnspan=3, sticky="ew"
        )

        preview = ttk.Frame(frame)
        preview.grid(row=8, column=0, columnspan=3, sticky="nsew", pady=10)

        self.cover_preview = ttk.Label(
            preview, text="COVER IMAGE", style="Section.TLabel", anchor="center"
        )
        self.cover_preview.pack(side="left", padx=15)

        self.stego_preview = ttk.Label(
            preview, text="STEGO IMAGE", style="Section.TLabel", anchor="center"
        )
        self.stego_preview.pack(side="left", padx=15)

        self.metrics_var = tk.StringVar(value="MSE: -    |    PSNR: -")
        ttk.Label(frame, textvariable=self.metrics_var).grid(
            row=9, column=0, columnspan=3, sticky="w", pady=5
        )

        ttk.Button(
            frame,
            text="SAVE STEGO IMAGE",
            command=self.save_stego,
            style="Action.TButton",
        ).grid(row=10, column=1, sticky="w", pady=10)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(8, weight=1)

    def update_message_size(self, _event=None):
        if not self.message_text.edit_modified():
            return

        message = self.message_text.get("1.0", "end-1c")
        size_bytes = len(message.encode("utf-8"))
        if size_bytes == 0:
            category = "Belum ada pesan"
        elif size_bytes <= 100:
            category = "Kecil (maks. 100 byte)"
        elif size_bytes <= 1024:
            category = "Sedang (101-1.024 byte)"
        elif size_bytes <= MAX_MESSAGE_BYTES:
            category = "Besar (1.025-5.120 byte)"
        else:
            category = "ERROR: Melebihi batas 5.120 byte"

        self.message_size_var.set(
            f"Ukuran pesan: {size_bytes:,} byte | Kategori: {category}"
        )
        self.message_text.edit_modified(False)

    def build_extract_tab(self):
        frame = self.extract_content

        ttk.Label(frame, text="Stego Image (PNG/BMP)").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Button(frame, text="Choose Image", command=self.choose_stego).grid(
            row=0, column=1, padx=10, sticky="w"
        )

        self.stego_label = ttk.Label(frame, text="No image selected")
        self.stego_label.grid(row=1, column=0, columnspan=3, sticky="w", pady=8)

        ttk.Label(frame, text="Stego-Key").grid(row=2, column=0, sticky="w", pady=8)
        self.extract_key = ttk.Entry(frame, width=45, show="*")
        self.extract_key.grid(row=2, column=1, sticky="w")

        ttk.Button(
            frame,
            text="EXTRACT MESSAGE",
            command=self.do_extract,
            style="Action.TButton",
        ).grid(row=3, column=1, sticky="w", pady=15)

        ttk.Label(frame, text="Extracted Message").grid(
            row=4, column=0, sticky="nw", pady=5
        )
        self.extracted_text = tk.Text(
            frame,
            height=12,
            width=80,
            wrap="word",
            bg="#ffffff",
            fg="#263b37",
            insertbackground="#176b56",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#c9d8d0",
            highlightcolor="#176b56",
            padx=10,
            pady=9,
            font=("Segoe UI", 10),
        )
        self.extracted_text.grid(row=4, column=1, columnspan=2, sticky="nsew")

        self.extract_status = tk.StringVar(value="Status: Waiting")
        ttk.Label(
            frame, textvariable=self.extract_status, style="Status.TLabel"
        ).grid(row=5, column=0, columnspan=3, sticky="ew", pady=10)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)

    def build_analysis_tab(self):
        frame = self.analysis_content

        ttk.Label(
            frame,
            text="Enhanced LSB Visualization",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        image_frame = ttk.LabelFrame(frame, text="Analysis Images", padding=12)
        image_frame.pack(fill="x", pady=(0, 10))

        ttk.Label(image_frame, text="Cover Image (PNG/BMP)").grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=5
        )
        ttk.Button(
            image_frame,
            text="Choose Cover",
            command=self.choose_analysis_cover,
        ).grid(row=0, column=1, sticky="w", pady=5)
        self.analysis_cover_label = ttk.Label(
            image_frame, text="No cover image selected"
        )
        self.analysis_cover_label.grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(0, 8)
        )

        ttk.Label(image_frame, text="Stego Image (PNG/BMP)").grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=5
        )
        ttk.Button(
            image_frame,
            text="Choose Stego",
            command=self.choose_analysis_stego,
        ).grid(row=2, column=1, sticky="w", pady=5)
        self.analysis_stego_label = ttk.Label(
            image_frame, text="No stego image selected"
        )
        self.analysis_stego_label.grid(
            row=3, column=0, columnspan=3, sticky="w", pady=(0, 8)
        )

        ttk.Button(
            image_frame,
            text="ANALYZE IMAGES",
            command=self.analyze_images,
            style="Action.TButton",
        ).grid(row=4, column=1, sticky="w", pady=(5, 0))

        self.analysis_metrics_var = tk.StringVar(value="MSE: -    |    PSNR: -")
        ttk.Label(
            image_frame, textvariable=self.analysis_metrics_var
        ).grid(row=5, column=0, columnspan=3, sticky="w", pady=(10, 0))

        ttk.Button(
            frame,
            text="Choose Image for LSB Visualization",
            command=self.visualize_selected_lsb,
        ).pack(anchor="w", pady=5)

        ttk.Label(
            frame,
            text=(
                "The visualization highlights the least significant bit plane "
                "for visual inspection."
            ),
            wraplength=800,
        ).pack(anchor="w", pady=5)

        ttk.Button(
            frame,
            text="Save Histogram of Cover/Stego",
            command=self.save_histograms,
        ).pack(anchor="w", pady=15)

    @staticmethod
    def _image_filetypes():
        return [
            ("Image files", "*.png *.jpg *.jpeg *.bmp"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("BMP files", "*.bmp"),
            ("All files", "*.*"),
        ]

    def choose_analysis_cover(self):
        path = filedialog.askopenfilename(
            title="Choose Cover Image",
            filetypes=self._image_filetypes(),
        )
        if not path:
            return
        try:
            self.analysis_cover_image = Image.open(path).convert("RGB")
            self.analysis_cover_path = path
            self.analysis_cover_label.config(text=path)
            self.analysis_metrics_var.set("MSE: -    |    PSNR: -")
        except Exception as exc:
            messagebox.showerror("Error", f"Cannot open cover image:\n{exc}")

    def choose_analysis_stego(self):
        path = filedialog.askopenfilename(
            title="Choose Stego Image",
            filetypes=self._image_filetypes(),
        )
        if not path:
            return
        try:
            self.analysis_stego_image = Image.open(path).convert("RGB")
            self.analysis_stego_path = path
            self.analysis_stego_label.config(text=path)
            self.analysis_metrics_var.set("MSE: -    |    PSNR: -")
        except Exception as exc:
            messagebox.showerror("Error", f"Cannot open stego image:\n{exc}")

    def analyze_images(self):
        if self.analysis_cover_image is None or self.analysis_stego_image is None:
            messagebox.showwarning(
                "Warning", "Please choose both cover and stego images."
            )
            return

        try:
            mse = calculate_mse(
                self.analysis_cover_image, self.analysis_stego_image
            )
            psnr = calculate_psnr(
                self.analysis_cover_image, self.analysis_stego_image
            )
            psnr_text = "inf" if psnr == float("inf") else f"{psnr:.4f} dB"
            self.analysis_metrics_var.set(
                f"MSE: {mse:.6f}    |    PSNR: {psnr_text}"
            )
        except ValueError as exc:
            messagebox.showerror("Analysis Error", str(exc))
        except Exception as exc:
            messagebox.showerror("Error", f"Image analysis failed:\n{exc}")

    def choose_cover(self):
        path = filedialog.askopenfilename(
            title="Choose Cover Image",
            filetypes=self._image_filetypes(),
        )
        if not path:
            return

        try:
            image = Image.open(path).convert("RGB")
            self.cover_path = path
            self.cover_image = image
            capacity = calculate_capacity_bytes(image)
            self.cover_label.config(text=path)
            self.capacity_var.set(f"{capacity:,} bytes")
            self.show_preview(image, self.cover_preview)
            self.embed_status.set("Status: Cover image loaded")
        except Exception as exc:
            messagebox.showerror("Error", f"Cannot open image:\n{exc}")

    def choose_stego(self):
        path = filedialog.askopenfilename(
            title="Choose Stego Image",
            filetypes=self._image_filetypes(),
        )
        if not path:
            return
        self.stego_path = path
        self.stego_label.config(text=path)
        self.extract_status.set("Status: Stego image loaded")

    def do_embed(self):
        if self.cover_image is None:
            messagebox.showwarning("Warning", "Please choose a PNG/BMP cover image.")
            return

        message = self.message_text.get("1.0", "end-1c")
        key = self.embed_key.get()

        if not message:
            messagebox.showwarning("Warning", "Message cannot be empty.")
            return
        if not key:
            messagebox.showwarning("Warning", "Stego-key cannot be empty.")
            return

        message_size = len(message.encode("utf-8"))
        if message_size > MAX_MESSAGE_BYTES:
            error = (
                f"Ukuran pesan {message_size:,} byte melebihi batas maksimum "
                f"{MAX_MESSAGE_BYTES:,} byte."
            )
            self.embed_status.set(f"Status: Error - {error}")
            messagebox.showerror("Batas Ukuran Pesan", error)
            return

        try:
            stego = embed_message(self.cover_image, message, key)
            self.stego_image = stego

            mse = calculate_mse(self.cover_image, stego)
            psnr = calculate_psnr(self.cover_image, stego)

            self.show_preview(stego, self.stego_preview)
            self.metrics_var.set(f"MSE: {mse:.6f}    |    PSNR: {psnr:.4f} dB")
            self.embed_status.set("Status: Message embedded successfully")

            path = filedialog.asksaveasfilename(
                title="Save Stego Image",
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("BMP", "*.bmp")],
                initialfile="stego_result.png",
            )
            if path:
                stego.save(path)
                self.stego_path = path
                messagebox.showinfo("Success", f"Stego image saved:\n{path}")
        except ValueError as exc:
            messagebox.showerror("Capacity / Validation Error", str(exc))
        except Exception as exc:
            messagebox.showerror("Error", f"Embedding failed:\n{exc}")

    def do_extract(self):
        if not self.stego_path:
            messagebox.showwarning("Warning", "Please choose a stego image.")
            return

        key = self.extract_key.get()
        if not key:
            messagebox.showwarning("Warning", "Stego-key cannot be empty.")
            return

        try:
            image = Image.open(self.stego_path).convert("RGB")
            message = extract_message(image, key)

            self.extracted_text.delete("1.0", "end")
            self.extracted_text.insert("1.0", message)
            self.extract_status.set("Status: Extraction successful")
        except Exception as exc:
            self.extracted_text.delete("1.0", "end")
            self.extract_status.set("Status: Extraction failed")
            messagebox.showerror(
                "Extraction Failed",
                "The message could not be extracted.\n\n"
                "Possible causes: wrong stego-key, unsupported/corrupted image, "
                "or the image was recompressed as JPEG.\n\n"
                f"Details: {exc}",
            )

    def visualize_selected_lsb(self):
        path = filedialog.askopenfilename(
            title="Choose Image",
            filetypes=self._image_filetypes(),
        )
        if not path:
            return
        try:
            image = Image.open(path).convert("RGB")
            lsb = visualize_lsb(image)
            save_path = filedialog.asksaveasfilename(
                title="Save Enhanced LSB",
                defaultextension=".png",
                filetypes=[("PNG", "*.png")],
                initialfile="enhanced_lsb.png",
            )
            if save_path:
                lsb.save(save_path)
                messagebox.showinfo("Success", f"Enhanced LSB saved:\n{save_path}")
        except Exception as exc:
            messagebox.showerror("Error", f"LSB visualization failed:\n{exc}")

    def save_histograms(self):
        cover_image = self.analysis_cover_image
        stego_image = self.analysis_stego_image
        if cover_image is None or stego_image is None:
            cover_image = self.cover_image
            stego_image = self.stego_image

        if cover_image is None or stego_image is None:
            messagebox.showwarning(
                "Warning", "Please choose both cover and stego images first."
            )
            return

        path = filedialog.asksaveasfilename(
            title="Save Histogram",
            defaultextension=".png",
            filetypes=[("PNG", "*.png")],
            initialfile="histogram_comparison.png",
        )
        if not path:
            return

        try:
            save_histogram(cover_image, stego_image, path)
            messagebox.showinfo("Success", f"Histogram saved:\n{path}")
        except Exception as exc:
            messagebox.showerror("Error", f"Histogram generation failed:\n{exc}")

    def save_stego(self):
        if self.stego_image is None:
            messagebox.showwarning("Warning", "No stego image available.")
            return
        path = filedialog.asksaveasfilename(
            title="Save Stego Image",
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("BMP", "*.bmp")],
            initialfile="stego_result.png",
        )
        if path:
            self.stego_image.save(path)
            self.stego_path = path
            messagebox.showinfo("Saved", f"Stego image saved:\n{path}")

    @staticmethod
    def show_preview(image, label):
        preview = image.copy()
        preview.thumbnail((350, 260))
        photo = ImageTk.PhotoImage(preview)
        label.configure(image=photo, text="")
        label.image = photo


if __name__ == "__main__":
    root = tk.Tk()
    try:
        ttk.Style().theme_use("clam")
    except tk.TclError:
        pass
    app = SteganographyApp(root)
    root.mainloop()
