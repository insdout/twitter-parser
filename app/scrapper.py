import os
from utils import recent_tweets_crawler, get_client, env_variable_handler


def main(bearer_token, query, tweets_limit, since,
         until, folder_path, tweets_per_request, sleep_delay):

    # Get Twitter API client
    client = get_client(bearer_token=bearer_token)

    """
    # Build the query
    NOT USED FOR NOW,
    PASSING QUERY AS ARGUMENT IS MORE FLEXIBLE

    query = query_builder(
        body=args.query_body,
        include_retweets=args.include_retweets,
        language=args.query_language,
        seed=args.query_seed,
        start_date=args.start_date,
        end_date=args.end_date
    )
    """

    # Scrap recent tweets
    recent_tweets_crawler(
        client=client,
        query=query,
        tweets_limit=tweets_limit,
        since=since,
        until=until,
        folder_path=folder_path,
        tweets_per_request=tweets_per_request,
        sleep_delay=sleep_delay)


if __name__ == "__main__":

    bearer_token = env_variable_handler(os.getenv("SCRAPPER_TOKEN"))
    query = env_variable_handler(os.getenv("QUERY"))

    tweets_limit = env_variable_handler((os.getenv("SCRAPPER_TWEETS_LIMIT")))
    tweets_limit = int(tweets_limit) if tweets_limit is not None else None

    since = env_variable_handler(os.getenv("SCRAPPER_SINCE"))
    until = env_variable_handler(os.getenv("SCRAPPER_UNTIL"))
    folder_path = env_variable_handler(os.getenv("SCRAPPER_FOLDER_PATH"))

    tweets_per_request = env_variable_handler(os.getenv("SCRAPPER_TWEETS_PER_REQUEST"))
    tweets_per_request = int(tweets_per_request) if tweets_per_request is not None else None

    sleep_delay = env_variable_handler(os.getenv("SCRAPPER_SLEEP_DELAY"))
    sleep_delay = int(sleep_delay) if sleep_delay is not None else None

    print(f"Passed env variables:\n"
          f"Bearer Token: {bearer_token}\n"
          f"Query: {query}\n"
          f"Tweets Limit: {tweets_limit}\n"
          f"Since: {since}\n"
          f"Until: {until}\n"
          f"Folder Path: {folder_path}\n"
          f"Tweets per Request: {tweets_per_request}\n"
          f"Sleep Delay: {sleep_delay}")

    main(
        bearer_token=bearer_token,
        query=query,
        tweets_limit=tweets_limit,
        since=since,
        until=until,
        folder_path=folder_path,
        tweets_per_request=tweets_per_request,
        sleep_delay=sleep_delay
        )
