import os
import pandas as pd
import sqlite3
from pathlib import Path

class StructuredToSQL:
    def __init__(self,db_path: str,files_dir:str=None,  use_dask: bool = False, threshold_mb: int = 100):

        self.files = files_dir
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.use_dask = use_dask
        self.threshold_mb = threshold_mb

    def _get_file_size_mb(self, filepath):
        return os.path.getsize(filepath) / (1024 * 1024)
    
    def _clean_dataframe(self, df):
        df = df.dropna(how='all')  # Drop fully empty rows
        df = df.dropna(axis=1, how='all')  # Drop fully empty columns
        return df
    
    def _rename_duplicate_columns(self,df):
        """
        Rename duplicate columns dynamically in a DataFrame by appending suffixes like _1, _2, etc.
        Example:
        ['費用', '費用', '費用'] ➜ ['費用', '費用_1', '費用_2']
        """
        from collections import defaultdict

        seen = defaultdict(int)
        new_columns = []

        for col in df.columns:
            if seen[col]:
                new_col = f"{col}_{seen[col]}"
            else:
                new_col = col
            seen[col] += 1
            new_columns.append(new_col)

        df.columns = new_columns
        return df

    

    def _insert_into_sql(self, df, table_name, mode="replace"):
        df = self._clean_dataframe(df)
        if not df.empty:
            try:
                df.to_sql(table_name, self.conn, if_exists=mode, index=False)
                print(f"✅ Inserted into table '{table_name}' ({len(df)} rows)")
            except Exception as e:
                print(f"❌ Error inserting into table '{table_name}': {e}")
        else:
            print(f"Skipped table '{table_name}' — cleaned DataFrame is empty")

    def _load_with_pandas(self, file_path, table_name):
        encodings_to_try = ['utf-8']#, 'shift_jis', 'iso-8859-1','cp932']
        for encoding in encodings_to_try:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                print(f"→ DF Columns: {df.columns.tolist()}")
                print("→ DF Preview:")
                print(df.head(2))
                self._insert_into_sql(df, table_name)
                print(f"[pandas] Loaded '{file_path}' → table '{table_name}' using encoding '{encoding}'")
                return
            except UnicodeDecodeError as e:
                print(f" Encoding '{encoding}' failed for {file_path}: {e}")
            except Exception as e:
                print(f"❌ Unexpected error for {file_path}: {e}")
                return
        print(f"❌ All encoding attempts failed for {file_path}")

    def _load_with_dask(self, file_path, table_name):
        import dask.dataframe as dd
        try:
            sample = pd.read_csv(file_path, nrows=5)
            print(f"→ Sample Columns: {sample.columns.tolist()}")
            col_dtypes = {col: 'object' for col in sample.columns}

            ddf = dd.read_csv(file_path, blocksize="64MB", engine='python', dtype=col_dtypes)

            for i in range(ddf.npartitions):
                chunk = ddf.get_partition(i).compute()
                mode = 'append' if i > 0 else 'replace'
                self._insert_into_sql(chunk, table_name, mode=mode)

            print(f"[dask] Loaded '{file_path}' → table '{table_name}'")
        except Exception as e:
            print(f"❌ Failed to load {file_path} with Dask: {e}")

    def _load_xlsx_with_pandas(self, file_path, table_name):
        try:
            excel_file = pd.ExcelFile(file_path, engine="openpyxl")
            for sheet_name in excel_file.sheet_names:
                df = excel_file.parse(sheet_name)
                full_table_name = f"{table_name}_{sheet_name}".lower()
                self._insert_into_sql(df, full_table_name)
                print(f"[xlsx] Loaded sheet '{sheet_name}' from '{file_path}' → table '{full_table_name}'")
        except Exception as e:
            print(f"❌ Failed to load Excel file {file_path}: {e}")

    def process_files(self):
        for full_path in self.files:
            file_lower = full_path.lower()
            table_name = os.path.splitext(file_lower)[0]
            file_size_mb = self._get_file_size_mb(full_path)
            try:
                if file_lower.endswith(".csv"):
                    if self.use_dask or file_size_mb > self.threshold_mb:
                        self._load_with_dask(full_path, table_name)
                    else:
                        self._load_with_pandas(full_path, table_name)
                elif file_lower.endswith((".xlsx", ".xlsm")):
                    self._load_xlsx_with_pandas(full_path, table_name)
                else:
                    print(f"⚠️ Skipping unsupported file: {full_path}")
            except Exception as e:
                print(f"❌ Error processing {full_path}: {e}")

    def process_individual_file(self,file_path=None):
        file_lower = file_path.lower()
        table_name = Path(file_lower).stem
        file_size_mb = self._get_file_size_mb(file_path)
        try:
            if file_lower.endswith(".csv"):
                if self.use_dask or file_size_mb > self.threshold_mb:
                    self._load_with_dask(file_path, table_name)
                else:
                    self._load_with_pandas(file_path, table_name)
            elif file_lower.endswith((".xlsx", ".xlsm")):
                self._load_xlsx_with_pandas(file_path, table_name)
            else:
                print(f"⚠️ Skipping unsupported file: {file_path}")
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    def close(self):
        self.conn.close()
