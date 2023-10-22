import os
from datetime import datetime
import tweepy
import json
import csv
import time


def get_client(bearer_token):
    """Returns a Twitter API client authenticated with bearer token.
    Reads the bearer token from a JSON file named 'credentials.json' in the same directory.

    Returns:
        tweepy.Client: Authenticated Twitter API client.
    """

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


def get_tweets(client, query, start_time=None, end_time=None, next_token=None, max_results=100):
    """
    Retrieve recent tweets based on a given query.

    Args:
        client: Twitter API client.
        query (str): Search query.
        start_time (str, optional): Start time for filtering tweets (ISO 8601 format).
        end_time (str, optional): End time for filtering tweets (ISO 8601 format).
        next_token (str, optional): Token for paginating through results.
        max_results (int, optional): Maximum number of results to retrieve (default is 100).

    Returns:
        dict: Response containing recent tweets.

    Raises:
        Exception: If an error occurs while fetching tweets.

    Note:
        - `start_time` and `end_time` should be in ISO 8601 format (YYYY-MM-DDTHH:mm:ssZ).
        - This function uses the 'search_recent_tweets' method from the Twitter API client.

    Example:
        response = get_tweets(client, query="#Python", max_results=50)
        print(response)

    """
   
    expansions = ["author_id"]  #["author_id" , "in_reply_to_user_id", "geo.place_id"]
    tweet_fields = ["author_id", "created_at", "text", "lang", "public_metrics"]
    user_fields =  ["profile_image_url", "name", "description", "created_at", "verified", "location", "public_metrics", "url", "withheld"]
    place_fields = None

    try:
        response = client.search_recent_tweets(
            query,
            max_results=max_results,
            next_token=next_token,
            start_time=start_time,
            end_time=end_time,
            expansions=expansions,
            tweet_fields=tweet_fields,
            user_fields=user_fields,
            place_fields=place_fields
        )

        return response

    except Exception as e:
        print("Error getting tweets", e)


