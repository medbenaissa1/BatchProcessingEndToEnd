import datetime as dt
import json
import os

from dotenv import load_dotenv
from endpoint import (
    get_paginated_featured_playlists,
    get_paginated_spotify_playlist,
)
from authentication import get_token

# Load environment variables
load_dotenv("./env", override=True)

CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")

# Spotify API URLs
URL_TOKEN = "https://accounts.spotify.com/api/token"
URL_FEATURE_PLAYLISTS = "https://api.spotify.com/v1/browse/featured-playlists"
URL_PLAYLIST_ITEMS = "https://api.spotify.com/v1/playlists"
PLAYLIST_ITEMS_FIELDS = (
    "href,name,owner(!href,external_urls),items(added_at,track(name,href,album(name,href),artists(name,href))),"
    "offset,limit,next,previous,total"
)

def main():
    # Step 1: Getting an access token
    kwargs = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "url": URL_TOKEN,
    }

    try:
        token = get_token(**kwargs)

        if not token or "access_token" not in token:
            print("Failed to obtain access token.")
            return

    except Exception as e:
        print(f"Error during token retrieval: {e}")
        return

    # Step 2: Get the featured playlists
    featured_playlists = get_paginated_featured_playlists(
        base_url=URL_FEATURE_PLAYLISTS,
        access_token=token.get("access_token"),
        get_token=get_token,
        **kwargs,
    )

    if not featured_playlists:
        print("No featured playlists were found.")
        return

    print("Featured playlists have been extracted.")

    # Step 3: Extract playlist IDs
    playlists_ids = [playlist["id"] for playlist in featured_playlists]
    print(f"Total number of featured playlists extracted: {len(playlists_ids)}")

    # Step 4: Fetch information for each playlist
    print("Fetching detailed information for each playlist...")
    playlists_items = {}

    for playlist_id in playlists_ids:
        try:
            playlist_data = get_paginated_spotify_playlist(
                base_url=URL_PLAYLIST_ITEMS,
                access_token=token.get("access_token"),
                playlist_id=playlist_id,
                fields=PLAYLIST_ITEMS_FIELDS,
                get_token=get_token,
                **kwargs,
            )

            if playlist_data:
                playlists_items[playlist_id] = playlist_data
                print(f"Playlist {playlist_id} has been processed successfully.")

        except Exception as e:
            print(f"Error processing playlist {playlist_id}: {e}")

    # Step 5: Save data to JSON file
    if playlists_items:
        current_time = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        filename = f"playlist_items_{current_time}.json"

        try:
            with open(f"./{filename}", "w") as playlists_file:
                json.dump(playlists_items, playlists_file, indent=4)

            print(f"Data has been saved successfully to {filename}")
        except Exception as e:
            print(f"Error saving data to file: {e}")
    else:
        print("No data was available to be saved.")


if __name__ == "__main__":
    main()

