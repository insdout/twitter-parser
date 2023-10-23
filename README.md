# Twitter Data Scraper

This repository contains a set of Python scripts for scraping and processing Twitter data. The scripts are designed to be educational and demonstrate various tasks related to working with Twitter API and processing tweet data.

## Scripts

### `scrapper.py`

This script provides a command-line interface for building and executing Twitter search queries. It takes various parameters such as query body, inclusion of retweets, language, seed term, date range, and more.

**Script Overview**

The script performs the following tasks:

1. **Twitter Data Crawling:** Uses the Twitter API to crawl recent tweets based on specified parameters.
Saves the crawled data as a CSV file.
Parameter Handling:
    - Reads environment variables to set various parameters, making the script highly configurable.

#### Usage
1. Before running the script, make sure to set the required environment variables. You can reference these variables in a .env file. Here are the expected environment variables:
    - `SCRAPPER_TOKEN`: Bearer token for Twitter API access.
    -  `QUERY`: The search query string to use for data retrieval.
    -  `SCRAPPER_TWEETS_LIMIT`: The maximum number of tweets to retrieve (default is None).
    - `SCRAPPER_SINCE`: Start date for the tweet search (default is None).
    - `SCRAPPER_UNTIL`: End date for the tweet search (default is None).
    - `SCRAPPER_FOLDER_PATH`: Path to the folder where the output CSV file will be saved.
    - `SCRAPPER_TWEETS_PER_REQUEST`: The number of tweets to request per API call (default is None).
    - `SCRAPPER_SLEEP_DELAY`: The delay in seconds between each API request (default is None).

### `translator_api.py`

This script is designed to process CSV files containing tweet data. It performs the following tasks:

1. **Arabic Text Extraction**: The script first extracts Arabic text from each tweet using a regular expression pattern. This pattern matches Arabic Unicode characters, allowing the script to identify and extract Arabic text segments.

2. **Translation with Google Cloud Translate API**: The extracted Arabic text is then translated to English using the Google Cloud Translate API. This enables the script to generate English translations for the Arabic text segments.

3. **Handling Language Variance**: If a tweet is not in Arabic (as determined by its language code), the script marks it as "not Arabic" in the translation column.

4. **CSV Output**: The translated results are then appended to the DataFrame in a new column labeled `en_translation`. The combined DataFrame is then saved to a new CSV file with a unique timestamp.

#### Usage

1. **Environment Variables**: Before running the script, make sure to set the required environment variables. You can reference these variables in a `.env` file. Here are the expected environment variables:

    - `FILE_TO_TRANSLATE`: Path to the input CSV file.
   - `TRANSLATION_OUTPUT_FOLDER`: Path to the output folder where the translated CSV file will be saved.
   - `TRANSLATION_BATCH_SIZE`: Batch size for translation (default is 20).
   - `TRANSLATION_API_DELAY`: Delay in seconds between translation batches (default is 0.0).



### `utils.py`

This module contains utility functions used by the above scripts. It includes functions for authenticating with the Twitter API, loading seed terms, building search queries, saving results to CSV, and more.

## Getting Started

1. Clone the repository to your local machine.
2. Obtain Twitter API bearer token and save it in a .env file by variable name  `SCRAPPER_TOKEN`.
3. Obtain Google cloud service account credentials and save them to ./app/google_credentials.json
4. Edit .env file variables according to your needs.
5. Build scrapper_image Docker image:
```bash
docker build -t scrapper_image -f Dockerfile.scrapper .
```
6. Build translator_image Docker image:
```bash
docker build -t translator_image -f Dockerfile.translator .
```
7. Use scrapper_image:
```bash
docker run -v $(pwd)/data:/app/data --env-file=.env -e QUERY="hamas -is:retweet  lang:en" scrapper_image

```
8. Use translator_image:

```bash
docker run -v $(pwd)/data:/app/data -v $(pwd)/output:/app/output --env-file=.env -e FILE_TO_TRANSLATE=data/20231020_230726.csv translator_image

```
## .env file:

```env
# Defaults for Translator image:
TRANSLATION_OUTPUT_FOLDER=./output
TRANSLATION_BATCH_SIZE=40
TRANSLATION_API_DELAY=0


# Defaults for Scrapper image:
SCRAPPER_TOKEN=[YOUR_TOKEN_HERE]
SCRAPPER_TWEETS_LIMIT=20
SCRAPPER_SINCE=None
SCRAPPER_UNTIL=None
SCRAPPER_FOLDER_PATH=./data
SCRAPPER_TWEETS_PER_REQUEST=10
SCRAPPER_SLEEP_DELAY=15
```

## Dependencies

- google-api-core==1.34.0
- google-auth==1.35.0
- google-cloud-core==1.7.3
- google-cloud-translate==3.12.1
- googleapis-common-protos==1.61.0
- pandas==2.1.1
- tqdm==4.65.0
- tweepy==4.14.0

