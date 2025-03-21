import streamlit as st
import pandas as pd
from waybacktweets import WaybackTweets, TweetsParser

def wayback_tweets_main():
    # ----- Streamlit App Title -----
    st.title("Wayback Tweets")
    st.write("Easily explore and download archived tweets from Twitter/X  using the Wayback Machine.")

    # ----- User Inputs -----
    username = st.text_input("Enter the Twitter username:", placeholder="e.g., elonmusk")
    start_date = st.date_input("Start date", help="Start date for filtering archived tweets.")
    end_date = st.date_input("End date", help="End date for filtering archived tweets.")

    # Optional: Filter by archived status codes
    status_codes_filter = st.multiselect(
        "Filter by archived status codes (optional):",
        options=["200", "404", "500", "403"],
        help="Select status codes to filter tweets. Leave empty to skip filtering."
    )

    # ----- Query Button -----
    if st.button("Query Tweets"):
        # Basic validation
        if not username:
            st.error("Please enter a valid Twitter username.")
        elif start_date > end_date:
            st.error("The end date must be after the start date.")
        else:
            st.info("Fetching archived tweets. Please wait...")
            try:
                # 1. Fetch data from WaybackTweets
                api = WaybackTweets(username)
                archived_tweets = api.get()  # Returns a list of archived tweets

                if archived_tweets:
                    # 2. Define fields to parse
                    field_options = [
                        "archived_timestamp",
                        "original_tweet_url",
                        "archived_tweet_url",
                    ]
                    
                    # 3. Parse tweets into structured format
                    parser = TweetsParser(archived_tweets, username, field_options)
                    parsed_tweets = parser.parse()

                    # 4. Convert parsed tweets to a DataFrame
                    df = pd.DataFrame(parsed_tweets)

                    # 5. Rename columns
                    df.rename(
                        columns={
                            "archived_timestamp": "timestamp",
                            "original_tweet_url": "original_url",
                            "archived_tweet_url": "archived_url",
                            "archived_statuscode": "statuscode"
                        },
                        inplace=True
                    )

                    # 6. Convert timestamp column to datetime
                    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

                    # 7. Filter by date range
                    filtered_df = df[
                        (df["timestamp"] >= pd.Timestamp(start_date)) &
                        (df["timestamp"] <= pd.Timestamp(end_date))
                    ]

                    # 8. Filter by status codes if selected
                    if status_codes_filter:
                        filtered_df = filtered_df[
                            filtered_df["statuscode"].isin(status_codes_filter)
                        ]

                    # 9. Display results
                    st.success(f"Found {len(filtered_df)} tweets in the specified range.")
                    if not filtered_df.empty:
                        st.write("Filtered Archived Tweets:")
                        st.dataframe(filtered_df)

                        # Generate CSV in memory
                        csv_data = filtered_df.to_csv(index=False).encode("utf-8")

                        # Streamlit Download Button
                        st.download_button(
                            label="Download Filtered Tweets as CSV",
                            data=csv_data,
                            file_name=f"{username}_archived_tweets.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("No tweets match the specified filters.")
                else:
                    st.warning("No archived tweets found for the given username.")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    
    # Footer with Copyright
    st.markdown("""
    ---
    © 2025, All rights reserved.
    Developed by ECLOGIC.
    """)

# Run the app
if __name__ == "__main__":
    wayback_tweets_main()

