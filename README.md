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
   discoverable.

   ### Windows (PowerShell)

   1. Open **PowerShell** and navigate to the project directory, for example:

      ```powershell
      cd C:\path\to\gene-report-reader
      ```

   2. (Optional) Create and activate a virtual environment:

      ```powershell
      py -m venv .venv
      .\.venv\Scripts\Activate.ps1
      ```

   3. Install the dependencies and the package in editable mode:

      ```powershell
      py -m pip install --upgrade pip
      py -m pip install olmOCR2
      py -m pip install -e .
      ```

   ### macOS (Terminal)

   1. Open the **Terminal** app and move into the project directory, for example:

      ```bash
      cd /path/to/gene-report-reader
      ```

   2. (Optional) Create and activate a virtual environment:

      ```bash
      python3 -m venv .venv
      source .venv/bin/activate
      ```

   3. Install the dependencies and the package in editable mode:

      ```bash
      python3 -m pip install --upgrade pip
      python3 -m pip install olmOCR2
      python3 -m pip install -e .
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
