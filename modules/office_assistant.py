
import os
import re
from pathlib import Path
from datetime import datetime

import pandas as pd
from openpyxl import load_workbook
from docx import Document


# =====================================================
# PROJECT FOLDERS
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

OUTPUT_DIR = BASE_DIR / "output"
EXCEL_OUTPUT_DIR = OUTPUT_DIR / "excel"
WORD_OUTPUT_DIR = OUTPUT_DIR / "word"

EXCEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
WORD_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# =====================================================
# EXCEL FUNCTIONS
# =====================================================

def list_excel_sheets(uploaded_file):
    """Get all worksheet names from an uploaded Excel workbook."""

    uploaded_file.seek(0)

    workbook = load_workbook(
        uploaded_file,
        read_only=True,
        data_only=False
    )

    try:
        return workbook.sheetnames
    finally:
        workbook.close()
        uploaded_file.seek(0)


def read_excel_file(uploaded_file, sheet_name=None):
    """Read data from the selected Excel worksheet."""

    uploaded_file.seek(0)

    try:
        df = pd.read_excel(
            uploaded_file,
            sheet_name=sheet_name if sheet_name else 0
        )
        return df

    finally:
        uploaded_file.seek(0)


def summarize_excel_file(uploaded_file, sheet_name=None):
    """Generate a detailed summary of an Excel worksheet."""

    df = read_excel_file(uploaded_file, sheet_name)

    summary = []

    summary.append("EXCEL WORKBOOK SUMMARY")
    summary.append("=" * 40)

    summary.append(f"Worksheet: {sheet_name or 'First Sheet'}")
    summary.append(f"Total Rows: {len(df)}")
    summary.append(f"Total Columns: {len(df.columns)}")

    summary.append(
        f"Duplicate Rows: {df.duplicated().sum()}"
    )

    summary.append("\nCOLUMN NAMES")
    summary.append("-" * 40)

    for column in df.columns:
        summary.append(str(column))

    summary.append("\nMISSING VALUES")
    summary.append("-" * 40)

    summary.append(
        df.isnull().sum().to_string()
    )

    summary.append("\nDATA TYPES")
    summary.append("-" * 40)

    summary.append(
        df.dtypes.to_string()
    )

    summary.append("\nSTATISTICAL SUMMARY")
    summary.append("-" * 40)

    summary.append(
        df.describe(include="all").transpose().to_string()
    )

    return "\n".join(summary)


# =====================================================
# UPDATE EXCEL CELL
# =====================================================

def convert_excel_value(value):
    """Convert user input into an appropriate Excel value."""

    value = str(value).strip()

    if value == "":
        return None

    # Formula
    if value.startswith("="):
        return value

    # Integer or decimal
    try:
        number = float(value)

        if number.is_integer():
            return int(number)

        return number

    except ValueError:
        return value


def update_excel_cell(
    uploaded_file,
    sheet_name,
    cell_address,
    new_value
):
    """
    Update a specific cell in an existing worksheet.

    Example:
        Sheet name: Sheet1
        Cell address: G2
        New cell value: =SUM(B2:B10)

    The original uploaded workbook remains unchanged.
    """

    if not sheet_name:
        raise ValueError("Please select a worksheet.")

    cell_address = str(cell_address).strip().upper()

    if not re.fullmatch(
        r"[A-Z]{1,3}[1-9][0-9]*",
        cell_address
    ):
        raise ValueError(
            "Invalid cell address. Example: A1, B5, G10."
        )

    if new_value is None or str(new_value).strip() == "":
        raise ValueError("Please enter a new cell value.")

    uploaded_file.seek(0)

    workbook = load_workbook(
        uploaded_file,
        data_only=False
    )

    try:

        if sheet_name not in workbook.sheetnames:
            raise ValueError(
                f"Worksheet '{sheet_name}' does not exist."
            )

        worksheet = workbook[sheet_name]

        # Update existing worksheet cell
        worksheet[cell_address] = convert_excel_value(new_value)

        # Enable automatic formula recalculation on opening
        if (
            isinstance(worksheet[cell_address].value, str)
            and worksheet[cell_address].value.startswith("=")
        ):
            workbook.calculation.fullCalcOnLoad = True
            workbook.calculation.forceFullCalc = True
            workbook.calculation.calcMode = "auto"

        # Create output file
        original_name = getattr(
            uploaded_file,
            "name",
            "workbook.xlsx"
        )

        file_name = (
            f"{Path(original_name).stem}_updated_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.xlsx"
        )

        output_path = EXCEL_OUTPUT_DIR / file_name

        workbook.save(output_path)

        return str(output_path)

    finally:
        workbook.close()
        uploaded_file.seek(0)


# =====================================================
# DOWNLOAD EXCEL WORKBOOK
# =====================================================

def get_excel_download_data(uploaded_file):
    """Return the original Excel workbook bytes for download."""

    uploaded_file.seek(0)
    data = uploaded_file.getvalue()
    uploaded_file.seek(0)

    return data


def export_sheet_to_csv(df):
    """Convert a selected worksheet DataFrame to CSV bytes."""

    return df.to_csv(index=False).encode("utf-8")


# =====================================================
# WORD DOCUMENT FUNCTIONS
# =====================================================

def read_word_file(uploaded_file):
    """Read text from an uploaded Word document."""

    document = Document(uploaded_file)

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    return "\n".join(paragraphs)


def create_word_file(title, content):
    """Create and save a Word document."""

    document = Document()

    document.add_heading(
        title or "Office Document",
        level=1
    )

    for line in content.splitlines():
        document.add_paragraph(line)

    file_name = (
        f"document_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.docx"
    )

    output_path = WORD_OUTPUT_DIR / file_name

    document.save(output_path)

    return str(output_path)


# =====================================================
# WORD DOCUMENT INFORMATION
# =====================================================

def get_word_document_info(uploaded_file):
    """Get basic information from an uploaded Word document."""

    document = Document(uploaded_file)

    paragraph_count = len(document.paragraphs)

    text = "\n".join(
        paragraph.text for paragraph in document.paragraphs
    )

    word_count = len(text.split())

    return {
        "paragraph_count": paragraph_count,
        "word_count": word_count,
        "character_count": len(text),
        "text": text
    }


# =====================================================
# END OF OFFICE ASSISTANT MODULE
# =====================================================