def tweets_to_csv(response, destination_name):
    """
    Convert tweet data from a Twitter API response to a CSV file.

    Args:
        response (dict): Response from a Twitter API request.
        destination_name (str): Name of the destination CSV file.

    Returns:
        None

    Raises:
        Exception: If an error occurs while writing to the CSV file.

    Note:
        - The function expects a response in the format returned by the Twitter API.
        - The CSV file will include columns for tweet metadata such as creation timestamp,
          tweet ID, author ID, username, name, URLs, tweet content, language, retweet count, and like count.
        - If the specified CSV file already exists, the function will append new data to it.

    Example:
        response = { ... }  # Response from a Twitter API request
        destination_name = "tweets_data.csv"
        tweets_to_csv(response, destination_name)

    """
    usersdict = {x.id: {"username": x.username, "name": x.name} for x in response.includes['users']}

    tweet_data = [
        [
            "created_at",
            "tweet_id",
            "author_id",
            "username",
            "name",
            "user_url",
            "tweet_url",
            "text",
            "lang",
            "retweet_count",
            "like_count"
        ]
    ]

    for tweet in response.data:
        tweet_data.append(
            [
                tweet.created_at,
                tweet.id,
                tweet.author_id,
                usersdict[tweet.author_id]["username"],
                usersdict[tweet.author_id]["name"],
                f"https://twitter.com/{usersdict[tweet.author_id]['username']}",
                f"https://twitter.com/{usersdict[tweet.author_id]['username']}/status/{tweet.id}",
                tweet.text,
                tweet.lang,
                tweet.public_metrics["retweet_count"],
                tweet.public_metrics["like_count"],
            ]
        )

    # Check if the file already exists
    if not os.path.exists(destination_name):
        # If not, create it with headers
        with open(destination_name, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(tweet_data[0])

    # Append the rest of the data to the CSV
    row_counter = 0
    with open(destination_name, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for row in tweet_data[1:]:
            writer.writerow(row)
            row_counter += 1

    print(f"Wrote {row_counter} lines to {destination_name}.")


def recent_tweets_crawler(client, query, tweets_limit, since=None,
                          until=None, folder_path="./data/",
                          tweets_per_request=100, sleep_delay=15):
    """
    Crawl recent tweets from Twitter based on specified criteria.

    Args:
        client: Twitter API client.
        query (str): Twitter search query string.
        tweets_limit (int): Maximum number of tweets to collect.
        since (str, optional): Start date for the search in format 'YYYY-MM-DDTHH:mm:ssZ'.
        until (str, optional): End date for the search in format 'YYYY-MM-DDTHH:mm:ssZ'.
        folder_path (str, optional): Path to the folder for saving the data. Default is "./data/".
        tweets_per_request (int, optional): Number of tweets to retrieve per request. Default is 100.
        sleep_delay (int, optional): Delay in seconds between requests. Default is 15.

    Returns:
        None

    Note:
        - The function collects recent tweets based on the provided query and criteria.
        - The collected tweets are saved in a CSV file with a unique timestamp as the file name.
        - The function continues collecting tweets until the specified limit is reached or there are no more results.
        - The search can be further refined by specifying 'since' and 'until' parameters.

    Example:
        client = get_twitter_api_client()
        query = "#DataScience"
        tweets_limit = 1000
        recent_tweets_crawler(client, query, tweets_limit, since="2022-01-01T00:00:00Z")

    """

    # Generate a unique timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = os.path.join(folder_path, f"{timestamp}.csv")
    saved_tweets_count = 0
    next_token = None

    # Replace with time period of your choice
    # YYYY-MM-DDTHH:mm:ssZ
    # start_time = '2020-01-01T00:00:00Z'

    # Replace with time period of your choice
    # end_time = '2020-08-01T23:59:59Z'

    while True:
        response = get_tweets(
            client=client,
            query=query,
            start_time=since,
            end_time=until,
            next_token=next_token,
            max_results=tweets_per_request
        )

        """
        TODO: ADD RESPONSE HANDLING!
        ============================

        As in tweepy.paginator:
        +++++++++++++++++++++++++++++++++++++++++++++++++++++++
        response = self.method(*self.args, **self.kwargs)

        if isinstance(response, Response):
            meta = response.meta
        elif isinstance(response, dict):
            meta = response.get("meta", {})
        elif isinstance(response, requests.Response):
            meta = response.json().get("meta", {})
        else:
            raise RuntimeError(
                f"Unknown {type(response)} return type for "
                f"{self.method.__qualname__}"
            )

        self.previous_token = meta.get("previous_token")
        self.next_token = meta.get("next_token")
        self.count += 1

        return response
        +++++++++++++++++++++++++++++++++++++++++++++++++++++++
        """
        # Response meta content:
        # {'newest_id': '1715330213880472004',
        # 'oldest_id': '1715110596729840128',
        # 'result_count': 10,
        # 'next_token': 'b26v89c19zqg8o3fr5efrxgy7ldru6bjtu3sygkg4jybh'}

        meta = response.meta
        results_count = meta["result_count"]
        next_token = meta["next_token"]

        if results_count is not None and results_count > 0:
            tweets_to_csv(response=response, destination_name=file_path)
            saved_tweets_count += results_count

            if saved_tweets_count >= tweets_limit:
                print("Finished scrapping.")
                break
            if next_token:
                print(f"Next token: {next_token}. Seved {saved_tweets_count} tweets.")
                time.sleep(sleep_delay)
            else:
                print("Finished scrapping.")
                break
        else:
            print("Finished scrapping.")
            break


def env_variable_handler(variable):
    """
    Handles a specific environment variable.

    Args:
        variable (str): The environment variable to handle.

    Returns:
        str or None: The processed value of the environment variable.
    """
    # Check if the variable is set
    if variable is not None:
        # Check if it's an empty string or the string "None"
        if variable == "" or variable.lower() == "none":
            return None
        else:
            return variable
    else:
        return None
