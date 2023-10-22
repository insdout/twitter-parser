import os
import re
import pandas as pd
from google.oauth2 import service_account
from google.cloud import translate
import time
from tqdm import tqdm
import json


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


def get_client():
    """
    Retrieves a Translation API client and sets the parent resource.

    Returns:
        tuple: A tuple containing the Translation API client and the parent resource.
    """

    credentials_path = "google_credentials.json"
    service_account_info = json.load(open(credentials_path))
    gcp_project_id = service_account_info["project_id"]

    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    client = translate.TranslationServiceClient(credentials=credentials)

    location = "global"

    parent = f"projects/{gcp_project_id}/locations/{location}"
    return client, parent


def batch_translate(client, parent, texts, batch_size=20, delay_seconds=0.0):
    """
    Translates a batch of texts using the provided Translation API client.

    Args:
        client: Translation API client.
        parent (str): Parent resource of the form `projects/project-number/locations/location`.
        texts (list): List of texts to be translated.
        batch_size (int, optional): Size of each translation batch. Default is 20.
        delay_seconds (float, optional): Delay in seconds between each batch. Default is 0.0.

    Returns:
        list: List of translated texts.
    """
    translated_texts = []
    for i in tqdm(range(0, len(texts), batch_size)):
        batch = texts[i: i+batch_size]
        response = client.translate_text(
            request={
                "parent": parent,
                "contents": batch,
                "mime_type": "text/plain",  # mime types: text/plain, text/html
                "target_language_code": "en",
            }
        )
        batch_result = [translation.translated_text for translation in response.translations]
        translated_texts.extend(batch_result)

        time.sleep(delay_seconds)

    return translated_texts


def main(file_path, output_folder="./output", batch_size=20, delay_seconds=0.0):
    """
    Process Arabic text from a CSV file, translate it to English, and save the results.

    Args:
        file_path (str): Path to the input CSV file.
        output_folder (str): Path to the output folder. Default is "./output".
        batch_size (int): Batch size for translation. Default is 20.
    """
    base_name = os.path.basename(file_path)
    file_name = os.path.splitext(base_name)[0]

    df = pd.read_csv(file_path)

    mask = df.lang == "ar"
    print(f"df len: {len(df)} len mask: {sum(mask)}")
    tweet_text = df[mask]["text"]
    clean_tweet_text = [extract_arabic(tweet) for tweet in tweet_text]

    client, parent = get_client()

    translation = batch_translate(
        client=client,
        parent=parent,
        texts=clean_tweet_text,
        batch_size=batch_size,
        delay_seconds=delay_seconds
    )
    print(f" translated len: {len(translation)}")

    df["en_translation"] = None
    df.loc[mask, "en_translation"] = translation

    csv_filename = os.path.join(output_folder, f"{file_name}_post_processed.csv")
    # Create folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    df.to_csv(csv_filename, index=False)
    print(f"Saved to: {csv_filename}")


if __name__ == "__main__":

    file_path = os.getenv("FILE_TO_TRANSLATE")
    output_folder = os.getenv("TRANSLATION_OUTPUT_FOLDER")
    batch_size = int(os.getenv("TRANSLATION_BATCH_SIZE"))
    delay_seconds = int(os.getenv("TRANSLATION_API_DELAY"))

    print(
        f"Passed env variables:\nfilepath: {file_path} {type(file_path)}"
        f"\noutput_folder: {output_folder} {type(output_folder)}"
        f"\nbatch_size: {batch_size} {type(batch_size)}"
        f"\ndelay_seconds: {delay_seconds} {type(delay_seconds)}"
    )

    main(file_path=file_path, output_folder=output_folder, batch_size=batch_size, delay_seconds=delay_seconds)