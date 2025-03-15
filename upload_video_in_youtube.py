import os
import shutil
import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
from database import update_video_status  # Import to update status
import time

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CREDENTIALS_FILE = "youtube_credentials.json"

def authenticate_youtube():
    """Authenticate with YouTube API, reusing credentials if available."""
    credentials = None

    # Load existing credentials if they exist
    if os.path.exists(CREDENTIALS_FILE):
        credentials = Credentials.from_authorized_user_file(CREDENTIALS_FILE, SCOPES)

    # If no valid credentials, authenticate and save them
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret_2.json", SCOPES)
            credentials = flow.run_local_server(port=8080)
            # Save credentials for future use
            with open(CREDENTIALS_FILE, 'w') as creds_file:
                creds_file.write(credentials.to_json())

    return build("youtube", "v3", credentials=credentials)


def upload_video(video_id, video_file, title, description, tags, category_id, publish_time):
    category_id = "24"
    """Call the new app's API to upload a video with the file."""
    api_url = "https://mushtastic-intelligence.com/api/upload_video"

    # Prepare the files and data for the multipart request
    #files = {'video_file': open(video_file, 'rb')}
    data = {
        "video_id": video_id,
        "title": title,
        "description": description,
        "tags": ",".join(tags),
        "category_id": category_id,
        "publish_time": publish_time.isoformat()
    }

    with open(video_file, 'rb') as video_handle:
        files = {'video_file': video_handle}
        response = requests.post(api_url, files=files, data=data)
        response.raise_for_status()  # Raise an exception for bad status codes
        result = response.json()
        print("----------------------------------------------------------------------")
        print(result["message"])

    try:
        # update_video_status(video_id, "Uploaded Successfully")
        #
        # # Move video to old_videos directory
        # old_videos_dir = os.path.join("video_outputs", "old_videos")
        # os.makedirs(old_videos_dir, exist_ok=True)
        # new_file_path = os.path.join(old_videos_dir, os.path.basename(video_file))
        #
        # time.sleep(5)
        # max_attempts = 5
        # for attempt in range(max_attempts):
        #     try:
        #         os.rename(video_file, new_file_path)
        #         print(f"Video moved to: {new_file_path}")
        #         break
        #     except PermissionError as e:
        #         if attempt < max_attempts - 1:
        #             print(f"Attempt {attempt + 1} failed: {e}. Retrying in 1 second...")
        #             time.sleep(1)
        #         else:
        #             print(f"Failed to move video after {max_attempts} attempts: {e}")
        #             raise

        return result["response"]
    except requests.exceptions.RequestException as e:
        print(f"Failed to upload video: {e}")
        #update_video_status(video_id, "Upload Failed")
        raise
    finally:
        files['video_file'].close()
def upload_video_old(video_id, video_file, title, description, tags, category_id, publish_time):
    category_id = "24"
    """Upload a video to YouTube and update its status."""

    title = title + " #shorts"
    youtube = authenticate_youtube()
    ist_offset = timedelta(hours=5, minutes=30)
    publish_time = publish_time - ist_offset  # Convert IST to UTC

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": "private",
            "license": "youtube",
            "publishAt": publish_time.isoformat(),
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype="video/*")
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
    # Update status in database after successful upload
    # update_video_status(video_id, "Uploaded Successfully")
    #
    # old_videos_dir = os.path.join("video_outputs", "old_videos")
    # os.makedirs(old_videos_dir, exist_ok=True)  # Create directory if it doesn’t exist
    # new_file_path = os.path.join(old_videos_dir, os.path.basename(video_file))
    #
    # # Ensure the file is no longer in use by retrying the move with a small delay
    # max_attempts = 5
    # for attempt in range(max_attempts):
    #     try:
    #         shutil.move(video_file, new_file_path)
    #         os.remove(video_file)
    #         print(f"Video moved to: {new_file_path}")
    #         break
    #     except PermissionError as e:
    #         if attempt < max_attempts - 1:
    #             print(f"Attempt {attempt + 1} failed: {e}. Retrying in 1 second...")
    #             import time
    #             time.sleep(1)  # Wait briefly before retrying
    #         else:
    #             print(f"Failed to move video after {max_attempts} attempts: {e}")
    #             raise  # Re-raise the exception if all attempts fail
    return response

if __name__ == "__main__":
    video_file = "video_outputs/got.mp4"
    title = "Unbelievable Game of Thrones Revelation: The Stark Who Served as Hand Before Ned!"
    description = """[Your description here]"""
    tags = ['game of thrones stark family', 'ned stark hand of the king']
    category_id = "24"
    ist_publish_time = datetime.strptime("2025-02-25 11:30", "%Y-%m-%d %H:%M")
    upload_response = upload_video(1, video_file, title, description, tags, category_id, ist_publish_time)  # Dummy video_id
    print(f"Video uploaded. Video ID: {upload_response['id']}")