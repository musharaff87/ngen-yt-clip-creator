import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta, timezone

def get_authenticated_service():
    # Load credentials from the JSON file
    with open("youtube_secrets.json", "r") as file:
        creds_data = json.load(file)

    creds = Credentials(
        token=creds_data["access_token"],
        refresh_token=creds_data["refresh_token"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=creds_data["scopes"]
    )

    # Build the YouTube API client with the credentials
    youtube = build("youtube", "v3", credentials=creds)
    return youtube

def upload_video(video_file, title, description, tags, category_id, publish_time):
    youtube = get_authenticated_service()
    ist_offset = timedelta(hours=5, minutes=30)
    publish_time = publish_time - ist_offset
    # Prepare the video metadata
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "private",  # Video will be private until publish time
            "license": "youtube",
            "publishAt": publish_time.isoformat(),  # Schedule publish time
            "selfDeclaredMadeForKids": False  # Set whether the video is made for kids
        }
    }

    # Create media file upload instance
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype="video/*")

    # Call YouTube API to upload the video
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%.")

    print("Upload Complete!")
    return response


if __name__ == "__main__":
    # Authenticate and initialize the YouTube API service
    #youtube = get_authenticated_service()

    # Define video details
    video_file = "video_outputs/Did you know that Taylor Swift just broke the record for the most Billboard Hot 100 entries by a female artist_ 🤯.mp4"
    title = "TAYLOR SWIFT BREAKS BILLBOARD RECORD! 🤯 Most Hot 100 Entries EVER by a WOMAN"
    description = "You won't believe this! Taylor Swift just shattered the record for the most Billboard Hot 100 entries by a female artist!  🤯  This is HUGE news for Swifties and music lovers everywhere.  Check out this video to see why Taylor is truly the QUEEN of the charts! 👑"
    tags = ['Taylor Swift', 'Billboard Hot 100', 'Record', 'Music', 'Female Artist', 'Pop Music', 'Swifties', 'Music News', 'Chart History', 'Queen of Pop', 'Music Charts', 'Billboard', 'Latest Music', 'Trending Music', 'Taylor Swift News']
    category_id = "22"  # 22 is for 'People & Blogs'. Adjust based on your content.

    # Get publish time input in IST from user
    ist_publish_time_str = "2024-11-05 10:00" #input("Enter the publish time in IST (format: YYYY-MM-DD HH:MM): ")
    ist_publish_time = datetime.strptime(ist_publish_time_str, "%Y-%m-%d %H:%M")

    # Convert IST to UTC
    ist_offset = timedelta(hours=5, minutes=30)
    publish_time = ist_publish_time #- ist_offset  # Convert IST time to UTC

    # Upload the video
    upload_response = upload_video(video_file, title, description, tags, category_id, publish_time)

    # Print the response
    print(f"Video uploaded. Video ID: {upload_response['id']}")