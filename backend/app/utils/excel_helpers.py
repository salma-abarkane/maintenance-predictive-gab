from __future__ import annotations

from io import BytesIO
from typing import Iterable

import pandas as pd
from fastapi import UploadFile


def load_excel_file(upload_file: UploadFile, required_sheets: Iterable[str] | None = None) -> pd.ExcelFile:
    """Read an uploaded Excel file and validate the required sheets."""
    filename = upload_file.filename or ''
    if not filename.lower().endswith(('.xlsx', '.xls')):
        raise ValueError('Format de fichier invalide. Veuillez importer un fichier Excel .xlsx ou .xls.')

    content = upload_file.file.read()
    if not content:
        raise ValueError('Le fichier Excel importé est vide.')

    workbook = pd.ExcelFile(BytesIO(content))
    missing_sheets = [sheet for sheet in (required_sheets or []) if sheet not in workbook.sheet_names]
    if missing_sheets:
        raise ValueError(f"Feuille Excel manquante: {', '.join(missing_sheets)}")

    upload_file.file.seek(0)
    return workbook
