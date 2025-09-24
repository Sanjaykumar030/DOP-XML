import re
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_video_details(api_key, video_url):
    """
    Fetches details for a given YouTube video URL.

    Args:
        api_key (str): Your YouTube Data API v3 key.
        video_url (str): The URL of the YouTube video.

    Returns:
        dict: A dictionary containing the video details, or None if an error occurs.
    """
    # Regex to extract video ID from various YouTube URL formats
    video_id_match = (
        re.search(r"(?<=v=)[\w-]+", video_url) or
        re.search(r"(?<=be/)[\w-]+", video_url) or
        re.search(r"(?<=embed/)[\w-]+", video_url)
    )

    if not video_id_match:
        print("Error: Could not extract video ID from the URL.")
        return None

    video_id = video_id_match.group(0)

    try:
        # Build the YouTube API client
        youtube = build("youtube", "v3", developerKey=api_key)

        # Request video details
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics,status",
            id=video_id
        )

        response = request.execute()

        if not response.get('items'):
            print("Error: Video not found or API request failed.")
            return None

        return response['items'][0]

    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def print_video_details(video):
    """Prints the extracted video details in an organized manner."""
    if not video:
        return

    # Extract details from the video object
    snippet = video.get('snippet', {})
    content_details = video.get('contentDetails', {})
    statistics = video.get('statistics', {})
    status = video.get('status', {})

    title = snippet.get('title', 'N/A')
    description = snippet.get('description', 'N/A')
    published = snippet.get('publishedAt', 'N/A')
    channel = snippet.get('channelTitle', 'N/A')
    channel_id = snippet.get('channelId', 'N/A')
    tags = snippet.get('tags', [])
    category_id = snippet.get('categoryId', 'N/A')
    duration = content_details.get('duration', 'N/A')
    views = statistics.get('viewCount', 'N/A')
    likes = statistics.get('likeCount', 'N/A')
    comments = statistics.get('commentCount', 'N/A')
    privacy = status.get('privacyStatus', 'N/A')
    video_url = f"https://www.youtube.com/watch?v={video['id']}"

    # Print in an organized manner
    print("\n=== YouTube Video Details ===")
    print(f"Title       : {title}")
    print(f"Channel     : {channel} (ID: {channel_id})")
    print(f"Published   : {published}")
    print(f"Category ID : {category_id}")
    print(f"Duration    : {duration}")
    print(f"Views       : {views}")
    print(f"Likes       : {likes}")
    print(f"Comments    : {comments}")
    print(f"Privacy     : {privacy}")
    print(f"Tags        : {', '.join(tags) if tags else 'None'}")
    print(f"URL         : {video_url}")
    print(f"Description :\n{description[:400]}...") # Print first 400 chars of description
    print("============================")


if _name_ == "_main_":
    api_key = "AIzaSyC-XYZ" 

    if api_key == "YOUR_API_KEY":
        print("Please replace 'YOUR_API_KEY' with your actual YouTube Data API key.")
    else:
        # Get user input for the video URL
        video_url_input = input("Please enter the YouTube video URL: ")
        
        # Get and print the details
        video_details = get_video_details(api_key, video_url_input)
        print_video_details(video_details)
