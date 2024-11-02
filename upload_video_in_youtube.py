from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from datetime import datetime, timedelta, timezone

# Replace these with your actual tokens
ACCESS_TOKEN = "ya29.a0AeDClZBAdTJTJTxQly5gTA9HZPOBh-ifJN8J5TFEjGnUhx29GrBg18QSfdY8wwz51mZOCwqO_RpZKQjLvSTcIg-tSNsy3xm6XB0yL2Gnrq6qtsWSjNhCzZUfsf2zjkWJGUTMFGbP4Sp4U3Pt6H05lUdZNbvarrZ25ARbzJDlaCgYKAaASARISFQHGX2MijpNTEUkhs2LEuDm3zS6hzA0175"
REFRESH_TOKEN = "1//04KRAh_caalhzCgYIARAAGAQSNwF-L9IrYlVZTd8acpOmIEu3gjL4SAfKsKWxtAoGDak9p7axLpvCHDTGdNHhHmnOIhe_API0UFQ"
CLIENT_ID = "917617153669-gjvkjgie84mc81l65a4pqjfdhqgf2mn1.apps.googleusercontent.com"  # Replace with your client ID
CLIENT_SECRET = "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"  # Replace with your client secret
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service():
    # Load credentials from existing access and refresh tokens
    creds = Credentials(
        token=ACCESS_TOKEN,
        refresh_token=REFRESH_TOKEN,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES
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
            "selfDeclaredMadeForKids": True  # Set whether the video is made for kids
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
    video_file = "video_outputs/history_Ballon_dor_football_award_created.mp4"
    title = "The History of the BALLON D'OR: Football's Most Prestigious Award"
    description = "Discover the fascinating history of the Ballon d'Or, football's most prestigious award. From its inception by France Football in 1956, the Ballon d'Or has become the ultimate prize, awarded annually to the player voted the best in the world. Learn how legends like Messi, Ronaldo, and other football greats have made their mark on this legacy of excellence, skill, and global influence in the game."
    tags = [
        "Ballon d'Or",
        "Football Awards",
        "Best Football Players",
        "Lionel Messi",
        "Cristiano Ronaldo",
        "Cr7",
        "GOAT",
        "2024 Ballon d'Or",
        "Football Highlights",
        "World Cup",
        "Champions League",
        "Top Football Players",
        "Football History",
        "Messi vs Ronaldo",
        "Football Skills",
        "FIFA Rankings",
        "Goalkeeper Saves"
    ]
    category_id = "22"  # 22 is for 'People & Blogs'. Adjust based on your content.

    # Get publish time input in IST from user
    ist_publish_time_str = "2024-10-29 02:13" #input("Enter the publish time in IST (format: YYYY-MM-DD HH:MM): ")
    ist_publish_time = datetime.strptime(ist_publish_time_str, "%Y-%m-%d %H:%M")

    # Convert IST to UTC
    ist_offset = timedelta(hours=5, minutes=30)
    publish_time = ist_publish_time - ist_offset  # Convert IST time to UTC

    # Upload the video
    upload_response = upload_video(video_file, title, description, tags, category_id, publish_time)

    # Print the response
    print(f"Video uploaded. Video ID: {upload_response['id']}")