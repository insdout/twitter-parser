import os
import re
import argparse
import torch
import pandas as pd
from transformers import pipeline


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


def main(file_path, output_folder="./output", batch_size=15):
    """
    Process Arabic text from a CSV file, translate it to English, and save the results.

    Args:
        file_path (str): Path to the input CSV file.
        output_folder (str): Path to the output folder. Default is "./output".
        batch_size (int): Batch size for translation. Default is 15.
    """
    base_name = os.path.basename(file_path)
    file_name = os.path.splitext(base_name)[0]

    df = pd.read_csv(file_path)

    mask = df.lang == "ar"
    print(f"df len: {len(df)} len mask: {sum(mask)}")
    tweet_text = df[mask]["text"]
    clean_tweet_text = [extract_arabic(tweet) for tweet in tweet_text]

    # Check if GPU Available:
    device = "cuda" if torch.cuda.is_available() else "cpu"
    device_index = -1
    if device == "cuda":
        device_index = 0
    print(f"Running on: {device}: {device_index}")

    pipe = pipeline("translation", model="Helsinki-NLP/opus-mt-ar-en", device=device_index, batch_size=batch_size)
    translation = [t['translation_text'] for t in pipe(clean_tweet_text)]
    print(f" translated len: {len(translation)}")

    df["en_translation"] = None
    df.loc[mask, "en_translation"] = translation

    csv_filename = os.path.join(output_folder, f"{file_name}_post_processed.csv")
    # Create folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    df.to_csv(csv_filename, index=False)
    print(f"Saved to: {csv_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Arabic text from a CSV file and translate it to English.")
    parser.add_argument("file_path", type=str, default="data/20231020_230726.csv", help="Path to the input CSV file.")
    parser.add_argument("--output-folder", type=str, default="./output", help="Path to the output folder. Default is './output'.")
    parser.add_argument("--batch-size", type=int, default=15, help="Batch size for translation. Default is 15.")
    args = parser.parse_args()

    main(file_path=args.file_path, output_folder=args.output_folder, batch_size=args.batch_size)
