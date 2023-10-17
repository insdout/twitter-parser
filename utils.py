import os
from datetime import datetime
import pandas as pd
import tweepy
import json


def get_client():
    """Returns a Twitter API client authenticated with bearer token.
    Reads the bearer token from a JSON file named 'credentials.json' in the same directory.

    Returns:
        tweepy.Client: Authenticated Twitter API client.
    """
    my_tokens = 'credentials.json'

    # Open the JSON file
    with open(my_tokens, 'r') as file:
        credentials = json.load(file)

    bearer_token = credentials["bearer_token"]

    # Twitter Authentification:
    client = tweepy.Client(bearer_token)
    return client


def load_seeds(path="./seeds.json"):
    """Load seed terms from a JSON file.

    Args:
        path (str, optional): Path to the JSON file. Defaults to "./seeds.json".

    Returns:
        dict: Dictionary of query seed phrases
    """
    with open(path, 'r', encoding='utf-8') as json_file:
        seeds = json.load(json_file)
    return seeds


def query_builder(body, include_retweets=False, language="", seed="", start_date="", end_date=""):
    """Builds a Twitter search query.

    Args:
        body (str): The main body of the query.
        include_retweets (bool, optional): Include retweets in search results. Defaults to False.
        language (str, optional): Language code to filter results (e.g., 'en' for English). Defaults to "".
        seed (str, optional): Seed term to append to the query. Defaults to "".
        start_date (str, optional): Start date for the time range (format: "yyyy-mm-dd"). Defaults to "".
        end_date (str, optional): End date for the time range (format: "yyyy-mm-dd"). Defaults to "".

    Returns:
        str: The constructed Twitter search query.
    """
    query = body
    seed_dict = load_seeds()

    if seed:
        query += f" {seed_dict[seed]}"

    if not include_retweets:
        query += " -is:retweet"

    if language in {"en", "ar", "he"}:
        query += f" lang:{language}"

    if start_date:
        query += f" since:{start_date}"

    if end_date:
        query += f" until:{end_date}"

    return query


def save_results_csv(tweets_df, folder_path="./data"):
    """Save tweets DataFrame to a CSV file with a unique timestamp as the file name.

    Args:
        tweets_df (pd.DataFrame): DataFrame containing tweets data.
        folder_path (str, optional): Path to the folder where the CSV 
        file will be saved. Defaults to "./data".

    Returns:
        str: The file path of the saved CSV file.
    """
    # Generate a unique timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Define the file path
    file_path = os.path.join(folder_path, f"{timestamp}.csv")

    # Create folder if it doesn't exist
    os.makedirs(folder_path, exist_ok=True)

    # Write the data to the CSV file
    tweets_df.to_csv(file_path, sep=",", index=False)
    print(f"Saved at {file_path}")
    return file_path


def run_query(client, query, max_results=10, limit=10, save=True):
    """
    Run a Twitter API query and process the results.

    Args:
        client: The Twitter API client.
        query (str): The search query.
        max_results (int, optional): Maximum number of results to retrieve. Defaults to 10.
        limit (int, optional): Maximum number of API requests to make. Defaults to 10.
        save (bool, optional): Whether to save the results to a CSV file. Defaults to True.

    Returns:
        pd.DataFrame: DataFrame containing processed tweet data.
    """
    try:
        tweets = tweepy.Paginator(
            client.search_recent_tweets,
            query,
            max_results=max_results,
            tweet_fields=[
                "author_id",
                "created_at",
                "text",
                "lang",
                "public_metrics",
                "context_annotations",
                "geo",
                "source"
            ]
        ).flatten(limit=limit)

        tweets_list = [
            [
                tweet.created_at,                       # Timestamp of when the tweet was created
                tweet.id,                               # Unique identifier for the tweet
                tweet.text,                             # The content of the tweet
                tweet.lang,                             # Language of the tweet
                tweet.public_metrics["retweet_count"],  # Number of retweets
                tweet.public_metrics["like_count"],     # Number of likes
                tweet.author_id,                        # ID of the author
                tweet.source,                           # Source or platform used to post the tweet
                tweet.context_annotations,              # Context annotations associated with the tweet
                tweet.geo                               # Geographical information (if available)
            ]
            for tweet in tweets
        ]

        tweets_df = pd.DataFrame(
            tweets_list,
            columns=[
                "Created At",
                "Tweet Id",
                "Text",
                "lang",
                "retweet_count",
                "like_count",
                "author_id",
                "source",
                "context_annotations",
                "geo"
            ]
        )

        if save:
            save_results_csv(tweets_df, folder_path="./data")
        return tweets_df

    except BaseException as e:
        print("failed on_status,", str(e))
