# Clinical Genetic Report Reader

This project provides a small desktop utility for extracting key information
from clinical genetic reports.  It combines the `olmOCR2` OCR engine with a
Tkinter-based GUI that lets you pick a report image, run OCR, and export the
resulting table as Markdown for downstream clinical workflows.

## Features

- Load scanned clinical report images (PNG, JPEG, TIFF, BMP, ...).
- Run OCR using `olmOCR2` and display the recognised text.
- Parse common report patterns into a tidy key/value table.
- Export the table to Markdown for inclusion in patient notes.

## Getting started

1. Install dependencies (Tkinter is included with most Python distributions) and
   install the package in editable mode so the ``gene_report_reader`` module is
   discoverable:

   ```bash
   pip install olmOCR2
   pip install -e .
   ```

2. Launch the application:

   ```bash
   python -m gene_report_reader.gui
   ```

3. Use **Load Image** to select a report, then **Run OCR** to extract the text.
   The parsed fields appear in the table and can be exported via
   **Export Markdown**.

> **Note:** If `olmOCR2` exposes a non-standard API, you may need to adapt
> `gene_report_reader/ocr_client.py` with the appropriate integration logic.
