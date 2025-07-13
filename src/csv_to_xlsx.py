import pandas as pd
import os

def convert_csv_to_xlsx(input_csv_path: str):
    """
    Reads a CSV file from the specified input path and saves it as an
    XLSX (Excel) file to the specified output path using Pandas.

    Args:
        input_csv_path (str): The full path to the input CSV file.
        output_xlsx_path (str): The full path where the output XLSX file
                                will be saved.
    """
    try:
        # Check if the input CSV file exists
        if not os.path.exists(input_csv_path):
            print(f"Error: Input CSV file not found at '{input_csv_path}'")
            return

        # Read the CSV file into a Pandas DataFrame
        df = pd.read_csv(input_csv_path)
        base_name = os.path.splitext(input_csv_path)[0] # Gets 'sample_data' from 'sample_data.csv'
        output_xlsx_path = f"{base_name}.xlsx"

        # Save the DataFrame to an XLSX file
        # index=False prevents Pandas from writing the DataFrame index as a column in Excel
        df.to_excel(output_xlsx_path, index=False)

        print(f"Successfully converted '{input_csv_path}' to '{output_xlsx_path}'")

    except FileNotFoundError:
        # This specific error is caught by the os.path.exists check, but good to have
        print(f"Error: A file was not found during the operation. Check paths.")
    except pd.errors.EmptyDataError:
        print(f"Error: The CSV file at '{input_csv_path}' is empty.")
    except pd.errors.ParserError:
        print(f"Error: Could not parse the CSV file. Check its format.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")



# Define input and output file paths
input_file = "/Users/jbc/Documents/SevenSix/etl_data_extraction/data/s3_downloads/営業本部/営業活動/名刺データ/eight20250225132647utf8.csv"

# Call the function to convert the CSV to XLSX
convert_csv_to_xlsx(input_file)

