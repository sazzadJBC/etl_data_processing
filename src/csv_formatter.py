from pathlib import Path
import pandas as pd



# --- CSV CLEANING LOGIC ---

def clean_csv(input_path: Path, output_path: Path, rows_to_skip: int):
    """
    Reads a CSV file, skipping initial rows, and saves the cleaned CSV.

    :param input_path: Path to the original CSV file
    :param output_path: Path where the cleaned CSV will be saved
    :param rows_to_skip: Number of initial rows to skip
    """
    try:
        # Read CSV, skipping problematic header rows
        df = pd.read_csv(input_path, skiprows=rows_to_skip, encoding='utf-8')

        # Save cleaned data
        df.to_csv(output_path, index=False, encoding='utf-8')

        print(f"✅ Successfully cleaned: {input_path.name}")
        print(f"   Saved cleaned CSV to: {output_path}")

    except FileNotFoundError:
        print(f"❌ File not found: {input_path}")
    except Exception as e:
        print(f"❌ An error occurred during CSV cleaning: {e}")
        print("Check the number of rows to skip and file encoding.")


if __name__ == "__main__":

    # --- CONFIGURATION ---

    # Path to your problematic CSV file
    PROBLEM_CSV_PATH = Path(r"C:\Users\LENOVO\Documents\JBC_Work\SevenSix\ETL\RawDataForETL\private\eight20250225132647utf8.csv")

    # How many rows to skip at the top of the file
    ROWS_TO_SKIP = 5  # adjust this as needed

    # Path for the cleaned CSV
    CLEANED_CSV_PATH = PROBLEM_CSV_PATH.parent / f"cleaned_{PROBLEM_CSV_PATH.name}"
    clean_csv(PROBLEM_CSV_PATH, CLEANED_CSV_PATH, ROWS_TO_SKIP)
