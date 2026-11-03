from pathlib import Path
import pandas as pd

def excel_preview(file_path):
    path = Path(file_path)
    if not path.is_file():
        return f"File not found: {path}"
    df = pd.read_excel(path)
    return df.head(10).to_string(index=False)

def excel_summary(file_path):
    path = Path(file_path)
    if not path.is_file():
        return f"File not found: {path}"
    df = pd.read_excel(path)
    return (
        f"Rows: {len(df)}\nColumns: {len(df.columns)}\n"
        f"Column names: {list(df.columns)}\n"
        f"Missing values:\n{df.isna().sum().to_string()}\n"
        f"Numeric summary:\n{df.describe().to_string() if not df.select_dtypes('number').empty else 'No numeric columns.'}"
    )
