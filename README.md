# Twitter Data Scraper

This repository contains a set of Python scripts for scraping and processing Twitter data. The scripts are designed to be educational and demonstrate various tasks related to working with Twitter API and processing tweet data.

## Scripts

### `scrapper.py`

This script provides a command-line interface for building and executing Twitter search queries. It takes various parameters such as query body, inclusion of retweets, language, seed term, date range, and more.

Usage:
```bash
python scrapper.py --query-body "Your Query Here" --include-retweets --query-language "en" --query-seed "example" --start-date "yyyy-mm-dd" --end-date "yyyy-mm-dd" --max-results 100 --limit 200 --no-save-results
```

### `postprocess.py`

This script is designed to process CSV files containing tweet data. It performs the following tasks:

1. **Arabic Text Extraction**: The script first extracts Arabic text from each tweet using a regular expression pattern. This pattern matches Arabic Unicode characters, allowing the script to identify and extract Arabic text segments.

2. **Translation with Hugging Face**: The extracted Arabic text is then passed through a Hugging Face translation pipeline. The pipeline uses the model `Helsinki-NLP/opus-mt-tc-big-ar-en` to perform Arabic to English translation. This enables the script to generate English translations for the Arabic text segments.

3. **Handling Language Variance**: If a tweet is not in Arabic (as determined by its language code), the script marks it as "not arabic" in the translation column.

4. **CSV Output**: The translated results are then appended to the DataFrame in a new column labeled `translation`. The combined DataFrame is then saved to a new CSV file with a unique timestamp.

Usage:
```bash
python postprocess.py --folder-path "./data"
```
### `utils.py`

This module contains utility functions used by the above scripts. It includes functions for authenticating with the Twitter API, loading seed terms, building search queries, saving results to CSV, and more.

## Getting Started

1. Clone the repository to your local machine.
2. Ensure you have the necessary dependencies installed (e.g., pandas, tweepy, transformers).
3. Obtain Twitter API credentials and save them in a file named `credentials.json`.
4. Run the scripts according to the provided usage instructions.

## Dependencies

- pandas
- tweepy
- transformers
