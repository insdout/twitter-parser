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

This script processes CSV files containing tweet data. It extracts Arabic text, translates it to English (if applicable), and saves the results to a new CSV file.

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
