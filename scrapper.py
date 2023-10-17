import argparse
from utils import query_builder, run_query, get_client

def main():
    parser = argparse.ArgumentParser(description="Twitter Search Query Builder and Runner")

    # Define command line arguments
    parser.add_argument("--query-body", type=str, default="", help="The main body of the query")
    parser.add_argument("--include-retweets", action="store_true", help="Include retweets in search results")
    parser.add_argument("--query-language", type=str, default="ar", help="Language code to filter results (e.g., 'en' for English)")
    parser.add_argument("--query-seed", type=str, default="hamas", help="Seed term to append to the query")
    parser.add_argument("--start-date", type=str, default="", help="Start date for the time range (format: 'yyyy-mm-dd')")
    parser.add_argument("--end-date", type=str, default="", help="End date for the time range (format: 'yyyy-mm-dd')")
    parser.add_argument("--max-results", type=int, default=100, help="Maximum number of results to retrieve")
    parser.add_argument("--limit", type=int, default=200, help="Maximum number of API requests to make")
    parser.add_argument("--no-save-results", action="store_false", help="Whether to save the results to a CSV file")

    args = parser.parse_args()

    # Get Twitter API client
    client = get_client()

    # Build the query
    query = query_builder(
        body=args.query_body,
        include_retweets=args.include_retweets,
        language=args.query_language,
        seed=args.query_seed,
        start_date=args.start_date,
        end_date=args.end_date
    )

    # Run the query
    run_query(
        client=client,
        query=query,
        max_results=args.max_results,
        limit=args.limit,
        save=args.no_save_results
    )


if __name__ == "__main__":
    main()
