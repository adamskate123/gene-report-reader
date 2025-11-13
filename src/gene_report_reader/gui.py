"""Tkinter GUI for converting genetic reports into structured tables."""

from __future__ import annotations

import pathlib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

from .ocr_client import OCRClient, OCRClientError
from .parser import ParsedReport, format_markdown_table, parse_report_text


class Application(tk.Tk):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Clinical Genetic Report Reader")
        self.geometry("820x520")

        self._ocr_client: Optional[OCRClient] = None
        self._report: Optional[ParsedReport] = None
        self._image_path: Optional[pathlib.Path] = None

        self._build_widgets()

    # ------------------------------------------------------------------ Widgets
    def _build_widgets(self) -> None:
        main_frame = ttk.Frame(self, padding=12)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        load_button = ttk.Button(button_frame, text="Load Image", command=self._on_load)
        load_button.pack(side=tk.LEFT)

        process_button = ttk.Button(
            button_frame, text="Run OCR", command=self._on_process, state=tk.NORMAL
        )
        process_button.pack(side=tk.LEFT, padx=(8, 0))

        export_button = ttk.Button(
            button_frame, text="Export Markdown", command=self._on_export
        )
        export_button.pack(side=tk.LEFT, padx=(8, 0))

        self.status_label = ttk.Label(button_frame, text="Select a report image to begin.")
        self.status_label.pack(side=tk.RIGHT)

        # Treeview for the extracted table
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        self.tree = ttk.Treeview(tree_frame, columns=("Field", "Value"), show="headings")
        self.tree.heading("Field", text="Field")
        self.tree.heading("Value", text="Value")
        self.tree.column("Field", width=200, anchor=tk.W)
        self.tree.column("Value", width=580, anchor=tk.W)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Raw OCR text for troubleshooting
        raw_frame = ttk.LabelFrame(main_frame, text="Raw OCR Text", padding=8)
        raw_frame.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        self.raw_text = tk.Text(raw_frame, wrap=tk.WORD, height=10)
        self.raw_text.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------ Callbacks
    def _on_load(self) -> None:
        filetypes = [
            ("Images", "*.png *.jpg *.jpeg *.tif *.tiff *.bmp"),
            ("All files", "*.*"),
        ]
        path = filedialog.askopenfilename(title="Select report image", filetypes=filetypes)
        if not path:
            return

        self._image_path = pathlib.Path(path)
        self.status_label.configure(text=f"Loaded {self._image_path.name}")
        self.raw_text.delete("1.0", tk.END)
        self.tree.delete(*self.tree.get_children())
        self._report = None

    def _ensure_ocr_client(self) -> OCRClient:
        if self._ocr_client is None:
            self._ocr_client = OCRClient()
        return self._ocr_client

    def _on_process(self) -> None:
        if not self._image_path:
            messagebox.showinfo("No image", "Please load an image first.")
            return

        try:
            client = self._ensure_ocr_client()
            text = client.extract_text(str(self._image_path))
        except OCRClientError as exc:
            messagebox.showerror("OCR unavailable", str(exc))
            self.status_label.configure(text="OCR failed")
            return
        except Exception as exc:  # pragma: no cover - defensive UI guard
            messagebox.showerror("OCR error", f"An unexpected error occurred: {exc}")
            self.status_label.configure(text="OCR failed")
            return

        self.raw_text.delete("1.0", tk.END)
        self.raw_text.insert(tk.END, text)

        self._report = parse_report_text(text)
        self._populate_table(self._report.key_values)
        self.status_label.configure(text="OCR complete")

    def _populate_table(self, pairs) -> None:
        self.tree.delete(*self.tree.get_children())
        for field, value in pairs:
            self.tree.insert("", tk.END, values=(field, value))

    def _on_export(self) -> None:
        if not self._report:
            messagebox.showinfo("Nothing to export", "Run OCR before exporting.")
            return

        markdown = self._report.to_markdown()
        path = filedialog.asksaveasfilename(
            title="Save Markdown",
            defaultextension=".md",
            filetypes=(("Markdown", "*.md"), ("All files", "*.*")),
        )
        if not path:
            return

        pathlib.Path(path).write_text(markdown, encoding="utf-8")
        messagebox.showinfo("Export complete", f"Saved table to {path}")


def main() -> None:
    app = Application()
    app.mainloop()


if __name__ == "__main__":  # pragma: no cover - GUI entry point
    main()
