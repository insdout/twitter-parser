import os
import pandas as pd
from transformers import pipeline
import re
from datetime import datetime
import argparse
import torch


def extract_arabic(text):
    """
    Extracts Arabic text from a given string.

    Args:
        text (str): Input text.

    Returns:
        str: Extracted Arabic text.
    """
    arabic_pattern = r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+'
    arabic_text = re.findall(arabic_pattern, text)
    return " ".join(arabic_text)


def process_arabic_text(text, hf_pipeline):
    """
    Processes Arabic text using a Hugging Face translation pipeline.

    Args:
        text (str): Arabic input text.
        hf_pipeline: Hugging Face translation pipeline.

    Returns:
        str: Translated text.
    """
    text = extract_arabic(text)
    en_translated = hf_pipeline(text)[0]["translation_text"]
    return en_translated 


def assemble_df(folder_path="./data"):
    """
    Assembles a DataFrame by concatenating CSV files in a given folder.

    Args:
        folder_path (str, optional): Path to the folder containing CSV files. Defaults to "./data".

    Returns:
        pd.DataFrame: Combined DataFrame.
    """
    all_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".csv")]

    # Initialize an empty DataFrame
    combined_df = pd.DataFrame()

    # Loop through all CSV files and concatenate them
    for file in all_files:
        df = pd.read_csv(file)
        combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df


def main(folder_path="./data"):
    """
    Main function to process CSV files in a folder.

    Args:
        folder_path (str, optional): Path to the folder containing CSV files. Defaults to "./data".
    """
    df = assemble_df(folder_path=folder_path)

    # Check if GPU Available:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    device_index = -1
    if device == "cuda":
        device_index = 0
    print(f"Running on: {device}: {device_index}")

    pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-tc-big-ar-en", device=device_index)
    df['translation'] = df.apply(lambda row: process_arabic_text(row['Text'], pipe) if row['lang'] == 'ar' else "not arabic", axis=1)

    # Generate a unique timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join("./output", f"{timestamp}_post_processed.csv")
    # Create folder if it doesn't exist
    os.makedirs("./output", exist_ok=True)
    df.to_csv(csv_filename, index=False)
    print(f"Saved to: {csv_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CSV files in a folder.")
    parser.add_argument("--folder-path", type=str, default="./data", help="Path to the folder containing CSV files.")
    args = parser.parse_args()

    main(folder_path=args.folder_path)
